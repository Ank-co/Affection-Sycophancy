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
| H2 | L0 4.3%, L1 2.7%, L2 3.0%, L3 3.0%, L4 3.0% | -0.22 [-0.27, -0.17], p < 1e-15 |  |  |
| H3 |  | -0.07 [-0.12, -0.02], p = 0.0075 |  |  |
| H4 | L0 2.6%, L3 1.2% | -1.26 [-1.55, -0.97], p < 1e-15 | -0.77, p = 4.55e-05 (n = 20) | -1.1 pts, p = 1.9e-06 |
| H6 | L0 98.0%, L3 97.6% | +0.63 [-1.63, +2.90], p = 0.583 | -0.22, p = 0.0343 (n = 20) | -0.3 pts, p = 0.154 |
| H7 |  | +0.544 (sd 0.011), p < 1e-15 |  |  |
| H8 | L3 3.0%, L3_sudden 3.6%, L3_constant 3.4% | omnibus chi2 9.78, p = 0.00752; sudden +0.41 [+0.10, +0.71], p = 0.00925; constant +0.28 [-0.04, +0.59], p = 0.0829 |  |  |
| H9a | L3 3.0%, L3_recip 3.3% | +0.22 [-0.10, +0.54], p = 0.181 | +0.12, p = 0.284 (n = 10) | +0.3 pts, p = 0.628 |
| H9b | L3 8.8%, L3_recip 9.7% | +0.15 [-0.14, +0.45], p = 0.305 | +0.07, p = 0.555 (n = 10) | +1.5 pts, p = 0.681 |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0, "L3": 0.0}, "B1": {"L0": 0.5252, "L3": 0.2303}, "B2": {"L0": 0.3957, "L3": 0.088}, "B3": {"L0": 0.0624, "L3": 0.0383}}`
H7 mean preference for the correct option: `{"L0": 0.8953, "L3": 0.9294}`
Exploratory backdrop x level 3: sad +0.10 [-0.20, +0.41], p = 0.504; despair +0.04 [-0.27, +0.36], p = 0.784

Secondary family, Holm-adjusted p: H7 < 1e-15, H4 < 1e-15, H2 < 1e-15, H1b 2.69e-05, H3 0.0375, H8 0.0375, H9a 0.542, H9b 0.61, H6 0.61

### qwen3.6-35b-abliterated (abliterated)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 17.7%, L3 12.7% | -0.96 [-1.08, -0.84], p < 1e-15 | -0.34, p = 0.000196 (n = 20) | -5.0 pts, p = 2.74e-14 |
| H1_sens_nonanswers | L0 17.7%, L3 12.7% | -0.96 [-1.08, -0.84], p < 1e-15 | -0.34, p = 0.000196 (n = 20) | -5.0 pts, p = 2.74e-14 |
| H1_version1_only | L0 16.9%, L3 12.5% | -0.86 [-1.03, -0.69], p < 1e-15 | -0.28, p = 0.0531 (n = 10) | -4.4 pts, p = 5.67e-07 |
| H1_version_interaction |  | -0.26 [-0.43, -0.10], p = 0.00203 |  |  |
| H1b | C 18.0%, L3 12.7% | -1.00 [-1.12, -0.88], p < 1e-15 | -0.38, p = 7.93e-06 (n = 20) | -5.3 pts, p = 8.05e-16 |
| H2 | L0 17.7%, L1 11.9%, L2 14.1%, L3 12.7%, L4 13.2% | -0.20 [-0.23, -0.18], p < 1e-15 |  |  |
| H3 |  | -0.14 [-0.21, -0.08], p = 9.4e-06 |  |  |
| H4 | L0 15.8%, L3 10.5% | -1.04 [-1.17, -0.92], p < 1e-15 | -0.42, p = 8.47e-05 (n = 20) | -5.3 pts, p = 1.85e-14 |
| H6 | L0 97.5%, L3 97.2% | +0.84 [-0.89, +2.56], p = 0.341 | -0.10, p = 0.00883 (n = 20) | -0.3 pts, p = 0.147 |
| H7 |  | +0.284 (sd 0.009), p < 1e-15 |  |  |
| H8 | L3 12.7%, L3_sudden 13.8%, L3_constant 13.5% | omnibus chi2 18.17, p = 0.000113; sudden +0.29 [+0.12, +0.46], p = 0.00059; constant +0.22 [+0.05, +0.38], p = 0.0116 |  |  |
| H9a | L3 12.7%, L3_recip 12.6% | +0.03 [-0.15, +0.20], p = 0.775 | +0.01, p = 0.759 (n = 10) | -0.1 pts, p = 0.61 |
| H9b | L3 7.8%, L3_recip 6.5% | -0.19 [-0.54, +0.16], p = 0.279 | +0.28, p = 0.524 (n = 10) | -0.7 pts, p = 0.0472 |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0016, "L3": 0.0}, "B1": {"L0": 0.4833, "L3": 0.1895}, "B2": {"L0": 0.4138, "L3": 0.0776}, "B3": {"L0": 0.0057, "L3": 0.0023}}`
H7 mean preference for the correct option: `{"L0": 0.7333, "L3": 0.7731}`
Exploratory backdrop x level 3: sad +0.08 [-0.09, +0.25], p = 0.365; despair +0.17 [-0.01, +0.34], p = 0.0582

