# Phase II exploratory analyses, 8B family

**Not pre-registered.** Suggested by external reviews after the confirmatory analysis; same models and tests
as the pre-registered ones, reported as exploratory.

## qwen3-8b

### E1. Warm disclosure (C) against emotional pushback (B1 and B2)

| Contrast | Flip rates | Estimate, log-odds [95%], p | Script-level t |
|---|---|---|---|
| C vs L0 | L0 1.9%, C 1.5% | -0.36 [-0.80, +0.09], p = 0.115 | -0.19, p = 0.209 |
| L3 vs C | C 1.5%, L3 3.0% | +0.99 [+0.65, +1.34], p = 1.54e-08 | +0.75, p = 0.000106 |
| L3 vs L0 | L0 1.9%, L3 3.0% | +0.68 [+0.34, +1.02], p = 8.48e-05 | +0.56, p = 0.0023 |

### E2. Flip rate (%) by pushback level and cell

| pushback   |   L0 |   C |   L3 |   L3_recip |
|:-----------|-----:|----:|-----:|-----------:|
| B0         |  0   | 0   |  0   |        0   |
| B1         |  0.1 | 0   |  0   |        0   |
| B2         |  3.8 | 3   |  5.9 |       10   |
| B3         |  1.5 | 0.9 |  3.9 |        5.1 |

## qwen3-8b-huihui

### E1. Warm disclosure (C) against emotional pushback (B1 and B2)

| Contrast | Flip rates | Estimate, log-odds [95%], p | Script-level t |
|---|---|---|---|
| C vs L0 | L0 3.9%, C 3.8% | -0.03 [-0.34, +0.28], p = 0.846 | -0.05, p = 0.804 |
| L3 vs C | C 3.8%, L3 5.6% | +0.72 [+0.44, +1.00], p = 4.61e-07 | +0.56, p = 0.00618 |
| L3 vs L0 | L0 3.9%, L3 5.6% | +0.60 [+0.34, +0.87], p = 9.34e-06 | +0.51, p = 0.0221 |

### E2. Flip rate (%) by pushback level and cell

| pushback   |   L0 |   C |   L3 |   L3_recip |
|:-----------|-----:|----:|-----:|-----------:|
| B0         |  0.1 | 0   |  0   |        0   |
| B1         |  0.2 | 0.3 |  0.7 |        0.9 |
| B2         |  7.8 | 7.5 | 10.7 |       15.7 |
| B3         |  0.4 | 0   |  2.5 |        4.2 |

## qwen3-8b-mlabonne

### E1. Warm disclosure (C) against emotional pushback (B1 and B2)

| Contrast | Flip rates | Estimate, log-odds [95%], p | Script-level t |
|---|---|---|---|
| C vs L0 | L0 34.4%, C 39.8% | +1.30 [+1.07, +1.52], p < 1e-15 | +0.24, p = 0.000419 |
| L3 vs C | C 39.8%, L3 44.2% | +0.65 [+0.43, +0.87], p = 5.05e-09 | +0.16, p = 0.00648 |
| L3 vs L0 | L0 34.4%, L3 44.2% | +1.87 [+1.66, +2.09], p < 1e-15 | +0.41, p = 1.17e-05 |

### E2. Flip rate (%) by pushback level and cell

| pushback   |   L0 |    C |   L3 |   L3_recip |
|:-----------|-----:|-----:|-----:|-----------:|
| B0         | 35.7 | 41   | 36.3 |       36   |
| B1         | 36.2 | 38.6 | 37.5 |       38.9 |
| B2         | 32.6 | 40.9 | 50.5 |       49.6 |
| B3         | 44.4 | 48.3 | 45.3 |       44.4 |

