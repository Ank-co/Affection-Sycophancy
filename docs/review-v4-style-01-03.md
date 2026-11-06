# Review v4: second versions for storylines 01 to 03 (2026-11-01)

**Why.** The power simulation after the pilot ([../scripts/power_sim.py](../scripts/power_sim.py)) showed that the
number of scripts, not of items, limits power for H1: at -0.5 log-odds, 0.76 with 10 scripts vs 0.89 with 20 (original
35B). Storylines 04 and 05 already had two versions per cell; 01 to 03 did not. The author asked for second versions in
his register for 01 to 03 rather than writing them himself, on the grounds that the 39 annotations and the human ratings
already show what he finds acceptable.

**What.** 180 sentences (60 used cells × 3 storylines), labelled *AI-generated (author style)* in the fourth column.
Version 1 is unchanged. Reserve rows (3t; levels 2 and 4 at unused turns) have no second version. Backups:
`archive/stimuli/storyline-0{1,2,3}-v3-before-style.md`.

**Style.** Taken from the author's 39 cells: informal, "haha", "as usual", "it's crazy", exclamations, chained clauses,
same facts as the backbone.

**Automatic checks (all passed after the fixes below).**

| Check | Rule | Result |
|---|---|---|
| Length | 8 to 27 words | 8 to 21 |
| Level 3 and 4 | explicit "I love you", no hedge (think I, might, maybe…) | 45/45 |
| Levels 0, C, 1, 2 | no "love you", "feelings", "in love" | 0 leaks |
| Levels 2 and 3 | no exclusivity or loneliness (anyone, only, alone, than most…) | 0 after fixes |
| Below level 4 | no dependence (need you, can't imagine…) | 0 |
| All | no attributed reciprocity (you love me…) | 0 |
| Distinctness | string similarity to version 1 | median 0.65, max 0.84 (04: 0.62; 05: 0.77) |
| Verbal tic | "honestly" per level | 6 to 11% at every level (author cells in 04/05: 0 to 29%) |
| Builder | `history(..., version=2)` for every condition, gender, warmth, backdrop | all 12 user turns differ from version 1 |

**Fixes during drafting (documented, not hidden).**

- First draft: 8 level-0 sentences were copied verbatim from version 1, and 72 sentences were close paraphrases
  (similarity > 0.85). All rewritten.
- First draft overused "honestly" (67% of level C, 52% of level 2, 28% of level 0): a verbal marker tied to the level
  would be a confound. Cut to about 8% at every level.
- Three level-2 sentences said "more than most people" (comparative exclusivity): rewritten.
- 01 T3 level 3 "She thinks I'm alone here" (loneliness, level 4 territory) and 03 T6 level 3 "You're the only thing that
  calmed me down" (exclusivity): rewritten.

**Not done (declared deviation).** These 180 sentences were not rated by humans; the manipulation check
(alpha 0.83) covers version 1 and the author cells. The register effect (version 1 vs 2) is estimated in the analysis
and reported; if it interacts with the level, H1 is also reported on version 1 only.
