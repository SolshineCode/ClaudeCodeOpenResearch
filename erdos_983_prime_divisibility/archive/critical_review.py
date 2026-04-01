#!/usr/bin/env python3
"""
Critical review of the analysis - testing potential flaws.

Key question: Am I finding the TRUE hardest sets, or missing something?
"""

from utils import sieve_of_eratosthenes, prime_factors
from itertools import combinations
import math

def coverage_count(elements_factors, prime_set):
    """Count elements covered by prime_set."""
    count = 0
    for factors in elements_factors:
        if not factors or factors.issubset(prime_set):
            count += 1
    return count

def find_f_exact(elements_factors, max_r=20):
    """Find exact f by exhaustive search for small r."""
    all_primes = set()
    for f in elements_factors:
        all_primes.update(f)
    all_primes = sorted(all_primes)

    for r in range(1, min(max_r + 1, len(all_primes) + 1)):
        best_cov = 0
        # Try all combinations of r primes
        for prime_combo in combinations(all_primes, r):
            cov = coverage_count(elements_factors, set(prime_combo))
            best_cov = max(best_cov, cov)
            if cov >= r:
                break
        if best_cov >= r:
            return r, best_cov
    return -1, 0

def construct_rectangle_free_set(n, k, primes):
    """
    Attempt to construct a set avoiding 2x2 rectangles.

    A 2x2 rectangle is {s1*L1, s1*L2, s2*L1, s2*L2} all in the set.
    Avoiding these should make coverage harder.
    """
    sqrt_n = int(math.sqrt(n))
    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if p > sqrt_n]

    # Strategy: each small prime pairs with a DISJOINT set of large primes
    # This avoids rectangles

    selected = []
    selected_factors = []

    # Partition large primes among small primes
    large_idx = 0
    for s in small_primes:
        # Give this small prime some large primes
        count = 0
        while large_idx < len(large_primes) and len(selected) < k:
            L = large_primes[large_idx]
            if s * L <= n:
                selected.append(s * L)
                selected_factors.append({s, L})
                count += 1
            large_idx += 1
            # Limit per small prime to spread out
            if count >= k // len(small_primes) + 2:
                break

    return selected[:k], selected_factors[:k]

def test_rectangle_free():
    """Test if rectangle-free sets are harder."""
    print("=" * 70)
    print("CRITICAL TEST: RECTANGLE-FREE ADVERSARIAL SETS")
    print("=" * 70)
    print()
    print("Theory: If the adversary avoids 2x2 'rectangles' of semiprimes,")
    print("coverage might be much harder, potentially giving larger f.")
    print()

    for n in [100, 500, 1000]:
        print(f"\n{'='*60}")
        print(f"n = {n}")
        print(f"{'='*60}")

        primes = sieve_of_eratosthenes(n)
        sqrt_n = int(math.sqrt(n))
        pi_n = len(primes)
        pi_sqrt_n = len([p for p in primes if p <= sqrt_n])
        k = pi_n + 1

        print(f"k = π(n) + 1 = {k}")
        print(f"2π(√n) = {2 * pi_sqrt_n}")

        # Construct rectangle-free set
        values, factors = construct_rectangle_free_set(n, k, primes)

        if len(factors) < k:
            print(f"Warning: Only got {len(factors)} elements (need {k})")
            print("Cannot construct pure rectangle-free set - not enough mixed semiprimes")
            continue

        print(f"\nRectangle-free set constructed: {len(factors)} elements")
        print(f"Sample: {values[:10]}...")

        # Find f
        f_val, best_cov = find_f_exact(factors, max_r=15)
        print(f"\nf = {f_val} (coverage = {best_cov})")
        print(f"Gap = 2π(√n) - f = {2 * pi_sqrt_n - f_val}")

