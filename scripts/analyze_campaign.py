"""Analysis of the Phase II campaign, exactly as pre-registered (docs/preregistration.md §6).

    python scripts/analyze_campaign.py --family 35B:qwen3.6-35b-base-i1:qwen3.6-35b-abliterated
    python scripts/analyze_campaign.py --family 35B:<original>:<abl> --family 8B:<original>:<abl1>:<abl2>
    python scripts/analyze_campaign.py --pilot     # runs the same code on the dev pilot (pipeline check)

A family = original model, then its abliterated versions. Writes results/campaign/ANALYSIS-<split>.md and a JSON of
every estimate. Needs numpy, pandas, scipy, statsmodels.

Model for every binary outcome: logistic mixed model, random intercepts for items and scripts (statsmodels
BinomialBayesMixedGLM, variational Bayes); fixed effects: the contrast of interest + option order (correct option
first) + version (1 or 2). Test: z = posterior mean / posterior sd, two-sided. Robustness (reported, not
confirmatory): paired t-test across scripts on the empirical log-odds difference; item-level paired Wilcoxon on
per-item rates; the rate difference in points. Random intercepts also include script x cell, so that the condition
effect may vary across scripts (mean-field variational Bayes is otherwise prone to overconfidence).
Non-answers: excluded (primary); counted as not adopting the false belief (sensitivity).
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
SESOI = 0.5  # smallest effect of interest, log-odds


# ---------------------------------------------------------------- data
def load(model: str, split: str, pilot: bool = False) -> pd.DataFrame:
    if pilot:
        d = pd.read_json(ROOT / "results" / "pilot" / f"{model}.jsonl", lines=True)
        d["cell"] = d["condition"]; d["version"] = 1; d["warmth"] = "acknowledging"; d["backdrop"] = "neutral"
        d["script"] = d.storyline.astype(str) + "-" + d.gender.str[0] + "-v1"
    else:
        d = pd.read_json(ROOT / "results" / "campaign" / model / f"{split}.jsonl", lines=True)
    d["model"] = model
    # Letters from JSON cut short by max_tokens (docs/deviations.md, 2026-11-01): same rule as the runner.
    from campaign import parse_answer
    for raw_col, ans_col in (("raw", "answer"), ("raw_after", "answer_after")):
        if raw_col in d:
            fix = d[ans_col].isna() & d[raw_col].notna()
            d.loc[fix, ans_col] = [parse_answer(r)[0] for r in d.loc[fix, raw_col]]
    d["answered"] = d.answer.isin(["A", "B"])
    d["adopt"] = (d.answer == d.wrong).astype(int)
    d["correct"] = (d.answer == d.key).astype(int)
    d["cf"] = d.correct_first.astype(int)
    d["v2"] = (d.version == 2).astype(int)
    if "pushback" in d:
        d["flip"] = np.where(d.pushback.notna(), (d.answer_after == d.wrong).astype(float), np.nan)
    return d


def fb(d, cells, answered=True):
    x = d[(d.form == "false_belief") & d.cell.isin(cells)]
    return x[x.answered] if answered else x


# ---------------------------------------------------------------- models
def glmm(df: pd.DataFrame, y: str, terms: list[str], test: list[str]) -> dict:
    """Logistic mixed model, item + script random intercepts. Returns estimate, sd, z, p for each tested term."""
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    df = df.dropna(subset=[y]).copy()
    covs = [t for t in ["cf", "v2"] if df[t].nunique() > 1 and t not in terms]
    formula = f"{y} ~ " + " + ".join(terms + covs)
    out = {"n": int(len(df)), "formula": formula}
    if df[y].nunique() < 2:
        out["error"] = "outcome constant"; return out
    # random intercepts: item, script, and script x cell (lets the condition effect vary across scripts)
    df["sc"] = df["model"].astype(str) + "|" + df["script"].astype(str) + "|" + df["cell"].astype(str)
    vc = {"item": "0 + C(item)", "script": "0 + C(script)", "sc": "0 + C(sc)"}
    m = BinomialBayesMixedGLM.from_formula(formula, vc, df)
    r = m.fit_vb()
    names = list(m.exog_names)
    for t in test:
        i = names.index(t)
        est, sd = float(r.fe_mean[i]), float(r.fe_sd[i])
        z = est / sd
        out[t] = {"estimate": est, "sd": sd, "z": z, "p": float(2 * stats.norm.sf(abs(z))),
                  "ci95": [est - 1.96 * sd, est + 1.96 * sd]}
    out["sd_item"], out["sd_script"], out["sd_script_x_cell"] = [float(np.exp(v)) for v in r.vcp_mean]
    return out


def wald_joint(res: dict, terms: list[str]) -> dict:
    """Omnibus test of several coefficients (mean-field posterior: independent normals)."""
    chi2 = sum(res[t]["z"] ** 2 for t in terms)
    return {"chi2": chi2, "df": len(terms), "p": float(stats.chi2.sf(chi2, len(terms)))}


def lmm_pref(df: pd.DataFrame, test: str) -> dict:
    """H7: logit of the renormalized preference for the correct option; item random intercept + script component."""
    import statsmodels.formula.api as smf
    df = df.dropna(subset=["p_correct"]).copy()
    p = df.p_correct.clip(1e-4, 1 - 1e-4)
    df["lp"] = np.log(p / (1 - p))
    covs = [t for t in ["cf", "v2"] if df[t].nunique() > 1 and t != test]
    df["sc"] = df["script"].astype(str) + "|" + df["cell"].astype(str)
    m = smf.mixedlm("lp ~ " + " + ".join([test] + covs), df, groups="item",
                    vc_formula={"script": "0 + C(script)", "sc": "0 + C(sc)"}).fit(reml=True)
    return {"n": int(len(df)), test: {"estimate": float(m.params[test]), "sd": float(m.bse[test]),
                                       "z": float(m.tvalues[test]), "p": float(m.pvalues[test])}}


def item_wilcoxon(df, y, flag):
    g = df.groupby(["item", flag])[y].mean().unstack()
    if g.shape[1] < 2:
        return None
    dlt = (g[1] - g[0]).dropna()
    if np.allclose(dlt, 0):
        return {"p": 1.0, "n_items": int(len(dlt))}
    return {"p": float(stats.wilcoxon(dlt, zero_method="pratt").pvalue), "n_items": int(len(dlt)),
            "mean_diff_points": float(100 * dlt.mean())}


def script_t(df, y, flag):
    """Robustness: paired t-test across scripts on the empirical log-odds difference (flag 1 vs 0)."""
    g = df.groupby(["script", flag])[y].agg(["sum", "size"])
    el = np.log((g["sum"] + 0.5) / (g["size"] - g["sum"] + 0.5)).unstack()
    if el.shape[1] < 2:
        return None
    dlt = (el[1] - el[0]).dropna()
    if len(dlt) < 3:
        return None
    r = stats.ttest_1samp(dlt, 0.0)
    return {"p": float(r.pvalue), "n_scripts": int(len(dlt)), "mean_diff_logodds": float(dlt.mean())}


def holm(ps: dict) -> dict:
    keys = sorted((k for k in ps if ps[k] is not None), key=lambda k: ps[k])
    out, run = {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (len(keys) - i) * ps[k]))
        out[k] = run
    return out


# ---------------------------------------------------------------- hypotheses
def contrast(d, cells_a, cells_b, y="adopt", rows=None):
    """cells_b vs cells_a (flag = 1 for b)."""
    x = rows if rows is not None else fb(d, cells_a + cells_b)
    x = x.copy(); x["flag"] = x.cell.isin(cells_b).astype(int)
    r = glmm(x, y, ["flag"], ["flag"])
    r["rates"] = {c: float(x[x.cell == c][y].mean()) for c in cells_a + cells_b}
    r["wilcoxon"] = item_wilcoxon(x, y, "flag")
    r["script_t"] = script_t(x, y, "flag")
    return r


def per_model(d: pd.DataFrame) -> dict:
    R = {}
    have = set(d.cell)
    # H1 and its sensitivity analysis (non-answers counted as not adopting)
    R["H1"] = contrast(d, ["L0"], ["L3"])
    R["H1_sens_nonanswers"] = contrast(d, ["L0"], ["L3"], rows=fb(d, ["L0", "L3"], answered=False))
    v1 = d[d.version == 1]
    R["H1_version1_only"] = contrast(v1, ["L0"], ["L3"])
    if d.v2.nunique() > 1:
        x = fb(d, ["L0", "L3"]).copy(); x["flag"] = (x.cell == "L3").astype(int); x["flag_v2"] = x.flag * x.v2
        R["H1_version_interaction"] = glmm(x, "adopt", ["flag", "v2", "flag_v2"], ["flag_v2"])
    if "C" in have:
        R["H1b"] = contrast(d, ["C"], ["L3"])
    # H2 dose: gradual cells L0..L4, level as a numeric trend
    dose = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}
    if {"L1", "L2", "L4"} <= have:
        x = fb(d, list(dose)).copy(); x["level"] = x.cell.map(dose)
        R["H2"] = glmm(x, "adopt", ["level"], ["level"])
        R["H2"]["rates"] = {c: float(x[x.cell == c].adopt.mean()) for c in dose}
    # H3 pressure: flips after pushback, L3 vs L0, x pushback level (0..3)
    if "pushback" in d:
        x = d[(d.form == "false_belief") & d.cell.isin(["L0", "L3"]) & d.pushback.notna()].copy()
        x = x[x.answer_after.isin(["A", "B"])]
        x["flag"] = (x.cell == "L3").astype(int); x["b"] = x.pushback.str[1].astype(int); x["flag_b"] = x.flag * x.b
        R["H3"] = glmm(x, "flip", ["flag", "b", "flag_b"], ["flag_b", "flag"])
        R["H3"]["rates"] = x.groupby(["cell", "pushback"]).flip.mean().unstack().round(4).to_dict()
    # H4 divergence across contexts: plain correct, false belief adopted, same item x script
    pl = d[(d.form == "plain") & d.answered][["cell", "item", "script", "correct"]].rename(columns={"correct": "pc"})
    m = fb(d, ["L0", "L3"]).merge(pl, on=["cell", "item", "script"])
    R["H4"] = contrast(d, ["L0"], ["L3"], rows=m[m.pc == 1])
    # H6 plain accuracy
    x = d[(d.form == "plain") & d.answered & d.cell.isin(["L0", "L3"])]
    R["H6"] = contrast(d, ["L0"], ["L3"], y="correct", rows=x)
    # H7 internal preference (false-belief form)
    x = fb(d, ["L0", "L3"]).copy(); x["flag"] = (x.cell == "L3").astype(int)
    R["H7"] = lmm_pref(x, "flag")
    R["H7"]["mean_pref"] = x.groupby("cell").p_correct.mean().round(4).to_dict()
    # H8 trajectory at level 3 (gradual reference)
    if {"L3_sudden", "L3_constant"} <= have:
        x = fb(d, ["L3", "L3_sudden", "L3_constant"]).copy()
        x["sudden"] = (x.cell == "L3_sudden").astype(int); x["constant"] = (x.cell == "L3_constant").astype(int)
        r = glmm(x, "adopt", ["sudden", "constant"], ["sudden", "constant"])
        r["omnibus"] = wald_joint(r, ["sudden", "constant"])
        r["rates"] = {c: float(x[x.cell == c].adopt.mean()) for c in ["L3", "L3_sudden", "L3_constant"]}
        R["H8"] = r
    # H9 assistant reciprocity: adoption, and flips after B2
    if "L3_recip" in have:
        R["H9a"] = contrast(d, ["L3"], ["L3_recip"])
        x = d[(d.form == "false_belief") & d.cell.isin(["L3", "L3_recip"]) & (d.pushback == "B2")]
        x = x[x.answer_after.isin(["A", "B"])]
        R["H9b"] = contrast(d, ["L3"], ["L3_recip"], y="flip", rows=x)
    # Exploratory: backdrop x condition
    if {"L0_sad", "L3_sad", "L0_despair", "L3_despair"} <= have:
        x = fb(d, ["L0", "L3", "L0_sad", "L3_sad", "L0_despair", "L3_despair"]).copy()
        x["l3"] = x.cell.str.startswith("L3").astype(int)
        x["sad"] = x.cell.str.endswith("_sad").astype(int); x["despair"] = x.cell.str.endswith("_despair").astype(int)
        x["l3_sad"] = x.l3 * x.sad; x["l3_despair"] = x.l3 * x.despair
        R["X_backdrop"] = glmm(x, "adopt", ["l3", "sad", "despair", "l3_sad", "l3_despair"], ["l3_sad", "l3_despair"])
    return R


def h5(d_orig: pd.DataFrame, d_abl: pd.DataFrame) -> dict:
    """Interaction model x condition (L3 vs L0) on the items both models share."""
    items = set(d_orig.item) & set(d_abl.item)
    x = pd.concat([fb(d_orig, ["L0", "L3"]).assign(abl=0), fb(d_abl, ["L0", "L3"]).assign(abl=1)])
    x = x[x.item.isin(items)].copy()
    x["flag"] = (x.cell == "L3").astype(int); x["flag_abl"] = x.flag * x.abl
    return glmm(x, "adopt", ["flag", "abl", "flag_abl"], ["flag_abl"])


SECONDARY = [("H1b", "flag"), ("H2", "level"), ("H3", "flag_b"), ("H4", "flag"), ("H6", "flag"), ("H7", "flag"),
             ("H8", None), ("H9a", "flag"), ("H9b", "flag")]


def pval(R, h, term):
    if h not in R or "error" in R[h]:
        return None
    return R[h]["omnibus"]["p"] if term is None else R[h][term]["p"]


# ---------------------------------------------------------------- report
def fmt(r, term="flag"):
    if r is None or "error" in r or term not in r:
        return "n/a"
    t = r[term]
    return f"{t['estimate']:+.2f} [{t['ci95'][0]:+.2f}, {t['ci95'][1]:+.2f}], p = {t['p']:.3g}" if "ci95" in t else \
        f"{t['estimate']:+.3f} (sd {t['sd']:.3f}), p = {t['p']:.3g}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", action="append", help="NAME:original[:abliterated...]")
    ap.add_argument("--split", default="test", choices=["test", "dev"])
    ap.add_argument("--pilot", action="store_true", help="run on the dev pilot (pipeline check, L0/C/L3 only)")
    args = ap.parse_args()
    fams = args.family or ["35B:qwen3.6-35b-base-i1:qwen3.6-35b-abliterated"]
    tag = "pilot" if args.pilot else args.split
    allres, lines = {}, [f"# Phase II analysis ({tag})", "",
                         "Log-odds estimates from the pre-registered mixed logistic model, 95% interval, two-sided p.",
                         f"Smallest effect of interest: |{SESOI}|.", ""]
    h1_p = {}
    for fam in fams:
        name, orig, *abls = fam.split(":")
        data = {m: load(m, args.split, args.pilot) for m in [orig, *abls]}
        for m, d in data.items():
            print(f"fitting {m} ...", flush=True)
            R = per_model(d); allres[m] = R
            if m == orig:
                h1_p[m] = R["H1"]["flag"]["p"]
        for a in abls:
            print(f"fitting H5 {orig} vs {a} ...", flush=True)
            allres[f"H5:{orig}:{a}"] = h5(data[orig], data[a])
        lines += [f"## Family {name}", ""]
        for m in [orig, *abls]:
            R = allres[m]
            role = "original" if m == orig else "abliterated"
            lines += [f"### {m} ({role})", "", "| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |",
                      "|---|---|---|---|---|"]
            for h, term in [("H1", "flag"), ("H1_sens_nonanswers", "flag"), ("H1_version1_only", "flag"),
                            ("H1_version_interaction", "flag_v2")] + SECONDARY:
                if h not in R:
                    continue
                r = R[h]
                rates = ", ".join(f"{k} {100 * v:.1f}%" for k, v in r.get("rates", {}).items()
                                  if isinstance(v, float)) if isinstance(r.get("rates"), dict) else ""
                est = (f"omnibus chi2 {r['omnibus']['chi2']:.2f}, p = {r['omnibus']['p']:.3g}; sudden {fmt(r, 'sudden')};"
                       f" constant {fmt(r, 'constant')}") if term is None else fmt(r, term)
                w = r.get("wilcoxon")
                ws = f"{w.get('mean_diff_points', 0):+.1f} pts, p = {w['p']:.3g}" if w else ""
                s = r.get("script_t")
                ss = f"{s['mean_diff_logodds']:+.2f}, p = {s['p']:.3g} (n = {s['n_scripts']})" if s else ""
                lines.append(f"| {h} | {rates} | {est} | {ss} | {ws} |")
            if "H3" in R:
                lines += ["", f"H3 flip rates by cell and pushback level: `{json.dumps(R['H3']['rates'])}`"]
            if "H7" in R:
                lines += [f"H7 mean preference for the correct option: `{json.dumps(R['H7']['mean_pref'])}`"]
            if "X_backdrop" in R:
                lines += [f"Exploratory backdrop x level 3: sad {fmt(R['X_backdrop'], 'l3_sad')}; "
                          f"despair {fmt(R['X_backdrop'], 'l3_despair')}"]
            if m == orig:
                sec = holm({h: pval(R, h, t) for h, t in SECONDARY})
                lines += ["", "Secondary family, Holm-adjusted p: " +
                          ", ".join(f"{h} {p:.3g}" for h, p in sec.items())]
            lines.append("")
        h5_adj = holm({a: allres[f"H5:{orig}:{a}"]["flag_abl"]["p"] for a in abls}) if abls else {}
        for a in abls:
            r = allres[f"H5:{orig}:{a}"]
            lines += [f"**H5** {a} vs {orig}, interaction abliterated x level 3: {fmt(r, 'flag_abl')}"
                      f" (Holm over recipes: {h5_adj[a]:.3g})", ""]
    adj = holm(h1_p)
    lines += ["## Primary hypothesis H1 (Holm over the original models)", "",
              "| Model | Estimate [95%], p | Holm p | Beyond the smallest effect of interest |", "|---|---|---|---|"]
    for m, p in h1_p.items():
        t = allres[m]["H1"]["flag"]
        beyond = "yes" if (t["ci95"][0] > SESOI or t["ci95"][1] < -SESOI) else \
            ("within ±0.5 (equivalence)" if (t["ci95"][0] > -SESOI and t["ci95"][1] < SESOI) else "undetermined")
        lines.append(f"| {m} | {fmt(allres[m]['H1'])} | {adj[m]:.3g} | {beyond} |")
    out = ROOT / "results" / ("pilot" if args.pilot else "campaign")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"ANALYSIS-{tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / f"analysis-{tag}.json").write_text(json.dumps(allres, indent=1, default=float), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
