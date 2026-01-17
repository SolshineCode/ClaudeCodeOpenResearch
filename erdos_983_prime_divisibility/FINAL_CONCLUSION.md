# Final Conclusion: Erdős Problem #983

## Date: January 2026

---

## The Question

> Is it true that $2\pi(n^{1/2}) - f(\pi(n)+1, n) \to \infty$ as $n \to \infty$?

---

## Answer: UNCERTAIN (Requires More Analysis)

**CORRECTION:** My earlier claim that "the gap is O(1)" was based on a calculation error.

### The Actual Bounds

**Upper Bound (Erdős-Straus):**
$$f(\pi(n)+1, n) \leq 2\pi(\sqrt{n}) + 1$$

**Lower Bound (Woett's Construction):**
$$f(\pi(n)+1, n) \geq \pi((2-\varepsilon)\sqrt{n}) + 1$$

### Gap Between Bounds

Using the Prime Number Theorem:
- $2\pi(\sqrt{n}) \sim \frac{4\sqrt{n}}{\ln n}$
- $\pi((2-\varepsilon)\sqrt{n}) \sim \frac{(4-2\varepsilon)\sqrt{n}}{\ln n}$

**Gap between bounds:** $\frac{2\varepsilon\sqrt{n}}{\ln n} \to \infty$ for any fixed $\varepsilon > 0$

So the bounds are **NOT tight** for large n. The gap between upper and lower bounds grows!

---

## What We Actually Know

### Verified at n = 100

| Quantity | Value |
|----------|-------|
| Upper bound: 2π(√n) + 1 | 9 |
| Lower bound: π(19) + 1 | 9 |
| Computed f | 9 |
| Gap = 2π(√n) - f | 8 - 9 = -1 |

At n=100, the bounds **happen to coincide** (both equal 9). This is a small-n coincidence, not a general property.

### The Erdős-Straus Asymptotic

The theorem states:
$$f(\pi(n)+1, n) = 2\pi(n^{1/2}) + o_A\left(\frac{n^{1/2}}{(\log n)^A}\right)$$

This says f is very close to 2π(√n), with error smaller than √n/(log n)^A for any A.

**Interpretation:**
- If f ≈ 2π(√n) + O(1), then gap ≈ O(1), answer is **NO**
- If f ≈ 2π(√n) - ω(1), then gap → +∞, answer is **YES**

The Erdős-Straus asymptotic suggests f tracks 2π(√n) closely, but doesn't specify the sign or exact magnitude of the error.

---

## Honest Assessment

### What is SOLID:

1. ✓ Definition correction: "strictly more than r" (Woett, confirmed by reference to [Er70b])
2. ✓ Quantifier order: adversarial formulation is correct (Tao)
3. ✓ At n=100: f = 9 = upper bound = lower bound
4. ✓ Upper bound: f ≤ 2π(√n) + 1

### What is UNCERTAIN:

1. ✗ Whether f tracks the upper or lower bound for large n
2. ✗ The sign of (f - 2π(√n)) for large n
3. ✗ Whether the gap is O(1), o(1), or ω(1)
4. ✗ My automated construction failed for n > 100

### My Earlier Error:

I incorrectly claimed the lower bound was ≈ 2π(√n) - O(1). This is wrong because:
- Lower bound = π((2-ε)√n) + 1 ≈ (4-2ε)√n/ln n
- This is NOT 2π(√n) - O(1), it's 2π(√n) - 2ε√n/ln n
- The gap 2ε√n/ln n grows with n for fixed ε

---

## Possible Answers to the Main Question

### If f ≈ 2π(√n) + O(1) (tracks upper bound):

Gap = 2π(√n) - f ≈ -O(1)

**Answer: NO** (gap is bounded, possibly negative)

### If f is between bounds:

Gap could be anywhere from -1 to 2ε√n/ln n

**Answer: DEPENDS** on where exactly f lies

### If f ≈ lower bound:

Gap ≈ 2ε√n/ln n → ∞

**Answer: YES** (gap tends to infinity)

---

## Recommendations for Resolution

1. **Obtain [Er70b]** and study the proof to understand the error term structure

2. **Compute f for larger n** with correct Woett construction:
   - n = 1000, 5000, 10000
   - Check if f tracks upper bound or lies in between

3. **Determine the sign** of f - 2π(√n) from the Erdős-Straus proof

4. **Analyze asymptotically** whether the error term is bounded or growing

---

## Current Best Guess

Based on:
- The Erdős-Straus asymptotic suggesting f ≈ 2π(√n)
- The n=100 data point showing f = upper bound
- The upper bound being simpler (2π(√n) + 1 vs complex lower bound)

**Tentative guess: NO** - the gap is likely O(1), not → ∞

But this is a **guess**, not a proven result. The uncertainty is significant.

---

## Summary Table

| Aspect | Status |
|--------|--------|
| Definition correction | ✓ Confirmed |
| Quantifier order | ✓ Confirmed |
| f(26, 100) = 9 | ✓ Verified |
| Gap = O(1) claim | ✗ UNCERTAIN (earlier error corrected) |
| Main question answer | **UNKNOWN** (needs more work) |

---

## References

- [Er70b] P. Erdős, "Some applications of graph theory to number theory" (1969), p. 138
- erdosproblems.com Problem #983
- Forum Thread #983 (Woett's comment, Oct 2025)
- GitHub teorth/erdosproblems Issue #216
- Tao's confirmation (Jan 2026)
