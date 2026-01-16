#!/usr/bin/env python3
"""
Focused testing on HARD SETS for Erdős Problem #983

The hardest sets are those containing only squarefree composites
(products of distinct primes), which require multiple primes each to cover.
"""

import math
from itertools import combinations
from typing import Set, List, Dict, Tuple
import time

def sieve_of_eratosthenes(n: int) -> List[int]:
    """Return list of primes up to n."""
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]

def prime_factorization_set(n: int, primes: List[int]) -> Set[int]:
    """Return set of prime factors of n."""
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

def is_squarefree(n: int, primes: List[int]) -> bool:
    """Check if n is squarefree."""
    if n <= 1:
        return n == 1
    temp = n
    for p in primes:
        if p * p > temp:
            break
        if temp % p == 0:
            count = 0
            while temp % p == 0:
                count += 1
                temp //= p
            if count > 1:
                return False
    return True

def get_squarefree_composites(n: int, primes: List[int]) -> List[Tuple[int, Set[int]]]:
    """
    Return list of (m, prime_factors) for squarefree composites m <= n.
    """
    prime_set = set(primes)
    result = []
    for m in range(2, n + 1):
        if m in prime_set:
            continue  # Skip primes
        factors = prime_factorization_set(m, primes)
        if len(factors) >= 2 and is_squarefree(m, primes):
            result.append((m, factors))
    return result

def is_covered(prime_factors: Set[int], covering_primes: Set[int]) -> bool:
    """Check if an element with given prime factors is covered."""
    return prime_factors.issubset(covering_primes)

def coverage_count(elements: List[Set[int]], covering_primes: Set[int]) -> int:
    """Count how many elements are covered."""
    return sum(1 for factors in elements if is_covered(factors, covering_primes))

def find_best_coverage_exhaustive(elements: List[Set[int]], r: int, all_primes: List[int]) -> int:
    """
    Find the maximum coverage with exactly r primes (exhaustive).
    """
    # Get relevant primes (those that appear in some element)
    relevant_primes = set()
    for factors in elements:
        relevant_primes |= factors
    relevant_primes = sorted(relevant_primes)

    if r >= len(relevant_primes):
        # Using all relevant primes covers everything
        return len(elements)

    max_coverage = 0
    for prime_combo in combinations(relevant_primes, r):
        prime_set = set(prime_combo)
        cov = coverage_count(elements, prime_set)
        max_coverage = max(max_coverage, cov)

    return max_coverage

def find_best_coverage_greedy(elements: List[Set[int]], r: int) -> int:
    """
    Greedy approximation for best coverage with r primes.
    """
    # Get relevant primes
    relevant_primes = set()
    for factors in elements:
        relevant_primes |= factors

    chosen = set()
    remaining_elements = list(range(len(elements)))

    for _ in range(min(r, len(relevant_primes))):
        if not remaining_elements:
            break

        best_prime = None
        best_gain = -1

        for p in relevant_primes:
            if p in chosen:
                continue
            # Count elements that would be covered if we add p
            gain = 0
            for idx in remaining_elements:
                if is_covered(elements[idx], chosen | {p}):
                    gain += 1
            if gain > best_gain:
                best_gain = gain
                best_prime = p

        if best_prime is None:
            break

        chosen.add(best_prime)
        # Update remaining elements
        remaining_elements = [idx for idx in remaining_elements
                           if not is_covered(elements[idx], chosen)]

    return coverage_count(elements, chosen)

def find_f_for_elements(elements: List[Set[int]], all_primes: List[int],
                        use_exhaustive: bool = True) -> int:
    """
    Find minimum r such that r primes cover >= r elements.
    """
    n_elements = len(elements)

    # Get relevant primes
    relevant_primes = set()
    for factors in elements:
        relevant_primes |= factors
    n_relevant = len(relevant_primes)

    for r in range(1, n_elements + 1):
        if use_exhaustive and r <= 12 and n_relevant <= 20:
            max_cov = find_best_coverage_exhaustive(elements, r, all_primes)
        else:
            max_cov = find_best_coverage_greedy(elements, r)

        if max_cov >= r:
            return r

    return n_elements

