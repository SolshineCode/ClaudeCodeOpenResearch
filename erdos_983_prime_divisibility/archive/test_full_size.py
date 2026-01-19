#!/usr/bin/env python3
"""
Test f(k,n) with FULL SIZE sets (k = π(n)+1)

This is the critical test for the main question of Erdős Problem #983.
"""

import math
from itertools import combinations
from typing import Set, List, Tuple
import random

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
    """Count elements covered by prime_set."""
    return sum(1 for f in elements_factors if (not f) or f.issubset(prime_set))

def greedy_coverage(elements_factors: List[Set[int]], r: int, all_primes: List[int]) -> Tuple[int, Set[int]]:
    """Greedy algorithm to find good coverage with r primes."""
    relevant = set()
    for f in elements_factors:
        relevant |= f
    relevant_primes = sorted(relevant)

    chosen = set()
    for _ in range(min(r, len(relevant_primes))):
        best_p = None
        best_cov = -1
        for p in relevant_primes:
            if p in chosen:
                continue
            cov = coverage_count(elements_factors, chosen | {p})
            if cov > best_cov:
                best_cov = cov
                best_p = p
        if best_p:
            chosen.add(best_p)

    return coverage_count(elements_factors, chosen), chosen

def exhaustive_best_coverage(elements_factors: List[Set[int]], r: int) -> int:
    """Find best coverage with exactly r primes (exhaustive for small cases)."""
    relevant = set()
    for f in elements_factors:
        relevant |= f
    relevant_primes = sorted(relevant)

    if r >= len(relevant_primes):
        return len(elements_factors)

    max_cov = 0
    for combo in combinations(relevant_primes, r):
        cov = coverage_count(elements_factors, set(combo))
        max_cov = max(max_cov, cov)

    return max_cov

def find_f_for_set(elements_factors: List[Set[int]], max_r: int = None) -> int:
    """Find minimum r such that r primes cover >= r elements."""
    n = len(elements_factors)
    if max_r is None:
        max_r = n

    relevant = set()
    for f in elements_factors:
        relevant |= f
    n_relevant = len(relevant)

    for r in range(1, max_r + 1):
        # Use exhaustive for small cases
        if r <= 15 and n_relevant <= 25:
            max_cov = exhaustive_best_coverage(elements_factors, r)
        else:
            max_cov, _ = greedy_coverage(elements_factors, r, [])

        if max_cov >= r:
            return r

    return max_r

def construct_adversarial_set(n: int, k: int, primes: List[int], strategy: str) -> List[Set[int]]:
    """
    Construct an adversarial set of size k using different strategies.
    Returns list of prime factor sets.
    """
    all_elements = list(range(1, n + 1))
    prime_set = set(primes)
    sqrt_n = int(math.sqrt(n))
    small_primes = set(p for p in primes if p <= sqrt_n)
    large_primes = [p for p in primes if p > sqrt_n and p <= n]

    if strategy == "all_primes_plus_composite":
        # All primes plus one composite
        A = list(primes) + [6]  # 6 = 2*3
        A = A[:k]
        return [prime_factors(a, primes) for a in A]

    elif strategy == "all_large_primes_plus_small":
        # All large primes plus small elements
        A = large_primes[:]
        needed = k - len(A)
        small_elements = [m for m in range(2, sqrt_n + 1)]
        A.extend(small_elements[:needed])
        A = A[:k]
        return [prime_factors(a, primes) for a in A]

    elif strategy == "spread_semiprimes":
        # Products of 2 distinct primes, maximizing spread
        semiprimes = []
        for i, p in enumerate(primes):
            for q in primes[i+1:]:
                if p * q <= n:
                    semiprimes.append((p * q, {p, q}))

        # Sort by having least common primes
        random.shuffle(semiprimes)
        A = []
        used_primes = set()
        for m, factors in semiprimes:
            if len(A) >= k:
                break
            # Prefer elements with new primes
            new_primes = factors - used_primes
            if new_primes or len(A) < k // 2:
                A.append(factors)
                used_primes |= factors

        # Fill remaining with any elements if needed
        while len(A) < k:
            for m in range(2, n + 1):
                if len(A) >= k:
                    break
                f = prime_factors(m, primes)
                if f and f not in A:
                    A.append(f)

        return A[:k]

    elif strategy == "maximize_distinct_primes":
        # Try to use as many distinct primes as possible
        elements = []
        for m in range(2, n + 1):
            f = prime_factors(m, primes)
            if len(f) >= 2:  # Only composites with 2+ factors
                elements.append((m, f))

        # Sort by number of factors descending
        elements.sort(key=lambda x: len(x[1]), reverse=True)

        A = []
        all_used = set()
        for m, f in elements:
            if len(A) >= k:
                break
            A.append(f)
            all_used |= f

        # Fill with primes if needed
        while len(A) < k:
            for p in primes:
                if len(A) >= k:
                    break
                if {p} not in A:
                    A.append({p})

        return A[:k]

    else:  # "random"
        A = random.sample(all_elements, k)
        return [prime_factors(a, primes) for a in A]