**H5** qwen3.6-35b-abliterated vs qwen3.6-35b-base-i1, interaction abliterated x level 3: -0.11 [-0.22, -0.00], p = 0.0476 (Holm over recipes: 0.0476)

## Family 8B

### qwen3-8b (original)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 12.9%, L3 19.5% | +0.96 [+0.85, +1.07], p < 1e-15 | +0.50, p = 3.54e-11 (n = 20) | +6.6 pts, p = 1.96e-08 |
| H1_sens_nonanswers | L0 12.9%, L3 19.5% | +0.96 [+0.85, +1.07], p < 1e-15 | +0.50, p = 3.54e-11 (n = 20) | +6.6 pts, p = 1.96e-08 |
| H1_version1_only | L0 12.2%, L3 19.3% | +1.51 [+1.32, +1.69], p < 1e-15 | +0.54, p = 2.18e-05 (n = 10) | +7.1 pts, p = 2.24e-05 |
| H1_version_interaction |  | -0.09 [-0.24, +0.06], p = 0.245 |  |  |
| H1b | C 14.5%, L3 19.5% | +0.75 [+0.64, +0.86], p < 1e-15 | +0.36, p = 1.85e-07 (n = 20) | +5.0 pts, p = 1.55e-09 |
| H2 | L0 12.9%, L1 13.9%, L2 15.3%, L3 19.5%, L4 18.9% | +0.28 [+0.25, +0.30], p < 1e-15 |  |  |
| H3 |  | +0.34 [+0.24, +0.44], p = 1.49e-11 |  |  |
| H4 | L0 10.4%, L3 16.3% | +1.02 [+0.91, +1.14], p < 1e-15 | +0.53, p = 5.38e-10 (n = 20) | +6.7 pts, p = 1.35e-07 |
| H6 | L0 96.5%, L3 95.6% | -0.66 [-0.85, -0.47], p = 2.35e-11 | -0.26, p = 0.000109 (n = 20) | -1.0 pts, p = 0.00666 |
| H7 |  | -0.219 (sd 0.022), p < 1e-15 |  |  |
| H8 | L3 19.5%, L3_sudden 17.0%, L3_constant 22.4% | omnibus chi2 44.92, p = 1.76e-10; sudden -0.39 [-0.55, -0.23], p = 2.74e-06; constant +0.37 [+0.22, +0.53], p = 1.69e-06 |  |  |
| H9a | L3 19.5%, L3_recip 19.0% | -0.10 [-0.26, +0.06], p = 0.212 | -0.05, p = 0.135 (n = 10) | -0.5 pts, p = 0.177 |
| H9b | L3 5.9%, L3_recip 10.0% | +0.86 [+0.44, +1.28], p = 5.94e-05 | +0.51, p = 0.0193 (n = 10) | +4.3 pts, p = 0.0149 |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0, "L3": 0.0}, "B1": {"L0": 0.001, "L3": 0.0}, "B2": {"L0": 0.0382, "L3": 0.0594}, "B3": {"L0": 0.0147, "L3": 0.0388}}`
H7 mean preference for the correct option: `{"L0": 0.8363, "L3": 0.7874}`
Exploratory backdrop x level 3: sad -0.00 [-0.16, +0.15], p = 0.952; despair -0.07 [-0.23, +0.09], p = 0.374

Secondary family, Holm-adjusted p: H2 < 1e-15, H4 < 1e-15, H1b < 1e-15, H7 < 1e-15, H3 7.45e-11, H6 9.39e-11, H8 5.29e-10, H9b 0.000119, H9a 0.212

### qwen3-8b-huihui (abliterated)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 12.5%, L3 21.3% | +1.40 [+1.28, +1.51], p < 1e-15 | +0.65, p = 5.71e-13 (n = 20) | +8.9 pts, p = 1.14e-16 |
| H1_sens_nonanswers | L0 12.5%, L3 21.3% | +1.40 [+1.28, +1.51], p < 1e-15 | +0.65, p = 5.71e-13 (n = 20) | +8.9 pts, p = 1.14e-16 |
| H1_version1_only | L0 10.8%, L3 19.3% | +2.16 [+1.96, +2.36], p < 1e-15 | +0.68, p = 3.39e-06 (n = 10) | +8.5 pts, p = 3.16e-11 |
| H1_version_interaction |  | +0.00 [-0.16, +0.16], p = 0.979 |  |  |
| H1b | C 15.2%, L3 21.3% | +0.98 [+0.87, +1.10], p < 1e-15 | +0.41, p = 1.23e-11 (n = 20) | +6.1 pts, p = 1.47e-12 |
| H2 | L0 12.5%, L1 14.4%, L2 16.3%, L3 21.3%, L4 20.7% | +0.40 [+0.37, +0.43], p < 1e-15 |  |  |
| H3 |  | +0.24 [+0.15, +0.33], p = 2.34e-07 |  |  |
| H4 | L0 9.9%, L3 17.8% | +1.45 [+1.33, +1.57], p < 1e-15 | +0.67, p = 2.1e-12 (n = 20) | +8.7 pts, p = 2.74e-14 |
| H6 | L0 96.9%, L3 95.5% | -0.07 [-0.66, +0.52], p = 0.818 | -0.42, p = 1.46e-07 (n = 20) | -1.4 pts, p = 0.000147 |
| H7 |  | -0.334 (sd 0.026), p < 1e-15 |  |  |
| H8 | L3 21.3%, L3_sudden 18.0%, L3_constant 26.8% | omnibus chi2 132.12, p = 2.05e-29; sudden -0.50 [-0.66, -0.33], p = 4.53e-09; constant +0.79 [+0.63, +0.94], p < 1e-15 |  |  |
| H9a | L3 21.3%, L3_recip 20.6% | -0.10 [-0.27, +0.06], p = 0.22 | -0.03, p = 0.258 (n = 10) | -0.7 pts, p = 0.108 |
| H9b | L3 10.7%, L3_recip 15.7% | +0.92 [+0.53, +1.32], p = 4.55e-06 | +0.56, p = 0.032 (n = 10) | +6.4 pts, p = 0.00235 |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0011, "L3": 0.0}, "B1": {"L0": 0.0021, "L3": 0.0069}, "B2": {"L0": 0.0777, "L3": 0.1068}, "B3": {"L0": 0.0041, "L3": 0.0253}}`
H7 mean preference for the correct option: `{"L0": 0.8385, "L3": 0.7692}`
Exploratory backdrop x level 3: sad -0.01 [-0.17, +0.15], p = 0.942; despair -0.00 [-0.16, +0.16], p = 0.961

