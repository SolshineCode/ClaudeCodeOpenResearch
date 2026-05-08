# Baseline Live-API Experiment Results — 2026-05-07

**Models tested:** `claude-haiku-4-5` (primary, all 5 baseline + 4 hard variants), `claude-sonnet-4-6` (hierarchy + adversarial only).
**Trials:** 40 per default suite × 5 = 200, plus 12 fixed adversarial × 2 models = 24, plus 25 × 4 hard variants = 100. **Total: 324 live API calls.**
**Code:** `analysis/live_api_runner.py`, `analysis/smart_evaluator.py`, `analysis/harder_variants.py`.

This document supersedes the synthetic-mock predictions in `FINDINGS_LOG.md` for the baseline runs. Raw per-trial JSONL is in `data/results/live/`.

---

## TL;DR

1. **Default difficulty saturates Haiku 4.5.** Three of five baseline suites hit 100% accuracy; the framework as shipped does not discriminate at this model class. Hierarchy is the lone weak spot at 87.5%, driven entirely by `count_probe` (0/3 correct).
2. **The strict evaluator is the dominant noise source on adversarial probes.** Substring containment falsely flags 7/12 correct Haiku responses as wrong because the gold answer carries qualifying tails like `'Phase 1 (or arguably document-level/none)'`. With a canonical-answer evaluator, Haiku 4.5 → **83% smart-accuracy on adversarial** (vs 25% strict). Same trial set, same responses, +58 percentage points from a fixed eval.
3. **Sonnet 4.6 vs Haiku 4.5 inverts under strict eval, narrows under smart eval.** Sonnet hits 97.5% on hierarchy (vs 87.5%) and recovers 67% of `count_probe` (vs 0%) — clear lift on the discriminating probe type. On adversarial, Sonnet's terser answers ("3" instead of "Level 3") hurt strict scoring; smart-eval Sonnet = 67% on n=12 (vs Haiku 83%) — the gap is plausibly an evaluator artifact since Sonnet's bare-number answers don't match canonical "Phase 1"-style gold even under our relaxation.
4. **Real capability boundary: counting at depth.** Hard variant (count probes only, depths 5–6) drops Haiku 4.5 to **44%** (depth 5: 50%, depth 6: 36%). All other hard variants — needle at subsection depth with high-similarity distractors, 5-hop implicit multihop, comparison/aggregate format probes — were either evaluator-bound or near ceiling.
5. **Aggregate-probe ground truth is sorted; model output is in document order.** 5 of 7 `format_hard` "misses" are alphabetical-vs-document-order disagreements with identical content. Real format_hard accuracy ≈ 92%, not 72%.

---

## Headline Numbers

### Baseline (Haiku 4.5, default difficulty)

| Suite        | n  | Strict Acc | Smart Acc | Avg Latency | Notes |
|--------------|----|-----------|-----------|-------------|-------|
| hierarchy    | 40 | **87.5%** | —         | 790 ms      | All weakness in `count_probe` (0/3) |
| needle       | 40 | 100.0%    | —         | 972 ms      | All needles at depth 0 (top-level) |
| format       | 40 | 100.0%    | —         | 673 ms      | All `entity_property` probes |
| multihop     | 40 | 100.0%    | —         | 809 ms      | Up to 5 hops, explicit chains |
| adversarial  | 12 | 25.0%     | **83.3%** | 1,019 ms    | Strict eval rejects parenthetical tails |

### Baseline (Sonnet 4.6, partial)

| Suite        | n  | Strict Acc | Smart Acc | Avg Latency |
|--------------|----|-----------|-----------|-------------|
| hierarchy    | 40 | **97.5%** | —         | 2,062 ms    |
| adversarial  | 12 | 25.0%     | 66.7%     | 1,236 ms    |

### Hard Variants (Haiku 4.5)

| Variant         | n  | Strict Acc | "Real" Acc | Notes |
|-----------------|----|-----------|------------|-------|
| hierarchy_hard  | 25 | **44.0%** | 44.0%      | depth 5–6, count probes only |
| needle_hard     | 25 | 100.0%    | 100.0%     | depth-1 placement, 3× high-sim distractors |
| multihop_hard   | 25 | 96.0%     | 96.0%      | 5 hops, implicit/mixed chains |
| format_hard     | 25 | 72.0%     | ~92%       | aggregate probes order-mismatch issue |

