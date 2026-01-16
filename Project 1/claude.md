# Project 1 - Claude Context

## Project Focus

AI Document Intelligence & LLM Mechanistic Interpretability Games

## Scope

This project explores the intersection of:
- **Document Intelligence**: How LLMs parse, understand, and reason about structured documents
- **Mechanistic Interpretability**: Probing the internal mechanisms by which models process information
- **Interactive Games**: Structured challenges that reveal model behavior and capabilities

## Working Guidelines

1. Focus on this project folder only - ignore sibling project folders
2. Experiments should be reproducible and well-documented
3. Prioritize insights that could generalize across models and document types
4. Build tools that make interpretability accessible and interactive

---

## Project Structure

```
Project 1/
├── RESEARCH_PLAN.md              # Theoretical framework and methodology
├── README.md                     # Project overview
├── claude.md                     # This file
│
├── experiments/                  # Experimental code
│   ├── structural/               # Hierarchy perception experiments
│   │   └── hierarchy_perception.py
│   ├── attention/                # Attention archaeology experiments
│   │   └── needle_in_structure.py
│   ├── format/                   # Format sensitivity experiments
│   │   └── isomorphic_content.py
│   └── reasoning/                # Multi-hop reasoning experiments
│       └── multi_hop_document.py
│
├── tools/                        # Reusable utilities
│   └── document_generator.py     # Parameterized document generation
│
├── data/
│   ├── stimuli/                  # Experiment protocols (JSON)
│   └── results/                  # Experimental outputs
│
└── analysis/
    ├── experiment_runner.py      # Framework for running experiments
    ├── statistical_analysis.py   # Analysis utilities
    └── findings/                 # Research findings
        └── FINDINGS_LOG.md
```

---

## Experiment Suite

### 1. Hierarchy Perception (`experiments/structural/`)
Tests whether LLMs can accurately perceive document hierarchy.
- **Probes**: Depth perception, parent/child relationships, sibling identification, path tracing, counting
- **Variables**: Document depth (1-6), format (MD/JSON/XML/text), branching factor
- **Key Question**: How does structural accuracy degrade with complexity?

### 2. Needle in Structure (`experiments/attention/`)
Probes where models "attend" when searching documents.
- **Design**: Key-value facts embedded at controlled positions with distractors
- **Variables**: Needle depth, local position, distractor similarity, format
- **Key Question**: Do headers act as attention anchors?

### 3. Isomorphic Content (`experiments/format/`)
Tests format-independence of document understanding.
- **Design**: Identical semantic content in 7 formats
- **Formats**: Markdown (prose/table), JSON, XML, YAML, plain text, CSV
- **Key Question**: Which format-question type combinations excel/fail?

### 4. Multi-Hop Reasoning (`experiments/reasoning/`)
Tests reasoning across document sections.
- **Design**: Embedded reasoning chains (2-5 hops) with explicit/implicit links
- **Variables**: Hop count, link type, format
- **Key Question**: How does accuracy scale with chain length?

---

## Quick Start

```python
# Generate a sample document with probes
from tools.document_generator import generate_experiment_stimulus

stimulus = generate_experiment_stimulus(
    seed=42,
    max_depth=3,
    format='markdown',
    num_probes=5
)
print(stimulus['document'])
print(stimulus['probes'])

# Generate experiment trials
from experiments.structural.hierarchy_perception import generate_sample_trials
trials = generate_sample_trials('shallow', num_samples=5)

# Run analysis
from analysis.statistical_analysis import generate_analysis_report
report = generate_analysis_report(results, 'experiment_name', ['depth', 'format'])
```

---

## Key Research Questions

1. How do attention patterns shift when processing different document structures?
2. Can we design "games" that reliably surface specific model behaviors?
3. What probing techniques best reveal document understanding mechanisms?
4. How can we make interpretability findings actionable for practitioners?

---

## Current Status

- [x] Theoretical framework established
- [x] Four experiment protocols designed and implemented
- [x] Document generation tools built
- [x] Analysis framework created
- [ ] Baseline experiments to run
- [ ] Results analysis
- [ ] Cross-experiment synthesis

---

## Core Principles

1. **Ground Truth**: Every probe has an objectively correct answer
2. **Minimal Pairs**: Isolate variables by changing one thing at a time
3. **Reproducibility**: Seed-controlled generation for exact replication
4. **Simple Implementations**: Complex questions, simple code
