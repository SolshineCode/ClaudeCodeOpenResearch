#!/usr/bin/env python3
"""
Finding TRULY HARD sets for Erdős Problem #983

The hardest sets should have:
1. No primes, 1, or prime powers (these are "easy" - covered by 1 prime)
2. Elements that are products of DISTINCT primes
3. Prime factors as SPREAD OUT as possible (low overlap)
"""

import math
from itertools import combinations
from typing import Set, List, Tuple

from utils import sieve_of_eratosthenes, prime_factors

def is_squarefree(n: int, primes: List[int]) -> bool:
    if n <= 1:
        return n == 1
    temp = n
    for p in primes:
        if p * p > temp:
            break
        count = 0
        while temp % p == 0:
            count += 1
            temp //= p
            if count > 1:
                return False
    return True

def coverage_count(elements_factors: List[Set[int]], prime_set: Set[int]) -> int:
    return sum(1 for f in elements_factors if f and f.issubset(prime_set))

def find_best_coverage(elements_factors: List[Set[int]], r: int) -> Tuple[int, Set[int]]:
    """Find best coverage with r primes."""
    relevant = set()
    for f in elements_factors:
        relevant |= f
    relevant_primes = sorted(relevant)

    if r >= len(relevant_primes):
        return len([f for f in elements_factors if f]), set(relevant_primes)

    max_cov = 0
    best_primes = set()

    # Exhaustive for small cases
    if r <= 12 and len(relevant_primes) <= 25:
        for combo in combinations(relevant_primes, r):
            prime_set = set(combo)
            cov = coverage_count(elements_factors, prime_set)
            if cov > max_cov:
                max_cov = cov
                best_primes = prime_set
    else:
        # Greedy
        chosen = set()
        for _ in range(r):
            best_p = None
            best_gain = -1
            for p in relevant_primes:
                if p in chosen:
                    continue
                cov = coverage_count(elements_factors, chosen | {p})
                if cov > best_gain:
                    best_gain = cov
                    best_p = p
            if best_p:
                chosen.add(best_p)
        max_cov = coverage_count(elements_factors, chosen)
        best_primes = chosen

    return max_cov, best_primes

def find_f(elements_factors: List[Set[int]]) -> int:
    """Find minimum r such that r primes cover >= r elements."""
    # Filter out empty factor sets (element 1)
    non_trivial = [f for f in elements_factors if f]

    for r in range(1, len(non_trivial) + 1):
        max_cov, _ = find_best_coverage(non_trivial, r)
        if max_cov >= r:
            return r

    return len(non_trivial)

def construct_hardest_set(n: int, k: int, primes: List[int]) -> Tuple[List[Set[int]], List[int]]:
    """
    Construct a set that maximizes f by using squarefree composites with spread factors.
    """
    prime_set = set(primes)

    # Get all squarefree composites (products of 2+ distinct primes)
    sq_composites = []
    for m in range(6, n + 1):  # Start from 6 = 2*3
        if m in prime_set:
            continue
        factors = prime_factors(m, primes)
        if len(factors) >= 2 and is_squarefree(m, primes):
            sq_composites.append((m, factors))

    print(f"  Available squarefree composites: {len(sq_composites)}")

    if len(sq_composites) < k:
        # Not enough - need to include some easier elements
        print(f"  Warning: Only {len(sq_composites)} squarefree composites, need {k}")
        # Add prime powers as fallback
        for m in range(2, n + 1):
            if m not in prime_set:
                factors = prime_factors(m, primes)
                if len(factors) == 1:  # Prime power
                    sq_composites.append((m, factors))
                    if len(sq_composites) >= k:
                        break

    # Strategy: greedily select elements to MINIMIZE efficiency (spread factors)
    selected = []
    used_primes = set()

    # First pass: prefer elements that introduce NEW primes
    # Sort deterministically by number of factors (descending), then by value
    remaining = sorted(sq_composites, key=lambda x: (-len(x[1]), x[0]))

    while len(selected) < k and remaining:
        # Find element with most new primes
        best_elem = None
        best_new = -1
        best_idx = -1

        for i, (m, factors) in enumerate(remaining):
            new_primes = len(factors - used_primes)
            if new_primes > best_new:
                best_new = new_primes
                best_elem = (m, factors)
                best_idx = i

        if best_elem is None:
            break

        selected.append(best_elem)
        used_primes |= best_elem[1]
        remaining.pop(best_idx)

    # Fill remaining slots
    while len(selected) < k and remaining:
        elem = remaining.pop()
        selected.append(elem)
        used_primes |= elem[1]

    values = [m for m, _ in selected]
    factors = [f for _, f in selected]

    return factors, values

