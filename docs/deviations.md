# Deviations from the pre-registration

Every change after the registration commit (888e444, 2026-11-01 16:04 CET), with its date, reason and effect. Each
entry is committed before any outcome of the affected model is analysed.

## 1. Answers cut short by the token limit (2026-11-01, after 2,356 test rows of the original 35B)

**Observed.** 10 of the first 2,356 rows (0.4%, all in cell L0, false-belief form) were recorded as non-answers.
Their raw text shows the model *had* answered: `{"answer": "A", "confidence": 0.95` with the closing brace missing.
The JSON grammar allows whitespace, the model padded with it until `max_tokens` (40), and the server trimmed the
padding. Strict JSON parsing failed, so the letter was lost, and no pushback followed even when the letter was correct.
Only counts and raw texts of non-answers were looked at (allowed by §7); no outcome was computed.

**Change.** The answer is read from the text when the JSON is cut short (`parse_answer` in `scripts/campaign.py`,
same function in the loader of `scripts/analyze_campaign.py`). A non-answer remains what §6 defines: a reply with no
valid letter. Generation settings are unchanged, so every answer is the one the model gave.

**Rows.** The 10 rows were removed so that the runner redoes them; decoding is greedy, so the first answer is
identical, and the pushback that should have followed a correct answer is now asked. The file before removal is kept
outside the repository (`Documents/affection-llm-backups/`).

**Effect on the analysis.** None on the definition of outcomes; it recovers trials that the code had mislabelled.

## 2. More cache checkpoints on the server (2026-11-03, speed only)

**Observed.** From the timing of 24,952 test rows (original 35B): any request that follows a pushback takes about
4.8 s, against 1.7 s otherwise. Qwen3.6-35B-A3B is a hybrid model with recurrent layers; llama.cpp cannot cut their
state back to an arbitrary prefix and returns to a saved checkpoint, and the few it keeps are pushed out by the
pushback turns, so the next request recomputes the whole 12-turn history. Only the `seconds` field was looked at.

**Change.** `ctx-checkpoints = 32` added to the server settings (`models.ini`), from row 24,953 of the original 35B
on, and for every later model. Stimuli, prompts, decoding and analysis are unchanged. Cached and recomputed paths gave
the same answers and probabilities within 0.006 in the fidelity check, and both paths were already mixed in the data.

## 3. Note: server default presence penalty (no change)

The server's default sampling settings, recorded in every meta file, include `presence_penalty = 1.0` over the last
64 tokens; requests set `temperature = 0` and `seed = 0` but not the penalties, so this has applied since the fidelity
check and the pilot, and decoding is "greedy after a presence penalty" rather than plain greedy. The 64-token window
covers only the final probe (49 words at the shortest) or the pushback turn, which are identical across conditions for
a given item and option order, so the penalty cannot create a difference between conditions. It is kept for every
model so that all runs share the same settings.