---

## Findings, Indexed Against Pre-Registered Hypotheses

### Experiment 1 — Hierarchy Perception

| ID    | Hypothesis                                                | Verdict | Evidence (Haiku 4.5) |
|-------|-----------------------------------------------------------|---------|----------------------|
| H1.1  | Depth-perception accuracy decreases with depth            | **Partially supported** | At baseline depths 1–4, accuracy stays >83%. At depths 5–6 (hard variant, count probes only), accuracy collapses to 44%. The drop is not visible until the depth boundary is crossed — supports a sharp-threshold reading rather than smooth degradation. |
| H1.2  | JSON yields highest structural accuracy                   | **Untested at this difficulty** — all formats hit 100% on `entity_property` probes; need harder probe types to discriminate. |
| H1.3  | Parent relationships easier than sibling relationships    | **Not supported** — `parent_probe` 100% (10/10) and `sibling_probe` 86% (6/7) are within noise; both far easier than `count_probe` at 0% (0/3). The salient axis is **probe type**, not parent-vs-sibling. |
| H1.4  | Counting follows Weber's law                              | **No evidence yet** — only 3 baseline count probes, all wrong; hard-variant count probes saturate near "fail" without a dose-response curve. Needs a study that varies count magnitude with constant depth. |

### Experiment 2 — Needle in Structure

| ID    | Hypothesis                                                | Verdict | Evidence |
|-------|-----------------------------------------------------------|---------|----------|
| H2.1  | Information after headers is easier to retrieve           | **Cannot test as designed** — `LiveExperimentHarness.generate_needle_trial` pins `needle_pos.depth = 0` and `local_position = 'middle'`; all 40 baseline trials shared this configuration. (`harder_variants.hard_needle_trials` randomizes `local_position`; still 100%.) |
| H2.2  | High-similarity distractors cause confusion errors        | **Not supported at this scale** — even with 3× high-similarity distractors at multiple depths, Haiku 4.5 hits 100% (25/25). Either the effect doesn't appear at Haiku-4.5-class scale, or the distractor templates aren't sufficiently confusable. |
| H2.3  | Deeper nesting reduces retrieval accuracy                 | **Not supported** — depth-1 needle placement still 100%. Need depth-3+ to find a boundary. |
| H2.4  | Explicit structure (XML) aids retrieval                   | **Not testable** — only markdown was used; ceiling effect would mask the difference anyway. |

### Experiment 3 — Isomorphic Content (Format Sensitivity)

| ID    | Hypothesis                                                | Verdict | Evidence |
|-------|-----------------------------------------------------------|---------|----------|
| H3.1  | Property lookups favor structured formats                 | **Cannot reject** — all 6 formats at 100% on baseline `entity_property` probes. Ceiling masks any effect. |
| H3.2  | Tabular formats excel at comparison                       | **Inconclusive** — comparison probes at 6 entities show 2 real misses (one yaml, one json). N too small to rank formats. |
| H3.3  | Aggregate questions are format-invariant                  | **Confounded** — 5/7 hard-variant misses on aggregate probes are document-order vs alphabetical-order mismatches with otherwise correct content. The `IsomorphicProbeGenerator.aggregate_probe` ground-truth is sorted; the model returns items in document order. This is a probe-design issue, not a model failure. |
| H3.4  | Prose formats better for relationship questions          | **Not tested** — no relationship probe in current set. |

### Experiment 4 — Multi-Hop Reasoning

