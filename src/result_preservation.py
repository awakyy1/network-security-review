"""Preserve repeated V2 experiment records with hashes and corrected aggregation."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .v2_repetitions import _markdown_report, aggregate_results


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65_536), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read JSON object {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _base_commit(repository_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError(f"Unable to identify repository base commit: {error}") from error
    return result.stdout.strip()


def _scientific_state_files(repository_root: Path) -> list[Path]:
    candidates = [
        *sorted((repository_root / "src").glob("*.py")),
        *sorted((repository_root / "research" / "v2").glob("*.json")),
        *sorted((repository_root / "research" / "v2" / "fixtures").glob("*.jsonl")),
        repository_root / "examples" / "nmap" / "synthetic-enterprise.xml",
        repository_root / "requirements.txt",
        repository_root / "requirements-dev.txt",
        repository_root / "pyproject.toml",
    ]
    return [path for path in candidates if path.is_file()]


def preserve_repeated_results(
    source_directory: str | Path,
    destination_directory: str | Path,
    repository_root: str | Path,
    *,
    execution_source_state: str,
) -> dict[str, Any]:
    """Copy raw records byte-for-byte and regenerate aggregate accounting.

    ``execution_source_state`` must explicitly state whether the hashed source
    snapshot is exact or retrospective. This prevents an uncommitted research
    state from being described as stronger provenance than was actually kept.
    """
    if execution_source_state not in {"exact", "retrospective"}:
        raise ValueError("execution_source_state must be exact or retrospective")
    source = Path(source_directory).resolve()
    destination = Path(destination_directory).resolve()
    root = Path(repository_root).resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Preservation destination is not empty: {destination}")

    original_summary_path = source / "summary.json"
    original_summary = _read_object(original_summary_path)
    run_paths = sorted(source.glob("run-*/benchmark.json"))
    expected_repetitions = int(original_summary.get("repetitions", 0))
    if not run_paths or len(run_paths) != expected_repetitions:
        raise ValueError(
            f"Expected {expected_repetitions} run records from the original summary; found {len(run_paths)}"
        )
    runs = [_read_object(path) for path in run_paths]
    corrected_summary = aggregate_results(runs)
    corrected_summary["model"] = original_summary.get("model")
    corrected_summary["manifest"] = original_summary.get("manifest")

    destination.mkdir(parents=True, exist_ok=True)
    runs_destination = destination / "runs"
    runs_destination.mkdir()
    artifact_records = []
    for index, json_path in enumerate(run_paths, start=1):
        markdown_path = json_path.with_suffix(".md")
        for source_path, suffix in ((json_path, ".json"), (markdown_path, ".md")):
            if not source_path.is_file():
                raise ValueError(f"Missing run artifact: {source_path}")
            target = runs_destination / f"run-{index:03d}{suffix}"
            shutil.copyfile(source_path, target)
            source_hash = _sha256(source_path)
            if _sha256(target) != source_hash:
                raise ValueError(f"Hash mismatch after preserving {source_path}")
            artifact_records.append(
                {
                    "source": source_path.relative_to(root).as_posix(),
                    "preserved": target.relative_to(root).as_posix(),
                    "bytes": source_path.stat().st_size,
                    "sha256": source_hash,
                }
            )

    for name in ("summary.json", "summary.md"):
        source_path = source / name
        target = destination / f"original-{name}"
        shutil.copyfile(source_path, target)
        artifact_records.append(
            {
                "source": source_path.relative_to(root).as_posix(),
                "preserved": target.relative_to(root).as_posix(),
                "bytes": source_path.stat().st_size,
                "sha256": _sha256(source_path),
            }
        )

    preserved_at = datetime.now(timezone.utc).isoformat()
    provenance = {
        "schema_version": "1.0",
        "preserved_at": preserved_at,
        "repository_base_commit": _base_commit(root),
        "execution_source_state": execution_source_state,
        "execution_source_state_note": (
            "The hashes below describe the exact source state used for execution."
            if execution_source_state == "exact"
            else "The execution used an uncommitted source state that was not hashed at launch; the hashes below "
            "are a retrospective preservation snapshot and must not be presented as the exact execution state."
        ),
        "scientific_state_files": [
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in _scientific_state_files(root)
        ],
        "raw_artifacts": artifact_records,
        "accounting_note": (
            "The original aggregate counted deterministic validation rejection as lack of API/JSON/schema success. "
            "The corrected projection separates received API responses, JSON parsing, schema validity, and final "
            "semantic grounding acceptance. Raw run records are preserved byte-for-byte."
        ),
    }
    corrected_summary["preservation"] = {
        "preserved_at": preserved_at,
        "provenance_file": "provenance.json",
        "raw_runs_preserved": len(run_paths),
        "execution_source_state": execution_source_state,
    }
    (destination / "summary.json").write_text(
        json.dumps(corrected_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (destination / "summary.md").write_text(_markdown_report(corrected_summary), encoding="utf-8")
    (destination / "provenance.json").write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return corrected_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory", type=Path)
    parser.add_argument("destination_directory", type=Path)
    parser.add_argument("--repository-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--execution-source-state", choices=("exact", "retrospective"), required=True)
    arguments = parser.parse_args(argv)
    try:
        summary = preserve_repeated_results(
            arguments.source_directory,
            arguments.destination_directory,
            arguments.repository_root,
            execution_source_state=arguments.execution_source_state,
        )
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(
        f"Preserved {summary['repetitions']} {summary['protocol']} repetitions; "
        f"accepted_grounding_rate={summary['ollama']['accepted_grounding_rate']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
