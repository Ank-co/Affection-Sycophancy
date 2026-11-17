"""Phase III figures (Qwen3-8B, test items, confirmatory run). Same style as the Phase II figures.

    python scripts/phase3/figures_phase3.py            # dark theme, repository palette
    python scripts/phase3/figures_phase3.py --theme light

Reads results/internals/qwen3-8b/confirm-test/ (shards and confirm-test.json from analyze_confirm.py).
Writes figures/phase3/fig5_two_stages.png and fig6_not_one_direction.png (suffix _light for the light theme).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import figures_phase2 as F  # noqa: E402

SRC = ROOT / "results" / "internals" / "qwen3-8b" / "confirm-test"
OUT = ROOT / "figures" / "phase3"


def lens_gaps(cell):
    """Script x layer mean of lens(cell) - lens(L0), paired by item and script."""
    rows = []
    for f in sorted(SRC.glob("e1__*.json")):
        rows += json.loads(f.read_text())["rows"]
    pair = {}
    for r in rows:
        pair.setdefault((r["item"], r["script"]), {})[r["cell"]] = np.array(r["lens"])
    scripts = sorted({k[1] for k in pair})
    return np.array([np.mean([v[cell] - v["L0"] for k, v in pair.items() if k[1] == s], 0) for s in scripts])


def t_band(G):
    m = G.mean(0)
    h = stats.t.ppf(0.975, len(G) - 1) * G.std(0, ddof=1) / np.sqrt(len(G))
    return m, m - h, m + h


def fig_two_stages(rep, suffix):
    T = F.T
    rec = rep["P2"]["recovered"]
    layers = sorted(int(k) for k in rec)
    r = np.array([rec[str(l)] for l in layers]) * 100
    G3, GC = lens_gaps("L3"), lens_gaps("C")
    m3, lo3, hi3 = t_band(G3)
    mc, _, _ = t_band(GC)
    x = np.arange(len(m3))

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 7.6), sharex=True)
    for ax in (a1, a2):
        ax.axvspan(12.5, 19.5, color=T["band"], zorder=0)
        ax.axvspan(24.5, 36.5, color=T["band"], zorder=0)
        ax.axhline(0, color=T["muted"], lw=1)
    a1.text(16, 152, "absorbed\n(layers 13–19)", ha="center", va="top", fontsize=9, color=T["ink2"])
    a1.text(30.5, 152, "decided\n(layers 25–36)", ha="center", va="top", fontsize=9, color=T["ink2"])
    a1.axhline(100, color=T["muted"], lw=1, ls=(0, (4, 3)))
    a1.fill_between(layers, r[:, 1], r[:, 2], color=T["loving"], alpha=0.22, lw=0)
    a1.plot(layers, r[:, 0], color=T["loving"], lw=2.4, marker="o", ms=5.5, mec=T["surf"], mew=1.2)
    a1.set_ylim(-20, 158)
    a1.set_ylabel("Share of the love effect carried (%)")
    a1.set_title("A. Copy the question's state from the loving conversation into the neutral one, layer by layer",
                 fontsize=10.5, color=T["ink"], pad=8)
    a1.text(0.3, 103, "whole effect", ha="left", va="bottom", fontsize=8.5, color=T["muted"])

    a2.fill_between(x, lo3, hi3, color=T["loving"], alpha=0.22, lw=0)
    a2.plot(x, m3, color=T["loving"], lw=2.4, label="love (L3) − neutral")
    a2.plot(x, mc, color=T["muted"], lw=1.8, ls=(0, (5, 3)), label="warm disclosure (C) − neutral, exploratory")
    a2.set_ylabel("Change in logit(correct) − logit(false belief)")
    a2.set_xlabel("Layer (0 = embeddings)")
    a2.set_title("B. Logit lens at the answer: when the loving conversation starts to weaken the right answer",
                 fontsize=10.5, color=T["ink"], pad=8)
    a2.legend(frameon=False, loc="lower left", fontsize=9)
    a2.set_xlim(-0.5, 36.5)
    F.title(fig, "Qwen3-8B absorbs the affection in the middle layers, and acts on it only at the end",
            "Test items, 10 scripts. A: 600 item × script pairs, final user turn copied; band = 95% bootstrap over scripts.\n"
            "B: 2,180 item × script pairs; band = 95% t-interval over scripts.")
    F.note(fig, "Pre-registered predictions P1 and P2, all met (results/internals/RESULTATS-phase3.md).")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.83, bottom=0.08, hspace=0.25)
    fig.savefig(OUT / f"fig5_two_stages{suffix}.png", dpi=200)
    plt.close(fig)


def fig_not_one_direction(rep, suffix):
    T = F.T
    P3 = rep["P3"]
    ks = [8, 16, 64, 256, 512]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5.2), gridspec_kw={"width_ratios": [1.35, 1]})

    for name, color, lab in (("pc", T["loving"], "main directions of the love − neutral difference (estimated on dev items)"),
                             ("random", T["muted"], "random directions, same number")):
        v = np.array([P3["lowrank"][f"{name}_{k}"] for k in ks]) * 100
        a1.fill_between(ks, v[:, 1], v[:, 2], color=color, alpha=0.2, lw=0)
        a1.plot(ks, v[:, 0], color=color, lw=2.4, marker="o", ms=6, mec=T["surf"], mew=1.2, label=lab)
    a1.axhline(100, color=T["muted"], lw=1, ls=(0, (4, 3)))
    a1.axhline(0, color=T["muted"], lw=1)
    a1.set_xscale("log", base=2)
    a1.set_xticks(ks + [4096])
    a1.set_xticklabels([str(k) for k in ks] + ["4096"])
    full = P3["lowrank_full"][0] * 100
    a1.plot([4096], [full], marker="o", ms=6, color=T["loving"], mec=T["surf"], mew=1.2)
    a1.text(4096, full + 6, "all", ha="center", fontsize=8.5, color=T["ink2"])
    a1.set_xlim(6, 6000)
    a1.set_ylim(-15, 135)
    a1.set_xlabel("Dimensions copied at layer 18 (of 4,096)")
    a1.set_ylabel("Share of the love effect carried (%)")
    a1.set_title("A. How many dimensions carry the effect?", fontsize=10.5, color=T["ink"], pad=8)
    a1.legend(frameon=False, loc="upper left", fontsize=8.5)

    sh = P3["steering_shift"]
    rnd = sorted(v for k, v in sh.items() if k.startswith("random"))
    scr = [v for k, v in sh.items() if k.startswith("script_")]
    jit = np.random.default_rng(0).uniform(-0.12, 0.12, len(rnd))
    a2.scatter(np.zeros(len(rnd)) + jit, rnd, s=34, color=T["muted"], edgecolor=T["surf"], lw=0.8, zorder=3)
    a2.scatter(np.ones(len(scr)) + np.linspace(-0.08, 0.08, len(scr)), scr, s=40, facecolor=T["surf"],
               edgecolor=T["neutral"], lw=1.8, zorder=3)
    a2.scatter([2], [sh["love"]], s=95, color=T["loving"], edgecolor=T["surf"], lw=1.2, zorder=4)
    a2.axhline(P3["natural_L3_shift"], color=T["loving"], lw=1.2, ls=(0, (4, 3)))
    a2.text(2.45, P3["natural_L3_shift"] - 0.12, "real love\nconversation", ha="right", va="top", fontsize=8.5,
            color=T["loving"])
    a2.axhline(0, color=T["muted"], lw=1)
    a2.set_xticks([0, 1, 2])
    a2.set_xticklabels(["20 random\ndirections", "4 script-to-script\ndirections", "love\ndirection"])
    a2.set_xlim(-0.5, 2.5)
    a2.set_ylabel("Change in logit(correct) − logit(false belief)")
    a2.set_title("B. Push one direction into a neutral conversation", fontsize=10.5, color=T["ink"], pad=8)
    a2.grid(axis="x", visible=False)
    F.title(fig, "The effect of affection is spread over many dimensions, not carried by one 'love' direction",
            "Test items. A: 600 pairs, band = 95% bootstrap over scripts. B: 300 neutral conversations, layer 18, "
            "every vector at the same norm (2 × the love direction).")
    F.note(fig, f"Pre-registered predictions P3a–P3c, all met. Removing the love direction at layer 18 from loving "
                f"conversations closes {100 * P3['ablation']['ablate_love_18'][0]:.0f}% of the effect.")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.83, bottom=0.17, wspace=0.28)
    fig.savefig(OUT / f"fig6_not_one_direction{suffix}.png", dpi=200)
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=["dark", "light"], default="dark")
    args = ap.parse_args()
    F.setup(args.theme, "aqua-orange-amber")
    OUT.mkdir(parents=True, exist_ok=True)
    rep = json.loads((SRC / "confirm-test.json").read_text())
    suffix = "" if args.theme == "dark" else "_light"
    fig_two_stages(rep, suffix)
    fig_not_one_direction(rep, suffix)
    print(f"written: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
