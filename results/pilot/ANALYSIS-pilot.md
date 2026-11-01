# Phase II analysis (pilot)

Log-odds estimates from the pre-registered mixed logistic model, 95% interval, two-sided p.
Smallest effect of interest: |0.5|.

## Family 35B

### qwen3.6-35b-base-i1 (original)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 7.1%, L3 5.2% | -1.00 [-1.48, -0.52], p = 4.27e-05 | -0.28, p = 0.0236 (n = 10) | -1.8 pts, p = 0.00683 |
| H1_sens_nonanswers | L0 7.0%, L3 5.2% | -1.00 [-1.48, -0.52], p = 4.31e-05 | -0.27, p = 0.0243 (n = 10) | -1.8 pts, p = 0.00683 |
| H1_version1_only | L0 7.1%, L3 5.2% | -1.00 [-1.48, -0.52], p = 4.27e-05 | -0.28, p = 0.0236 (n = 10) | -1.8 pts, p = 0.00683 |
| H1b | C 5.7%, L3 5.2% | -0.37 [-0.86, +0.11], p = 0.133 | -0.07, p = 0.382 (n = 10) | -0.5 pts, p = 0.551 |
| H3 |  | -1.12 [-1.32, -0.92], p = 1.85e-28 |  |  |
| H4 | L0 4.4%, L3 2.3% | -1.12 [-1.64, -0.59], p = 2.91e-05 | -0.56, p = 0.0111 (n = 10) | -1.9 pts, p = 0.0123 |
| H6 | L0 97.1%, L3 96.7% | -0.14 [-0.80, +0.52], p = 0.678 | -0.10, p = 0.227 (n = 10) | -0.4 pts, p = 0.183 |
| H7 |  | +0.544 (sd 0.026), p = 3.36e-97 |  |  |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0067, "L3": 0.0044}, "B2": {"L0": 0.4526, "L3": 0.071}}`
H7 mean preference for the correct option: `{"L0": 0.8704, "L3": 0.9048}`

Secondary family, Holm-adjusted p: H7 1.68e-96, H3 7.38e-28, H4 8.73e-05, H1b 0.266, H6 0.678

### qwen3.6-35b-abliterated (abliterated)

| Test | Rates | Estimate [95%], p | Script-level t (log-odds) | Item-level Wilcoxon |
|---|---|---|---|---|
| H1 | L0 23.0%, L3 18.0% | -0.90 [-1.18, -0.63], p = 8.17e-11 | -0.27, p = 0.0184 (n = 10) | -5.0 pts, p = 0.000375 |
| H1_sens_nonanswers | L0 23.0%, L3 18.0% | -0.90 [-1.18, -0.63], p = 8.17e-11 | -0.27, p = 0.0184 (n = 10) | -5.0 pts, p = 0.000375 |
| H1_version1_only | L0 23.0%, L3 18.0% | -0.90 [-1.18, -0.63], p = 8.17e-11 | -0.27, p = 0.0184 (n = 10) | -5.0 pts, p = 0.000375 |
| H1b | C 21.8%, L3 18.0% | -0.74 [-1.01, -0.46], p = 1.75e-07 | -0.23, p = 0.0321 (n = 10) | -3.9 pts, p = 0.000543 |
| H3 |  | -0.36 [-0.54, -0.18], p = 0.000104 |  |  |
| H4 | L0 20.7%, L3 16.0% | -0.85 [-1.13, -0.58], p = 9.03e-10 | -0.27, p = 0.0219 (n = 10) | -4.6 pts, p = 0.00118 |
| H6 | L0 96.9%, L3 97.3% | +0.45 [-0.09, +0.98], p = 0.104 | +0.14, p = 0.154 (n = 10) | +0.4 pts, p = 0.525 |
| H7 |  | +0.175 (sd 0.024), p = 4.02e-13 |  |  |

H3 flip rates by cell and pushback level: `{"B0": {"L0": 0.0, "L3": 0.0}, "B2": {"L0": 0.3708, "L3": 0.0995}}`
H7 mean preference for the correct option: `{"L0": 0.7176, "L3": 0.7462}`

**H5** qwen3.6-35b-abliterated vs qwen3.6-35b-base-i1, interaction abliterated x level 3: +0.29 [+0.03, +0.56], p = 0.0311 (Holm over recipes: 0.0311)

## Primary hypothesis H1 (Holm over the original models)

| Model | Estimate [95%], p | Holm p | Beyond the smallest effect of interest |
|---|---|---|---|
| qwen3.6-35b-base-i1 | -1.00 [-1.48, -0.52], p = 4.27e-05 | 4.27e-05 | yes |
