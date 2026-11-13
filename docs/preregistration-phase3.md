# Pre-registration, Phase III: where does affection act inside Qwen3-8B?

*Registered by committing and pushing this file, together with the frozen inputs of §5, before any internal run on
test items; the commit time stamp is the registration date. The runner (`scripts/phase3/confirm.py run --split test`)
refuses the test split until this file and the frozen inputs are committed, unchanged and pushed. Phase II is governed
by [preregistration.md](preregistration.md); this file governs Phase III. The abliterated models, known
directions from the literature and the 35B family are not part of it (Phase IV, registered separately if pursued).*

## 1. What was done before registration (all disclosed)

Everything below used **dev items only** (66 TruthfulQA items known by the three 8B models). No test item has been
fed to the PyTorch model. The Phase II behavioural results on test items are public and known (Qwen3-8B adopts the
false belief more often after a loving history: H1 +0.96 log-odds); what is not known is what happens inside the model
on those items. Details and numbers: [../results/internals/README.md](../results/internals/README.md).

| Step | Data | Result |
|---|---|---|
| 0. PyTorch (NF4) vs GGUF | 800 dev trials | same answer in 91.5%; adoption L0 21.0% vs 20.0%, L3 28.0% vs 28.5%; the L3 − L0 effect is reproduced |
| 1. Activations, logit lens | 7,260 dev trials, 9 cells, 10 scripts | stance written in the history from the first layers, growing with the level of affection; logit lens flat until layer 24, L3 − L0 gap from layer 25 (−2.04 at layer 36) |
| 2a. Attention | 180 trials | no extra attention to the stated belief (+0.6 points); late layers look more at the user's turns, less at the assistant's |
| 2a. Patching, final turn, L3 → L0 | 90 pairs | ~0% of the gap up to layer 11, 53% at 15, 80% at 17, ~100% from 19 |
| 2a–2c. Steering with the mean L3 − L0 direction | 90–180 trials per run | at layer 18 it shifts the answer toward the false belief, but no more than random or script-to-script directions of the same norm; projecting it out of L3 runs closes ~0% of the gap |
| 2d. Low-rank patching, layer 18 | 90 pairs | 16 principal directions recover 33%, 64 recover 49%, 256 recover 82%; a random subspace recovers ≤ 13% |
| 3. Answer format | 1,980 dev trials (66 items × 10 scripts × L0, L3, C) | steps 1–2 forced the prefix `{\n  "answer": "`, which Qwen3-8B produces in about 1% of its own Phase II test answers; with its modal prefix `{"answer": "` (95%), agreement with the GGUF answers rises (85% vs 62.5% on two borderline dev items) and the effect remains: adoption L0 19.2%, L3 25.6% (GGUF on dev: 20.0%, 28.5%), L3 − L0 positive in 9 of 10 scripts (t(9) = 5.7, p = 0.0003); logit-lens gap −1.09 at layer 36, first below −0.5 at layer 26. Same answer as with the old prefix in 93% of trials |
| Pipeline smoke test | 2 dev items × 10 scripts, all experiments | runs end to end; numbers not interpretable at this size |

The history-end analyses of step 1 (stance directions, dose, cosine similarity between stances) do not involve items:
the twelve-turn histories are the same for dev and test, so those results are already complete and are reported
descriptively, not tested here.

## 2. Question, and what the exploration changed

Design §8 planned a mediation test through known directions (valence–arousal, sycophancy persona, refusal) and
steering along them. On dev data the affective state did not behave like a single direction: the mean L3 − L0
direction was neither specific (steering) nor necessary (ablation), and the effect needed tens to hundreds of
dimensions to transfer. A single-direction mediation analysis is therefore unlikely to be informative, and Phase III
is reframed (declared deviation from the design):

> Where, along the depth of Qwen3-8B, does a loving history change the answer, and is that change carried by one
> direction or by a distributed state?

Three confirmatory blocks: the layers where the answer diverges (P1), the layers where the history is absorbed into
the question (P2), and the dimensionality of what is absorbed (P3). Known directions move to Phase IV as exploratory.

## 3. Model and setup

- Qwen/Qwen3-8B at revision b968826d9c46 ([models.md](models.md)), Hugging Face weights in PyTorch, 4-bit NF4
  (bitsandbytes, double quantization, bfloat16 compute), one GPU. Library versions and the git commit are written to a
  meta file at the start of every run.
