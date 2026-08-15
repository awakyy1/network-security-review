"""Generate V1.1 article figures from preserved results and declared architecture."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(REPOSITORY_ROOT / ".cache" / "matplotlib"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

BLUE = "#2F2F2F"
ORANGE = "#777777"
GREEN = "#555555"
RED = "#1F1F1F"
GRAY = "#666666"
LIGHT_GRAY = "#F3F3F3"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def empirical_overlap(first: list[int], second: list[int]) -> float:
    """Return the discrete empirical overlap coefficient on exact observed values."""
    if not first or not second:
        raise ValueError("Overlap requires two non-empty samples")
    first_counts = Counter(first)
    second_counts = Counter(second)
    support = first_counts.keys() | second_counts.keys()
    return sum(min(first_counts[item] / len(first), second_counts[item] / len(second)) for item in support)


def _save(fig: plt.Figure, output: Path, stem: str) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("pdf", "png"):
        path = output / f"{stem}.{suffix}"
        fig.savefig(path, bbox_inches="tight", dpi=300)
        paths.append(path)
    plt.close(fig)
    return paths


def architecture_figure(output: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(7.2, 2.25))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    boxes = [
        (0.02, "1. Evidence", "Nmap inventory\nNetwork and endpoint events"),
        (0.27, "2. Detection", "Validation and rules\nStable evidence identifiers"),
        (0.52, "3. LLM review", "Local inference\nSchema and output validator"),
        (0.77, "4. Human decision", "Independent confirmation\nOptional reversible action"),
    ]
    for x, title, body in boxes:
        patch = FancyBboxPatch(
            (x, 0.29),
            0.21,
            0.42,
            boxstyle="round,pad=0.012,rounding_size=0.02",
            linewidth=1.1,
            edgecolor=RED,
            facecolor=LIGHT_GRAY,
        )
        ax.add_patch(patch)
        ax.text(
            x + 0.105,
            0.60,
            title,
            ha="center",
            va="center",
            fontsize=7.7,
            weight="bold",
            color=RED,
            linespacing=1.0,
        )
        ax.text(x + 0.105, 0.41, body, ha="center", va="center", fontsize=6.4, linespacing=1.25)
    for x in (0.23, 0.48, 0.73):
        ax.add_patch(FancyArrowPatch((x, 0.5), (x + 0.035, 0.5), arrowstyle="-|>", mutation_scale=12, color=GRAY))
    ax.text(0.625, 0.14, "The model has no credentials or direct containment path", ha="center", fontsize=7.5)
    return _save(fig, output, "architecture-trust-boundaries")


def experimental_flow_figure(output: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(5.8, 4.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def box(y: float, height: float, title: str, body: str) -> None:
        x = 0.20
        width = 0.60
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                width,
                height,
                boxstyle="round,pad=0.01",
                linewidth=1.1,
                edgecolor=RED,
                facecolor=LIGHT_GRAY,
            )
        )
        ax.text(
            x + width / 2,
            y + height * 0.70,
            title,
            ha="center",
            va="center",
            weight="bold",
            color=RED,
            fontsize=8,
        )
        ax.text(x + width / 2, y + height * 0.35, body, ha="center", va="center", fontsize=6.8, linespacing=1.3)

    box(0.80, 0.14, "Phase A: functional checks", "Inert fixtures and endpoint truth matrix")
    box(
        0.43,
        0.28,
        "Phase B: detector evaluation",
        "B1: inspected CTU-13 diagnostics\nB2: RBot development and DonBot holdout\nB3: synthetic implementation transfer",
    )
    box(0.22, 0.14, "Phase C: local LLM evaluation", "Three models, three prompts, adversarial tests and ablations")
    box(0.01, 0.14, "Human assessment", "Not performed in this revision; no automatic actions")
    for start, end in ((0.80, 0.71), (0.43, 0.36), (0.22, 0.15)):
        ax.add_patch(FancyArrowPatch((0.5, start), (0.5, end), arrowstyle="-|>", mutation_scale=11, color=GRAY))
    return _save(fig, output, "experimental-flow")


def ctu_metrics_figure(root: Path, output: Path) -> list[Path]:
    historical = _read_json(root / "research" / "v2" / "results" / "ctu13-external-validation-v1.json")
    prospective_development = _read_json(
        root / "research" / "v1.1" / "results" / "ctu13-confirmatory-development-2026-08-15" / "development-tuning.json"
    )
    prospective_holdout = _read_json(
        root / "research" / "v1.1" / "results" / "ctu13-confirmatory-holdout-2026-08-15" / "confirmatory-holdout.json"
    )
    historical_by_role = {item["role"]: item for item in historical["sources"]}
    datasets = [
        ("Virut\nhistorical dev.", historical_by_role["development"]["metrics"]),
        ("NSIS.ay\ninspected holdout", historical_by_role["holdout"]["metrics"]),
        ("RBot\nprospective dev.", prospective_development["selected"]["metrics"]),
        ("DonBot\nfrozen holdout", prospective_holdout["evaluation"]["metrics"]),
    ]
    x = list(range(len(datasets)))
    width = 0.34
    f1 = [item[1]["f1"] for item in datasets]
    mcc = [item[1]["matthews_correlation_coefficient"] for item in datasets]
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar([item - width / 2 for item in x], f1, width, label="F1", color=BLUE)
    ax.bar(
        [item + width / 2 for item in x],
        mcc,
        width,
        label="MCC",
        color=ORANGE,
        edgecolor="black",
        hatch="//",
    )
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylim(-0.4, 1.0)
    ax.set_ylabel("Metric value")
    ax.set_xticks(x, [item[0] for item in datasets])
    ax.legend(frameon=False, ncols=2, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    ax.text(0.5, -0.25, "Historical inspected pair", ha="center", transform=ax.get_xaxis_transform(), fontsize=8)
    ax.text(2.5, -0.25, "Prospectively gated pair", ha="center", transform=ax.get_xaxis_transform(), fontsize=8)
    return _save(fig, output, "ctu13-development-holdout-metrics")


def traceability_figure(root: Path, output: Path) -> list[Path]:
    result = _read_json(root / "research" / "v2" / "results" / "phase-c-comparison-v1.json")
    grounded = result["phase_a"]["grounded"]
    historical = result["phase_a"]["historical"]
    labels = ["Exact finding IDs", "Exact evidence IDs", "System accepted"]
    grounded_values = [
        grounded["exact_finding_coverage"],
        grounded["exact_evidence_coverage"],
        grounded["accepted"],
    ]
    historical_values = [
        historical["exact_finding_coverage"],
        historical["exact_evidence_coverage"],
        historical["grounding_valid"],
    ]
    x = list(range(len(labels)))
    width = 0.36
    fig, ax = plt.subplots(figsize=(6.7, 3.3))
    ax.bar([item - width / 2 for item in x], grounded_values, width, label="Grounded schema", color=BLUE)
    ax.bar(
        [item + width / 2 for item in x],
        historical_values,
        width,
        label="Reconstructed free text",
        color=ORANGE,
        edgecolor="black",
        hatch="//",
    )
    ax.set_ylim(0, 55)
    ax.set_ylabel("Responses out of 50")
    ax.set_xticks(x, labels)
    ax.legend(frameon=False, ncols=2, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    ax.grid(axis="y", alpha=0.25)
    for positions, values in (
        ([item - width / 2 for item in x], grounded_values),
        ([item + width / 2 for item in x], historical_values),
    ):
        for position, value in zip(positions, values, strict=True):
            ax.text(position, value + 1, str(value), ha="center", va="bottom", fontsize=8)
    return _save(fig, output, "grounded-free-text-traceability")


def beh002_distribution_figure(root: Path, output: Path) -> list[Path]:
    result = _read_json(
        root
        / "research"
        / "v1.1"
        / "results"
        / "ctu13-retrospective-window-analysis-2026-08-15"
        / "ctu13-window-analysis.json"
    )
    analysis = next(item for item in result["analyses"] if item["role"] == "holdout" and item["window_seconds"] == 300)
    values = {"botnet-origin": [], "normal-origin": []}
    for unit in analysis["units"]:
        values[unit["truth"]].append(unit["features"]["maximum_distinct_endpoints_in_60_seconds"])
    overlap = empirical_overlap(values["botnet-origin"], values["normal-origin"])
    fig, ax = plt.subplots(figsize=(6.8, 3.5))
    for truth, color, linestyle in (
        ("botnet-origin", BLUE, "-"),
        ("normal-origin", ORANGE, "--"),
    ):
        ordered = sorted(values[truth])
        cumulative = [(index + 1) / len(ordered) for index in range(len(ordered))]
        ax.step(
            ordered,
            cumulative,
            where="post",
            color=color,
            linestyle=linestyle,
            linewidth=2,
            label=f"{truth} (n={len(ordered)})",
        )
    ax.axvline(8, color="black", linestyle=":", linewidth=1.5, label="BEH-002 threshold = 8")
    ax.set_xscale("log")
    ax.set_xlabel("Maximum distinct destinations in any 60-second interval (log scale)")
    ax.set_ylabel("Empirical cumulative proportion")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, loc="lower right")
    ax.text(0.02, 0.92, f"Exact-value empirical overlap = {overlap:.3f}", transform=ax.transAxes, fontsize=8)
    return _save(fig, output, "beh002-holdout-distributions")


def generate_figures(repository_root: str | Path) -> list[Path]:
    root = Path(repository_root).resolve()
    output = root / "academic" / "artigo" / "generated" / "figures"
    paths = []
    paths.extend(architecture_figure(output))
    paths.extend(experimental_flow_figure(output))
    paths.extend(ctu_metrics_figure(root, output))
    paths.extend(traceability_figure(root, output))
    paths.extend(beh002_distribution_figure(root, output))
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    arguments = parser.parse_args(argv)
    try:
        paths = generate_figures(arguments.repository_root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.error(str(error))
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
