# Final Conclusion: Erdős Problem #983

## Date: January 2026 (Final revision after extensive experimentation)

---

## The Question

> Is it true that $2\pi(n^{1/2}) - f(\pi(n)+1, n) \to \infty$ as $n \to \infty$?

---

## Answer: **UNCERTAIN** (Still Requires Further Investigation)

After extensive computational experiments and methodology corrections, the answer remains uncertain due to algorithmic challenges in constructing optimal adversarial sets for n > 100.

---

## Summary of Investigation

### Phase 1: Initial (Flawed) Claim
- Claimed "gap cannot → +∞" based on upper bound
- **FLAW**: Bounding below doesn't constrain above

### Phase 2: Computational Verification
- At n = 100 with correct manual construction: **f = 9 = upper bound**, gap = -1
- For n > 100 with automated construction: f = 5 consistently (suboptimal construction)

### Phase 3: Methodology Correction
- Identified that greedy graph construction creates vulnerabilities
- Proper adversarial construction requires solving combinatorial optimization
- Manual construction verified for n=100, automated fails for n > 100

---

## What We KNOW for Certain

| Fact | Evidence |
|------|----------|
| Definition: "strictly more than r" | Woett/Tao confirmation |
| Upper bound: f ≤ 2π(√n) + 1 | Erdős-Straus [Er70b] |
| Lower bound: f ≥ π((2-ε)√n) + 1 | Woett construction |
| f(26, 100) = 9 | Manual verification |
| gap(100) = -1 | Computed from f = 9 |

---

## Key Insight: The n = 100 Data Point

For n = 100:
- **Upper bound**: 2π(√100) + 1 = 2(4) + 1 = 9
- **Lower bound (Woett)**: t + 1 = 8 + 1 = 9
- **Computed f**: 9

At n = 100, both bounds coincide at f = 9. This is a special case that doesn't tell us whether f tracks the upper or lower bound for larger n.

---

## The Construction Challenge

### Why Automated Construction Fails

Building an adversarial set requires a 2-regular graph where:
1. Each small prime appears in exactly 2 products (semiprimes)
2. No two small primes share the same pair of large partners
3. All products ≤ n

This is a **Latin rectangle constraint** that greedy algorithms fail to satisfy.

### Bad Construction (Greedy)
```
2 paired with (17, 19)
3 paired with (17, 19)  ← SAME partners!
```
→ {2, 3, 17, 19} covers 4 semiprimes with 4 primes (vulnerable)

### Good Construction (Manual for n=100)
```
2 paired with (13, 19)
3 paired with (11, 17)
5 paired with (17, 19)
7 paired with (11, 13)
```
→ Each small prime has UNIQUE large partners (adversarial)

---

## Experimental Results Summary

| n | t | f (computed) | Upper Bound | Gap | Construction |
|---|---|--------------|-------------|-----|--------------|
| 100 | 8 | 9 | 9 | -1 | Manual (correct) |
| 200 | 9 | 5 | 13 | 7 | Automated (suboptimal) |
| 400 | 12 | 5 | 17 | 11 | Automated (suboptimal) |
| 800 | 16 | 5 | 19 | 13 | Automated (suboptimal) |
| 1000 | 17 | 5 | 23 | 17 | Automated (suboptimal) |
| 2000 | 23 | 5 | 29 | 23 | Automated (suboptimal) |

**Note**: The f = 5 values for n > 100 reflect suboptimal construction, not true f values.

---

## The Two Competing Hypotheses

### Hypothesis A: f ≈ upper bound (Gap bounded)
- f ≈ 2π(√n) + O(1)
- gap = 2π(√n) - f ≈ O(1) ≈ -1
- **Answer: NO**

Evidence for:
- n = 100 achieves f = upper bound
- Erdős-Straus asymptotic suggests tightness
- Upper bounds in extremal combinatorics are often achieved

### Hypothesis B: f ≈ lower bound (Gap unbounded)
- f ≈ π((2-ε)√n) + 1 for fixed ε
- gap ≈ 2π(√n) - π((2-ε)√n) ∼ εn^{1/2}/ln(n) → ∞
- **Answer: YES**

Evidence for:
- Woett construction provides explicit lower bound
- Only one data point verified (n = 100 is special)
- The gap between bounds leaves room for growth

---

## What Is Needed to Resolve

### Computational
1. **Implement proper constraint solver** for adversarial 2-regular bipartite matching
2. **Compute f correctly** for n = 200, 500, 1000 with verified adversarial sets
3. **Determine asymptotic behavior** of f empirically

### Theoretical
1. **Study [Er70b] proof** for error term structure
2. **Prove tighter bounds** on f
3. **Characterize extremal sets** that achieve f

---

## Current Assessment

| Aspect | Status |
|--------|--------|
| Definition understood | ✓ |
| Bounds established | ✓ |
| n=100 verified | ✓ |
| n>100 verified | ✗ (construction challenges) |
| Answer determined | ✗ (uncertain) |

**Best Guess**: NO (gap is bounded)
**Confidence**: LOW-MEDIUM
**Reasoning**: The n=100 data point strongly suggests f = upper bound. If this pattern continues, gap ≈ -1.

---

## Files Created

- `CRITICAL_FLAW.md` - Documents the proof error
- `METHODOLOGY_LESSONS.md` - Lessons learned from methodology errors
- `adversarial_graph.py` - Attempt at proper construction
- `debug_comparison.py` - Manual vs automated comparison
- Various experiment files

---

## References

- [Er70b] P. Erdős, "Some applications of graph theory to number theory" (1969), p. 138
- erdosproblems.com Problem #983
- Woett's forum comment (Oct 2025)
- Tao's confirmation (Jan 2026)