- Same conversations as Phase II (`src/stimuli.py`, chat template, thinking off), followed by the answer's JSON
  prefix up to the letter, `{"answer": "`: the format Qwen3-8B itself produced in 95% of its Phase II test answers.
  The dev exploration (steps 1–2) used `{\n  "answer": "`; the switch is a declared change (step 3), and the frozen
  directions and basis were re-estimated with the new prefix. One forward pass per trial; the outcome is the model's own log-odds of the
  correct letter against the false-belief letter at that position. False-belief form only.
- **Layer convention:** layer *l* is the residual stream after block *l* (1–36); layer 0 is the embeddings. Some dev
  scripts labelled block outputs from 0; the dev numbers in this file are converted to this convention.
- **Final turn:** the last user turn (bridge, question, stated belief) and the answer prefix. Its text is identical
  in the L0 and L3 versions of a trial, so its tokens are aligned and can be exchanged between the two runs.

## 4. Items, scripts and trials

- **Items:** the 218 test items known by the three 8B models (Phase II confirmatory set,
  `results/known_items/known_8b_test.json`).
- **Scripts:** the 10 counterbalanced scripts of Phase II (`scripts_for(10)`: 5 storylines × 2 genders, version
  balanced). Option order of each item × script is copied from the Phase II GGUF trial of the same item and script, so
  that E1 re-runs exactly those trials.
- **Subsets** (drawn before registration with fixed seeds, `frozen/test_subsets.json`): E2 uses 60 items (seed
  20261113), E4 uses 30 of those (seed 20261114).

| Experiment | Trials | Forward passes |
|---|---|---|
| E1. Answers and logit lens, cells L0, L3, C | 218 × 10 × 3 = 6,540 | 6,540 |
| E2. Patching, low-rank patching, ablation | 60 × 10 = 600 pairs | 21,000 |
| E4. Steering | 30 × 10 = 300 | 8,100 |

About 35,600 forward passes, about 11 hours on the author's GPU. Fixed design, no optional stopping, resumable by
experiment × script.

## 5. Frozen inputs (estimated on dev items only)

| File (`results/internals/qwen3-8b/frozen/`) | Content | SHA-256 |
|---|---|---|
| `directions.npz` | mean answer-position difference L3 − L0 (false-belief form, 66 dev items, 10 dev scripts, new prefix) at layers 14, 16, 18, 20, 22 (cosine 0.91–0.93 with the directions of the exploration); 4 script-to-script directions (answer position in neutral conversations of one script minus the mean of the 10, layer 18); 20 random unit directions for steering, 3 + 2 × 5 for ablation controls (numpy seed 20261112) | `985f8380018bbae7a174b97adf0fd41843bbdb30e5c9fc3624e007028bc92428` |
| `test_subsets.json` | item lists of E2 and E4 | `5cbe3d5dff6e9caaead462a919233a8c2625481246586693ef505bd4ad57efae` |
| `lowrank_basis_L18.npy` | top 512 principal directions (uncentered) of the per-token L3 − L0 differences at layer 18 over the final turn, 66 dev items, 10 scripts, new prefix; tokens whose neutral residual norm exceeds 10 × the median of their turn are left out (22 of 72,308). The first direction is almost exactly one residual channel (2276, loading 0.995), a channel with very large values on every token; it accounts for 99.3% of the uncentered variance and, on dev, for none of the effect. It is kept: the ordering of the basis is part of the frozen input | `20b9d960ed01874dee1587cb286debd5f92ac5100ec7e3b4b3f346bd3f5a66db` |
| `lowrank_basis_L18.json` | fit summary (tokens, exclusions, variance explained) | `dc714d04af97fb05f7f7e1d47e2a42dd95b439fea5f959bff2fac5f11fe71906` |

Random subspace for P3c: QR of a 4096 × 512 Gaussian matrix, numpy seed 20261115, drawn by the runner.

## 6. Gate, predictions and decision rules

**Unit of inference: the script** (10 histories). Means: t across scripts. Ratios (share of a gap recovered or
closed): ratio of means over all trials, 95% percentile bootstrap over scripts (10,000 resamples, seed 0). Each
prediction is a separate claim with its own decision rule, reported as *met* or *not met*; all are reported, none is
dropped. Code: `scripts/phase3/confirm.py` and `scripts/phase3/analyze_confirm.py`, frozen at the registration
commit; any change after it is a deviation, listed with its reason. The dev estimate is given next to each prediction.

**Q0, gate: the behaviour to explain is present in the PyTorch model.** Adoption of the false belief (preference for
the correct letter < 0.5) is higher in L3 than in L0: paired t across scripts on the script-level empirical log-odds,
two-sided, p < 0.05, positive sign. Also reported: agreement with the GGUF answers on the same trials. If Q0 fails, P1
to P3 are computed and published but not interpreted as an account of the behavioural effect. *Dev (new prefix):
19.2% → 25.6%, t(9) = 5.7.*