### qwen3-8b-mlabonne (abliterated)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 48.9%, L3 55.1% | +0.55 [+0.46, +0.64], p < 1e-15 | +0.25, p = 9.32e-05 (n = 20) | +6.2 pts, p = 2.33e-10 |
| H1_sens_nonanswers | L0 48.9%, L3 55.1% | +0.55 [+0.46, +0.64], p < 1e-15 | +0.25, p = 9.32e-05 (n = 20) | +6.2 pts, p = 2.33e-10 |
| H1_version1_only | L0 48.3%, L3 52.4% | +0.59 [+0.43, +0.74], p = 2.76e-13 | +0.17, p = 0.0421 (n = 10) | +4.1 pts, p = 0.00104 |
| H1_version_interaction |  | +0.38 [+0.25, +0.51], p = 3.53e-09 |  |  |
| H1b | C 54.2%, L3 55.1% | +0.08 [-0.01, +0.17], p = 0.0941 | +0.03, p = 0.394 (n = 20) | +0.8 pts, p = 0.249 |
| H2 | L0 48.9%, L1 45.5%, L2 50.6%, L3 55.1%, L4 57.7% | +0.22 [+0.20, +0.24], p < 1e-15 |  |  |
| H3 |  | +0.21 [+0.14, +0.28], p = 1.96e-08 |  |  |
| H4 | L0 44.3%, L3 51.1% | +0.57 [+0.48, +0.66], p < 1e-15 | +0.28, p = 0.00012 (n = 20) | +7.2 pts, p = 3.69e-10 |
| H6 | L0 91.9%, L3 91.6% | -0.06 [-0.24, +0.12], p = 0.491 | -0.01, p = 0.729 (n = 20) | -0.3 pts, p = 0.803 |
| H7 |  | -0.981 (sd 0.054), p < 1e-15 |  |  |
| H8 | L3 55.1%, L3_sudden 53.1%, L3_constant 70.4% | omnibus chi2 486.06, p = 2.84e-106; sudden -0.19 [-0.31, -0.06], p = 0.00393; constant +1.53 [+1.39, +1.67], p < 1e-15 |  |  |
| H9a | L3 55.1%, L3_recip 57.8% | +0.27 [+0.14, +0.40], p = 6.61e-05 | +0.11, p = 0.0141 (n = 10) | +2.8 pts, p = 1.84e-06 |
| H9b | L3 50.5%, L3_recip 49.6% | -0.09 [-0.58, +0.39], p = 0.71 | -0.11, p = 0.292 (n = 10) | +0.3 pts, p = 0.636 |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.357, "L3": 0.3631}, "B1": {"L0": 0.362, "L3": 0.3747}, "B2": {"L0": 0.3262, "L3": 0.505}, "B3": {"L0": 0.4442, "L3": 0.4528}}`
H7 mean preference for the correct option: `{"L0": 0.5083, "L3": 0.4486}`
Exploratory backdrop x level 3: sad +0.16 [+0.04, +0.29], p = 0.0107; despair +0.03 [-0.10, +0.16], p = 0.646

**H5** qwen3-8b-huihui vs qwen3-8b, interaction abliterated x level 3: +0.30 [+0.19, +0.40], p = 2.05e-08 (Holm over recipes: 2.05e-08)

**H5** qwen3-8b-mlabonne vs qwen3-8b, interaction abliterated x level 3: -0.25 [-0.34, -0.17], p = 1.52e-09 (Holm over recipes: 3.05e-09)

## Primary hypothesis H1 (Holm over the original models)

| Model | Estimate [95%], p | Holm p | Beyond the smallest effect of interest |
|---|---|---|---|
| qwen3.6-35b-base-i1 | -0.85 [-1.06, -0.63], p = 1.42e-14 | 1.42e-14 | yes |
| qwen3-8b | +0.96 [+0.85, +1.07], p < 1e-15 | 1.58e-67 | yes |
