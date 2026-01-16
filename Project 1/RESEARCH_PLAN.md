# Research Plan: Document Intelligence & Mechanistic Interpretability Games

## Theoretical Framework

### Core Hypothesis

Large language models develop **implicit structural representations** when processing documents that are:
1. **Hierarchically organized** - mirroring document tree structures
2. **Format-sensitive** - different for markdown vs. JSON vs. plain text
3. **Queryable through behavioral probing** - revealing internal mechanisms without direct access to weights

### Why This Matters

Understanding how LLMs process documents has implications for:
- **Reliability**: When can we trust document-based reasoning?
- **Alignment**: Do models "understand" structure or pattern-match?
- **Capability elicitation**: How to best format information for LLM consumption?
- **Interpretability**: What computational primitives underlie document understanding?

---

## Research Methodology

### Approach: Behavioral Mechanistic Interpretability

Since we cannot directly inspect model weights, we use **behavioral probing** - carefully designed inputs that reveal internal processing through output patterns. This is analogous to:
- Psychophysics in cognitive science
- Black-box testing in software engineering
- Lesion studies in neuroscience (via prompt perturbation)

### The "Game" Framework

Each experiment is structured as a **game** with:
1. **Rules**: Precise task definition
2. **Stimuli**: Carefully constructed document inputs
3. **Probes**: Questions that reveal specific mechanisms
4. **Predictions**: What different hypotheses predict
5. **Scoring**: Quantifiable success metrics

---

## Experimental Domains

### Domain 1: Structural Encoding

**Question**: How do models represent document hierarchy?

**Experiments**:
- Depth perception tests (can models count nesting levels?)
- Sibling relationship probes (what's "next to" what?)
- Ancestor/descendant reasoning (what contains what?)
- Cross-reference resolution (following internal links)

### Domain 2: Attention Archaeology

**Question**: Where do models "look" when processing documents?

**Experiments**:
- Needle-in-haystack with structural cues
- Distractor resistance at different hierarchy levels
- Attention proxy through paraphrase location
- Information integration across sections

### Domain 3: Format Sensitivity

**Question**: How does representation format affect processing?

**Experiments**:
- Isomorphic content in different formats (MD, JSON, XML, plain)
- Format-specific affordance tests
- Cross-format transfer (learn in one, test in another)
- Adversarial formatting edge cases

### Domain 4: Reasoning Traces

**Question**: What computational steps underlie document reasoning?

**Experiments**:
- Multi-hop reasoning with explicit vs. implicit structure
- Compositional generalization across document patterns
- Error pattern analysis (where do models fail systematically?)
- Chain-of-thought decomposition alignment

---

## Experimental Design Principles

### 1. Minimal Pairs
Compare stimuli that differ in exactly one structural property to isolate effects.

### 2. Ground Truth
Every experiment has objectively correct answers derivable from the document.

### 3. Controls
Include baseline conditions that test for confounds (memorization, statistical shortcuts).

### 4. Gradients
Test along continuous dimensions (depth, length, complexity) to find capability boundaries.

### 5. Replication
Multiple instances of each pattern to distinguish systematic behavior from noise.

---

## Success Criteria

### Immediate Goals
- [ ] Establish baseline performance on structural tasks
- [ ] Identify at least 3 robust behavioral signatures of document processing
- [ ] Create reusable experimental framework

### Medium-term Goals
- [ ] Map capability boundaries across document complexity
- [ ] Develop predictive model of when document reasoning succeeds/fails
- [ ] Publish reproducible findings

### Long-term Vision
- Contribute to mechanistic understanding of transformer document processing
- Inform best practices for document-based LLM applications
- Bridge behavioral and weights-based interpretability

---

## File Organization

```
Project 1/
├── RESEARCH_PLAN.md          # This document
├── README.md                 # Project overview
├── claude.md                 # AI assistant context
├── experiments/              # Experimental code and protocols
│   ├── structural/           # Domain 1: Structural encoding
│   ├── attention/            # Domain 2: Attention archaeology
│   ├── format/               # Domain 3: Format sensitivity
│   └── reasoning/            # Domain 4: Reasoning traces
├── data/                     # Test stimuli and results
│   ├── stimuli/              # Input documents
│   └── results/              # Experimental outputs
├── analysis/                 # Analysis code and findings
│   └── findings/             # Documented discoveries
└── tools/                    # Reusable utilities
```

---

## Next Steps

1. **Build structural probing experiments** - Start with hierarchy depth perception
2. **Create stimulus generation tools** - Parameterized document generators
3. **Establish baselines** - Run initial experiments to calibrate
4. **Iterate based on findings** - Let results guide deeper investigation
