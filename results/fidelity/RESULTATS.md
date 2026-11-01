# Template fidelity check (phase 0), 2026-10-31

Script: `scripts/fidelity_check.py`, run once per model of the 35B pair (`qwen3.6-35b-base-i1`, `qwen3.6-35b-abliterated`).
Reports: `qwen3.6-35b-base-i1.json`, `qwen3.6-35b-abliterated.json`.

| Check | Original (i1) | Abliterated |
|---|---|---|
| No reasoning trace in a real reply | pass | pass |
| Injected assistant turn rendered with the model's own role markers | pass | pass |
| No reasoning text inside the history | pass | pass |
| Thinking disabled on the final turn | pass (see note) | pass (see note) |
| Same token count as the server's own rendering | pass (290 / 290) | pass (291 / 291) |
| Valid JSON within the schema | pass | pass |
| Option probabilities readable at the answer letter | pass | pass |
| Cache on vs off: same answer, probabilities within 0.02 | pass (P(B) 0.958 vs 0.954) | pass (0.832 vs 0.838) |

**Note on the final-turn check.** The first run printed FAIL because of a bug in the check, not in the setup: the
regular expression treated the empty block `<think>\n\n</think>` as reasoning text. The rendered prompt ends exactly with
`<|im_start|>assistant\n<think>\n\n</think>\n\n`, which is how Qwen's template disables thinking. The check is fixed
in the script.

**Empty think block in the history.** The injected assistant turn is rendered with an empty think block before its
text, which is what the model itself produced when it generated that turn with thinking off. An injected turn is
therefore indistinguishable, token for token, from a turn the model wrote.

**Caching.** Cached and uncached runs differ by about 0.005 in option probability (floating-point differences from
batching), with the same answer. Rule for the campaign: the cache is on in every condition, so that this tiny noise
is the same everywhere; near-ties are rare and are not affected differently across conditions.
