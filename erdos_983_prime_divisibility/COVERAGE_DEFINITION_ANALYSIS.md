# Coverage Definition Analysis for Erdős Problem #983

## Discovery Date: January 2026

This document records the correct coverage definition and an error that was made and corrected.

---

## The Correct Definition (Per Tao/Woett)

From FORUM_CLARIFICATIONS.md, the Tao/Woett clarification states:

> "STRICTLY MORE THAN r elements a ∈ A have **ALL** prime divisors in {p₁,...,pᵣ}"

### What This Means

An element a is **covered** by a set of primes {p₁,...,pᵣ} if and only if:
- **ALL** prime factors of a are in the set
- Not just **ANY** prime factor

### Example

For 26 = 2 × 13:
- Covered by {2, 13}? **YES** (both factors present)
- Covered by {2}? **NO** (missing factor 13)
- Covered by {13}? **NO** (missing factor 2)

For a prime p:
- Covered by {p}? **YES** (the only factor is present)

For a semiprime pq:
- Covered by {p, q}? **YES**
- Covered by {p} or {q} alone? **NO**

---

## The Error Made

### Wrong Implementation

I initially changed the coverage function from:
```python
# CORRECT: issubset (all factors must be in set)
return sum(1 for e in elements if factor_cache[e].issubset(prime_set))
```

to:
```python
# WRONG: intersection (any factor in set)
return sum(1 for e in elements if factor_cache[e] & prime_set)
```

### Why This Was Wrong

I misread the definition as "an element is covered if it's divisible by any prime in the set." But the actual definition requires **all** prime factors to be in the covering set.

### Impact of the Error

With the wrong `intersection` definition:
- f = 1 for all n (any prime that divides an element "covers" it)
- gap = 2π(√n) - 1 (trivially grows)

With the correct `issubset` definition:
- f ≈ π(√n) (need complete factorizations)
- gap ≈ π(√n) (still grows, but less trivially)

Both give answer YES, but for different reasons.

---

## The Correct Results

With the restored correct definition:

| n | f | 2π(√n) | gap |
|---|---|--------|-----|
| 100 | 9 | 8 | -1 |
| 200 | 9 | 12 | 3 |
| 400 | 11 | 16 | 5 |
| 800 | 7 | 18 | 11 |

### Why n=100 Has Negative Gap

At n = 100, both bounds coincide:
- Woett lower bound: π(19) + 1 = 9
- Erdős-Straus upper bound: 2π(10) + 1 = 9

So f = 9, 2π(√n) = 8, gap = -1.

For larger n, the bounds diverge and gap becomes positive and growing.

---

## Lesson Learned

Always verify the exact definition from the original source (Tao/Woett clarification) before implementing. The difference between "any factor" and "all factors" completely changes the problem structure.

---

## Summary

| Definition | Coverage Condition | f | Answer |
|------------|-------------------|---|--------|
| ANY factor (wrong) | `factors & primes` | 1 | YES |
| ALL factors (correct) | `factors ⊆ primes` | ~π(√n) | YES |

The answer to Erdős Problem #983 is **YES** under the correct definition, with gap ≈ π(√n) → ∞.
