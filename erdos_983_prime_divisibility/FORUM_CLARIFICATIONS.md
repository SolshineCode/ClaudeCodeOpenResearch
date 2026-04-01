# Forum Clarifications: Erdős Problem #983

## Date: January 2026

## Summary

Following computational investigation and GitHub issue #216 on teorth/erdosproblems, clarifications were obtained from the erdosproblems.com forum regarding the correct definition of f(k,n).

## Key Clarifications

### 1. "Strictly More Than r" (Woett, Oct 2025)

**Original problem statement error:** "at least r many a ∈ A"

**Correct definition:** "strictly more than r elements a ∈ A"

From Woett's comment:
> In the referenced paper by Erdős they require that there are **strictly more than r** elements a ∈ A that are only divisible by r primes, as opposed to 'at least r many a ∈ A'.

**Why this matters:**
- With "at least r": r=1 works whenever A contains any prime (1 prime covers 1 element ≥ 1)
- With "strictly more than r": r=1 requires covering >1 elements, preventing degeneracy
- This is why k must be larger than π(n) — with the correct definition, f(k,n) is undefined for sets containing only primes

### 2. Quantifier Order Confirmed (Tao, Jan 2026)

**Confirmed:** The quantifier order on erdosproblems.com is correct.

From Tao's comment:
> The reference is [Er70b, p. 138]. I think the quantifier order is as stated (the primes depend on the set A), this can be seen from context by looking at the various proofs of partial results in [Er70b].

**Definition structure:**
```
f(k,n) = min r such that:
  FOR ANY A ⊆ {1,...,n} with |A| = k,
  THERE EXIST primes p₁,...,pᵣ such that
  STRICTLY MORE THAN r elements a ∈ A
  have all prime divisors in {p₁,...,pᵣ}
```

This IS an adversarial/worst-case problem: the set A is chosen first (by an adversary), then we must find covering primes.

## Woett's Lower Bound Construction

Woett provided the explicit construction from [Er70b]:

Let p₁ < p₂ < ... < pₜ be primes ≤ (2-ε)√n.

**Set A₀:** t pairs of products pᵢpⱼ < n where each pᵢ (i ≤ t) appears in exactly 2 products.

**Full set A** (with |A| = π(n)+1):
```
A := A₀ ∪ {2pₜ₊₁, 3pₜ₊₁} ∪ ⋃_{i=t+2}^{π(n)} {pᵢ}
```

For this set: r = t+1, giving lower bound f(π(n)+1, n) > t = π((2-ε)√n).

Combined with upper bound f(π(n)+1, n) ≤ 2π(√n) + 1, this yields:
```
f(k,n) = (4 + o(1)) · √n / log n  for π(n) < k < (3/2 + o(1)) · n/log n
```

## Impact on Previous Work

Our computational testing used the INCORRECT "at least r" definition, which explains why we found f ≈ 3-4 (constant) instead of f ≈ 2π(√n).

**Previous results:** Correctly computed f for the wrong function
**Going forward:** Must re-implement with "strictly more than r" condition

## References

- [Er70b] P. Erdős, "Some applications of graph theory to number theory" (1969), p. 138
- GitHub Issue: https://github.com/teorth/erdosproblems/issues/216
- Forum Thread: https://www.erdosproblems.com/forum/thread/983
- Woett's comment: 10:10 on 08 Oct 2025
- Tao's comment: January 2026

## Acknowledgments

- Woett: For the critical "strictly more than r" correction and detailed lower bound construction
- Terence Tao: For confirming quantifier order and providing the exact reference
- Harshit057: For initial discussion on GitHub issue #216
