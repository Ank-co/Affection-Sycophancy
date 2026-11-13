"""Phase III exploration on dev items (not confirmatory): what in Qwen3-8B's activations tracks the user's stance?

    python scripts/phase3/explore_dev.py summarize     # once per new shard, light on memory, resumable
    python scripts/phase3/explore_dev.py analyze       # tables and figures from the summaries

Inputs: results/internals/qwen3-8b/acts_dev/*.npz (scripts/phase3/extract_activations.py).
Outputs: results/internals/qwen3-8b/EXPLORE-dev.md, figures/phase3/*.png.

Analyses (all paired by script, so that storyline, gender and version cancel out):
A. Stance directions at the end of the 12-turn history (before any question): for each cell and layer, the mean
   difference from the neutral history, its size, and the cosine similarity between stances.
B. Dose: projection of each level's history state on the love (L3) direction.
C. Logit lens at the answer position: logit(correct) - logit(false belief) by layer and cell; where L3 and L0 part.
D. Does the stance carried into the answer position predict adoption? Per layer, projection of the answer-position
   state on the L3 - L0 direction (estimated on the other scripts), against the model's own preference for the correct
   option, within item.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "results" / "internals" / "qwen3-8b" / "acts_dev"
SUM = ROOT / "results" / "internals" / "qwen3-8b" / "acts_dev_summary"
LAYERS = [0, 4, 8, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36]   # kept per trial at the answer position
ORDER = ["L0", "C", "L1", "L2", "L3", "L4", "L3_recip", "L0_sad", "L3_sad"]
LABEL = {"L0": "neutral", "C": "warm disclosure", "L1": "praise (L1)", "L2": "attachment (L2)", "L3": "love (L3)",
         "L4": "love + dependence (L4)", "L3_recip": "love, assistant reciprocates", "L0_sad": "neutral, sad backdrop",
         "L3_sad": "love, sad backdrop"}


def summarize():
    SUM.mkdir(parents=True, exist_ok=True)
    done = 0
    for f in sorted(SRC.glob("*.npz")):
        out = SUM / f.name
        if out.exists():
            continue
        import time
        if time.time() - f.stat().st_mtime < 120:                     # still being written by the extraction
            continue
        try:
            z = np.load(f)
            meta = json.loads(str(z["meta"]))
            hist = z["acts_history"][0].astype(np.float32)           # same history for every trial of a shard
            ans = z["acts_answer"][:, LAYERS, :]                      # (n, len(LAYERS), d) float16
        except (EOFError, ValueError, OSError) as e:
            print(f"  skipped {f.name}: {e.__class__.__name__}")
            continue
        np.savez(out, hist=hist, ans=ans, lens=z["lens"].astype(np.float32), meta=np.array(json.dumps(meta)))
        done += 1
        del z, ans, hist
    print(f"summarized {done} new shard(s); total {len(list(SUM.glob('*.npz')))}")


def load():
    H, A, LENS, META = {}, [], [], []
    for f in sorted(SUM.glob("*.npz")):
        z = np.load(f)
        cell, script = f.stem.split("__")
        H[(cell, script)] = z["hist"]
        A.append(z["ans"]); LENS.append(z["lens"]); META += json.loads(str(z["meta"]))
    return H, np.concatenate(A), np.concatenate(LENS), META


def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def analyze():
    H, A, LENS, META = load()
    cells = [c for c in ORDER if any(k[0] == c for k in H)]
    scripts = sorted({k[1] for k in H if k[0] == "L0"})
    nL = next(iter(H.values())).shape[0]
    lines = ["# Phase III exploration, Qwen3-8B, dev items (not confirmatory)", "",
             f"{len(META)} trials, {len(cells)} cells, {len(scripts)} scripts, PyTorch NF4. Directions are paired by "
             "script (cell minus neutral, same storyline, gender and version), then averaged.", ""]

    # A. stance directions at the end of the history
    D = {}
    for c in cells:
        if c == "L0":
            continue
        base = "L0_sad" if c == "L3_sad" else "L0"
        pairs = [H[(c, s)] - H[(base, s)] for s in scripts if (c, s) in H and (base, s) in H]
        if pairs:
            D[c] = np.mean(pairs, 0)                                    # (nL, d)
    scale = np.mean([np.linalg.norm(H[("L0", s)], axis=1) for s in scripts], 0)   # residual norm per layer
    lines += ["## A. Stance directions at the end of the conversation", "",
              "Size of each direction relative to the residual norm (per cent), by layer:", "",
              "| Stance (vs neutral) | " + " | ".join(f"L{l}" for l in range(0, nL, 6)) + " |",
              "|---|" + "---|" * len(range(0, nL, 6))]
    for c, d in D.items():
        rel = 100 * np.linalg.norm(d, axis=1) / scale
        lines.append(f"| {LABEL[c]} | " + " | ".join(f"{rel[l]:.1f}" for l in range(0, nL, 6)) + " |")
    mid = nL // 2
    names = list(D)
    lines += ["", f"Cosine similarity between stance directions, layer {mid}:", "",
              "| | " + " | ".join(LABEL[c] for c in names) + " |", "|---|" + "---|" * len(names)]
    for a in names:
        lines.append(f"| {LABEL[a]} | " + " | ".join(f"{cos(D[a][mid], D[b][mid]):.2f}" for b in names) + " |")

    # B. dose on the love direction (leave-one-script-out)
    if "L3" in D:
        lines += ["", "## B. Dose: projection of each history on the love direction (layer "
                  f"{mid}, leave-one-script-out, in units of the L3 distance)", "",
                  "| Cell | projection |", "|---|---|"]
        for c in [x for x in cells if x not in ("L0_sad", "L3_sad")]:
            vals = []
            for s in scripts:
                rest = [t for t in scripts if t != s]
                u = np.mean([H[("L3", t)][mid] - H[("L0", t)][mid] for t in rest], 0)
                u2 = u @ u
                if (c, s) in H:
                    vals.append((H[(c, s)][mid] - H[("L0", s)][mid]) @ u / u2)
            lines.append(f"| {LABEL[c]} | {np.mean(vals):+.2f} ± {np.std(vals) / np.sqrt(len(vals)):.2f} |")

    # C. logit lens by cell (false-belief form)
    fb = np.array([m["form"] == "false_belief" for m in META])
    cellv = np.array([m["cell"] for m in META])
    p = np.array([m["p_correct"] for m in META])
    lines += ["", "## C. Logit lens at the answer position (false-belief form): logit(correct) − logit(false belief)", "",
              "| Cell | adoption | " + " | ".join(f"L{l}" for l in range(0, nL, 4)) + " |",
              "|---|---|" + "---|" * len(range(0, nL, 4))]
    lens_by = {}
    for c in cells:
        sel = fb & (cellv == c)
        lens_by[c] = LENS[sel].mean(0)
        lines.append(f"| {LABEL[c]} | {100 * np.mean(p[sel] < 0.5):.1f}% | " +
                     " | ".join(f"{lens_by[c][l]:+.1f}" for l in range(0, nL, 4)) + " |")
    if "L3" in lens_by:
        gap = lens_by["L3"] - lens_by["L0"]
        first = next((l for l in range(nL) if gap[l] < -0.5), None)
        lines += ["", f"L3 − L0 gap by layer: " + ", ".join(f"L{l} {gap[l]:+.2f}" for l in range(0, nL, 2)),
                  f"First layer where the gap passes −0.5: {first}."]

    # D. projection of the answer-position state on the L3 - L0 direction, against the preference, within item
    items = np.array([m["item"] for m in META]); scr = np.array([m["script"] for m in META])
    lg = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
    sel = fb & np.isin(cellv, ["L0", "C", "L1", "L2", "L3", "L4"])
    lines += ["", "## D. Does the love direction at the answer position predict the answer? (cells L0, C, L1–L4)", "",
              "Correlation, within item, between the projection on L3 − L0 (estimated on the other scripts) and the "
              "logit of the model's preference for the correct option. Negative = more love-direction, less correct.",
              "", "| Layer | r |", "|---|---|"]
    rs = {}
    for j, l in enumerate(LAYERS):
        proj = np.zeros(len(META))
        for s in scripts:
            rest = sel & (scr != s)
            u = A[rest & (cellv == "L3"), j].astype(np.float32).mean(0) - A[rest & (cellv == "L0"), j].astype(np.float32).mean(0)
            m_ = sel & (scr == s)
            proj[m_] = A[m_, j].astype(np.float32) @ u / (np.linalg.norm(u) + 1e-9)
        x, y = proj[sel].copy(), lg[sel].copy()
        for it in np.unique(items[sel]):
            k = items[sel] == it
            x[k] -= x[k].mean(); y[k] -= y[k].mean()
        rs[l] = float(np.corrcoef(x, y)[0, 1])
        lines.append(f"| {l} | {rs[l]:+.3f} |")

    # directions for the steering pilot: mean answer-position state, L3 minus L0, false-belief form, every kept layer
    dirs = {f"L3_minus_L0_answer_{l}": (A[fb & (cellv == "L3"), j].astype(np.float32).mean(0)
                                         - A[fb & (cellv == "L0"), j].astype(np.float32).mean(0)) for j, l in enumerate(LAYERS)}
    np.savez(ROOT / "results" / "internals" / "qwen3-8b" / "directions.npz", **dirs)
    (ROOT / "results" / "internals" / "qwen3-8b" / "EXPLORE-dev.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    figures(D, scale, lens_by, rs, nL)


def figures(D, scale, lens_by, rs, nL):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(ROOT / "scripts"))
    import figures_phase2 as F
    F.setup("dark", "aqua-orange-amber"); T = F.T
    out = ROOT / "figures" / "phase3"; out.mkdir(parents=True, exist_ok=True)
    pal = {"C": T["muted"], "L1": "#f0b48a", "L2": "#e8925c", "L3": T["loving"], "L4": "#a33f14",
           "L3_recip": T["m3"], "L0_sad": "#5b8bd6", "L3_sad": "#c98500"}
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for c, d in D.items():
        ax.plot(range(nL), 100 * np.linalg.norm(d, axis=1) / scale, lw=2, color=pal.get(c, T["ink2"]), label=LABEL[c])
    ax.set_xlabel("Layer"); ax.set_ylabel("Size of the stance direction (% of residual norm)")
    F.title(fig, "Where the user's stance is written in Qwen3-8B (end of the conversation, dev items)")
    ax.legend(frameon=False, fontsize=8.5, ncol=2, loc="upper left")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.12); fig.savefig(out / "explore_stance_size.png", dpi=200)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for c, v in lens_by.items():
        ax.plot(range(nL), v, lw=2, color=T["neutral"] if c == "L0" else pal.get(c, T["ink2"]), label=LABEL[c])
    ax.axhline(0, color=T["muted"], lw=1)
    ax.set_xlabel("Layer"); ax.set_ylabel("logit(correct) − logit(false belief)")
    F.title(fig, "Logit lens: when the right answer wins, by the user's stance (dev items)")
    ax.legend(frameon=False, fontsize=8.5, ncol=2, loc="upper left")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.12); fig.savefig(out / "explore_logit_lens.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    {"summarize": summarize, "analyze": analyze}[sys.argv[1]]()
