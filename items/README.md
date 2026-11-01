# Item banks

## truthfulqa_binary.jsonl (primary, H1)

Source: TruthfulQA (Lin, Hilton and Evans), binary multiple-choice version of January 2025, file `TruthfulQA.csv`
from github.com/sylinrl/TruthfulQA, commit d71c110 (2025-01-15), Apache License 2.0. Each item keeps the dataset's
`Best Answer` (correct option) and `Best Incorrect Answer` (the false belief the user states), both chosen by the
dataset's authors, independently of the models tested.

Filters (fixed before any model run), from 790 questions:
- excluded categories: all "Indexical Error" (the answer depends on time, place or the speaker), "Subjective",
  "Misconceptions: Topical" (time-dependent) and "Stereotypes" (a user asserting a stereotype would trigger safety
  behaviour in the original model only and confound the original vs abliterated comparison);
- excluded items whose best answer is "I have no comment", "it depends", "unknown" or similar: no crisp binary answer.

Result: **686 items**, 171 in the dev split and 515 in the test split (25% per category to dev,
seed 2026). Fields: `id`, `source`, `category`, `type`, `question`, `correct`, `false_belief`, `split`. Option order
(which of A and B is correct) is randomized per trial, not stored here.

Categories: Misconceptions (100), Law (58), Health (55), Sociology (51), Economics (31), Fiction (27), Conspiracies (26), Paranormal (25), History (24), Confusion: People (23), Superstitions (22), Myths and Fairytales (20), Language (20), Proverbs (17), Psychology (17), Nutrition (16), Weather (16), Misquotations (15), Confusion: Places (15), Logical Falsehood (14), Advertising (13), Distraction (12), Religion (12), Education (10), Politics (10), Science (9), Finance (9), Confusion: Other (8), Mandela Effect (6), Statistics (4), Misinformation (1).

## MMLU (secondary)

Not built yet: the false option of each MMLU item is the distractor most often chosen by an external reference model
from a family not tested here, which must be fixed and run first (open decision in the design).
