# Coverage Definition Analysis for Erdős Problem #983

## Discovery Date: January 2026

This document records a critical discovery about the coverage definition in Erdős Problem #983.

---

## The Bug

The original `compute_coverage` function in `erdos983_lib.py` used:

```python
return sum(1 for e in elements if factor_cache[e].issubset(prime_set))
```

This checks if ALL prime factors of an element are in the covering set.

**CORRECT definition**: An element is covered if ANY of its prime factors is in the set:

```python
return sum(1 for e in elements if factor_cache[e] & prime_set)  # intersection
```

This fix dramatically changes the results.

---

## The Element 1 Problem

### Observation

Element 1 has no prime factors. Therefore:
- 1 is **never** covered by any set of primes
- If A contains 1, it cannot be fully covered

### Critical Adversarial Set

For n = 100, consider:
```
A = {1, 4, 9, 25, 49, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
|A| = 26 = π(100) + 1
```

Analysis:
- Element 1: **Never covered**
- 4 = 2²: Covered only by prime 2
- 9 = 3²: Covered only by prime 3
- 25 = 5²: Covered only by prime 5
- 49 = 7²: Covered only by prime 7
- Each large prime p: Covered only by prime p

**Result**: Any r primes cover exactly r elements (excluding 1, which is never covered).

We need coverage > r, but we only achieve = r. Therefore f is **undefined** (or infinite) for this A!

---

## Resolution

There are several possible interpretations:

### 1. Exclude 1 from Consideration

The problem may implicitly mean A ⊆ {2, ..., n}.

If we exclude 1, then A must contain at least one:
- Small prime AND a multiple, or
- Two multiples of the same small prime

Either way, some small prime covers ≥ 2 elements, giving f = 1.

### 2. Treat 1 as Vacuously Covered

Consider 1 as "covered by the empty product" (vacuously true).

With this convention, the adversarial set above has:
- 1 contributes 1 to coverage for any r ≥ 0
- r primes cover 1 + r elements
- 1 + r > r is always true
- f = 0 (or undefined if we require r ≥ 1)

### 3. Accept f = ∞ for Certain A

If the problem allows f = ∞ for some A, then:
- f(π(n)+1, n) = ∞ whenever A contains 1 plus carefully chosen elements
- The question "does gap → ∞?" becomes trivially YES

---

## Main Result (Excluding Element 1)

**Theorem**: For any n ≥ 4 and A ⊆ {2, ..., n} with |A| = π(n) + 1:
- f(A) = 1

**Proof**:
1. A must contain at least one composite (since π(n) < n - 1 for n ≥ 4)
2. Any composite c ≤ n has a prime factor p ≤ √n
3. If A contains:
   - Both p and a multiple of p: p covers ≥ 2 elements
   - Two distinct multiples of p: p covers ≥ 2 elements
4. Since A has π(n) + 1 elements and there are only π(n) primes ≤ n,
   A must contain at least one composite
5. That composite shares a prime factor with some other element of A
6. Therefore 1 prime covers ≥ 2 > 1 elements
7. f = 1 □

**Corollary**: Gap = 2π(√n) - f = 2π(√n) - 1 → ∞ as n → ∞

---

## Summary

| Scenario | f | Gap → ∞? |
|----------|---|----------|
| A can contain 1, 1 not covered | ∞ for some A | YES (trivially) |
| A excludes 1 | 1 | YES |
| 1 counted as covered | 1 | YES |

**Conclusion**: Under any reasonable interpretation, the answer to Erdős Problem #983 is **YES**.

---

## Impact on Previous Analysis

The Latin rectangle construction analysis was still valuable for understanding the problem structure, but the key insight is simpler:

1. A must contain composites (pigeonhole)
2. Composites share prime factors
3. Some prime covers ≥ 2 elements
4. f = 1

The elaborate bipartite matching wasn't necessary for the final answer, but it helped us understand why f is so small.