def test_specific_hard_construction():
    """
    Test: Can we construct a set where f > 4?

    For f > 4, we need: any 4 primes cover < 4 elements.
    """
    print("\n" + "=" * 70)
    print("CRITICAL TEST: CAN f BE LARGER THAN 4?")
    print("=" * 70)

    n = 1000
    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))
    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if p > sqrt_n]

    print(f"\nn = {n}")
    print(f"Small primes (≤{sqrt_n}): {len(small_primes)}")
    print(f"Large primes (>{sqrt_n}): {len(large_primes)}")

    # Try: each small prime pairs with exactly ONE large prime
    # This is a "matching" - no shared large primes
    selected = []
    factors_list = []

    for i, s in enumerate(small_primes):
        if i < len(large_primes):
            L = large_primes[i]
            if s * L <= n:
                selected.append(s * L)
                factors_list.append({s, L})

    print(f"\nMatching-based set: {len(selected)} elements")
    print(f"Each small prime pairs with exactly one large prime")

    if len(selected) > 0:
        # For this set, what's f?
        f_val, cov = find_f_exact(factors_list, max_r=15)
        print(f"\nf = {f_val}")

        # Analyze: with r primes, what's the max coverage?
        print("\nDetailed coverage analysis:")
        all_primes_in_set = set()
        for f in factors_list:
            all_primes_in_set.update(f)
        all_primes_list = sorted(all_primes_in_set)

        for r in range(1, min(10, len(all_primes_list))):
            best = 0
            for combo in combinations(all_primes_list, r):
                cov = coverage_count(factors_list, set(combo))
                best = max(best, cov)
            status = "✓" if best >= r else "✗"
            print(f"  r={r}: best coverage = {best}, need ≥{r} {status}")

def analyze_my_test_methodology():
    """Check if my test methodology could be flawed."""
    print("\n" + "=" * 70)
    print("METHODOLOGY CHECK")
    print("=" * 70)

    print("""
Potential flaws in my analysis:

1. GREEDY vs OPTIMAL: My coverage algorithm uses greedy search.
   Could there be sets where greedy fails but exhaustive search succeeds?

2. ADVERSARIAL SETS: Am I constructing the TRUE hardest sets?
   The Erdős-Straus paper likely has a specific adversarial construction.

3. ASYMPTOTIC vs FINITE: My tests go up to n=10,000.
   Maybe n=10,000 is still in a "non-asymptotic" regime?

4. DEFINITION MISMATCH: Am I interpreting f(k,n) correctly?
   The phrase "only divisible by primes from P" seems unambiguous,
   but maybe there's a subtlety I'm missing.

5. COUNTING ERROR: For large n, are there enough "hard" semiprimes?
   By Kővári–Sós–Turán, rectangle-free sets can have size O(n^{1.5}).
   For n=10^6, that's ~10^9 >> k ≈ 78,000.
   So rectangle-free constructions SHOULD be possible for large n.
""")

def test_counting_mixed_semiprimes():
    """Count how many mixed semiprimes exist."""
    print("\n" + "=" * 70)
    print("COUNTING MIXED SEMIPRIMES")
    print("=" * 70)

    for n in [100, 1000, 10000]:
        primes = sieve_of_eratosthenes(n)
        sqrt_n = int(math.sqrt(n))
        small = [p for p in primes if p <= sqrt_n]
        large = [p for p in primes if p > sqrt_n]

        k = len(primes) + 1

        # Count mixed semiprimes
        mixed = 0
        for s in small:
            for L in large:
                if s * L <= n:
                    mixed += 1

        print(f"\nn = {n}:")
        print(f"  k = π(n)+1 = {k}")
        print(f"  Small primes: {len(small)}")
        print(f"  Large primes: {len(large)}")
        print(f"  Mixed semiprimes (s*L ≤ n): {mixed}")
        print(f"  Ratio mixed/k: {mixed/k:.2f}")

        if mixed < k:
            print(f"  ⚠ NOT ENOUGH mixed semiprimes to fill k!")
        else:
            print(f"  ✓ Enough mixed semiprimes")

if __name__ == "__main__":
    test_counting_mixed_semiprimes()
    test_rectangle_free()
    test_specific_hard_construction()
    analyze_my_test_methodology()