def analyze_coverage_in_detail(elements_factors: List[Set[int]], values: List[int]):
    """Detailed coverage analysis."""
    all_primes = set()
    for f in elements_factors:
        all_primes |= f
    all_primes = sorted(all_primes)

    print(f"\n  Set values: {values[:15]}{'...' if len(values) > 15 else ''}")
    print(f"  Set size: {len(elements_factors)}")
    print(f"  Total distinct primes: {len(all_primes)}")
    print(f"  Efficiency ratio (elements/primes): {len(elements_factors)/len(all_primes):.3f}")

    # Elements with no factors (should be 0 for proper hard sets)
    trivial = sum(1 for f in elements_factors if not f)
    print(f"  Trivially covered elements (1 or primes): {trivial}")

    print("\n  Coverage analysis:")
    for r in range(1, min(20, len(all_primes) + 1)):
        cov, best_p = find_best_coverage(elements_factors, r)
        status = "✓" if cov >= r else "✗"
        print(f"    r={r:2d}: best coverage = {cov:3d}, need ≥{r:2d} {status}")
        if cov >= r:
            print(f"          Best primes: {sorted(best_p)}")
            break

    f_val = find_f(elements_factors)
    return f_val

def test_hard_set_construction(n: int):
    """Test hard set construction for given n."""
    print(f"\n{'='*70}")
    print(f"TRULY HARD SET TEST: n = {n}")
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

    print("\n--- Constructing hardest possible set ---")
    elements_factors, values = construct_hardest_set(n, k, primes)

    if len(elements_factors) < k:
        print(f"  Could only construct {len(elements_factors)} elements")
        return None, two_pi_sqrt

    f_val = analyze_coverage_in_detail(elements_factors, values)

    print(f"\n  f for this hard set: {f_val}")
    print(f"  Gap = 2π(√n) - f = {two_pi_sqrt} - {f_val} = {two_pi_sqrt - f_val}")

    return f_val, two_pi_sqrt

def test_pure_semiprime_sets(n: int):
    """Test sets consisting ONLY of semiprimes (products of exactly 2 distinct primes)."""
    print(f"\n{'='*70}")
    print(f"PURE SEMIPRIME TEST: n = {n}")
    print(f"{'='*70}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))
    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])
    k = pi_n + 1

    # Get all semiprimes up to n
    semiprimes = []
    prime_set = set(primes)
    for m in range(6, n + 1):
        factors = prime_factors(m, primes)
        if len(factors) == 2 and is_squarefree(m, primes):
            semiprimes.append((m, factors))

    print(f"Total semiprimes up to {n}: {len(semiprimes)}")
    print(f"Need k = {k} elements")

    if len(semiprimes) < k:
        print("Not enough semiprimes for a pure semiprime set")
        return

    # Construct set with maximum spread
    print("\n--- Maximum spread construction ---")
    selected = []
    used_primes = set()

    # Sort deterministically by value for reproducibility
    remaining = sorted(semiprimes, key=lambda x: x[0])

    while len(selected) < k and remaining:
        # Prefer semiprimes with maximum new primes
        best = None
        best_new = -1
        best_idx = -1
        for i, (m, factors) in enumerate(remaining):
            new = len(factors - used_primes)
            if new > best_new:
                best_new = new
                best = (m, factors)
                best_idx = i
        if best:
            selected.append(best)
            used_primes |= best[1]
            remaining.pop(best_idx)
        else:
            # No element adds new primes; just take any
            selected.append(remaining.pop())

    elements_factors = [f for _, f in selected]
    values = [m for m, _ in selected]

    f_val = analyze_coverage_in_detail(elements_factors, values)

    print(f"\n  f for pure semiprime set: {f_val}")
    print(f"  2π(√n) = {2 * pi_sqrt_n}")
    print(f"  Gap = {2 * pi_sqrt_n - f_val}")

    return f_val

def main():
    print("="*70)
    print("FINDING TRULY HARD SETS FOR ERDŐS PROBLEM #983")
    print("="*70)
    print("\nHard sets should:")
    print("- Contain NO primes, 1, or prime powers")
    print("- Contain products of 2+ DISTINCT primes")
    print("- Have prime factors as spread out as possible")
    print()

    results = []

    for n in [100, 200, 300, 500, 750, 1000]:
        f_val, two_pi_sqrt = test_hard_set_construction(n)
        if f_val is not None:
            results.append((n, two_pi_sqrt, f_val, two_pi_sqrt - f_val))

    print("\n" + "="*70)
    print("SUMMARY OF HARD SET ANALYSIS")
    print("="*70)
    print(f"{'n':<8} {'2π(√n)':<10} {'f (hard)':<10} {'Gap':<10}")
    print("-" * 40)
    for n, two_pi, f, gap in results:
        print(f"{n:<8} {two_pi:<10} {f:<10} {gap:<10}")

    if results:
        gaps = [g for _, _, _, g in results]
        print(f"\nGap range: [{min(gaps)}, {max(gaps)}]")

        # Check trend
        if len(results) >= 3:
            first_half = gaps[:len(gaps)//2]
            second_half = gaps[len(gaps)//2:]
            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)
            print(f"Average gap (first half): {avg_first:.2f}")
            print(f"Average gap (second half): {avg_second:.2f}")

            if avg_second < avg_first - 2:
                print("\n✓ Gap appears to be DECREASING - consistent with bounded gap")
            elif avg_second > avg_first + 2:
                print("\n⚠ Gap appears to be INCREASING - theory may need revision")
            else:
                print("\n✓ Gap appears STABLE")

    print("\n" + "="*70)
    print("TESTING PURE SEMIPRIME SETS")
    print("="*70)

    for n in [200, 500, 1000]:
        test_pure_semiprime_sets(n)

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()
