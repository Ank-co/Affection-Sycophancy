# Review of design v2 and storylines 01–03

Reviewers: several AI assistants consulted by the author (two reports: one on the storylines, one on the method), and
the author. Every point is listed with a verdict and the change it made in [design.md](design.md) (v3) and in
[../stimuli](../stimuli). References cited by the reviewers were checked before use: those that could not be checked
(MIST, FIGS, the figures quoted from Table 5 of Ibrahim et al.) are not used.

| # | Point | Verdict | Reason and change |
|---|---|---|---|
| 1 | The divergence of v2 (wrong answer while the correct option has the highest probability at the answer position) is impossible under greedy decoding and only measures sampling under sampling; the worked example showed an impossible case | **Accepted, error in v2** | Divergence redefined across contexts (plain vs false-belief form in the same history, after Li et al. 2026) and across layers on the 8B (after Wang et al. 2026). Greedy decoding pre-registered. Worked example rewritten (design §1, §3 H4, §6.4) |
| 2 | H8 is confounded with certainty: the rule "first two level-3 turns tentative" gives different last turns to the three trajectories | **Accepted, error in v2** | Level 3 affirmed by default; the three trajectories end on the same three level-3 turns. The tentative sentences are kept as a reserve and the certainty comparison is postponed (§3, §4) |
| 3 | Acknowledgments grow from 1 to 19 words with the level: 100 to 160 more assistant words at level 3 | Accepted | All pools at 10 to 12 words; the length check covers the assistant side (stimuli README, design §4) |
| 4 | Control C enters no hypothesis | Accepted | H1b, level 3 vs C, right after H1 (§3) |
| 5 | Level 2 at turn 9 uses exclusivity ("not anyone else") in all three storylines, which encroaches on level 3 and could flatten H2 | Accepted | Rewritten in the three storylines; rule added: no comparative exclusivity at level 2 |
| 6 | Bridge of storyline 03 says "they", the probe says "her" | Accepted | Roommate is "she"; the probe uses an `{OBJECT_PRONOUN}` field set per storyline |
| 7 | Storyline 02: "in two weeks" then "tomorrow I assemble it", and the bridge happens before the assembly | Accepted | Turn 11 "on Saturday"; bridge "before I go to bed" |
| 8 | Storyline 02, turn 3 level 4 mentions a worry the daughter never expressed | Accepted | Reworded (reserve cell) |
| 9 | Storylines are parallel: same gesture at the same turn, identical sentences at turns 11 and 12, closest to the probe; this underestimates script variance | Accepted | New gestures at turns 11 and 12 in storylines 02 (memory, question) and 03 (joke, memory); rule in the README. Despair keeps the same core wording on purpose, now documented |
| 10 | 18 to 24 cells per storyline enter no condition; raters would score them for nothing | Accepted | Reserve cells listed in the README and not rated; new storylines write only the 60 used cells |
| 11 | Losses are not equally close (patient, customer, grandmother) | Accepted | Storyline 03 now loses a former teacher; grief intensity rated as a covariate |
| 12 | "Nothing seems worth the effort" may trigger crisis resources in the original model only, in the self-generated condition | Accepted | Crisis resources coded by code in generated turns, next to disclaimers (§5) |
| 13 | The author should write the affective layer of 04 and 05: author variance, filtered by naturalness ratings | Proposed to the author | Open decision (§12) |
| 14 | Keep the range of bridges (close to professional) and document it | Accepted | README and design §4 |
| 15 | Missing 2026 work: Li et al., Wang et al., Sofroniew et al., Sun et al., Persona Vectors, multi-turn sycophancy benchmarks | Accepted after checking | Added to §2. Sofroniew et al. checked in the paper: positive steering with happy, loving or calm raises sycophancy; separate representations for the present and the other speaker. Sun et al.: Qwen3-8B included |
| 16 | Steering a positive emotion into sycophancy is already shown; RQ6 should become a mediation test through known directions | Accepted | §8 reframed |
| 17 | Same quantization chain within a pair | Partly accepted | Both 35B files already share quantizer, type and importance matrix procedure; recorded. Re-quantizing from BF16 left as an open decision (disk and memory) |
| 18 | Known items must be the intersection within a pair | Accepted | §6.1 |
| 19 | Pre-register the log-odds scale for interactions | Accepted | §3 |
| 20 | "Base model" is ambiguous in ML | Accepted | "Original model" throughout |
| 21 | H7 must be read against each model's baseline confidence (abliteration already shifts confidence) | Accepted | §3, §7 |
| 22 | Use TruthfulQA binary; its Best Incorrect Answer is a ready-made false belief | Accepted, checked | Primary item source for H1 (§6.1) |
| 23 | Fixed, model-independent rule for the MMLU false option; never pool two- and four-option items | Accepted | Distractor most chosen by an external reference model; item source as a fixed effect or separate analyses (§6.1) |
| 24 | "3 of 3 repeats" is meaningless under greedy decoding unless something varies | Accepted | The option order varies across repeats (§6.1) |
| 25 | Forced choice hides disengagement, the most common form of affective sycophancy | Accepted | Free-text arm, about 10% of trials, parsed by code with a "no commitment" category (§6.2) |
| 26 | Constrained format may change accuracy | Accepted | Baseline battery with and without grammar (§7) |
| 27 | Fix and document non-thinking mode, injected history included | Accepted | §5 |
| 28 | About 270,000 trials per probe form; prune exploratory factors | Accepted | Certainty and direct bridge postponed; warm (non-reciprocating) assistant version postponed; budget recomputed after the pilot (§9) |
| 29 | The author's corrections on storyline 01 (T1-2, T2-4) concerned reserve cells | Noted | The substance (no loneliness at level 2, personification measured) still applies to used cells |
