"""Draw vector article figures from frozen results; no inference or detector reruns."""

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
from matplotlib.patches import FancyArrowPatch  # noqa: E402

INK, SECONDARY, RULE, GRID = "#20252B", "#68717A", "#B8BEC4", "#E8EBEE"
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["STIXGeneral"],
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": RULE,
        "axes.linewidth": 0.65,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": SECONDARY,
        "ytick.color": INK,
        "xtick.labelsize": 9,
        "ytick.labelsize": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": "white",
    }
)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def empirical_overlap(first: list[int], second: list[int]) -> float:
    """Return overlap of the exact-value empirical probability masses."""
    if not first or not second:
        raise ValueError("Overlap requires two non-empty samples")
    first_counts, second_counts = Counter(first), Counter(second)
    support = first_counts.keys() | second_counts.keys()
    return sum(min(first_counts[x] / len(first), second_counts[x] / len(second)) for x in support)


def _save(fig: plt.Figure, output: Path, stem: str) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    paths = []
    for suffix in ("pdf", "png"):
        path = output / f"{stem}.{suffix}"
        metadata = {"CreationDate": None, "ModDate": None} if suffix == "pdf" else None
        fig.savefig(path, bbox_inches="tight", pad_inches=0.06, dpi=300, metadata=metadata)
        paths.append(path)
    plt.close(fig)
    return paths


def architecture_figure(output: Path) -> list[Path]:
    fig, ax = plt.subplots(figsize=(7.2, 2.05))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 7.2), ylim=(0, 2.05))
    ax.axis("off")
    centers = [0.66, 2.12, 3.58, 5.04, 6.50]
    stages = [
        ("Evidence", "Nmap inventory\nNetwork events\nEndpoint events"),
        ("Rule evaluation", "Normalize events\nApply fixed rules\nAssign evidence IDs"),
        ("Local model", "Prioritize findings\nPropose controls\nNo execution access"),
        ("Output validator", "Check schema\nVerify evidence IDs\nEnforce policy"),
        ("Analyst", "Review evidence\nConfirm incident\nAuthorize response"),
    ]
    for x, (title, body) in zip(centers, stages, strict=True):
        ax.plot([x - 0.61, x + 0.61], [1.52, 1.52], color=INK, lw=0.8)
        ax.text(x, 1.34, title, ha="center", va="center", fontsize=10, fontweight="bold")
        ax.text(x, 0.82, body, ha="center", va="center", fontsize=9, linespacing=1.45)
    for left, right in zip(centers, centers[1:]):
        ax.add_patch(
            FancyArrowPatch(
                (left + 0.63, 1.34), (right - 0.63, 1.34), arrowstyle="-|>", mutation_scale=8, lw=0.7, color=SECONDARY
            )
        )
    for x in (2.85, 4.31):
        ax.plot([x, x], [0.38, 1.78], color=SECONDARY, lw=0.7, linestyle=(0, (3, 3)))
    ax.text(3.58, 1.88, "UNTRUSTED GENERATION", ha="center", fontsize=8, color=SECONDARY)
    ax.text(
        3.60,
        0.13,
        "Rejected outputs stop at the validator; model output never authorizes an action.",
        ha="center",
        va="center",
        fontsize=9,
        color=SECONDARY,
    )
    return _save(fig, output, "architecture-trust-boundaries")


def experimental_flow_figure(output: Path) -> list[Path]:
    """Map distinct evidence roles without implying sequential data flow."""
    fig, ax = plt.subplots(figsize=(7.2, 3.15))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 7.2), ylim=(0, 3.15))
    ax.axis("off")
    columns = (0.06, 1.30, 4.22)
    for x, title in zip(columns, ("Evaluation", "Evidence", "What it evaluates"), strict=True):
        ax.text(x, 2.94, title, fontsize=10, fontweight="bold", va="center")
    ax.plot([0.04, 7.15], [2.76, 2.76], lw=0.8, color=INK)
    rows = [
        ("A  Functional", "Constructed network and endpoint cases", "Implementation conformance"),
        ("B1  Historical", "Virut development; NSIS.ay holdout", "Rule errors and window sensitivity"),
        ("B2  Prospective", "RBot development; frozen DonBot holdout", "Performance on one unseen family"),
        ("B3  Transfer", "CTU-13-derived synthetic flows", "Parser and representation transfer"),
        ("C  Local LLM", "Three models; prompts and adversarial pairs", "Traceability, policy and availability"),
    ]
    for i, row in enumerate(rows):
        y = 2.48 - i * 0.46
        for x, value in zip(columns, row, strict=True):
            ax.text(x, y, value, fontsize=9, va="center")
        ax.plot([0.04, 7.15], [y - 0.23, y - 0.23], lw=0.5, color=RULE)
    ax.text(
        0.06,
        0.16,
        "Not evaluated: benefit to analysts, production effectiveness or live containment.",
        fontsize=9,
        color=SECONDARY,
        va="center",
    )
    return _save(fig, output, "experimental-flow")


