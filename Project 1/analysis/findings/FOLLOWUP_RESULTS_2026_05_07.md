# Follow-up: Sonnet 4.6 Hard-Variant Sweep + Cross-Model Phrasing Probe

**Date:** 2026-05-07 (continuation of [BASELINE_RESULTS_2026_05_07.md](BASELINE_RESULTS_2026_05_07.md))
**New trials:** 75 hard-variant + 60 phrasing = 135 additional API calls.
**Auto-table:** [RESULTS_TABLE.md](RESULTS_TABLE.md) (regenerable via `python analysis/comparison_table.py --write`).

This doc completes two open items from the baseline report: (a) Sonnet 4.6 vs Haiku 4.5 across the *hard* variants (not just hierarchy), and (b) Sonnet 4.6 on the depth-phrasing probe.

## Cross-Model Hard-Variant Comparison

| Suite           | n  | Haiku 4.5 | Sonnet 4.6 | Δ (Sonnet − Haiku) |
|-----------------|----|-----------|------------|---------------------|
| hierarchy_hard  | 25 | 44.0%     | 80.0%      | +36.0 pp            |
| needle_hard     | 25 | 100.0%    | 100.0%     | 0                   |
| multihop_hard   | 25 | 96.0%     | 100.0%     | +4.0 pp             |
| format_hard     | 25 | 72.0%     | 92.0%      | +20.0 pp            |

The only place Sonnet shows a *large* lift is `hierarchy_hard` (the count-probe at depth 5–6 difficulty). On `format_hard`, the +20 pp gap shrinks substantially when the aggregate-probe order-mismatch artifact is corrected — both models actually have nearly all items correct in those misses; Sonnet just produces them in alphabetical order more often.

`needle_hard` and `multihop_hard` were already at ceiling on Haiku; Sonnet maintains. Latency cost: Sonnet runs 2–4× slower per trial (avg 2,000–3,500 ms vs 700–2,000 ms on Haiku) and uses 2–4× more output tokens.

## Phrasing Probe — Sonnet 4.6 vs Haiku 4.5

Same 28 documents (depths 3–7 × 4 reps), same three question phrasings:

### Sonnet 4.6

| depth | "depth level d" | "exactly d+1 # chars" | "leaf-level headings" |
|-------|-----------------|------------------------|------------------------|
| 3     | 100%            | 100%                   | 100%                   |
| 4     | 100%            | 100%                   | 100%                   |
| 5     | 75%             | 100%                   | 100%                   |
| 6     | 100%            | 100%                   | 100%                   |
| 7     | 100%            | 100%                   | 100%                   |

### Haiku 4.5 (reproduced from baseline report for comparison)

| depth | "depth level d" | "exactly d+1 # chars" | "leaf-level headings" |
|-------|-----------------|------------------------|------------------------|
| 3     | 100%            | 100%                   | 100%                   |
| 4     | 50%             | 100%                   | 100%                   |
| 5     | 25%             | 100%                   | 100%                   |
| 6     | **0%**          | **100%**               | **100%**               |
| 7     | 25%             | 100%                   | 100%                   |

**Key insight:** Sonnet 4.6 is essentially immune to the phrasing — only one trial wrong (1/28 across the whole sweep). Haiku 4.5 is sensitive only to the abstract "depth level d" wording and recovers fully under the surface-feature wordings.

Together with the cross-model hard-variant comparison, this paints a coherent picture: **Haiku 4.5's apparent weakness on hierarchy depth-counting is a question-comprehension limitation, not a structure-traversal limitation**. Sonnet 4.6 either parses the abstract phrasing more reliably, or has a stronger prior to override it.

## Updated Capability Map (Both Models, Hard-Variant Headlines)

```
                                  HAIKU 4.5      SONNET 4.6
  hierarchy_hard (count, d=5-6)   ●●●●○○○○○○     ●●●●●●●●○○
  needle_hard (depth-1, hi-sim)   ●●●●●●●●●●     ●●●●●●●●●●
  multihop_hard (5-hop impl/mix)  ●●●●●●●●●●     ●●●●●●●●●●
  format_hard (cmp+agg, 6 ent.)   ●●●●●●●○○○     ●●●●●●●●●○
  adversarial (smart-eval)        ●●●●●●●●○○     ●●●●●●○○○○
  depth-count, original phrasing  ●●●○○○○○○○     ●●●●●●●●●○
  depth-count, surface phrasing   ●●●●●●●●●●     ●●●●●●●●●●
```

## Recommendations for Probe Authors

Combining baseline + follow-up findings, three concrete recommendations:

1. **For depth/structure queries, prompt with surface features when possible.** "How many headings start with `#####`?" outperforms "How many sections are at depth level 5?" on Haiku 4.5 by 75 percentage points at depth 6.

2. **For aggregate/list probes, evaluate order-insensitively.** Both models return items in document order more often than alphabetical. The current `IsomorphicProbeGenerator.aggregate_probe` ground truth is sorted; either sort the response or compare as sets.

3. **For adversarial probes with qualified gold answers, use canonical-answer extraction.** `analysis/smart_evaluator.py` recovers most of the gap; folding it into the canonical evaluator is the simplest fix. For terser models (Sonnet), even canonical matching can fail when the model gives a bare number ("3") for a gold answer like "Level 3" — consider also extracting a canonical short-form from the response.

## Aggregate-Probe Fix (added inline this PR)

`IsomorphicProbeGenerator.aggregate_probe` previously returned a comma-joined alphabetically-sorted string. Changed to return a list when the source value is list-typed; the evaluator's existing list branch performs order-insensitive set-membership matching. Re-running `format_hard` after the fix:

| Model         | Before fix | After fix |
|---------------|-----------|-----------|
| Haiku 4.5     | 72%       | **88%**   |
| Sonnet 4.6    | 92%       | **100%**  |

The +16 / +8 percentage-point lift is entirely from removing the alphabetical-sort artifact — same documents, same model responses, just an honest evaluator. The remaining 3 Haiku misses are real `comparison_probe` errors (not aggregate-order artifacts).

## Open Items After This Round

- **Multi-hop generator extension** to support 6–10 hops (currently capped silently at 5 by entity-pool size).
- **More-granular depth sweep on Sonnet 4.6.** Does the depth-5 dip (3/4) with "depth level d" reflect a real residual sensitivity, or sampling noise? Needs n≥20 at d=5.
- **Self-consistency.** Run the depth-5 "depth level d" Haiku trial 10× with seed=fixed; is the failure stochastic or deterministic?
