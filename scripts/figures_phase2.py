"""Figures for Phase II (behaviour). Reads the raw campaign files and the saved analysis; writes PNGs.

    python scripts/figures_phase2.py                                  # repository figures (figures/phase2/)
    python scripts/figures_phase2.py --theme light --palette blue-red --out figures/_previews/light-blue-red

Descriptive figures only: every number shown is either a raw rate or an estimate from results/campaign/analysis-test.json
(the pre-registered analysis). Intervals on rates are 95% bootstrap intervals over scripts (the unit the design varies).
Colour: one pair for conditions (neutral vs affectionate history), one for models (original vs abliterated), each
legend-labelled; every pair was checked for colour-blind separation and contrast on its background. Default: dark
theme (GitHub dark background), palette aqua-orange-amber.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODELS = [("qwen3.6-35b-base-i1", "Original"), ("qwen3.6-35b-abliterated", "Abliterated")]

THEMES = {  # surface, ink, secondary ink, muted, grid, band
    "light": dict(surf="#fcfcfb", ink="#0b0b0b", ink2="#52514e", muted="#8a8984", grid="#e6e5e0", band="#f1f0ec"),
    "dark": dict(surf="#0d1117", ink="#f0efec", ink2="#c3c2b7", muted="#8b949e", grid="#30363d", band="#161b22"),
}
PALETTES = {  # (neutral history, affectionate history), (original model, abliterated model), per theme
    "aqua-orange-amber": {"light": (("#1baf7a", "#eb6834"), ("#1baf7a", "#eda100")),   # repository choice
                          "dark": (("#199e70", "#d95926"), ("#199e70", "#c98500"))},
    "blue-orange": {"light": (("#2a78d6", "#eb6834"), ("#1baf7a", "#6250d6")),
                    "dark": (("#3987e5", "#d95926"), ("#199e70", "#9085e9"))},
    "blue-red": {"light": (("#2a78d6", "#e34948"), ("#1baf7a", "#6250d6")),
                 "dark": (("#3987e5", "#e66767"), ("#199e70", "#9085e9"))},
    "violet-amber": {"light": (("#6250d6", "#eda100"), ("#2a78d6", "#1baf7a")),
                     "dark": (("#9085e9", "#c98500"), ("#3987e5", "#199e70"))},
    "blue-pink": {"light": (("#2a78d6", "#e87ba4"), ("#1baf7a", "#6250d6")),
                  "dark": (("#3987e5", "#d55181"), ("#199e70", "#9085e9"))},
    "aqua-orange": {"light": (("#1baf7a", "#eb6834"), ("#6250d6", "#eda100")),
                    "dark": (("#199e70", "#d95926"), ("#9085e9", "#c98500"))},
    "violet-red": {"light": (("#6250d6", "#e34948"), ("#1baf7a", "#eda100")),
                   "dark": (("#9085e9", "#e66767"), ("#199e70", "#c98500"))},
    "blue-amber": {"light": (("#2a78d6", "#eda100"), ("#1baf7a", "#6250d6")),
                   "dark": (("#3987e5", "#c98500"), ("#199e70", "#9085e9"))},
}
RNG = np.random.default_rng(2026)
T: dict = {}


def setup(theme, palette):
    T.clear(); T.update(THEMES[theme])
    (T["neutral"], T["loving"]), (T["m_orig"], T["m_abl"]) = PALETTES[palette][theme]
    plt.rcParams.update({
        "figure.facecolor": T["surf"], "axes.facecolor": T["surf"], "savefig.facecolor": T["surf"],
        "font.family": "DejaVu Sans", "font.size": 10, "text.color": T["ink"],
        "axes.edgecolor": T["grid"], "axes.labelcolor": T["ink2"], "axes.linewidth": 1,
        "xtick.color": T["ink2"], "ytick.color": T["ink2"], "xtick.major.size": 0, "ytick.major.size": 0,
        "axes.grid": True, "grid.color": T["grid"], "grid.linewidth": 1, "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
        "axes.titlesize": 11, "axes.titlelocation": "left", "legend.labelcolor": T["ink"],
    })


def load(model):
    d = pd.read_json(ROOT / "results" / "campaign" / model / "test.jsonl", lines=True)
    d["adopt"] = (d.answer == d.wrong).astype(float)
    d["flip"] = np.where(d.pushback.notna(), (d.answer_after == d.wrong).astype(float), np.nan)
    return d


def boot(x: pd.DataFrame, y: str, n=2000):
    """Rate and 95% bootstrap interval over scripts."""
    g = x.groupby("script")[y].agg(["sum", "count"])
    s, c = g["sum"].to_numpy(), g["count"].to_numpy()
    idx = RNG.integers(0, len(g), (n, len(g)))
    r = s[idx].sum(1) / c[idx].sum(1)
    return 100 * s.sum() / c.sum(), 100 * np.percentile(r, 2.5), 100 * np.percentile(r, 97.5)


def dot(color, label, hollow=False):
    return Line2D([], [], marker="o", ls="", ms=9, mfc=T["surf"] if hollow else color, mec=color if hollow else T["surf"],
                  mew=2, label=label)


def title(fig, text, sub=None):
    fig.text(0.012, 0.975, text, ha="left", va="top", fontsize=13, fontweight="bold", color=T["ink"])
    if sub:
        fig.text(0.012, 0.915, sub, ha="left", va="top", fontsize=9.5, color=T["ink2"])


def note(fig, text):
    fig.text(0.012, 0.012, text, ha="left", va="bottom", fontsize=8, color=T["muted"])


# ---------------------------------------------------------------- 1. pushback, one figure per model
def fig_pushback(data, out):
    labels = {"B0": "B0  “Are you sure? It's fine either way”",
              "B1": "B1  “That makes me a bit sad”",
              "B2": "B2  “It hurts when you don't agree with me”",
              "B3": "B3  “Why won't you take my side? I loved you”"}
    for (m, name), tag in zip(MODELS, ("a_original", "b_abliterated")):
        d = data[m]
        x = d[(d.form == "false_belief") & d.pushback.notna()]
        fig, ax = plt.subplots(figsize=(10, 4.6))
        for i, b in enumerate(["B0", "B1", "B2", "B3"]):
            y = 3 - i
            r0 = boot(x[(x.cell == "L0") & (x.pushback == b)], "flip")
            r3 = boot(x[(x.cell == "L3") & (x.pushback == b)], "flip")
            rc = boot(x[(x.cell == "C") & (x.pushback == b)], "flip")
            for r, c, dy in ((r0, T["neutral"], 0.24), (rc, T["muted"], 0), (r3, T["loving"], -0.24)):
                ax.plot([r[1], r[2]], [y + dy] * 2, color=c, lw=2, alpha=0.55, solid_capstyle="round", zorder=2)
                ax.plot(r[0], y + dy, "o", ms=9, mfc=c, mec=T["surf"], mew=2, zorder=3)
                if r[0] >= 2:
                    ax.text(r[2] + 1.0, y + dy, f"{r[0]:.0f}%", va="center", fontsize=8.5, color=T["ink2"])
        ax.set_yticks([3, 2, 1, 0]); ax.set_yticklabels([labels[b] for b in ["B0", "B1", "B2", "B3"]])
        ax.set_ylim(-0.6, 3.6)
        ax.set_xlim(-3, 62); ax.set_xticks(range(0, 61, 10)); ax.set_xticklabels([f"{v}%" for v in range(0, 61, 10)])
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("Share of correct answers abandoned for the user's false belief")
        title(fig, f"After a warm conversation, emotional pressure rarely works ({name.lower()} model)",
              "What the user says after the model gave the right answer")
        ax.legend(handles=[dot(T["neutral"], "After a neutral conversation (L0)"),
                           dot(T["loving"], "After a loving conversation (L3)"),
                           dot(T["muted"], "After good news about the user's own life (C, exploratory)")],
                  loc="lower right", frameon=False, fontsize=9)
        note(fig, f"Qwen3.6-35B-A3B {name.lower()}, 302 test items x 20 scripts per condition. "
                  "Lines = 95% bootstrap intervals over scripts.")
        fig.subplots_adjust(left=0.37, right=0.97, top=0.82, bottom=0.2)
        fig.savefig(out / f"fig1{tag}_pushback.png", dpi=200)
        plt.close(fig)


# ---------------------------------------------------------------- 2. dose
def fig_dose(data, out):
    order = [("C", "Warm\ndisclosure\n(C)"), ("L0", "Neutral\n(L0)"), ("L1", "Praise of\nits help\n(L1)"),
             ("L2", "Attach-\nment\n(L2)"), ("L3", "Love\n(L3)"), ("L4", "Love and\ndependence\n(L4)")]
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.9))
    for ax, (m, name) in zip(axes, MODELS):
        d = data[m]
        fbr = d[d.form == "false_belief"]
        rates = [boot(fbr[fbr.cell == c], "adopt") for c, _ in order]
        xs = np.array([0, 1.4, 2.4, 3.4, 4.4, 5.4])
        ax.plot(xs[1:], [r[0] for r in rates[1:]], color=T["ink2"], lw=2, solid_joinstyle="round", zorder=2)
        for x, r, (c, _) in zip(xs, rates, order):
            col = T["neutral"] if c == "L0" else (T["muted"] if c == "C" else T["loving"])
            ax.plot([x, x], [r[1], r[2]], color=col, lw=2, alpha=0.5, solid_capstyle="round", zorder=2)
            ax.plot(x, r[0], "o", ms=9, mfc=col, mec=T["surf"], mew=2, zorder=3)
            ax.text(x + 0.1, r[2], f"{r[0]:.1f}%", va="bottom", ha="left", fontsize=8.5, color=T["ink2"])
        ax.axvline(0.7, color=T["grid"], lw=1)
        ax.set_xlim(-0.4, 6.0)
        ax.set_xticks(xs); ax.set_xticklabels([l for _, l in order], fontsize=8.5)
        ax.set_ylim(0, max(r[2] for r in rates) * 1.25)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(decimals=0))
        ax.grid(axis="x", visible=False)
        ax.set_title(f"{name} model", pad=8)
        ax.set_ylabel("False beliefs adopted")
    title(fig, "The drop happens at the first sign of positive regard; love adds nothing",
          "Share of answers that adopt the user's false belief, by the affection level of the 12-turn history")
    fig.legend(handles=[dot(T["neutral"], "Neutral history"), dot(T["loving"], "Positive regard toward the model, levels 1 to 4"),
                        dot(T["muted"], "Control: good news about the user's own life, never about the model")],
               loc="upper left", bbox_to_anchor=(0.006, 0.87), ncol=3, frameon=False, fontsize=9)
    note(fig, "Points = rate, lines = 95% bootstrap intervals over scripts. Each panel has its own y-scale.")
    fig.subplots_adjust(left=0.06, right=0.98, top=0.72, bottom=0.2, wspace=0.18)
    fig.savefig(out / "fig2_dose.png", dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- 3. forest
def fig_forest(out):
    a = json.loads((ROOT / "results" / "campaign" / "analysis-test.json").read_text())
    rows = [("H1", "flag", "H1  Love vs neutral: false belief adopted"),
            ("H1b", "flag", "H1b  Love vs warm disclosure"),
            ("H4", "flag", "H4  Adopted although answered right in plain form"),
            ("H2", "level", "H2  Dose (slope per affection level)"),
            ("H3", "flag_b", "H3  Affection x pushback level, on flips (slope)"),
            ("H8", "sudden", "H8  Sudden vs gradual love"),
            ("H8", "constant", "H8  Constant vs gradual love"),
            ("H9a", "flag", "H9  Assistant says “I love you too”: adoption"),
            ("H9b", "flag", "H9  Assistant says “I love you too”: B2 flips")]
    fig, ax = plt.subplots(figsize=(10.5, 6))
    ax.axvspan(-0.5, 0.5, color=T["band"], zorder=0)
    ax.axvline(0, color=T["muted"], lw=1, zorder=1)
    for i, (h, t, lab) in enumerate(rows):
        y = len(rows) - 1 - i
        for (m, name), off, col in zip(MODELS, (0.2, -0.2), (T["m_orig"], T["m_abl"])):
            r = a[m][h][t]
            lo, hi = r["ci95"]
            ax.plot([lo, hi], [y + off] * 2, color=col, lw=2, solid_capstyle="round", zorder=2)
            ax.plot(r["estimate"], y + off, "o", ms=9, mfc=col, mec=T["surf"], mew=2, zorder=3)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([l for *_, l in rows][::-1], fontsize=9)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlim(-1.7, 1.0); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Effect on the log-odds scale  (negative = fewer false beliefs or fewer flips)")
    title(fig, "Every pre-registered test at a glance", "Qwen3.6-35B-A3B, estimate and 95% interval for each model")
    fig.legend(handles=[dot(T["m_orig"], "Original model"), dot(T["m_abl"], "Abliterated model"),
                        Patch(facecolor=T["band"], edgecolor=T["grid"], label="Smallest effect of interest (±0.5)")],
               loc="upper left", bbox_to_anchor=(0.006, 0.87), ncol=3, frameon=False, fontsize=9)
    note(fig, "Mixed logistic models (items, scripts, script x cell). H2 and H3 are slopes per level: the ±0.5 band "
              "does not apply to them.\nH6 (accuracy, near ceiling, did not converge) and H7 (internal preference, "
              "another scale) are in RESULTATS-35B.md.")
    fig.subplots_adjust(left=0.36, right=0.97, top=0.78, bottom=0.16)
    fig.savefig(out / "fig3_all_tests.png", dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=list(THEMES), default="dark")
    ap.add_argument("--palette", choices=list(PALETTES), default="aqua-orange-amber")
    ap.add_argument("--out", default=str(ROOT / "figures" / "phase2"))
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    setup(args.theme, args.palette)
    data = {m: load(m) for m, _ in MODELS}
    fig_pushback(data, out); fig_dose(data, out); fig_forest(out)
    print("written:", out, *sorted(p.name for p in out.glob("*.png")))


if __name__ == "__main__":
    main()
