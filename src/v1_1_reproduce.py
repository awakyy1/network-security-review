"""One-command V1.1 verification and deterministic regeneration.

The default profile never calls a language model and never overwrites preserved
research evidence.  External datasets are optional because they are large and
their acquisition is separately controlled by frozen manifests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


def _non_system_path(path: Path) -> Path:
    resolved = path.resolve()
    if os.name == "nt" and resolved.drive.upper() == "C:":
        raise ValueError(f"V1.1 generated data must not use the system drive: {resolved}")
    return resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(command: Sequence[str], cwd: Path, records: list[dict[str, object]]) -> None:
    completed = subprocess.run(list(command), cwd=cwd, check=False, capture_output=True, text=True)
    record = {
        "command": list(command),
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    records.append(record)
    if completed.returncode:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stdout}{completed.stderr}"
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=("Verify V1.1 and regenerate deterministic artifacts without LLM inference.")
    )
    parser.add_argument("--repository-root", type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--ctu13-data-dir", type=Path)
    parser.add_argument("--download-ctu13", action="store_true")
    parser.add_argument("--run-ctu13", action="store_true")
    parser.add_argument("--run-second-dataset", action="store_true")
    parser.add_argument("--skip-tests", action="store_true")
    parser.add_argument("--skip-document", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = _non_system_path(args.repository_root or Path(__file__).resolve().parents[1])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_root = _non_system_path(args.output_root or root / "output" / f"v1.1-reproduction-{stamp}")
    data_dir = _non_system_path(args.ctu13_data_dir or root / "data" / "ctu13")
    runtime_paths = {
        "TEMP": root / ".tmp",
        "TMP": root / ".tmp",
        "MPLCONFIGDIR": root / ".cache" / "matplotlib",
        "TECTONIC_CACHE_DIR": root / ".cache" / "tectonic",
        "PIP_CACHE_DIR": root / ".cache" / "pip",
    }
    for variable, path in runtime_paths.items():
        safe_path = _non_system_path(path)
        safe_path.mkdir(parents=True, exist_ok=True)
        os.environ[variable] = str(safe_path)
    output_root.mkdir(parents=True, exist_ok=False)
    records: list[dict[str, object]] = []
    python = sys.executable

    try:
        if not args.skip_tests:
            _run([python, "-m", "pytest", "-q"], root, records)
            _run([python, "-m", "ruff", "check", "src", "tests"], root, records)
            _run(
                [python, "-m", "ruff", "format", "--check", "src", "tests"],
                root,
                records,
            )

        _run(
            [
                python,
                "src/nmap_to_zabbix.py",
                "--input",
                "examples/nmap/synthetic-enterprise.xml",
                "--output-dir",
                str(output_root / "synthetic-report"),
            ],
            root,
            records,
        )
        _run(
            [python, "-m", "src.v2_experiment", "--output-dir", str(output_root / "phase-a")],
            root,
            records,
        )
        _run(
            [
                python,
                "-m",
                "src.endpoint_experiment",
                "--manifest",
                "research/v1.1/endpoint-scenarios.json",
                "--output-dir",
                str(output_root / "endpoint"),
            ],
            root,
            records,
        )
        _run(
            [
                python,
                "-m",
                "src.counterfactual_policies",
                "--repository-root",
                str(root),
                "--output-dir",
                str(output_root / "counterfactual"),
            ],
            root,
            records,
        )

        if args.download_ctu13 or args.run_ctu13:
            command = [
                python,
                "-m",
                "src.ctu13_acquire",
                "--data-dir",
                str(data_dir),
            ]
            if args.download_ctu13:
                command.append("--download")
            _run(command, root, records)
        if args.run_ctu13:
            _run(
                [
                    python,
                    "-m",
                    "src.ctu13_analysis",
                    "--data-dir",
                    str(data_dir),
                    "--output-dir",
                    str(output_root / "ctu13-retrospective"),
                    "--window-seconds",
                    "60",
                    "300",
                    "600",
                ],
                root,
                records,
            )
        if args.run_second_dataset:
            _run(
                [
                    python,
                    "-m",
                    "src.second_dataset_experiment",
                    "--manifest",
                    "research/v1.1/second-dataset-run-2026-08-15.json",
                    "--output-dir",
                    str(output_root / "second-dataset"),
                ],
                root,
                records,
            )

        _run([python, "-m", "src.article_tables"], root, records)
        _run([python, "-m", "src.article_figures"], root, records)

        pdf = root / "academic" / "artigo" / "build-v1.1" / "main.pdf"
        if not args.skip_document:
            tectonic = shutil.which("tectonic")
            bundled = root / ".tools" / "tectonic" / "tectonic.exe"
            if tectonic is None and bundled.exists():
                tectonic = str(bundled)
            if tectonic is None:
                raise RuntimeError("Tectonic was not found; use --skip-document if intentional")
            _run(
                [tectonic, "-X", "compile", "main.tex", "--outdir", "build-v1.1"],
                root / "academic" / "artigo",
                records,
            )

        report = {
            "schema_version": "1.0",
            "status": "complete",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "repository_root": str(root),
            "output_root": str(output_root),
            "llm_inference_performed": False,
            "external_options": {
                "download_ctu13": args.download_ctu13,
                "run_ctu13": args.run_ctu13,
                "run_second_dataset": args.run_second_dataset,
            },
            "commands": records,
            "pdf": ({"path": str(pdf), "sha256": _sha256(pdf), "bytes": pdf.stat().st_size} if pdf.exists() else None),
        }
        report_path = output_root / "verification-report.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"V1.1 verification complete: {report_path}")
        return 0
    except Exception as exc:
        failure = {
            "schema_version": "1.0",
            "status": "failed",
            "error": str(exc),
            "commands": records,
        }
        (output_root / "verification-report.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