def ctu_metrics_figure(root: Path, output: Path) -> list[Path]:
    historical = _read_json(root / "research/v2/results/ctu13-external-validation-v1.json")
    development = _read_json(
        root / "research/v1.1/results/ctu13-confirmatory-development-2026-08-15/development-tuning.json"
    )
    holdout = _read_json(root / "research/v1.1/results/ctu13-confirmatory-holdout-2026-08-15/confirmatory-holdout.json")
    by_role = {item["role"]: item for item in historical["sources"]}
    datasets = [
        ("Virut / development", by_role["development"]["metrics"]),
        ("NSIS.ay / inspected holdout", by_role["holdout"]["metrics"]),
        ("RBot / development", development["selected"]["metrics"]),
        ("DonBot / frozen holdout", holdout["evaluation"]["metrics"]),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
    fig.subplots_adjust(left=0.29, right=0.96, top=0.82, bottom=0.13, wspace=0.32)
    y = [3.4, 2.4, 1.0, 0.0]
    for ax, metric, title, marker in zip(
        axes, ("f1", "matthews_correlation_coefficient"), ("F1", "MCC"), ("o", "s"), strict=True
    ):
        values = [row[1][metric] for row in datasets]
        ax.set_axisbelow(True)
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.axvline(0, color=RULE, lw=0.8)
        ax.scatter(values, y, s=25, marker=marker, color=INK, zorder=3)
        for value, row_y in zip(values, y, strict=True):
            ax.annotate(
                f"{value:.3f}", (value, row_y), xytext=(7, 0), textcoords="offset points", va="center", fontsize=9
            )
        ax.set_title(title, fontsize=11, fontweight="bold", loc="left", pad=15)
        ax.set_ylim(-0.5, 3.9)
        ax.axhline(1.7, color=RULE, lw=0.65, linestyle=(0, (3, 3)))
        ax.tick_params(axis="y", length=0, pad=8)
        ax.spines["left"].set_visible(False)
        ax.set_xlim((-0.06, 1.13) if metric == "f1" else (-1.08, 1.13))
        ax.set_xticks([0, 0.5, 1] if metric == "f1" else [-1, 0, 1])
    axes[0].set_yticks(y, [row[0] for row in datasets])
    return _save(fig, output, "ctu13-development-holdout-metrics")


def traceability_figure(root: Path, output: Path) -> list[Path]:
    result = _read_json(root / "research/v2/results/phase-c-comparison-v1.json")
    grounded, historical = result["phase_a"]["grounded"], result["phase_a"]["historical"]
    labels = ["Exact finding IDs", "Exact evidence IDs", "Accepted under exact-ID policy"]
    values = [
        [grounded["exact_finding_coverage"], grounded["exact_evidence_coverage"], grounded["accepted"]],
        [historical["exact_finding_coverage"], historical["exact_evidence_coverage"], historical["grounding_valid"]],
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    fig.subplots_adjust(left=0.30, right=0.91, top=0.73, bottom=0.28)
    for counts, offset, marker, color, label in zip(
        values, (0.13, -0.13), ("o", "s"), (INK, SECONDARY), ("Grounded schema", "Reconstructed free text"), strict=True
    ):
        positions = [2 + offset, 1 + offset, offset]
        ax.scatter(counts, positions, s=25, marker=marker, color=color, label=label, zorder=3)
        for count, row_y in zip(counts, positions, strict=True):
            ax.annotate(
                f"{count}/50",
                (count, row_y),
                xytext=(7, 0),
                textcoords="offset points",
                va="center",
                fontsize=9,
                color=color,
            )
    ax.set(xlim=(-2, 57), ylim=(-0.45, 2.45))
    ax.set_yticks([2, 1, 0], labels)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.tick_params(axis="y", length=0, pad=8)
    ax.spines["left"].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.legend(frameon=False, ncols=2, loc="lower left", bbox_to_anchor=(-0.01, 1.10), handletextpad=0.4)
    fig.text(
        0.30,
        0.07,
        "Protocols differ in instructions, decoding and format.\nThese counts measure traceability, not comparative analyst benefit.",
        fontsize=9,
        color=SECONDARY,
        linespacing=1.3,
    )
    return _save(fig, output, "grounded-free-text-traceability")


def beh002_distribution_figure(root: Path, output: Path) -> list[Path]:
    result = _read_json(
        root / "research/v1.1/results/ctu13-retrospective-window-analysis-2026-08-15/ctu13-window-analysis.json"
    )
    analysis = next(item for item in result["analyses"] if item["role"] == "holdout" and item["window_seconds"] == 300)
    values = {"botnet-origin": [], "normal-origin": []}
    for unit in analysis["units"]:
        values[unit["truth"]].append(unit["features"]["maximum_distinct_endpoints_in_60_seconds"])
    overlap = empirical_overlap(values["botnet-origin"], values["normal-origin"])
    fig, ax = plt.subplots(figsize=(7.2, 3.55))
    fig.subplots_adjust(left=0.10, right=0.98, top=0.86, bottom=0.19)
    for truth, color, linestyle in (("botnet-origin", INK, "-"), ("normal-origin", SECONDARY, (0, (4, 3)))):
        ordered = sorted(values[truth])
        cumulative = [(i + 1) / len(ordered) for i in range(len(ordered))]
        ax.step(
            ordered,
            cumulative,
            where="post",
            color=color,
            linestyle=linestyle,
            lw=1.6,
            label=f"{truth} (n={len(ordered)})",
        )
    ax.axvline(8, color=SECONDARY, linestyle=":", lw=1.1)
    ax.text(8, 1.04, "Threshold = 8", fontsize=9, ha="center", va="bottom", color=SECONDARY)
    ax.set(xscale="log", ylim=(0, 1.02))
    ax.set_xlabel("Maximum distinct destinations in a 60-second interval (log scale)", labelpad=8)
    ax.set_ylabel("Cumulative proportion", labelpad=8)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.legend(frameon=False, loc="lower right", handlelength=2.7)
    fig.text(0.10, 0.96, f"Exact-value empirical overlap: {overlap:.3f}", fontsize=9, color=SECONDARY)
    return _save(fig, output, "beh002-holdout-distributions")


def generate_figures(repository_root: str | Path) -> list[Path]:
    root = Path(repository_root).resolve()
    output = root / "academic/artigo/generated/figures"
    return (
        architecture_figure(output)
        + experimental_flow_figure(output)
        + ctu_metrics_figure(root, output)
        + traceability_figure(root, output)
        + beh002_distribution_figure(root, output)
    )


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
