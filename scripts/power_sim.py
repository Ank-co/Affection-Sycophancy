"""Power simulation for H1 (L3 vs L0), run before the test. Baselines and variances from the dev pilot.
Usage: python scripts/power_sim.py   (about 5 minutes; seed fixed)."""
import numpy as np
from scipy.stats import wilcoxon
rng=np.random.default_rng(2026)
def sim(b0, sd_item, sd_script, delta, n_items=302, n_scripts=10, reps=400, alpha=0.025):
    hits=0
    for _ in range(reps):
        u=rng.normal(0,sd_item,n_items); v0=rng.normal(0,sd_script,n_scripts); v3=rng.normal(0,sd_script,n_scripts)
        p0=1/(1+np.exp(-(b0+u[:,None]+v0[None,:]))); p3=1/(1+np.exp(-(b0+delta+u[:,None]+v3[None,:])))
        y0=rng.random(p0.shape)<p0; y3=rng.random(p3.shape)<p3
        d=y3.mean(1)-y0.mean(1)
        if np.allclose(d,0): continue
        p=wilcoxon(d,zero_method="pratt").pvalue
        hits+= p<alpha
    return hits/reps
print("Power, item-level paired Wilcoxon (conservative proxy for the mixed model), alpha 0.025 (Holm over 2 models)")
for name,b0,si,ss in (("original",-5.76,3.40,0.30),("abliterated",-2.16,2.45,0.48)):
    for ns in (10,20):
        row=[f"{sim(b0,si,ss,dl,n_scripts=ns):.2f}" for dl in (-0.8,-0.5,-0.3,0.3,0.5)]
        print(f"{name:12s} scripts={ns:2d}  delta -0.8:{row[0]}  -0.5:{row[1]}  -0.3:{row[2]}  +0.3:{row[3]}  +0.5:{row[4]}")