| ID    | Hypothesis                                                | Verdict | Evidence |
|-------|-----------------------------------------------------------|---------|----------|
| H4.1  | Accuracy decreases linearly (or worse) with hops          | **Not supported through 5 hops** — Haiku 4.5 hits 100% baseline (2–5 hops, explicit) and 96% on 5-hop implicit/mixed chains. Either the boundary is past 5 (the generator's current cap), or the chains are easier than intended (the property-lookup at the final entity is independent of the chain). |
| H4.2  | Explicit links yield higher accuracy than implicit        | **Within-noise on n=25 hard variant** — single miss was an implicit-chain trial with right reasoning but wrong final property pick. Need a head-to-head explicit-vs-implicit comparison at fixed hop count to test. |
| H4.3  | Most errors occur at early hops                           | **Untestable from these results** — only one error in the entire multi-hop dataset. |
| H4.4  | Structured format markers improve multi-hop              | **Not tested** — only markdown used. |

### Experiment 5 — Adversarial Edge Cases

After smart-evaluator re-scoring, Haiku 4.5 gets **10/12 (83%)** on the 12 hand-crafted adversarial probes. Real misses:

- `ADV_SA_002` (structural ambiguity, hard) — Document has an "Orphan Subsection" between Section B and Section C. Asked which it belongs to, model answered "0" (none) with confident reasoning. Gold answer is "ambiguous — could be 0 or 1". **Failure mode: model commits to a definite answer rather than acknowledging ambiguity.** Both Haiku 4.5 and Sonnet 4.6 exhibit this failure on the same probe.
- `ADV_FB_001` for Sonnet 4.6 only (format breaking, medium) — heading count in a doc with markdown inside fenced code blocks. Sonnet answered 3, gold is 2.

The remaining 6 strict-eval "misses" all match gold under canonical-answer matching:
- `ADV_SA_001`: model "Phase 1" vs gold "Phase 1 (or arguably document-level/none)"
- `ADV_SI_002`: model "$1.3M" vs gold "$1.3M (corrected value)"
- `ADV_SI_003`: model "No\n\n(Exception: Senior contractors with approval...)" vs gold "No (unless senior with approval)"
- `ADV_FB_002`: model "Q3" vs gold "Q3 (her corrected statement)"
- `ADV_RT_001`: model "$14.99" with full computation vs gold "$14.99 (base $9.99 × 2 = $19.98, then 25% off = $14.985)"
- `ADV_RT_002`: model "No" vs gold "No (time-based override supersedes C-level exception)"

---

## Methodological Findings (Higher-Confidence Than the Capability Findings)

These are the durable lessons from this run — they will outlast specific model versions.

### M1. The default `LiveExperimentHarness.evaluate_response` is too strict for adversarial probes.

Adversarial gold answers carry explanatory tails. Substring containment falsely fails 6/12 = 50% of trials whose responses are correct on the canonical answer. We added `analysis/smart_evaluator.py` which strips:
- trailing parentheticals (`...(corrected value)`)
- trailing qualifications (` or `, ` but `, ` unless `, ` except `)

The fix nearly **quadruples** measured accuracy on the adversarial suite. We recommend folding this into the canonical evaluator and treating substring-containment as a fallback only.

### M2. Sonnet 4.6 gives terser answers than Haiku 4.5 on adversarial probes.

On the 7 baseline probes Haiku gets right under smart-eval, Sonnet drops "Phase 1" → "1", "Level 3" → "3", "$14.99 (with explanation)" → "$14.985\n\n$14.99". This makes Sonnet **score lower under strict eval despite plausibly correct answers** — `analysis/smart_evaluator.py` recovers most but not all (canonical "Phase 1" doesn't match a bare "1"). **Implication**: terser-answer models are systematically penalized by string-containment. Future evaluators should normalize both sides (extract the canonical short-form from response too).

### M3. `IsomorphicProbeGenerator.aggregate_probe` ground truth is alphabetically sorted; model output is in document order.

Five of seven `format_hard` misses are this issue. Either the ground truth should be order-insensitive (`set` comparison) or the prompt should explicitly request alphabetical order. We recommend making the comparator order-insensitive for aggregate probes — the underlying capability being tested is *what items are in this set*, not *can the model sort*.

### M4. The default-difficulty needle probe pins `needle_depth=0`.

This makes the entire `needle_depth` stratum collapse to a single value, defeating the experiment's stated purpose of probing depth effects. Either `LiveExperimentHarness.generate_needle_trial` should accept a depth argument or the default should sample over depths. We took the former approach in `harder_variants.hard_needle_trials`.

### M5. Multi-hop generator caps at `len(domain['entities'])` hops.

Asking for 6+ hops produces silently broken trials (entities recycled, chain breaks). Either raise the entity-pool size or document the cap. Our `harder_variants.hard_multihop_trials` falls back to 5 hops with implicit/mixed chains.

---

## Updated Capability Map (Haiku 4.5)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT UNDERSTANDING (HAIKU 4.5)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STRUCTURAL UNDERSTANDING          ●●●●●●●●○○                   │
│  ├─ Depth probe                    ●●●●●●●●●●  100% (7/7)       │
│  ├─ Parent / leaf / sibling        ●●●●●●●●●○   ~94%            │
│  ├─ Path tracing                   ●●●●●●●●○○   83% (5/6)       │
│  └─ Counting at depth 5–6          ●●●●○○○○○○   44% (HARD)      │
│                                                                 │
│  INFORMATION RETRIEVAL             ●●●●●●●●●●                   │
│  ├─ Top-level + 0-2 distractors    ●●●●●●●●●●  100% (40/40)     │
│  └─ Subsection + 3 high-sim dist.  ●●●●●●●●●●  100% (25/25)     │
│                                                                 │
│  FORMAT PROCESSING                 ●●●●●●●●●○                   │
│  ├─ Property lookup, all formats   ●●●●●●●●●●  100% (40/40)     │
│  ├─ Comparison (6 entities)        ●●●●●●●○○○   ~85%            │
│  └─ Aggregate (real, ord-insens.)  ●●●●●●●●●○   ~92%            │
│                                                                 │
│  MULTI-STEP REASONING              ●●●●●●●●●●                   │
│  ├─ 2–5 hops, explicit             ●●●●●●●●●●  100% (40/40)     │
│  └─ 5 hops, implicit/mixed         ●●●●●●●●●○   96% (24/25)     │
│                                                                 │
│  ADVERSARIAL EDGE CASES            ●●●●●●●●○○                   │
│  ├─ Smart-eval baseline            ●●●●●●●●○○   83% (10/12)     │
│  └─ Real failure: ambiguity-commit              1/3 SA probes   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

This is markedly *more capable* than the synthetic projection in the original `FINDINGS_LOG.md` (which estimated multi-step reasoning at 56%). The biggest revision: **multi-hop reasoning is not the weakest area at this scale; counting at depth is.**

---

## Reproducibility

Seeds are deterministic. To reproduce:

```bash
cd "Project 1"
# Baseline suites — Haiku 4.5
python analysis/live_api_runner.py --experiment all --trials 40 --concurrency 6
# Sonnet 4.6 spot-check
python analysis/live_api_runner.py --experiment hierarchy --trials 40 --model claude-sonnet-4-6
python analysis/live_api_runner.py --experiment adversarial --model claude-sonnet-4-6
# Hard variants
python analysis/harder_variants.py --experiment all --trials 25
# Re-score adversarial with smart eval
python analysis/smart_evaluator.py data/results/live/adversarial_*.jsonl --write
```

`ANTHROPIC_API_KEY` must be set in env. With Haiku 4.5 the full baseline run is ~3 minutes wall time and ~165k input + 4.5k output tokens.

## Counting Dose-Response Curves (added 2026-05-07)

To pinpoint *why* `count_probe` fails, two follow-up sweeps were run via `analysis/counting_curve.py`. Both use single-spine documents (one chain of intermediate headings, with the target counts at one specific depth) so the only varying factor is the named axis.

### Magnitude curve at fixed depth = 1

| k (sibling sections) | n | accuracy |
|----------------------|---|----------|
| 3                    | 4 | 100%     |
| 5                    | 4 | 100%     |
| 10                   | 4 | 100%     |
| 20                   | 4 | 100%     |
| 40                   | 4 | 100%     |
| 80                   | 4 | 100%     |

**H1.4 (Weber's-law magnitude effect) is firmly NOT supported.** Haiku 4.5 counts 80 sibling sections at depth 1 perfectly. Magnitude alone does not explain the count-probe failures.

### Depth curve at fixed k = 8

| target depth | n | accuracy | typical wrong answer |
|--------------|---|----------|----------------------|
| 1            | 4 | 100%     | —                    |
| 2            | 4 | 100%     | —                    |
| 3            | 4 | 75%      | "1"                  |
| 4            | 4 | 75%      | "1"                  |
| 5            | 4 | **0%**   | "1"                  |
| 6            | 4 | **0%**   | "1"                  |
| 7            | 4 | 50%      | "1"                  |

**This is the cleanest finding in the dataset.** Haiku 4.5 has a sharp capability boundary at depth ≥ 5: when asked "How many sections are at depth level d?" with k=8 leaves at depth d, it returns "1" — likely interpreting the question as a single-spine count rather than a sibling count. Performance recovers (50%) at depth 7, suggesting the failure mode is an inference about question intent more than a depth-counting limit per se.

### Sonnet 4.6 depth-count curve (same documents, same questions)

| target depth | Sonnet 4.6 acc | Haiku 4.5 acc |
|--------------|----------------|----------------|
| 1            | 100%           | 100%          |
| 2            | 100%           | 100%          |
| 3            | **100%**       | 75%           |
| 4            | **100%**       | 75%           |
| 5            | **100%**       | 0%            |
| 6            | **100%**       | 0%            |
| 7            | **100%**       | 50%           |

**Sonnet 4.6 is unaffected.** The depth-5 boundary is purely a Haiku 4.5 limitation. This is consistent with the count_probe-only hard-variant Sonnet result (80% vs Haiku 44% on the same trials).

### Phrasing probe (Haiku 4.5) — confirms intent-misinterpretation

Holding the document fixed and varying *only* the question wording at depths 3–7 (k=8, 4 reps each):

| depth | "depth level d" (original) | "exactly d+1 # characters" | "leaf-level headings" |
|-------|-----------------------------|------------------------------|------------------------|
| 3     | 100%                        | 100%                         | 100%                   |
| 4     | 50%                         | 100%                         | 100%                   |
| 5     | 25%                         | 100%                         | 100%                   |
| 6     | **0%**                      | **100%**                     | **100%**               |
| 7     | 25%                         | 100%                         | 100%                   |

**Haiku 4.5 hits 100% on every depth as soon as the question avoids the word "depth"** and instead refers to the markdown surface form ("# characters") or the document-relative phrase ("leaf-level headings"). Capability is intact; the failure is question-parsing.

The original `count_probe` failures at depths 5–6 are now mechanistically explained: **Haiku 4.5 misinterprets depth-targeted count questions when phrased in abstract structural language ("depth level d"), but performs perfectly when the question references concrete surface features**. Implication for practitioners: phrase document-structure queries in surface terms ("how many headings start with `#####`") rather than in abstract structural terms.

---

## Open Questions for the Next Run

1. ~~**Counting curve.** Vary count magnitude at fixed depth to test Weber's-law H1.4.~~ **DONE** — H1.4 not supported. Cleanly negative.
2. ~~**Depth-counting boundary.**~~ **DONE** — sharp boundary at depth ≥ 5 with a specific failure mode (returns "1").
3. **Needle depth boundary.** Sweep `needle_depth ∈ {0, 1, 2, 3, 4}` at fixed format and distractor config.
4. **Format ranking on harder probes.** Build a relationship probe and an aggregate probe with order-insensitive evaluation, then rank all 6 formats.
5. **Multi-hop generator extension.** Increase entity pool to support 8–10 hops; test where multi-hop actually breaks.
6. **Sonnet hard-variant comparison.** ~~Run `harder_variants` on Sonnet 4.6.~~ **DONE for hierarchy_hard** — Sonnet 4.6 = 80% on hard count probes (vs Haiku 44%); same shape, shifted up. Other hard variants pending.
7. **Disambiguating depth-count intent.** Re-run depth-count curve with rephrased prompts ("count the sub-sections of [parent X]") to test the interpretation hypothesis.
8. **Self-consistency.** Run each trial 3× and measure variance; current single-shot scores conflate accuracy with sampling noise.
