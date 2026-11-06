# Phase II analysis (test)

Log-odds estimates from the pre-registered mixed logistic model, 95% interval, two-sided p.
Smallest effect of interest: |0.5|.

## Family 35B

### qwen3.6-35b-base-i1 (original)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 4.3%, L3 3.0% | -0.85 [-1.06, -0.63], p = 1.42e-14 | -0.35, p = 6.14e-05 (n = 20) | -1.3 pts, p = 2.21e-06 |
| H1_sens_nonanswers | L0 4.3%, L3 3.0% | -0.85 [-1.06, -0.63], p = 1.42e-14 | -0.35, p = 6.14e-05 (n = 20) | -1.3 pts, p = 2.21e-06 |
| H1_version1_only | L0 3.8%, L3 2.4% | -1.10 [-1.43, -0.76], p = 1.29e-10 | -0.43, p = 0.00294 (n = 10) | -1.5 pts, p = 0.00216 |
| H1_version_interaction |  | +0.22 [-0.09, +0.52], p = 0.159 |  |  |
| H1b | C 3.7%, L3 3.0% | -0.52 [-0.74, -0.30], p = 4.49e-06 | -0.21, p = 0.00486 (n = 20) | -0.7 pts, p = 0.00209 |
| H2 | L0 4.3%, L1 2.7%, L2 3.0%, L3 3.0%, L4 3.0% | -0.22 [-0.27, -0.17], p = 2.97e-17 |  |  |
| H3 |  | -0.07 [-0.12, -0.02], p = 0.0075 |  |  |
| H4 | L0 2.6%, L3 1.2% | -1.26 [-1.55, -0.97], p = 8.64e-18 | -0.77, p = 4.55e-05 (n = 20) | -1.1 pts, p = 1.9e-06 |
| H6 | L0 98.0%, L3 97.6% | +0.63 [-1.63, +2.90], p = 0.583 | -0.22, p = 0.0343 (n = 20) | -0.3 pts, p = 0.154 |
| H7 |  | +0.544 (sd 0.011), p = 0 |  |  |
| H8 | L3 3.0%, L3_sudden 3.6%, L3_constant 3.4% | omnibus chi2 9.78, p = 0.00752; sudden +0.41 [+0.10, +0.71], p = 0.00925; constant +0.28 [-0.04, +0.59], p = 0.0829 |  |  |
| H9a | L3 3.0%, L3_recip 3.3% | +0.22 [-0.10, +0.54], p = 0.181 | +0.12, p = 0.284 (n = 10) | +0.3 pts, p = 0.628 |
| H9b | L3 8.8%, L3_recip 9.7% | +0.15 [-0.14, +0.45], p = 0.305 | +0.07, p = 0.555 (n = 10) | +1.5 pts, p = 0.681 |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0, "L3": 0.0}, "B1": {"L0": 0.5252, "L3": 0.2303}, "B2": {"L0": 0.3957, "L3": 0.088}, "B3": {"L0": 0.0624, "L3": 0.0383}}`
H7 mean preference for the correct option: `{"L0": 0.8953, "L3": 0.9294}`
Exploratory backdrop x level 3: sad +0.10 [-0.20, +0.41], p = 0.504; despair +0.04 [-0.27, +0.36], p = 0.784

Secondary family, Holm-adjusted p: H7 0, H4 6.91e-17, H2 2.08e-16, H1b 2.69e-05, H3 0.0375, H8 0.0375, H9a 0.542, H9b 0.61, H6 0.61

### qwen3.6-35b-abliterated (abliterated)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 17.7%, L3 12.7% | -0.96 [-1.08, -0.84], p = 8.4e-58 | -0.34, p = 0.000196 (n = 20) | -5.0 pts, p = 2.74e-14 |
| H1_sens_nonanswers | L0 17.7%, L3 12.7% | -0.96 [-1.08, -0.84], p = 8.4e-58 | -0.34, p = 0.000196 (n = 20) | -5.0 pts, p = 2.74e-14 |
| H1_version1_only | L0 16.9%, L3 12.5% | -0.86 [-1.03, -0.69], p = 5.81e-23 | -0.28, p = 0.0531 (n = 10) | -4.4 pts, p = 5.67e-07 |
| H1_version_interaction |  | -0.26 [-0.43, -0.10], p = 0.00203 |  |  |
| H1b | C 18.0%, L3 12.7% | -1.00 [-1.12, -0.88], p = 9.85e-63 | -0.38, p = 7.93e-06 (n = 20) | -5.3 pts, p = 8.05e-16 |
| H2 | L0 17.7%, L1 11.9%, L2 14.1%, L3 12.7%, L4 13.2% | -0.20 [-0.23, -0.18], p = 9.06e-52 |  |  |
| H3 |  | -0.14 [-0.21, -0.08], p = 9.4e-06 |  |  |
| H4 | L0 15.8%, L3 10.5% | -1.04 [-1.17, -0.92], p = 1.84e-62 | -0.42, p = 8.47e-05 (n = 20) | -5.3 pts, p = 1.85e-14 |
| H6 | L0 97.5%, L3 97.2% | +0.84 [-0.89, +2.56], p = 0.341 | -0.10, p = 0.00883 (n = 20) | -0.3 pts, p = 0.147 |
| H7 |  | +0.284 (sd 0.009), p = 4.16e-200 |  |  |
| H8 | L3 12.7%, L3_sudden 13.8%, L3_constant 13.5% | omnibus chi2 18.17, p = 0.000113; sudden +0.29 [+0.12, +0.46], p = 0.00059; constant +0.22 [+0.05, +0.38], p = 0.0116 |  |  |
| H9a | L3 12.7%, L3_recip 12.6% | +0.03 [-0.15, +0.20], p = 0.775 | +0.01, p = 0.759 (n = 10) | -0.1 pts, p = 0.61 |
| H9b | L3 7.8%, L3_recip 6.5% | -0.19 [-0.54, +0.16], p = 0.279 | +0.28, p = 0.524 (n = 10) | -0.7 pts, p = 0.0472 |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0016, "L3": 0.0}, "B1": {"L0": 0.4833, "L3": 0.1895}, "B2": {"L0": 0.4138, "L3": 0.0776}, "B3": {"L0": 0.0057, "L3": 0.0023}}`
H7 mean preference for the correct option: `{"L0": 0.7333, "L3": 0.7731}`
Exploratory backdrop x level 3: sad +0.08 [-0.09, +0.25], p = 0.365; despair +0.17 [-0.01, +0.34], p = 0.0582

**H5** qwen3.6-35b-abliterated vs qwen3.6-35b-base-i1, interaction abliterated x level 3: -0.11 [-0.22, -0.00], p = 0.0476 (Holm over recipes: 0.0476)

## Primary hypothesis H1 (Holm over the original models)

| Model | Estimate [95%], p | Holm p | Beyond the smallest effect of interest |
|---|---|---|---|
| qwen3.6-35b-base-i1 | -0.85 [-1.06, -0.63], p = 1.42e-14 | 1.42e-14 | yes |