def test_full_size_sets(n: int, num_trials: int = 100):
    """
    Test f(k,n) with k = π(n)+1 using various adversarial strategies.
    """
    print(f"\n{'='*70}")
    print(f"FULL-SIZE SET TESTING: n = {n}")
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

    strategies = [
        "all_primes_plus_composite",
        "all_large_primes_plus_small",
        "spread_semiprimes",
        "maximize_distinct_primes",
        "random"
    ]

    max_f_overall = 0
    results = []

    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")

        max_f = 0
        trials = num_trials if strategy == "random" else 10

        for trial in range(trials):
            A_factors = construct_adversarial_set(n, k, primes, strategy)
            if len(A_factors) != k:
                continue

            f_A = find_f_for_set(A_factors)
            max_f = max(max_f, f_A)

        results.append((strategy, max_f))
        max_f_overall = max(max_f_overall, max_f)

        # Analysis of the set
        if strategy != "random":
            A_factors = construct_adversarial_set(n, k, primes, strategy)
            all_primes_used = set()
            for f in A_factors:
                all_primes_used |= f
            print(f"  Set size: {len(A_factors)}")
            print(f"  Distinct primes in set: {len(all_primes_used)}")
            print(f"  Elements with no factors (including 1): {sum(1 for f in A_factors if not f)}")
            print(f"  f for this strategy: {max_f}")
            print(f"  Gap = 2π(√n) - f = {two_pi_sqrt} - {max_f} = {two_pi_sqrt - max_f}")

    print(f"\n{'='*50}")
    print(f"SUMMARY for n = {n}")
    print(f"{'='*50}")
    print(f"2π(√n) = {two_pi_sqrt}")
    print(f"Maximum f found: {max_f_overall}")
    print(f"Gap = 2π(√n) - max(f) = {two_pi_sqrt - max_f_overall}")

    return max_f_overall, two_pi_sqrt

def main():
    print("="*70)
    print("TESTING ERDŐS PROBLEM #983 WITH FULL-SIZE SETS")
    print("="*70)
    print("\nKey question: Is 2π(n^{1/2}) - f(π(n)+1, n) bounded?")
    print("Testing with k = π(n)+1 elements\n")

    results = []

    for n in [30, 50, 75, 100, 150, 200, 300, 500]:
        try:
            max_f, two_pi_sqrt = test_full_size_sets(n, num_trials=50)
            gap = two_pi_sqrt - max_f
            results.append((n, two_pi_sqrt, max_f, gap))
        except Exception as e:
            print(f"Error for n={n}: {e}")
            continue

    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"{'n':<8} {'2π(√n)':<10} {'max f':<10} {'Gap':<10}")
    print("-" * 40)

    for n, two_pi_sqrt, max_f, gap in results:
        print(f"{n:<8} {two_pi_sqrt:<10} {max_f:<10} {gap:<10}")

    gaps = [g for _, _, _, g in results]
    print(f"\nGap range: [{min(gaps)}, {max(gaps)}]")

    # Check if bounded
    if max(abs(g) for g in gaps) <= 20:
        print("\n✓ GAP APPEARS BOUNDED")
        print("This supports the theoretical claim that 2π(√n) - f(π(n)+1, n) does NOT → ∞")
    else:
        print("\n⚠ Large gaps observed - further investigation needed")

    # Additional analysis
    print("\n" + "="*70)
    print("TREND ANALYSIS")
    print("="*70)

    # Check if gap grows with n
    if len(results) >= 4:
        early_gaps = [g for n, _, _, g in results if n <= 100]
        late_gaps = [g for n, _, _, g in results if n > 100]

        if early_gaps and late_gaps:
            print(f"Average gap for n ≤ 100: {sum(early_gaps)/len(early_gaps):.2f}")
            print(f"Average gap for n > 100: {sum(late_gaps)/len(late_gaps):.2f}")

            if abs(sum(late_gaps)/len(late_gaps)) > abs(sum(early_gaps)/len(early_gaps)) + 5:
                print("⚠ Gap may be growing with n")
            else:
                print("✓ Gap appears stable as n increases")

if __name__ == "__main__":
    main()