def analyze_hard_set_structure(n: int):
    """
    Analyze the structure of hard sets for a given n.
    """
    print(f"\n{'='*70}")
    print(f"HARD SET ANALYSIS FOR n = {n}")
    print(f"{'='*70}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))

    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    print(f"π(n) = {pi_n}, π(√n) = {pi_sqrt_n}, 2π(√n) = {2 * pi_sqrt_n}")

    k = pi_n + 1
    print(f"Target set size k = π(n) + 1 = {k}")

    # Get squarefree composites
    sq_composites = get_squarefree_composites(n, primes)
    print(f"\nSquarefree composites up to {n}: {len(sq_composites)}")

    if len(sq_composites) < k:
        print(f"  Not enough squarefree composites for a pure-semiprime set of size {k}")
        print(f"  Maximum hard set size: {len(sq_composites)}")
    else:
        print(f"  Can form hard sets of size {k} from squarefree composites")

    # Analyze prime factor distribution
    all_factors = set()
    factor_counts = {}
    for m, factors in sq_composites:
        all_factors |= factors
        for p in factors:
            factor_counts[p] = factor_counts.get(p, 0) + 1

    print(f"\nPrimes appearing in squarefree composites: {len(all_factors)}")
    print(f"Most common primes: {sorted(factor_counts.items(), key=lambda x: -x[1])[:5]}")

    return sq_composites, primes, k, pi_sqrt_n

def test_specific_hard_constructions(n: int):
    """
    Test specific hard set constructions.
    """
    sq_composites, primes, k, pi_sqrt_n = analyze_hard_set_structure(n)

    if len(sq_composites) < 5:
        print("Not enough squarefree composites for meaningful test")
        return

    print(f"\n{'='*70}")
    print(f"TESTING HARD CONSTRUCTIONS FOR n = {n}")
    print(f"{'='*70}")

    # Construction 1: Elements using the most distinct primes possible
    # Sort by number of prime factors (descending)
    sorted_by_factors = sorted(sq_composites, key=lambda x: len(x[1]), reverse=True)

    print("\n--- Construction 1: Elements with most prime factors ---")
    test_size = min(k, len(sq_composites), 15)
    elements1 = [factors for m, factors in sorted_by_factors[:test_size]]
    values1 = [m for m, factors in sorted_by_factors[:test_size]]
    print(f"Selected elements: {values1}")

    # Count distinct primes used
    all_primes_used = set()
    for factors in elements1:
        all_primes_used |= factors
    print(f"Distinct primes used: {len(all_primes_used)}")
    print(f"Efficiency ratio (elements/primes): {len(elements1)}/{len(all_primes_used)} = {len(elements1)/len(all_primes_used):.3f}")

    f1 = find_f_for_elements(elements1, primes)
    print(f"f for this set: {f1}")
    print(f"Gap 2π(√n) - f = {2*pi_sqrt_n} - {f1} = {2*pi_sqrt_n - f1}")

    # Construction 2: Maximize spread - use elements with disjoint prime factors
    print("\n--- Construction 2: Maximize prime spread ---")
    elements2 = []
    primes_used2 = set()

    for m, factors in sq_composites:
        # Add element if it introduces at least one new prime
        if not factors.issubset(primes_used2) or len(elements2) == 0:
            elements2.append(factors)
            primes_used2 |= factors
            if len(elements2) >= test_size:
                break

    print(f"Elements selected: {len(elements2)}")
    print(f"Distinct primes used: {len(primes_used2)}")
    print(f"Efficiency ratio: {len(elements2)/len(primes_used2):.3f}")

    f2 = find_f_for_elements(elements2, primes)
    print(f"f for this set: {f2}")
    print(f"Gap 2π(√n) - f = {2*pi_sqrt_n} - {f2} = {2*pi_sqrt_n - f2}")

    # Construction 3: Semiprimes with disjoint factor pairs
    print("\n--- Construction 3: Semiprimes (2 factors) only ---")
    semiprimes = [(m, factors) for m, factors in sq_composites if len(factors) == 2]
    print(f"Total semiprimes: {len(semiprimes)}")

    if len(semiprimes) >= 5:
        test_size3 = min(test_size, len(semiprimes))
        elements3 = [factors for m, factors in semiprimes[:test_size3]]
        values3 = [m for m, factors in semiprimes[:test_size3]]

        all_primes_used3 = set()
        for factors in elements3:
            all_primes_used3 |= factors

        print(f"Selected semiprimes: {values3}")
        print(f"Distinct primes used: {len(all_primes_used3)}")
        print(f"Efficiency ratio: {len(elements3)/len(all_primes_used3):.3f}")

        f3 = find_f_for_elements(elements3, primes)
        print(f"f for this set: {f3}")
        print(f"Gap 2π(√n) - f = {2*pi_sqrt_n} - {f3} = {2*pi_sqrt_n - f3}")

def exhaustive_search_hard_sets(n: int, max_sets: int = 10000):
    """
    Search for the hardest sets by examining squarefree composite combinations.
    """
    print(f"\n{'='*70}")
    print(f"EXHAUSTIVE SEARCH FOR HARDEST SETS (n = {n})")
    print(f"{'='*70}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))
    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    sq_composites = get_squarefree_composites(n, primes)

    k = pi_n + 1
    print(f"π(n) = {pi_n}, k = {k}, 2π(√n) = {2*pi_sqrt_n}")
    print(f"Squarefree composites available: {len(sq_composites)}")

    if len(sq_composites) < k:
        print(f"Cannot form pure squarefree set of size {k}")
        test_k = len(sq_composites)
    else:
        test_k = min(k, 12)  # Limit for computational feasibility

    print(f"Testing sets of size {test_k}")

    from math import comb
    total_possible = comb(len(sq_composites), test_k)
    print(f"Total possible combinations: {total_possible}")

    max_f = 0
    hardest_set = None
    count = 0

    if total_possible <= max_sets:
        # Exhaustive
        for combo in combinations(sq_composites, test_k):
            elements = [factors for m, factors in combo]
            f_val = find_f_for_elements(elements, primes, use_exhaustive=True)
            if f_val > max_f:
                max_f = f_val
                hardest_set = combo
            count += 1
            if count % 1000 == 0:
                print(f"  Checked {count}/{total_possible}, current max f = {max_f}")
    else:
        # Sample
        import random
        sq_list = list(sq_composites)
        for _ in range(max_sets):
            random.shuffle(sq_list)
            combo = tuple(sq_list[:test_k])
            elements = [factors for m, factors in combo]
            f_val = find_f_for_elements(elements, primes, use_exhaustive=(test_k <= 10))
            if f_val > max_f:
                max_f = f_val
                hardest_set = combo
            count += 1
            if count % 1000 == 0:
                print(f"  Sampled {count}/{max_sets}, current max f = {max_f}")

    print(f"\n✓ Search complete")
    print(f"Maximum f found: {max_f}")
    print(f"Gap: 2π(√n) - f = {2*pi_sqrt_n} - {max_f} = {2*pi_sqrt_n - max_f}")

    if hardest_set and len(hardest_set) <= 15:
        print(f"Hardest set: {[m for m, _ in hardest_set]}")
        all_factors = set()
        for m, factors in hardest_set:
            all_factors |= factors
        print(f"Total distinct primes: {len(all_factors)}")

    return max_f, 2*pi_sqrt_n - max_f

def verify_coverage_calculation(n: int):
    """
    Verify the coverage calculation with detailed output.
    """
    print(f"\n{'='*70}")
    print(f"VERIFICATION OF COVERAGE CALCULATIONS (n = {n})")
    print(f"{'='*70}")

    primes = sieve_of_eratosthenes(n)
    sq_composites = get_squarefree_composites(n, primes)

    # Take a small set for detailed analysis
    test_set = sq_composites[:6]
    print(f"\nTest set: {[(m, sorted(f)) for m, f in test_set]}")

    elements = [factors for m, factors in test_set]
    all_primes = set()
    for factors in elements:
        all_primes |= factors
    all_primes = sorted(all_primes)

    print(f"All primes involved: {all_primes}")
    print(f"Number of elements: {len(elements)}")
    print(f"Number of primes: {len(all_primes)}")

    print("\n--- Coverage by number of primes ---")
    for r in range(1, len(all_primes) + 1):
        max_cov = find_best_coverage_exhaustive(elements, r, primes)
        status = "✓" if max_cov >= r else "✗"
        print(f"r = {r}: max coverage = {max_cov} {'≥' if max_cov >= r else '<'} {r} {status}")

        # Show best combination
        if r <= 4:
            best_combo = None
            best_cov = 0
            for combo in combinations(all_primes, r):
                cov = coverage_count(elements, set(combo))
                if cov > best_cov:
                    best_cov = cov
                    best_combo = combo
            if best_combo:
                print(f"   Best combo: {best_combo} -> covers ", end="")
                covered = [m for (m, f), factors in zip(test_set, elements)
                          if f.issubset(set(best_combo))]
                print(covered)

    f_val = find_f_for_elements(elements, primes, use_exhaustive=True)
    print(f"\nf for this set: {f_val}")

def main():
    print("="*70)
    print("COMPREHENSIVE HARD SET TESTING FOR ERDŐS PROBLEM #983")
    print("="*70)
    print("\nFocus: Squarefree composites (products of distinct primes)")
    print("These are the 'hardest' elements to cover.\n")

    # Small verification
    verify_coverage_calculation(50)

    # Test specific constructions
    for n in [50, 100, 200]:
        test_specific_hard_constructions(n)

    # Exhaustive/sampling search
    print("\n" + "="*70)
    print("SEARCHING FOR HARDEST SETS")
    print("="*70)

    results = []
    for n in [30, 50, 75, 100, 150, 200]:
        max_f, gap = exhaustive_search_hard_sets(n, max_sets=5000)
        primes = sieve_of_eratosthenes(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt_n = len([p for p in primes if p <= sqrt_n])
        results.append((n, 2*pi_sqrt_n, max_f, gap))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY: Gap Analysis for Hard Sets")
    print("="*70)
    print(f"{'n':<8} {'2π(√n)':<10} {'max f':<10} {'Gap':<10} {'Theory':<15}")
    print("-"*55)
    for n, two_pi, max_f, gap in results:
        theory = "✓ Bounded" if -5 <= gap <= 5 else "⚠ Check"
        print(f"{n:<8} {two_pi:<10} {max_f:<10} {gap:<10} {theory:<15}")

    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    gaps = [g for _, _, _, g in results]
    print(f"Gap range observed: [{min(gaps)}, {max(gaps)}]")

    if all(-10 <= g <= 10 for g in gaps):
        print("✓ Gap appears BOUNDED - supporting the theoretical claim")
    else:
        print("⚠ Large gaps observed - theory may need revision")

if __name__ == "__main__":
    main()
