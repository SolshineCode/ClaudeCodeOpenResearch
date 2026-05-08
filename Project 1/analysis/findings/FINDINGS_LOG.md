# Research Findings Log

## Document Intelligence & Mechanistic Interpretability Games

This document tracks research findings, observations, and insights as experiments progress.

---

## Theoretical Foundations

### Core Framework

Our experimental approach treats document understanding as a **behavioral black box** that can be probed through carefully designed stimuli. Key assumptions:

1. **Observable Invariants**: Consistent patterns in model responses reveal underlying processing mechanisms
2. **Structural Isomorphism**: The same semantic content in different formats should yield equivalent understanding (if format-independent)
3. **Compositionality**: Complex document reasoning decomposes into identifiable primitive operations
4. **Graceful Degradation**: Capability boundaries reveal architectural constraints

### Experimental Design Philosophy

We employ a "games" metaphor because each experiment:
- Has **clear rules** (task specification)
- Uses **controlled stimuli** (parameterized document generation)
- Produces **scorable outcomes** (ground truth comparison)
- Reveals **strategy** (error pattern analysis)

---

## Experiment Suite Overview

### Experiment 1: Hierarchy Perception

**Status**: Live-tested (Haiku 4.5 + Sonnet 4.6, 2026-05-07). See [BASELINE_RESULTS_2026_05_07.md](BASELINE_RESULTS_2026_05_07.md).

**Headline**: Haiku 4.5 = 87.5% (40 trials, depths 1–4); Sonnet 4.6 = 97.5%. Hard variant (count probes only at depths 5–6) drops Haiku to **44%**.

**Hypotheses**:
| ID | Hypothesis | Status | Verdict |
|----|------------|--------|---------|
| H1.1 | Depth perception accuracy decreases with depth | Live-tested | **Partially supported** — sharp threshold at depth 5+, not smooth degradation |
| H1.2 | JSON format yields highest structural accuracy | Untested | Ceiling effect masks any difference; need harder probes |
| H1.3 | Parent relationships easier than sibling relationships | Live-tested | **Not supported** — both ~100%; salient axis is *probe type* (count_probe is the weakness) |
| H1.4 | Counting follows Weber's law | Live-tested | **No evidence yet** — needs a count-magnitude sweep at fixed depth |

---

### Experiment 2: Needle in Structure

**Status**: Live-tested. Haiku 4.5 = 100% on baseline (40 trials) and on hard variant (depth-1 placement, 3× high-similarity distractors, 25 trials). See [BASELINE_RESULTS_2026_05_07.md](BASELINE_RESULTS_2026_05_07.md).

**Hypotheses**:
| ID | Hypothesis | Status | Verdict |
|----|------------|--------|---------|
| H2.1 | Information after headers is easier to retrieve | **Cannot test as designed** — `LiveExperimentHarness.generate_needle_trial` pins needle to depth 0 / middle |
| H2.2 | High-similarity distractors cause confusion errors | Live-tested | **Not supported at this scale** — 100% even with 3× high-sim distractors |
| H2.3 | Deeper nesting reduces retrieval accuracy | Live-tested | **Not supported through depth 1** — need depth 3+ |
| H2.4 | Explicit structure (XML) aids retrieval | Untested | Ceiling effect would mask anyway |

---

### Experiment 3: Isomorphic Content Analysis

**Status**: Live-tested. Haiku 4.5 = 100% on baseline `entity_property` (40 trials, all 6 formats); 72% on hard variant — but **5 of 7 misses are evaluator artifacts** (model returns aggregate items in document order, ground truth is sorted alphabetically). See [BASELINE_RESULTS_2026_05_07.md](BASELINE_RESULTS_2026_05_07.md).

**Hypotheses**:
| ID | Hypothesis | Status | Verdict |
|----|------------|--------|---------|
| H3.1 | Property lookups favor structured formats | Live-tested | **Cannot reject** — all 6 formats at 100% on entity_property; ceiling masks effect |
| H3.2 | Tabular formats excel at comparison | Live-tested | Inconclusive (n=4 comparison probes, 2 misses across yaml/json) |
| H3.3 | Aggregate questions are format-invariant | Live-tested | **Confounded** — aggregate ground truth is sorted, model output is in document order; needs order-insensitive scoring |
| H3.4 | Prose formats better for relationship questions | Untested | No relationship probe in current set |

---

### Experiment 4: Multi-Hop Document Reasoning

