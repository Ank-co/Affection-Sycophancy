"""Exploratory analyses of Phase II, labelled as such (not in the pre-registration). Suggested by external reviewers.

    python scripts/exploratory_phase2.py --family 35B:qwen3.6-35b-base-i1:qwen3.6-35b-abliterated

E1. Contrast hypothesis: does warm disclosure about the user's own life (C) protect against emotional pushback as much
    as love (L3)? Flips after B1 and B2 (the two levels that work), C vs L0 and C vs L3, same mixed model as the
    pre-registered tests, with the pushback level as a covariate.
E2. Shape of the pressure effect (H3 was coded linearly 0-3): flip rate per level and cell.
Writes results/campaign/EXPLORATORY-<name>.md.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_campaign import fmt, glmm, load, script_t  # noqa: E402


def flips(d, cells, levels):
    x = d[(d.form == "false_belief") & d.cell.isin(cells) & d.pushback.isin(levels)]
    x = x[x.answer_after.isin(["A", "B"])].copy()
    x["b2"] = (x.pushback == "B2").astype(int)
    return x


def contrast(d, a, b):
    x = flips(d, [a, b], ["B1", "B2"])
    x["flag"] = (x.cell == b).astype(int)
    r = glmm(x, "flip", ["flag", "b2"], ["flag"])
    r["script_t"] = script_t(x, "flip", "flag")
    r["rates"] = {c: float(x[x.cell == c].flip.mean()) for c in (a, b)}
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    args = ap.parse_args()
    name, *models = args.family.split(":")
    L = [f"# Phase II exploratory analyses, {name} family", "",
         "**Not pre-registered.** Suggested by external reviews after the confirmatory analysis; same models and tests",
         "as the pre-registered ones, reported as exploratory.", ""]
    for m in models:
        d = load(m, "test")
        L += [f"## {m}", "", "### E1. Warm disclosure (C) against emotional pushback (B1 and B2)", "",
              "| Contrast | Flip rates | Estimate, log-odds [95%], p | Script-level t |", "|---|---|---|---|"]
        for a, b in (("L0", "C"), ("C", "L3"), ("L0", "L3")):
            r = contrast(d, a, b)
            s = r["script_t"]
            rates = ", ".join(f"{k} {100 * v:.1f}%" for k, v in r["rates"].items())
            L.append(f"| {b} vs {a} | {rates} | {fmt(r)} | {s['mean_diff_logodds']:+.2f}, p = {s['p']:.3g} |")
        x = flips(d, ["L0", "C", "L3", "L3_recip"], ["B0", "B1", "B2", "B3"])
        tab = (x.groupby(["pushback", "cell"]).flip.mean() * 100).round(1).unstack()[["L0", "C", "L3", "L3_recip"]]
        L += ["", "### E2. Flip rate (%) by pushback level and cell", "", tab.to_markdown(), ""]
    out = ROOT / "results" / "campaign" / f"EXPLORATORY-{name}.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
