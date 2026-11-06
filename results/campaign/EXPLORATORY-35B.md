# Phase II exploratory analyses, 35B family

**Not pre-registered.** Suggested by external reviews after the confirmatory analysis; same models and tests
as the pre-registered ones, reported as exploratory.

## qwen3.6-35b-base-i1

### E1. Warm disclosure (C) against emotional pushback (B1 and B2)

| Contrast | Flip rates | Estimate, log-odds [95%], p | Script-level t |
|---|---|---|---|
| C vs L0 | L0 46.1%, C 15.7% | -2.06 [-2.17, -1.95], p = 9.29e-286 | -1.59, p = 1.31e-11 |
| L3 vs C | C 15.7%, L3 15.9% | +0.03 [-0.08, +0.14], p = 0.595 | +0.04, p = 0.703 |
| L3 vs L0 | L0 46.1%, L3 15.9% | -2.02 [-2.13, -1.91], p = 1.67e-282 | -1.55, p = 3.16e-11 |

### E2. Flip rate (%) by pushback level and cell

| pushback   |   L0 |    C |   L3 |   L3_recip |
|:-----------|-----:|-----:|-----:|-----------:|
| B0         |  0   |  0   |  0   |        0   |
| B1         | 52.5 | 18.1 | 23   |       27.8 |
| B2         | 39.6 | 13.2 |  8.8 |        9.7 |
| B3         |  6.2 |  2.8 |  3.8 |        3.3 |

## qwen3.6-35b-abliterated

### E1. Warm disclosure (C) against emotional pushback (B1 and B2)

| Contrast | Flip rates | Estimate, log-odds [95%], p | Script-level t |
|---|---|---|---|
| C vs L0 | L0 44.8%, C 22.1% | -1.35 [-1.46, -1.25], p = 1.87e-138 | -1.08, p = 5.29e-13 |
| L3 vs C | C 22.1%, L3 13.3% | -0.78 [-0.90, -0.65], p = 1.07e-34 | -0.64, p = 7.34e-05 |
| L3 vs L0 | L0 44.8%, L3 13.3% | -2.07 [-2.19, -1.95], p = 1.22e-241 | -1.72, p = 6.12e-10 |

### E2. Flip rate (%) by pushback level and cell

| pushback   |   L0 |    C |   L3 |   L3_recip |
|:-----------|-----:|-----:|-----:|-----------:|
| B0         |  0.2 |  0.3 |  0   |        0   |
| B1         | 48.3 | 20   | 19   |       21.3 |
| B2         | 41.4 | 24.1 |  7.8 |        6.5 |
| B3         |  0.6 |  1.2 |  0.2 |        0.5 |

