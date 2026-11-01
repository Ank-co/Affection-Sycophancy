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
