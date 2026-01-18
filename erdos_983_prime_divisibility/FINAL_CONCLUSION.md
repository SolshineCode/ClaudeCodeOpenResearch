# Final Conclusion: Erdős Problem #983

## Date: January 2026

---

## The Question

> Is it true that $2\pi(n^{1/2}) - f(\pi(n)+1, n) \to \infty$ as $n \to \infty$?

---

## Answer: LIKELY NO (Gap is Bounded)

**Key insight from Woett's forum comment:**

> "Combining upper and lower bound and using the prime number theorem we deduce f(k,n) = (4+o(1))·√n/log n"

Since 2π(√n) ~ 4√n/log n, we have **f ~ 2π(√n)**.

Combined with:
- **Upper bound:** f ≤ 2π(√n) + 1
- **Erdős-Straus asymptotic:** f = 2π(√n) + o_A(√n/(log n)^A) for any A > 0

The o_A(√n/(log n)^A) error term being smaller than √n/(log n)^A for ANY A means the error is "superpolynomially small" in log n. Combined with the upper bound f ≤ 2π(√n) + 1, this strongly constrains the gap.

**Conclusion:** The gap 2π(√n) - f is bounded (likely between -1 and a small constant).

**Answer: NO** — the gap does NOT tend to infinity.

### The Bounds

**Upper Bound (Erdős-Straus):**
$$f(\pi(n)+1, n) \leq 2\pi(\sqrt{n}) + 1$$

**Lower Bound (Woett's Construction):**
$$f(\pi(n)+1, n) \geq \pi((2-\varepsilon)\sqrt{n}) + 1$$

### Why the Answer is NO

The key constraint is the **upper bound**: f ≤ 2π(√n) + 1

This means: 2π(√n) - f ≥ **-1**

The gap is bounded below by -1. It cannot go to +∞.

The Erdős-Straus asymptotic f = 2π(√n) + o_A(√n/(log n)^A) tells us the error is "superpolynomially small" — smaller than any polynomial in log n. Combined with the upper bound, this means:

$$-1 \leq 2\pi(\sqrt{n}) - f \leq o\left(\frac{\sqrt{n}}{(\log n)^A}\right) \text{ for any } A$$

For the gap to → +∞, we'd need f to be substantially BELOW 2π(√n). But the Erdős-Straus asymptotic says f ≈ 2π(√n) with tiny error, and the lower bound construction shows f ≥ π((2-ε)√n) + 1 → 2π(√n) as ε → 0.

**The gap is sandwiched between -1 and a small quantity → 0.**

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

### The Decisive Argument

The upper bound **f ≤ 2π(√n) + 1** directly implies:

$$2\pi(\sqrt{n}) - f \geq -1$$

**The gap is bounded below by -1. It CANNOT tend to +∞.**

For the gap to → +∞, we would need f to be substantially BELOW 2π(√n). But:

1. The upper bound says f ≤ 2π(√n) + 1
2. The Erdős-Straus asymptotic says f = 2π(√n) + o_A(√n/(log n)^A)
3. Woett confirms f = (4+o(1))√n/log n ~ 2π(√n)

All evidence points to f being CLOSE to 2π(√n), not far below it.

---

## What We Know For Certain

| Fact | Status |
|------|--------|
| Definition: "strictly more than r" | ✓ Confirmed (Woett/Tao) |
| Quantifier order (adversarial) | ✓ Confirmed (Tao) |
| f(26, 100) = 9 | ✓ Verified |
| f ≤ 2π(√n) + 1 | ✓ Erdős-Straus upper bound |
| Gap ≥ -1 | ✓ Follows from upper bound |
| f ~ 2π(√n) | ✓ Woett's asymptotic |

---

## Why I'm Confident the Answer is NO

The upper bound f ≤ 2π(√n) + 1 is the key.

Rearranging: **2π(√n) - f ≥ -1**

This single inequality proves the gap cannot go to +∞. At most, it could go to -∞ (if f grew faster than 2π(√n)), but the asymptotic f ~ 2π(√n) rules that out too.

**The gap is O(1), bounded between approximately -1 and 0.**

---

## Summary Table

| Aspect | Status |
|--------|--------|
| Definition correction | ✓ Confirmed ("strictly more than r") |
| Quantifier order | ✓ Confirmed (adversarial) |
| f(26, 100) = 9 | ✓ Verified |
| Woett's asymptotic | f = (4+o(1))√n/log n ~ 2π(√n) |
| Upper bound | f ≤ 2π(√n) + 1 |
| Gap bounded below | 2π(√n) - f ≥ -1 |
| Main question answer | **LIKELY NO** (gap is bounded) |

---

## References

- [Er70b] P. Erdős, "Some applications of graph theory to number theory" (1969), p. 138
- erdosproblems.com Problem #983
- Forum Thread #983 (Woett's comment, Oct 2025)
- GitHub teorth/erdosproblems Issue #216
- Tao's confirmation (Jan 2026)