**Status**: Live-tested. Haiku 4.5 = 100% on baseline (40 trials, 2–5 hops, explicit chains) and 96% on hard variant (5 hops, implicit/mixed). The single failure had correct chain reasoning but wrong final-property pick. See [BASELINE_RESULTS_2026_05_07.md](BASELINE_RESULTS_2026_05_07.md).

**Hypotheses**:
| ID | Hypothesis | Status | Verdict |
|----|------------|--------|---------|
| H4.1 | Accuracy decreases linearly (or worse) with hops | Live-tested | **Not supported through 5 hops** — generator currently caps at 5 (entity-pool size); test the boundary by extending the generator |
| H4.2 | Explicit links yield higher accuracy than implicit | Live-tested | Within noise on n=25; needs head-to-head at fixed hop count |
| H4.3 | Most errors occur at early hops | Untestable | Single error in entire dataset |
| H4.4 | Structured format markers improve multi-hop | Untested | Only markdown used |

---

### Experiment 5: Adversarial Edge Cases

**Status**: Protocol complete, 12 probes designed

**Categories**:
- Structural Ambiguity (orphaned content, competing hierarchies)
- Semantic Interference (similar entities, updated values, negation traps)
- Positional Bias (primacy trap, recency trap)
- Format Breaking (markdown in code, nested quotes)
- Reasoning Traps (conditional cascade, exception to exception)

**Key Insights from Probe Design**:
Each probe targets a specific failure mode with a known "trap answer" that reveals the weakness. This allows for diagnostic error analysis beyond simple accuracy.

---

## Live API Baseline (2026-05-07)

The first end-to-end run against actual model APIs is documented in **[BASELINE_RESULTS_2026_05_07.md](BASELINE_RESULTS_2026_05_07.md)**. Major takeaways supersede the synthetic-mock projections in the "Emergent Insights" section below:

| Suite        | Haiku 4.5 strict | Haiku 4.5 smart | Sonnet 4.6 strict | Hard-variant Haiku 4.5 |
|--------------|------------------|-----------------|-------------------|------------------------|
| hierarchy    | 87.5%            | —               | 97.5%             | 44% (count, depth 5–6) |
| needle       | 100%             | —               | —                 | 100% (depth-1, 3× hi-sim) |
| format       | 100%             | —               | —                 | ~92% (real, ord-insens.) |
| multihop     | 100%             | —               | —                 | 96% (5h implicit/mixed) |
| adversarial  | 25%              | **83%**         | 25% (smart 67%)   | — |

The most important methodological finding: **the strict substring evaluator falsely fails 5/12 correct adversarial responses** because gold answers carry parenthetical qualifications. `analysis/smart_evaluator.py` adds canonical-answer extraction and recovers them. Several "ceiling effects" in the original framework were also evaluator-bound; see Sections M3–M5 of the baseline report.

The capability map below was derived from synthetic mocks before any live data existed and is no longer current. The live-data version lives in BASELINE_RESULTS_2026_05_07.md.

---

## Preliminary Observations

### From Stimulus Development

1. **Format Rendering Differences**: The same hierarchical structure looks dramatically different across formats. Markdown uses whitespace/headers, JSON uses brackets/nesting, XML uses tags. This visual difference likely affects parsing strategies.

2. **Distractor Design Matters**: High-similarity distractors that share key words but differ in values are qualitatively different from those with different topics entirely. This suggests semantic vs lexical interference.

3. **Chain Length vs Document Length**: Multi-hop chains naturally increase document length. Need to control for this confound.

4. **Ground Truth Complexity**: Some "simple" structural questions (e.g., "list all siblings") require careful specification to have unambiguous answers.

### Methodological Notes

1. **Seed Control**: All stimulus generation uses seeds for reproducibility. Same seed + parameters → identical stimulus.

2. **Evaluator Design**: Matching model responses to expected answers requires careful evaluator design. Exact match too strict, contains too loose.

3. **Probe Type Balance**: Different probe types have different base difficulties. Need to analyze within probe type, not just aggregate.

---

## Emergent Insights

### From Framework Construction

During the process of building this experimental framework, several insights emerged:

#### 1. The Format Performance Gap

Synthetic testing (with realistic accuracy models) consistently shows:
- **JSON** performs best (~95% in demos)
- **Plain text** performs worst (~65-73%)
- Gap of 20-30 percentage points between best and worst formats

**Implication**: Format choice is not merely cosmetic—it fundamentally affects processing reliability.

#### 2. Capability Boundaries are Sharp

Analysis tools reveal that performance often drops sharply at specific thresholds rather than degrading gradually:
- ~40%+ accuracy drops observed at certain complexity levels
- Multi-hop reasoning shows particular sensitivity at 4-5 hops
- Distractor similarity has threshold effects (medium → high causes large drop)

