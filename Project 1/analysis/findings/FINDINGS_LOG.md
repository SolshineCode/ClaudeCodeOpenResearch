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

**Status**: Protocol complete, stimuli ready

**Core Questions**:
- Can models count nesting depth accurately?
- How do parent-child vs sibling relationships differ in recognizability?
- Does counting accuracy follow Weber's law (proportional difficulty)?

**Key Design Features**:
- Procedurally generated document trees with known structure
- Multiple formats (MD, JSON, XML, text) for same content
- Probes targeting specific structural relationships
- Systematic variation of depth (1-6) and breadth (narrow/wide)

**Hypotheses**:
| ID | Hypothesis | Status |
|----|------------|--------|
| H1.1 | Depth perception accuracy decreases with depth | Untested |
| H1.2 | JSON format yields highest structural accuracy | Untested |
| H1.3 | Parent relationships easier than sibling relationships | Untested |
| H1.4 | Counting follows Weber's law (difficulty ∝ magnitude) | Untested |

---

### Experiment 2: Needle in Structure

**Status**: Protocol complete, stimuli ready

**Core Questions**:
- Do structural markers (headers) act as attention anchors?
- How do high-similarity distractors affect retrieval?
- Is there a depth penalty for nested information?

**Key Design Features**:
- Embedded key-value facts at controlled positions
- Variable distractor similarity (none → high)
- Multiple format renderings
- Position tracking (depth × local position)

**Hypotheses**:
| ID | Hypothesis | Status |
|----|------------|--------|
| H2.1 | Information after headers is easier to retrieve | Untested |
| H2.2 | High-similarity distractors cause confusion errors | Untested |
| H2.3 | Deeper nesting reduces retrieval accuracy | Untested |
| H2.4 | Explicit structure (XML) aids retrieval | Untested |

---

### Experiment 3: Isomorphic Content Analysis

**Status**: Protocol complete, stimuli ready

**Core Questions**:
- Is document understanding truly format-independent?
- What format-specific affordances exist?
- How do different question types interact with format?

**Key Design Features**:
- Identical semantic content in 7 formats
- Same probing questions across all formats
- Question types: property lookup, relations, aggregates, comparisons
- Within-subject design isolates format effects

**Hypotheses**:
| ID | Hypothesis | Status |
|----|------------|--------|
| H3.1 | Property lookups favor structured formats (JSON, XML) | Untested |
| H3.2 | Tabular formats excel at comparison tasks | Untested |
| H3.3 | Aggregate questions are format-invariant | Untested |
| H3.4 | Prose formats better for relationship questions | Untested |

---

### Experiment 4: Multi-Hop Document Reasoning

**Status**: Protocol complete, stimuli ready

**Core Questions**:
- How does reasoning scale with chain length?
- Do explicit cross-references help?
- What are the failure modes in multi-hop reasoning?

**Key Design Features**:
- Embedded reasoning chains (2-5 hops)
- Three link types: explicit, implicit, mixed
- Ground truth reasoning traces for analysis
- Error categorization framework

**Hypotheses**:
| ID | Hypothesis | Status |
|----|------------|--------|
| H4.1 | Accuracy decreases linearly (or worse) with hops | Untested |
| H4.2 | Explicit links yield higher accuracy | Untested |
| H4.3 | Most errors occur at early hops (chain breaks) | Untested |
| H4.4 | Structured format markers improve multi-hop | Untested |

---

## Preliminary Observations

### From Stimulus Development

During stimulus generation and testing, we observed:

1. **Format Rendering Differences**: The same hierarchical structure looks dramatically different across formats. Markdown uses whitespace/headers, JSON uses brackets/nesting, XML uses tags. This visual difference likely affects parsing strategies.

2. **Distractor Design Matters**: High-similarity distractors that share key words but differ in values are qualitatively different from those with different topics entirely. This suggests semantic vs lexical interference.

3. **Chain Length vs Document Length**: Multi-hop chains naturally increase document length. Need to control for this confound.

4. **Ground Truth Complexity**: Some "simple" structural questions (e.g., "list all siblings") require careful specification to have unambiguous answers.

### Methodological Notes

1. **Seed Control**: All stimulus generation uses seeds for reproducibility. Same seed + parameters → identical stimulus.

2. **Evaluator Design**: Matching model responses to expected answers requires careful evaluator design. Exact match too strict, contains too loose.

3. **Probe Type Balance**: Different probe types have different base difficulties. Need to analyze within probe type, not just aggregate.

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
from analysis.experiment_runner import ExperimentRunner, MockModelInterface
from analysis.statistical_analysis import generate_analysis_report
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
```

---

## Next Steps

1. **Baseline Establishment**: Run initial trials to establish baseline performance
2. **Pilot Analysis**: Analyze pilot data to validate methodology
3. **Full Experiment Runs**: Execute complete experiment suites
4. **Cross-Experiment Analysis**: Look for patterns across experiments
5. **Capability Mapping**: Create comprehensive map of document understanding capabilities

---

## References

- Anthropic. "Scaling Monosemanticity" and related interpretability work
- DocVQA, InfographicVQA benchmarks
- Transformer Circuits Thread (Elhage et al.)
- "Lost in the Middle" (Liu et al.) - positional effects in long contexts

---

*Last updated: Initial creation*