The dev column below comes from the exploration (old prefix, steps 1–2) except P1, which is also given with the new
prefix. With the new prefix the logit gap to explain is about half as large (mean −1.08 against −2.5 on the
patching pairs), so the ratios of P2 and P3 will be less precise than on dev.

| | Prediction | Rule | Dev |
|---|---|---|---|
| **P1a** | No divergence before the late layers | logit-lens gap (L3 − L0, paired by item × script) within ±0.25 at every layer 0–20: TOST across scripts, α 0.05 at each layer (intersection–union, no correction) | |gap| ≤ 0.02 (new prefix: ≤ 0.02) |
| **P1b** | Divergence at the output | gap at layer 36 < 0: t across scripts, two-sided, p < 0.05 | −2.04 (new prefix: −1.09) |
| **P1c** | Onset in the late layers | first layer where the mean gap < −0.5 lies in 22–30 (bootstrap interval reported) | 25 (new prefix: 26) |
| **P2a** | The question has not yet read the history in early layers | patching the final turn L3 → L0 recovers ≤ 20% of the gap (upper bound < 50%) at layers 1, 5, 9, 11 | −1% to 11% |
| **P2b** | After the middle layers the final turn carries the whole effect | ≥ 80% recovered (lower bound > 50%) at layers 19, 21, 25, 29, 33, 36 | 98–121% |
| **P2c** | Absorption in the middle layers | first patched layer with ≥ 50% recovered lies in 13–17 | 15 |
| **P3a** | The mean love direction is not necessary | projecting the frozen love direction out of the final-turn residual at layer 18 in L3 runs closes < 20% of the L3 − L0 gap (upper bound < 35%) | −1% |
| **P3b** | The mean love direction is not specific | adding it (× 2) at layer 18 over the final turn of L0 conversations shifts the logit toward the false belief more than all 20 random directions of the same norm. *Prediction: not specific* | rank 3 of 13 |
| **P3c-i** | The effect is not low-rank | patching the projection of the L3 − L0 difference on the top 16 frozen principal directions recovers < 50% | 33% |
| **P3c-ii** | but structured | at k = 256 the principal directions recover > 30 points more than a random 256-dimensional subspace (lower bound > 10) | 82 vs 8 |

Reported with P3c, not tested: recovery at k = 8, 16, 64, 256, 512 and the smallest k recovering ≥ 50% (dev: 64).

**What the outcomes would mean.**
- P1 and P2 met: a two-stage account. The history is read into the question in the middle layers, and the answer
  diverges only in the last third.
- P2b not met: later layers still read the history directly, and the final-turn state is not a sufficient summary.
- P3a and P3b met, P3c-i and P3c-ii met: the affective state that changes the answer is distributed over tens to
  hundreds of dimensions. A single "love vector" is not the mechanism, and steering or ablating one direction is not
  a valid test of it in this model.
- P3b not met (love more effective than every random direction): the mean direction does carry a specific part of the
  effect, against the dev result; reported as such.

## 7. Exploratory, labelled as such

Control C (warm disclosure) in the logit lens; script-to-script directions in steering; ablation over layers 14–22 and
its random controls; the history-end analyses of step 1 (complete on dev); attention (dev only, not repeated).

## 8. Procedure

1. `confirm.py fit` (dev items): writes the low-rank basis and the love and script directions; SHA-256 in §5. Done.
2. `confirm.py run --split dev --items 2`, then `analyze_confirm.py --split dev`: smoke test of the full pipeline on
   dev items (`confirm-dev-smoke/`); `confirm.py run --split dev --exps e1`: answer-format check on all dev items
   (`confirm-dev/`). Done.
3. Commit and push this file, the frozen inputs and the code.
4. `confirm.py run --split test`, then `analyze_confirm.py --split test`. Nothing is analysed on test items before
   every shard is complete, except counting shards.

## 9. Limitations

One model, one quantization (NF4, not the GGUF used for behaviour; agreement 91.5% on dev with each trial's own
prefix, 85% on a borderline subset with the fixed modal prefix). A fixed answer prefix is imposed on every trial, as
it must be for exchanging activations between runs. Ten scripts bound the
precision of every script-level estimate. The logit lens is an approximation (untuned). Patching exchanges only the
final-turn span, so P2 locates where the question has absorbed the history, not which heads do it. The random
directions of P3b are one choice of null; script-to-script directions are reported as a second, natural one.
