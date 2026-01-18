# Archive Manifest: Erdős Problem #983 Investigation

## Archive Date: January 2026

This archive contains files from the investigation of Erdős Problem #983 that are
now superseded by the clean library structure. These files are preserved for
historical reference to document the investigation process, including mistakes
and intermediate results.

---

## Superseded Markdown Files

| File | Reason for Archive | Notes |
|------|-------------------|-------|
| `SOLUTION.md` | Early conclusion (UNCERTAIN) | Superseded by FINAL_CONCLUSION.md |
| `ERDOS_STRAUS_DISCREPANCY.md` | Early analysis of theorem | Incorporated into INVESTIGATION_REPORT.md |
| `REVISED_ANALYSIS.md` | Early revision attempt | Superseded by later analysis |
| `HONEST_ASSESSMENT.md` | Self-critique from early phase | Historical interest only |
| `CORRECTED_ANALYSIS.md` | After definition correction | Superseded by final analysis |
| `PROOF_SKETCH.md` | **WRONG ANSWER (NO)** | Based on flawed reasoning; contradicts correct answer (YES) |
| `MAIN_QUESTION_ANALYSIS.md` | Intermediate analysis | Incorporated into INVESTIGATION_REPORT.md |

### Critical Note on PROOF_SKETCH.md
This file incorrectly claims the answer is "NO" based on the flawed reasoning that
"gap ≥ -1 implies gap cannot → +∞". This is a logical fallacy documented in
CRITICAL_FLAW.md. The correct answer is **YES**.

---

## Superseded Python Files

### Development/Debugging Scripts

| File | Purpose | Why Archived |
|------|---------|--------------|
| `debug_comparison.py` | Compare manual vs automated construction | Debugging only |
| `debug_construction.py` | Debug Woett construction | Debugging only |
| `critical_review.py` | Review code for errors | One-time use |

### Experiment Scripts (superseded by run_analysis.py)

| File | Purpose | Why Archived |
|------|---------|--------------|
| `correct_experiment.py` | Corrected definition experiments | Superseded |
| `fast_experiment.py` | Quick testing | Superseded |
| `final_experiment.py` | "Final" experiments (not actually final) | Superseded |
| `definitive_experiment.py` | More experiments | Superseded |
| `optimized_experiment.py` | Performance testing | Superseded |
| `experimental_protocol.py` | Experimental framework | Superseded |

### Construction Scripts (superseded by erdos983_lib.py)

| File | Purpose | Why Archived |
|------|---------|--------------|
| `utils.py` | Original utility functions | Superseded by erdos983_lib.py |
| `woett_construction.py` | Early Woett implementation | Superseded |
| `woett_proper.py` | Improved Woett implementation | Incorporated into library |
| `adversarial_graph.py` | Graph construction attempts | Incorporated into library |
| `bipartite_construction.py` | Bipartite matching | Incorporated into library |
| `cycle_construction.py` | Cycle-based construction (failed approach) | Did not work |
| `proper_construction.py` | Another construction attempt | Superseded |
| `constraint_solver.py` | Latin matching solver | Incorporated into library |
| `improved_solver.py` | Better solver version | Incorporated into library |
| `comprehensive_analysis.py` | Full analysis script | Superseded by run_analysis.py |

### Test Scripts

| File | Purpose | Why Archived |
|------|---------|--------------|
| `test_theory.py` | Test theoretical predictions | Superseded |
| `test_hard_sets.py` | Test hard set constructions | Superseded |
| `test_truly_hard.py` | Test very hard sets | Superseded |
| `test_full_size.py` | Test full-size constructions | Superseded |
| `test_extended.py` | Extended testing | Superseded |
| `test_erdos_straus_set.py` | Test Erdős-Straus theorem | Superseded |
| `test_corrected_definition.py` | Test corrected f definition | Incorporated into library |
| `test_gap_analysis.py` | Test gap computations | Superseded by run_analysis.py |
| `test_large_factor_sets.py` | Test large factor sets | Superseded |

---

## Files NOT Archived (Active)

The following files remain in the main directory as the current, authoritative source:

### Documentation
- `INVESTIGATION_REPORT.md` - Comprehensive investigation history
- `FINAL_CONCLUSION.md` - Definitive answer with proof
- `FORUM_CLARIFICATIONS.md` - Definition corrections from Tao/Woett
- `CRITICAL_FLAW.md` - Documents logical fallacy in early proof
- `METHODOLOGY_LESSONS.md` - Lessons learned

### Code
- `erdos983_lib.py` - Clean, reusable library
- `run_analysis.py` - Definitive analysis script
- `Erdos983.lean` - Lean proof sketch (future work)

### Git
- `.gitignore` - Git configuration

---

## How to Use Archived Files

These files are preserved for historical reference. If you need to:

1. **Understand the investigation process**: Read `INVESTIGATION_REPORT.md` first
2. **See early mistakes**: Check `PROOF_SKETCH.md` and `CRITICAL_FLAW.md`
3. **Review old implementations**: Files in `archive/` directory

**Do not use archived Python files** - they contain bugs, incorrect definitions,
or inefficient implementations. Use `erdos983_lib.py` and `run_analysis.py` instead.

---

## Archive Statistics

- Markdown files archived: 7
- Python files archived: 23
- Total files archived: 30
- Files remaining active: 9

---

## Key Lessons from Archived Work

1. **PROOF_SKETCH.md** shows how a logical fallacy led to wrong answer (NO)
2. **cycle_construction.py** shows a failed algorithmic approach
3. **woett_construction.py** vs **woett_proper.py** shows definition correction impact
4. **debug_comparison.py** shows discovery of Latin rectangle constraint

For full lessons learned, see `METHODOLOGY_LESSONS.md` in the main directory.
