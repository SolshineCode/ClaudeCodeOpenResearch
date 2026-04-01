#!/usr/bin/env python3
"""
Test sets of semiprimes with LARGE prime factors.

Key insight: Semiprimes of form q*p where q ≤ √n and p > √n are hard because:
- They need BOTH q and p to be covered
- No small prime set alone covers any of them
"""

import math
from itertools import combinations
from typing import Set, List, Tuple

def sieve_of_eratosthenes(n: int) -> List[int]:
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

def prime_factors(n: int, primes: List[int]) -> Set[int]:
    if n <= 1:
        return set()
    factors = set()
    temp = n
    for p in primes:
        if p * p > temp:
            break
        if temp % p == 0:
            factors.add(p)
            while temp % p == 0:
                temp //= p
    if temp > 1:
        factors.add(temp)
    return factors

def coverage_count(elements_factors: List[Set[int]], prime_set: Set[int]) -> int:
    return sum(1 for f in elements_factors if f and f.issubset(prime_set))

def find_best_coverage_exhaustive(elements_factors: List[Set[int]], r: int, all_primes: List[int]) -> int:
    """Exhaustive search for best coverage with r primes."""
    if r >= len(all_primes):
        return len([f for f in elements_factors if f])

    max_cov = 0
    for combo in combinations(all_primes, r):
        cov = coverage_count(elements_factors, set(combo))
        max_cov = max(max_cov, cov)
    return max_cov

def find_f(elements_factors: List[Set[int]], all_primes: List[int], max_check: int = 30) -> int:
    """Find minimum r such that r primes cover >= r elements."""
    non_trivial = [f for f in elements_factors if f]

    for r in range(1, min(max_check, len(non_trivial)) + 1):
        if r <= 15 and len(all_primes) <= 30:
            max_cov = find_best_coverage_exhaustive(non_trivial, r, all_primes)
        else:
            # Greedy for larger cases
            chosen = set()
            relevant = set()
            for f in non_trivial:
                relevant |= f
            for _ in range(r):
                best_p = None
                best_cov = -1
                for p in relevant:
                    if p in chosen:
                        continue
                    cov = coverage_count(non_trivial, chosen | {p})
                    if cov > best_cov:
                        best_cov = cov
                        best_p = p
                if best_p:
                    chosen.add(best_p)
            max_cov = coverage_count(non_trivial, chosen)

        if max_cov >= r:
            return r

    return max_check

def construct_large_factor_set(n: int, k: int, primes: List[int]) -> Tuple[List[Set[int]], List[int]]:
    """
    Construct set of semiprimes q*p where q ≤ √n and p > √n.
    These are harder because they need BOTH a small and large prime to cover.
    """
    sqrt_n = int(math.sqrt(n))
    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if p > sqrt_n and p <= n]

    print(f"  Small primes (≤ √n = {sqrt_n}): {len(small_primes)}")
    print(f"  Large primes (> √n): {len(large_primes)}")

    # Generate semiprimes q*p where q ≤ √n, p > √n, and q*p ≤ n
    semiprimes = []
    for q in small_primes:
        for p in large_primes:
            if q * p <= n:
                semiprimes.append((q * p, {q, p}))

    print(f"  Large-factor semiprimes available: {len(semiprimes)}")

    if len(semiprimes) < k:
        print(f"  Warning: Only {len(semiprimes)} semiprimes, need {k}")
        # Add more elements if needed
        for m in range(2, n + 1):
            factors = prime_factors(m, primes)
            if len(factors) >= 2 and (m, factors) not in [(x, y) for x, y in semiprimes]:
                semiprimes.append((m, factors))
                if len(semiprimes) >= k:
                    break

    # Select k elements
    # Strategy: prioritize semiprimes with the LARGEST large prime factor
    semiprimes.sort(key=lambda x: max(x[1]), reverse=True)

    selected = semiprimes[:k]
    values = [m for m, _ in selected]
    factors = [f for _, f in selected]

    return factors, values

