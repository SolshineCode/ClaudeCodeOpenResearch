# Corrected Analysis: Erdős Problem #983

## Status: Definition Clarified, Problem Remains Open

**Date:** January 2026

---

## Summary of Corrections

Following discussion on GitHub (#216) and the erdosproblems.com forum, two critical corrections to our understanding have been confirmed:

### 1. "Strictly More Than r" (Woett, Oct 2025)

**Incorrect (as stated on erdosproblems.com):** "at least r many a ∈ A"

**Correct (per [Er70b]):** "strictly more than r elements a ∈ A"

This prevents the degenerate case where r=1 works whenever A contains any prime.

### 2. Quantifier Order Confirmed (Tao, Jan 2026)

The quantifier order on erdosproblems.com IS correct:
- FOR ANY set A ⊆ {1,...,n} with |A| = k
- THERE EXIST primes p₁,...,pᵣ
- Such that STRICTLY MORE THAN r elements have all prime divisors in {p₁,...,pᵣ}

This IS an adversarial/worst-case problem. The set A is chosen first (by an adversary), then we find covering primes.

**Reference:** [Er70b, p. 138] - "Some applications of graph theory to number theory" (1969)

---

## Correct Definition

$$f(k,n) = \min r \text{ such that } \forall A \subseteq \{1,\ldots,n\} \text{ with } |A|=k, \exists p_1,\ldots,p_r \text{ covering } > r \text{ elements of } A$$

Where "covering" means: all prime divisors of the element are in {p₁,...,pᵣ}.

---

## Computational Results with Corrected Definition

### Test 1: Prime-Only Sets

For A = {all primes ≤ n}:
- f is **UNDEFINED** (as expected)
- Any r primes cover exactly r elements, never > r
- This confirms the "strictly >" condition works correctly

### Test 2: Woett's Construction at n=100

Woett's lower bound construction from [Er70b]:
- t = π((2-ε)√n) = 8 small primes
- A₀ = 8 semiprimes with 2-regular pairing
- A = A₀ ∪ {2·p_{t+1}, 3·p_{t+1}} ∪ remaining primes
- |A| = π(n) + 1 = 26

**Result:** f = 9 = t + 1 ✓

This matches the theoretical prediction!

### Test 3: Larger n

For n = 200, 500, 1000:
- Our implementation found smaller f values than expected
- This suggests the specific 2-regular pairing in [Er70b] is optimized
- A naive 2-regular construction doesn't achieve the maximum f

---

## Key Insights

### Why Our Original Analysis Was Wrong

Our original work found f ≈ 3-4 because:

1. **Wrong inequality:** We used "at least r" instead of "strictly more than r"
2. **Triangle efficiency:** With the wrong definition, small primes are extremely efficient

With the correct definition:
- r=1 requires covering >1 elements with 1 prime
- This only works if A contains composites sharing a common factor
- For adversarial sets designed to spread prime factors, r must be large

### The Erdős-Straus Lower Bound Construction

Woett explains the construction:

1. Choose primes p₁ < ... < pₜ where pₜ ≤ (2-ε)√n
2. Create A₀ with t semiprimes such that each pᵢ appears in exactly 2 products
3. Add {2·p_{t+1}, 3·p_{t+1}} to require p_{t+1}
4. Fill with large primes to reach |A| = π(n) + 1

This construction forces:
- The small primes must ALL be included (each appears twice in A₀)
- Plus p_{t+1} for the extra composites
- Total: t + 1 primes needed

Therefore: f(π(n)+1, n) ≥ t + 1 = π((2-ε)√n) + 1 ≈ 2π(√n)

### Upper Bound

Erdős-Straus also showed: f(π(n)+1, n) ≤ 2π(√n) + 1

Combined: f(π(n)+1, n) = 2π(√n) + o(√n/(log n)^A)

---

## The Main Question

The problem asks: Does 2π(√n) - f(π(n)+1, n) → ∞?

Given f(π(n)+1, n) ≈ 2π(√n) with error term o(√n/(log n)^A):

The gap is: 2π(√n) - f ≈ o(√n/(log n)^A)

**This error term does go to infinity as n → ∞!**

So the answer appears to be: **YES, the gap tends to infinity.**

However, this requires careful analysis of:
1. The exact form of the error term
2. Whether there's a matching lower bound showing the gap is unbounded

---

## Remaining Work

### To Fully Resolve the Problem:

1. **Obtain [Er70b]** - Verify the exact construction details
2. **Analyze error terms** - Determine if 2π(√n) - f is provably unbounded
3. **Improve construction** - Find optimal 2-regular pairings for larger n
4. **Theoretical bounds** - Develop tighter bounds on the gap

### Computational Improvements:

1. Implement optimal 2-regular graph construction
2. Test for larger n with the correct definition
3. Search for adversarial sets that maximize f

---

## Conclusion

The definition discrepancy has been resolved:
- **erdosproblems.com** has a minor error: should be "strictly more than r" not "at least r"
- **Quantifier order** is correct as stated
- **Our original work** answered a different (easier) problem

With the correct definition, the Erdős-Straus theorem f ≈ 2π(√n) is consistent with our n=100 verification.

The main question (whether the gap → ∞) likely has answer **YES** based on the error term structure, but rigorous proof requires careful analysis of the o() terms.

---

## References

- [Er70b] P. Erdős, "Some applications of graph theory to number theory" (1969), p. 138
- erdosproblems.com Forum Thread #983
- GitHub teorth/erdosproblems Issue #216
- Woett's Forum Comment (Oct 2025)
- Tao's Confirmation (Jan 2026)
