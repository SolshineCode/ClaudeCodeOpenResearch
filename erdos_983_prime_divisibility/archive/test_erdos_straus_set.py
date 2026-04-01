#!/usr/bin/env python3
"""
Test the Erdős-Straus adversarial set construction:
A = {all primes p > √n} ∪ {elements from {1,...,√n}}

This set has:
- π(n) - π(√n) large primes (each requires its own prime to cover)
- π(√n) + 1 small elements (can be covered by small primes)
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
    """Count elements covered (all factors in prime_set, or element is 1)."""
    count = 0
    for f in elements_factors:
        if not f:  # Empty factor set = element is 1
            count += 1
        elif f.issubset(prime_set):
            count += 1
    return count

def find_best_coverage(elements_factors: List[Set[int]], r: int, all_primes: List[int]) -> int:
    """Find maximum coverage with r primes."""
    if r >= len(all_primes):
        return len(elements_factors)

    # For small cases, use exhaustive search
    if r <= 12 and len(all_primes) <= 40:
        max_cov = 0
        for combo in combinations(all_primes, r):
            cov = coverage_count(elements_factors, set(combo))
            max_cov = max(max_cov, cov)
        return max_cov
    else:
        # Greedy
        chosen = set()
        for _ in range(r):
            best_p = None
            best_cov = -1
            for p in all_primes:
                if p in chosen:
                    continue
                cov = coverage_count(elements_factors, chosen | {p})
                if cov > best_cov:
                    best_cov = cov
                    best_p = p
            if best_p:
                chosen.add(best_p)
        return coverage_count(elements_factors, chosen)

def find_f(elements_factors: List[Set[int]], all_primes: List[int], max_r: int = 100) -> int:
    """Find minimum r such that r primes cover >= r elements."""
    for r in range(1, max_r + 1):
        max_cov = find_best_coverage(elements_factors, r, all_primes)
        if max_cov >= r:
            return r
    return max_r

def construct_erdos_straus_set(n: int, primes: List[int]) -> Tuple[List[int], List[Set[int]]]:
    """
    Construct the Erdős-Straus adversarial set:
    A = {large primes} ∪ {small elements}

    where:
    - large primes = {p : √n < p ≤ n}
    - small elements = selected from {1, ..., ⌊√n⌋}
    """
    sqrt_n = int(math.sqrt(n))
    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    k = pi_n + 1

    # Large primes
    large_primes = [p for p in primes if sqrt_n < p <= n]

    # Small elements - we need k - len(large_primes) = pi(√n) + 1 of them
    needed_small = k - len(large_primes)

    # Choose small elements - try different strategies
    small_elements = list(range(1, sqrt_n + 1))  # All elements from 1 to √n

    # Take the first needed_small elements
    selected_small = small_elements[:needed_small]

    # Combine
    A = large_primes + selected_small

    # Compute factors
    factors = [prime_factors(a, primes) for a in A]

    return A, factors

def analyze_erdos_straus_set(n: int):
    """Analyze the Erdős-Straus adversarial set."""
    print(f"\n{'='*70}")
    print(f"ERDŐS-STRAUS SET ANALYSIS: n = {n}")
    print(f"{'='*70}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))

    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if sqrt_n < p <= n]

    k = pi_n + 1
    two_pi_sqrt = 2 * pi_sqrt_n

    print(f"n = {n}")
    print(f"√n ≈ {sqrt_n}")
    print(f"π(n) = {pi_n}")
    print(f"π(√n) = {pi_sqrt_n}")
    print(f"2π(√n) = {two_pi_sqrt}")
    print(f"k = π(n) + 1 = {k}")
    print(f"Small primes: {small_primes}")
    print(f"Large primes count: {len(large_primes)}")

    # Construct the set
    A, factors = construct_erdos_straus_set(n, primes)

    # Categorize elements
    large_prime_elements = [a for a in A if a in large_primes]
    small_elements = [a for a in A if a not in large_primes]

    print(f"\n--- Set composition ---")
    print(f"Large primes in A: {len(large_prime_elements)} (= π(n) - π(√n) = {pi_n - pi_sqrt_n})")
    print(f"Small elements in A: {len(small_elements)} (= π(√n) + 1 = {pi_sqrt_n + 1})")
    print(f"Small elements: {small_elements}")

    # Analyze coverage structure
    all_primes_used = set()
    for f in factors:
        all_primes_used |= f
    all_primes_list = sorted(all_primes_used)

    print(f"\n--- Coverage structure ---")
    print(f"Total distinct primes in A's factors: {len(all_primes_list)}")

    # Key insight: covering small elements vs large primes
    print(f"\nTo cover the {len(small_elements)} small elements:")
    print(f"  Need primes from {small_primes}")

    # With all small primes, how many small elements are covered?
    small_prime_set = set(small_primes)
    small_elem_factors = [prime_factors(a, primes) for a in small_elements]
    small_covered = sum(1 for f in small_elem_factors
                       if not f or f.issubset(small_prime_set))
    print(f"  Using all {len(small_primes)} small primes: cover {small_covered}/{len(small_elements)} small elements")

    # With all small primes, how many large primes are covered?
    large_prime_factors = [{p} for p in large_prime_elements]
    large_covered_by_small = sum(1 for f in large_prime_factors if f.issubset(small_prime_set))
    print(f"  Large primes covered by small primes: {large_covered_by_small}")

    print(f"\nTo cover the {len(large_prime_elements)} large primes:")
    print(f"  Each large prime p needs exactly {{p}} in the covering set")
    print(f"  Efficiency: 1 prime per 1 element")

    # Coverage analysis
    print(f"\n--- Coverage by r primes ---")

    for r in range(1, min(30, len(all_primes_list)) + 1):
        max_cov = find_best_coverage(factors, r, all_primes_list)
        status = "✓" if max_cov >= r else "✗"
        print(f"  r = {r:2d}: max coverage = {max_cov:3d}, need ≥ {r:2d} {status}")

        if max_cov >= r:
            # Find the optimal combination
            if r <= 10:
                for combo in combinations(all_primes_list, r):
                    if coverage_count(factors, set(combo)) >= r:
                        small_in_combo = [p for p in combo if p <= sqrt_n]
                        large_in_combo = [p for p in combo if p > sqrt_n]
                        print(f"      Optimal: {len(small_in_combo)} small + {len(large_in_combo)} large primes")
                        break
            break

    f_val = find_f(factors, all_primes_list)

    print(f"\n  f for Erdős-Straus set: {f_val}")
    print(f"  2π(√n) = {two_pi_sqrt}")
    print(f"  Gap = 2π(√n) - f = {two_pi_sqrt - f_val}")

    # Expected from Erdős-Straus theorem
    print(f"\n--- Comparison with Erdős-Straus theorem ---")
    print(f"  Theorem claims: f(π(n)+1, n) ≈ 2π(√n) = {two_pi_sqrt}")
    print(f"  Computed: f = {f_val}")
    print(f"  Discrepancy: {abs(two_pi_sqrt - f_val)}")

    return f_val, two_pi_sqrt

def main():
    print("="*70)
    print("TESTING ERDŐS-STRAUS ADVERSARIAL SET")
    print("="*70)
    print("\nThe Erdős-Straus set is: A = {large primes} ∪ {small elements}")
    print("where large primes are > √n and small elements are ≤ √n")
    print("\nThis should give f ≈ 2π(√n) according to the theorem.\n")

    results = []
    for n in [50, 100, 200, 500, 1000]:
        f_val, two_pi_sqrt = analyze_erdos_straus_set(n)
        results.append((n, two_pi_sqrt, f_val, two_pi_sqrt - f_val))

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"{'n':<8} {'2π(√n)':<10} {'f':<10} {'Gap':<10} {'Match?':<10}")
    print("-" * 50)
    for n, two_pi, f, gap in results:
        match = "YES" if abs(gap) <= 3 else "NO"
        print(f"{n:<8} {two_pi:<10} {f:<10} {gap:<10} {match:<10}")

    print("\nExpected: f ≈ 2π(√n), so Gap ≈ 0")

if __name__ == "__main__":
    main()