def analyze_large_factor_set(n: int):
    """Analyze a set of large-factor semiprimes."""
    print(f"\n{'='*70}")
    print(f"LARGE-FACTOR SEMIPRIME TEST: n = {n}")
    print(f"{'='*70}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))
    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    k = pi_n + 1
    two_pi_sqrt = 2 * pi_sqrt_n

    print(f"π(n) = {pi_n}, π(√n) = {pi_sqrt_n}")
    print(f"k = π(n) + 1 = {k}")
    print(f"2π(√n) = {two_pi_sqrt}")

    print("\n--- Constructing large-factor semiprime set ---")
    elements_factors, values = construct_large_factor_set(n, k, primes)

    if len(elements_factors) < k:
        print(f"  Could only construct {len(elements_factors)} elements")
        return None, two_pi_sqrt

    # Analyze the set
    all_primes_used = set()
    for f in elements_factors:
        all_primes_used |= f
    all_primes_list = sorted(all_primes_used)

    small_primes_in_set = [p for p in all_primes_list if p <= sqrt_n]
    large_primes_in_set = [p for p in all_primes_list if p > sqrt_n]

    print(f"\n  Set size: {len(elements_factors)}")
    print(f"  Sample values: {values[:10]}...")
    print(f"  Total distinct primes: {len(all_primes_list)}")
    print(f"    Small primes used: {len(small_primes_in_set)}")
    print(f"    Large primes used: {len(large_primes_in_set)}")

    # Coverage analysis
    print("\n  Coverage analysis:")

    # Test with only small primes
    small_cov = coverage_count(elements_factors, set(small_primes_in_set))
    print(f"  Using ALL {len(small_primes_in_set)} small primes alone: coverage = {small_cov}")

    # Test with various r
    for r in range(1, min(30, len(all_primes_list)) + 1):
        if r <= 15:
            max_cov = find_best_coverage_exhaustive(elements_factors, r, all_primes_list)
        else:
            # Greedy approximation
            chosen = set()
            for _ in range(r):
                best_p = None
                best_c = -1
                for p in all_primes_list:
                    if p in chosen:
                        continue
                    c = coverage_count(elements_factors, chosen | {p})
                    if c > best_c:
                        best_c = c
                        best_p = p
                if best_p:
                    chosen.add(best_p)
            max_cov = coverage_count(elements_factors, chosen)

        status = "✓" if max_cov >= r else "✗"
        print(f"    r = {r:2d}: max coverage = {max_cov:3d}, need ≥ {r:2d} {status}")
        if max_cov >= r:
            break

    f_val = find_f(elements_factors, all_primes_list)
    print(f"\n  f for this set: {f_val}")
    print(f"  Gap = 2π(√n) - f = {two_pi_sqrt} - {f_val} = {two_pi_sqrt - f_val}")

    return f_val, two_pi_sqrt

def test_bipartite_structure(n: int):
    """
    Analyze the bipartite structure: small primes vs large primes.
    For semiprimes q*p (q small, p large), coverage requires BOTH.
    """
    print(f"\n{'='*70}")
    print(f"BIPARTITE COVERAGE ANALYSIS: n = {n}")
    print(f"{'='*70}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))
    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if sqrt_n < p <= n]

    k = pi_n + 1

    print(f"π(n) = {pi_n}, π(√n) = {pi_sqrt_n}")
    print(f"Small primes (≤ {sqrt_n}): {small_primes}")
    print(f"Large primes count: {len(large_primes)}")

    # Build the semiprime matrix
    # Entry (q, p) = 1 if q*p ≤ n
    print("\n  Building semiprime coverage matrix...")

    coverage_matrix = {}
    for q in small_primes:
        for p in large_primes:
            if q * p <= n:
                coverage_matrix[(q, p)] = q * p

    print(f"  Total large-factor semiprimes: {len(coverage_matrix)}")

    # Analysis: if we pick s small primes and t large primes,
    # we cover the semiprimes at the intersection
    print("\n  Coverage by (s small, t large) prime choices:")
    header = "s\\t"
    print(f"  {header:<4}", end="")
    for t in range(1, min(10, len(large_primes)) + 1):
        print(f"{t:<5}", end="")
    print()

    for s in range(1, len(small_primes) + 1):
        print(f"  {s:<4}", end="")
        # Choose first s small primes and first t large primes
        chosen_small = small_primes[:s]
        for t in range(1, min(10, len(large_primes)) + 1):
            chosen_large = large_primes[:t]
            cov = sum(1 for (q, p) in coverage_matrix.keys()
                     if q in chosen_small and p in chosen_large)
            print(f"{cov:<5}", end="")
        print()

    # For r = s + t primes, we want coverage >= r
    # This means s*t >= s + t (approximately)
    # s*t - s - t >= 0
    # (s-1)(t-1) >= 1
    # So we need s >= 2 and t >= 2, OR one of them much larger

    print("\n  For r = s + t primes to cover ≥ r elements:")
    print("  Need (s-1)(t-1) ≥ 1 approximately, so s ≥ 2 AND t ≥ 2")
    print(f"  Minimum r = 2 + 2 = 4 in this bipartite case")
    print(f"  But optimal might use unequal s, t...")

    # Find optimal r
    best_r = float('inf')
    for s in range(1, len(small_primes) + 1):
        for t in range(1, min(50, len(large_primes)) + 1):
            r = s + t
            if r >= best_r:
                continue
            chosen_small = small_primes[:s]
            chosen_large = large_primes[:t]
            cov = sum(1 for (q, p) in coverage_matrix.keys()
                     if q in chosen_small and p in chosen_large)
            if cov >= r:
                best_r = r
                print(f"  Found: s={s}, t={t}, r={r}, coverage={cov}")

    print(f"\n  Minimum r for large-factor semiprimes: {best_r}")
    print(f"  2π(√n) = {2 * pi_sqrt_n}")
    print(f"  Gap = {2 * pi_sqrt_n - best_r}")

def main():
    print("="*70)
    print("TESTING LARGE-FACTOR SEMIPRIMES FOR ERDŐS PROBLEM #983")
    print("="*70)
    print("\nKey insight: Semiprimes q*p where q ≤ √n, p > √n require")
    print("BOTH a small AND large prime to cover. These should be hardest.\n")

    # Small n for detailed analysis
    test_bipartite_structure(100)

    # Larger n for trend analysis
    results = []
    for n in [100, 200, 500, 1000]:
        f_val, two_pi_sqrt = analyze_large_factor_set(n)
        if f_val:
            results.append((n, two_pi_sqrt, f_val, two_pi_sqrt - f_val))

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"{'n':<8} {'2π(√n)':<10} {'f':<10} {'Gap':<10}")
    print("-" * 40)
    for n, two_pi, f, gap in results:
        print(f"{n:<8} {two_pi:<10} {f:<10} {gap:<10}")

    if results:
        gaps = [g for _, _, _, g in results]
        print(f"\nGap range: [{min(gaps)}, {max(gaps)}]")

if __name__ == "__main__":
    main()
