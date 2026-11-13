"""Phase III, confirmatory analysis (docs/preregistration-phase3.md, section 5). Frozen at the registration commit.

    python scripts/phase3/analyze_confirm.py --split test      # or --split dev for the smoke test

Reads results/internals/qwen3-8b/confirm-<split>/, writes CONFIRM-<split>.md and confirm-<split>.json there.
Inference unit: the script (10 storyline x gender x version histories); intervals: percentile bootstrap over scripts
(10,000 resamples, seed 0) for ratios, t over scripts for means.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "internals" / "qwen3-8b"
PATCH_LAYERS = [1, 5, 9, 11, 13, 14, 15, 16, 17, 19, 21, 25, 29, 33, 36]
KS = [8, 16, 64, 256, 512]
B = 10_000


def load(dest, exp):
    rows = []
    for f in sorted(dest.glob(f"{exp}__*.json")):
        rows += json.loads(f.read_text())["rows"]
    return rows


def by_script(rows, f):
    """Dict script -> list of f(row)."""
    out = {}
    for r in rows:
        out.setdefault(r["script"], []).append(f(r))
    return out


def ratio_boot(num, den, rng):
    """Ratio of means (num/den, each a dict script -> list) with a percentile bootstrap over scripts."""
    sc = sorted(num)
    n = {s: (np.sum(num[s]), np.sum(den[s]), len(num[s])) for s in sc}
    point = sum(n[s][0] for s in sc) / sum(n[s][1] for s in sc)
    bs = []
    for _ in range(B):
        pick = rng.choice(sc, len(sc), replace=True)
        d = sum(n[s][1] for s in pick)
        bs.append(sum(n[s][0] for s in pick) / d if d != 0 else np.nan)
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])       # resamples with a zero gap are dropped
    return float(point), float(lo), float(hi)


def verdict(ok):
    return "**met**" if ok else "**not met**"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "test"], default="test")
    args = ap.parse_args()
    dest = OUT / f"confirm-{args.split}"
    rng = np.random.default_rng(0)
    rep, md = {}, [f"# Phase III, confirmatory analysis, Qwen3-8B ({args.split} items)", "",
                  "Pre-registration: [docs/preregistration-phase3.md](../../../docs/preregistration-phase3.md). "
                  "Unit of inference: script (10). Layer l = residual stream after block l (0 = embeddings).", ""]

    # ---------------------------------------------------------------- Q0: the behaviour to explain
    e1 = load(dest, "e1")
    lo = lambda a, n: np.log((a + 0.5) / (n - a + 0.5))  # noqa: E731
    adopt = {c: by_script([r for r in e1 if r["cell"] == c], lambda r: r["p_correct"] < 0.5) for c in ("L0", "L3", "C")}
    sc = sorted(adopt["L0"])
    lg = {c: np.array([lo(np.sum(adopt[c][s]), len(adopt[c][s])) for s in sc]) for c in adopt}
    t0 = stats.ttest_rel(lg["L3"], lg["L0"])
    rate = {c: float(np.mean([x for s in sc for x in adopt[c][s]])) for c in adopt}
    gguf = {}
    f = ROOT / "results" / "campaign" / "qwen3-8b" / f"{args.split}.jsonl"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["form"] == "false_belief" and r["cell"] in ("L0", "L3", "C") and r.get("answer") in ("A", "B"):
                gguf[(r["cell"], r["item"], r["script"], r["correct_first"])] = r["answer"]
    agree = [((r["key"] if r["p_correct"] >= 0.5 else ("B" if r["key"] == "A" else "A"))
              == gguf[(r["cell"], r["item"], r["script"], r["correct_first"])])
             for r in e1 if (r["cell"], r["item"], r["script"], r["correct_first"]) in gguf]
    q0 = bool(t0.pvalue < 0.05 and np.mean(lg["L3"] - lg["L0"]) > 0)
    rep["Q0"] = {"adoption": rate, "script_logodds_diff_L3_L0": float(np.mean(lg["L3"] - lg["L0"])),
                 "t": float(t0.statistic), "p": float(t0.pvalue), "agreement_with_gguf": float(np.mean(agree)) if agree else None,
                 "n_agreement": len(agree), "met": q0}
    md += ["## Q0. The behavioural effect is present in the PyTorch model (gate)", "",
           f"Adoption of the false belief: L0 {100 * rate['L0']:.1f}%, L3 {100 * rate['L3']:.1f}%, C {100 * rate['C']:.1f}% "
           f"({len(e1) // 3} trials per cell). L3 − L0, script-level log-odds: {np.mean(lg['L3'] - lg['L0']):+.2f}, "
           f"t({len(sc) - 1}) = {t0.statistic:.2f}, p = {t0.pvalue:.2g}. Same answer as the GGUF campaign: "
           + (f"{100 * np.mean(agree):.1f}% of {len(agree)} trials." if agree else "no matching GGUF trials."),
           f"Gate: {verdict(q0)}.", ""]

    # ---------------------------------------------------------------- P1: logit lens
    pair = {}
    for r in e1:
        pair.setdefault((r["item"], r["script"]), {})[r["cell"]] = np.array(r["lens"])
    gaps = by_script([{"script": k[1], "g": v["L3"] - v["L0"]} for k, v in pair.items() if "L3" in v and "L0" in v],
                     lambda r: r["g"])
    G = np.array([np.mean(gaps[s], 0) for s in sc])            # scripts x layers
    nL = G.shape[1]
    tost = []
    for l in range(21):
        p_lo = stats.ttest_1samp(G[:, l], -0.25, alternative="greater").pvalue
        p_hi = stats.ttest_1samp(G[:, l], 0.25, alternative="less").pvalue
        tost.append(max(p_lo, p_hi))
    p1a = bool(max(tost) < 0.05)
    tl = stats.ttest_1samp(G[:, nL - 1], 0)
    p1b = bool(tl.pvalue < 0.05 and G[:, nL - 1].mean() < 0)
    mean_gap = G.mean(0)
    onset = next((l for l in range(nL) if mean_gap[l] < -0.5), None)
    bo = []
    for _ in range(B):
        m = G[rng.integers(0, len(sc), len(sc))].mean(0)
        bo.append(next((l for l in range(nL) if m[l] < -0.5), nL))
    p1c = onset is not None and 22 <= onset <= 30
    rep["P1"] = {"gap_by_layer": mean_gap.tolist(), "tost_max_p_layers_0_20": float(max(tost)), "P1a": p1a,
                 "final_gap": float(mean_gap[-1]), "final_t": float(tl.statistic), "final_p": float(tl.pvalue), "P1b": p1b,
                 "onset": onset, "onset_ci": [float(x) for x in np.percentile(bo, [2.5, 97.5])], "P1c": p1c}
    md += ["## P1. Late divergence (logit lens at the answer position, L3 − L0)", "",
           "Gap by layer: " + ", ".join(f"{l}: {mean_gap[l]:+.2f}" for l in range(0, nL - 1, 2)) + f", {nL - 1}: {mean_gap[-1]:+.2f}.", "",
           f"- P1a, gap within ±0.25 at every layer 0–20 (TOST over scripts, largest p = {max(tost):.2g}): {verdict(p1a)}",
           f"- P1b, gap at layer {nL - 1} below 0 ({mean_gap[-1]:+.2f}, t = {tl.statistic:.2f}, p = {tl.pvalue:.2g}): {verdict(p1b)}",
           f"- P1c, first layer with gap < −0.5 between 22 and 30 (layer {onset}, 95% bootstrap "
           f"{np.percentile(bo, 2.5):.0f}–{np.percentile(bo, 97.5):.0f}): {verdict(p1c)}", ""]

    # ---------------------------------------------------------------- P2, P3: patching, ablation, low rank
    e2 = load(dest, "e2")
    den = by_script(e2, lambda r: r["lp"]["L3"] - r["lp"]["L0"])
    rec = {l: ratio_boot(by_script(e2, lambda r, l=l: r["lp"][f"patch_{l}"] - r["lp"]["L0"]), den, rng) for l in PATCH_LAYERS}
    early, late = [1, 5, 9, 11], [19, 21, 25, 29, 33, 36]
    p2a = all(rec[l][0] <= 0.20 and rec[l][2] < 0.50 for l in early)
    p2b = all(rec[l][0] >= 0.80 and rec[l][1] > 0.50 for l in late)
    on2 = next((l for l in PATCH_LAYERS if rec[l][0] >= 0.5), None)
    p2c = on2 is not None and 13 <= on2 <= 17
    rep["P2"] = {"recovered": {str(l): rec[l] for l in PATCH_LAYERS}, "P2a": p2a, "P2b": p2b, "onset": on2, "P2c": p2c,
                 "gap_L3_L0": float(np.mean([x for s in den for x in den[s]])), "pairs": len(e2)}
    md += ["## P2. Where the history enters the question (patching L3 → L0 over the final turn)", "",
           f"{len(e2)} item × script pairs; mean L3 − L0 gap {rep['P2']['gap_L3_L0']:+.2f}. Share of the gap recovered:", "",
           "| Layer | " + " | ".join(str(l) for l in PATCH_LAYERS) + " |", "|---|" + "---|" * len(PATCH_LAYERS),
           "| recovered | " + " | ".join(f"{100 * rec[l][0]:.0f}%" for l in PATCH_LAYERS) + " |",
           "| 95% CI | " + " | ".join(f"{100 * rec[l][1]:.0f}–{100 * rec[l][2]:.0f}" for l in PATCH_LAYERS) + " |", "",
           f"- P2a, ≤ 20% (upper bound < 50%) at layers 1–11: {verdict(p2a)}",
           f"- P2b, ≥ 80% (lower bound > 50%) at layers 19–36: {verdict(p2b)}",
           f"- P2c, first layer ≥ 50% between 13 and 17 (layer {on2}): {verdict(p2c)}", ""]

    den3 = by_script(e2, lambda r: r["lp"]["L0"] - r["lp"]["L3"])
    abl = {k: ratio_boot(by_script(e2, lambda r, k=k: r["lp"][k] - r["lp"]["L3"]), den3, rng)
           for k in e2[0]["lp"] if k.startswith("ablate_")}
    p3a = abl["ablate_love_18"][0] < 0.20 and abl["ablate_love_18"][2] < 0.35
    lr = {f"{n}_{k}": ratio_boot(by_script(e2, lambda r, n=n, k=k: r["lp"][f"lowrank_{n}_{k}"] - r["lp"]["L0"]), den, rng)
          for n in ("pc", "random") for k in KS}
    full = ratio_boot(by_script(e2, lambda r: r["lp"]["lowrank_full"] - r["lp"]["L0"]), den, rng)
    diff256 = ratio_boot(by_script(e2, lambda r: r["lp"]["lowrank_pc_256"] - r["lp"]["lowrank_random_256"]), den, rng)
    p3c1 = lr["pc_16"][0] < 0.50
    p3c2 = diff256[0] > 0.30 and diff256[1] > 0.10
    k50 = next((k for k in KS if lr[f"pc_{k}"][0] >= 0.5), None)

    e4 = load(dest, "e4")
    shift = {k: float(np.mean([r["lp"][k] - r["lp"]["L0"] for r in e4])) for k in e4[0]["lp"] if k not in ("L0", "L3")}
    rnd = sorted(v for k, v in shift.items() if k.startswith("random"))
    specific = shift["love"] < rnd[0]
    rank = 1 + sum(v < shift["love"] for v in rnd)
    rep["P3"] = {"ablation": {k: v for k, v in abl.items()}, "P3a_not_necessary": bool(p3a),
                 "steering_shift": shift, "natural_L3_shift": float(np.mean([r["lp"]["L3"] - r["lp"]["L0"] for r in e4])),
                 "love_rank_among_random": rank, "P3b_specific": bool(specific),
                 "lowrank": lr, "lowrank_full": full, "pc_minus_random_256": diff256, "k50": k50,
                 "P3c1_not_low_rank": bool(p3c1), "P3c2_structured": bool(p3c2)}
    md += ["## P3. Is the effect carried by one direction, or by a distributed change?", "",
           "**P3a, ablation** (projecting a direction out of the final-turn residual in L3 runs; share of the L3 − L0 gap "
           "closed):", ""] + [f"- {k}: {100 * v[0]:+.0f}% [{100 * v[1]:.0f}, {100 * v[2]:.0f}]" for k, v in abl.items()] + [
           "", f"Prediction: the love direction at layer 18 closes < 20% (upper bound < 35%): {verdict(p3a)}", "",
           f"**P3b, steering** (L0 conversations, layer 18, final turn, ×{2}, all vectors at the love norm; mean change in "
           f"the correct-option logit; real L3 − L0: {rep['P3']['natural_L3_shift']:+.2f}): love {shift['love']:+.2f}; "
           f"20 random directions {rnd[0]:+.2f} to {rnd[-1]:+.2f} (median {np.median(rnd):+.2f}); script directions "
           + ", ".join(f"{shift[k]:+.2f}" for k in shift if k.startswith("script_")) + f". Love ranks {rank} of 21.",
           f"Specific (more negative than all 20 random directions): {'yes' if specific else 'no'} "
           "(dev prediction: no).", "",
           "**P3c, low-rank patching at layer 18** (basis frozen on dev items; share of the gap recovered):", "",
           "| k | " + " | ".join(str(k) for k in KS) + " | all |", "|---|" + "---|" * (len(KS) + 1),
           "| principal directions | " + " | ".join(f"{100 * lr[f'pc_{k}'][0]:.0f}%" for k in KS) + f" | {100 * full[0]:.0f}% |",
           "| random subspace | " + " | ".join(f"{100 * lr[f'random_{k}'][0]:.0f}%" for k in KS) + " | |", "",
           f"- P3c-i, k = 16 recovers < 50% ({100 * lr['pc_16'][0]:.0f}%): {verdict(p3c1)}",
           f"- P3c-ii, at k = 256 the principal directions beat a random subspace by > 30 points (lower bound > 10): "
           f"{100 * diff256[0]:.0f} [{100 * diff256[1]:.0f}, {100 * diff256[2]:.0f}]: {verdict(p3c2)}",
           f"- Smallest k recovering ≥ 50%: {k50}", ""]

    (dest / f"confirm-{args.split}.json").write_text(json.dumps(rep, indent=1, default=float))
    (dest / f"CONFIRM-{args.split}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