**Implication**: Systems should be designed to operate within known capability boundaries, with fallbacks at edge cases.

#### 3. Multi-Step Reasoning is the Weakest Capability

Across all synthetic modeling, multi-hop reasoning consistently shows:
- Lower baseline accuracy (~56% in demos vs 82%+ for other tasks)
- Steepest degradation with complexity
- Most sensitive to confounds

**Implication**: Decompose multi-hop tasks where possible; validate reasoning chains step-by-step.

#### 4. Adversarial Probes Reveal Specific Mechanisms

The 12 adversarial probes each target a specific processing weakness:
- **Orphaned Content**: Tests section association direction
- **Updated Values**: Tests revision tracking
- **Primacy Trap**: Tests recency/frequency weighting
- **Exception to Exception**: Tests rule priority tracking

**Implication**: Error patterns are diagnostic—knowing *which* trap was triggered reveals *what* mechanism failed.

---

## Capability Map (Preliminary)

Based on framework analysis:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT UNDERSTANDING CAPABILITIES          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STRUCTURAL UNDERSTANDING          ●●●●●●●●○○  (~80%)          │
│  ├─ Depth perception               ●●●●●●●●●○                   │
│  ├─ Parent-child relationships     ●●●●●●●●○○                   │
│  └─ Sibling identification         ●●●●●●○○○○                   │
│                                                                 │
│  INFORMATION RETRIEVAL             ●●●●●●●●○○  (~82%)          │
│  ├─ Key-value extraction           ●●●●●●●●●○                   │
│  ├─ With distractors (low)         ●●●●●●●●○○                   │
│  └─ With distractors (high)        ●●●●○○○○○○                   │
│                                                                 │
│  FORMAT PROCESSING                 ●●●●●●●●○○  (~82%)          │
│  ├─ JSON                           ●●●●●●●●●●                   │
│  ├─ XML                            ●●●●●●●●○○                   │
│  ├─ YAML                           ●●●●●●●●○○                   │
│  └─ Plain text                     ●●●●●●○○○○                   │
│                                                                 │
│  MULTI-STEP REASONING              ●●●●●○○○○○  (~56%)          │
│  ├─ 2-hop chains                   ●●●●●●●○○○                   │
│  ├─ 3-hop chains                   ●●●●●●○○○○                   │
│  ├─ 4-hop chains                   ●●●●○○○○○○                   │
│  └─ 5-hop chains                   ●●●○○○○○○○                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Legend: ● = strong capability, ○ = weak/uncertain
```

---

## Running Experiments

### Prerequisites

```python
# From Project 1 root
from tools.document_generator import generate_experiment_stimulus
from experiments.structural.hierarchy_perception import generate_sample_trials
from experiments.attention.needle_in_structure import generate_experiment_suite
from experiments.format.isomorphic_content import generate_isomorphic_stimulus
from experiments.reasoning.multi_hop_document import create_multi_hop_trial
from experiments.adversarial.edge_case_probes import generate_all_probes
from analysis.experiment_runner import ExperimentRunner, MockModelInterface
from analysis.statistical_analysis import generate_analysis_report
from analysis.synthesis import CrossExperimentAnalyzer
from analysis.visualization import ASCIIChart, ReportGenerator
```

### Quick Start

```python
# Generate a single stimulus
stimulus = generate_experiment_stimulus(seed=42, max_depth=3, format='markdown')
print(stimulus['document'])
print(stimulus['probes'])

# Run mock experiment
runner = ExperimentRunner(MockModelInterface())
results = runner.run_experiment('test', trials, evaluator)

# Cross-experiment analysis
analyzer = CrossExperimentAnalyzer()
analyzer.load_results('experiment_name', results)
print(analyzer.generate_synthesis_report())
```

---

## Next Steps

1. **Live Model Testing**: Run experiments against actual LLM APIs
2. **Error Pattern Analysis**: Categorize failures by mechanism
3. **Boundary Mapping**: Precisely identify capability thresholds
4. **Intervention Testing**: Test prompting strategies at boundaries
5. **Publication Preparation**: Document findings for broader sharing

---

## References

- Anthropic. "Scaling Monosemanticity" and related interpretability work
- DocVQA, InfographicVQA benchmarks
- Transformer Circuits Thread (Elhage et al.)
- "Lost in the Middle" (Liu et al.) - positional effects in long contexts

---

*Last updated: Initial framework complete with emergent insights*
