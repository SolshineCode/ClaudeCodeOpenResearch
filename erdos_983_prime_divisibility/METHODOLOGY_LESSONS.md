# Methodology Lessons: Erdős Problem #983

## Date: January 2026

---

## Summary

During the investigation of Erdős Problem #983, several critical methodological errors were made and corrected. This document captures these lessons for future reference.

---

## Lesson 1: Logical Fallacy in Proof

### The Error
I claimed: "The upper bound f ≤ 2π(√n) + 1 implies gap ≥ -1, therefore gap cannot → +∞"

### Why It's Wrong
This is a **non sequitur**. Bounding a quantity below (-1) says nothing about whether it can grow to +∞. The gap could be:
- Bounded below by -1 AND bounded above by some constant (→ bounded)
- Bounded below by -1 AND unbounded above (→ can go to +∞)

Both are logically possible given only the lower bound.

### Lesson
**Always trace logical implications carefully. A bound in one direction tells you nothing about the other direction.**

---

## Lesson 2: Definition Precision Matters

### The Error
Initial code used `coverage >= r` instead of `coverage > r`.

### Why It's Wrong
The Woett correction clarified that f(k,n) requires **strictly more than r** elements covered, not "at least r". This seemingly small difference changes the computed values.

### Lesson
**Read problem definitions multiple times. Small words like "strictly" or "at least" fundamentally change the problem.**

---

## Lesson 3: Greedy Algorithms Can Fail for Adversarial Constructions

### The Error
Used greedy edge selection (smallest products first, or "spread" heuristic) to build the 2-regular graph.

### Why It's Wrong
For n=100, greedy gives edges like:
- 2 paired with (17, 19)
- 3 paired with (17, 19)

This creates a **vulnerability**: {2, 3, 17, 19} covers 4 semiprimes with only 4 primes.

The correct adversarial construction pairs each small prime with **different** large primes:
- 2 with (13, 19)
- 3 with (11, 17)
- 5 with (17, 19)
- 7 with (11, 13)

### Lesson
**Adversarial constructions require careful design. Greedy algorithms often produce suboptimal structures that are easy to attack.**

---

## Lesson 4: "Extras" Can Create Vulnerabilities

### The Error
Added composites like 2×p_{t+1} and 3×p_{t+1} to reach target size.

### Why It's Wrong (Initially Thought)
With wrong construction, {2, 3, p_t1} covers both extras AND the semiprimes involving 2, 3.

### Correction
With the **correct** adversarial construction, the extras actually HELP. For n=100:
- 9 primes {2,3,5,7,11,13,17,19,23} cover 10 elements (8 semiprimes + 2 extras sharing factors)
- f = 9 = upper bound ✓

### Lesson
**Don't remove components without understanding why they were there. The "vulnerability" was due to bad graph construction, not the extras themselves.**

---

## Lesson 5: Verify Assumptions on Multiple Test Cases

### The Error
Validated construction on n=100, then assumed automated construction would work for larger n.

### Why It's Wrong
The automated construction for n > 100 consistently gave f = 5 (way below expected), indicating fundamental failures in the graph building algorithm.

### Lesson
**Always verify intermediate results. A single working test case doesn't validate the general algorithm.**

---

## Lesson 6: Track Set Sizes Carefully

### The Error
Built sets A with wrong sizes (e.g., |A| = 25 instead of target 26).

### Why It's Wrong
The upper bound f ≤ 2π(√n) + 1 only applies when |A| = π(n) + 1. With wrong sizes, the bound may not hold.

### Lesson
**Verify constraints are satisfied. Check that |A| matches the target before computing f.**

---

## Key Algorithmic Insight

### The 2-Regular Graph Problem
Building an adversarial 2-regular graph requires:

1. **Bipartite structure**: Split primes into "small" (≤ √n) and "large" (in (√n, (2-ε)√n])
2. **No shared pairs**: Each small prime connects to a **unique pair** of large primes
3. **Product constraint**: All products pq must be ≤ n

This is essentially a **Latin rectangle constraint** on the bipartite adjacency matrix.

### Why Greedy Fails
Greedy approaches tend to:
- Favor edges with primes that have many valid partners
- Create clusters where multiple small primes share the same large partners
- Break the "uniqueness" property needed for adversarial strength

### Correct Approach
1. For small t, use brute force to find valid 2-regular bipartite matchings
2. For large t, use constraint satisfaction or combinatorial search
3. Verify adversarial property by checking f computation

---

## Current Status

### What We Know
1. **Definition confirmed**: f(k,n) = min r such that ∀A, ∃r primes covering >r elements
2. **Upper bound proven**: f ≤ 2π(√n) + 1
3. **Manual n=100**: f = 9 = upper bound, gap = -1

### What Remains Unknown
1. Whether f = upper bound for all n (would imply gap ≈ -1, Answer: NO)
2. Whether f = lower bound (t+1) for all n (would imply gap → ∞, Answer: YES)
3. Correct automated construction for n > 100

### The Challenge
Building the correct adversarial construction for large n requires solving a combinatorial optimization problem (2-regular bipartite matching with uniqueness constraint) that our greedy algorithms fail to solve.

---

## Recommendations for Future Work

1. **Implement proper constraint solver** for 2-regular bipartite matching
2. **Verify construction adversarially** by checking that small prime sets don't cover too many elements
3. **Test at multiple n values** before drawing conclusions
4. **Separate concerns**: f computation vs. construction quality

---

## References

- CRITICAL_FLAW.md - Documentation of the proof error
- debug_comparison.py - Comparison of manual vs automated construction
- adversarial_graph.py - Attempt at proper adversarial construction
