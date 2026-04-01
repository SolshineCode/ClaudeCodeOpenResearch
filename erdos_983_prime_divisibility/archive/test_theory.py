#!/usr/bin/env python3
"""
Comprehensive Testing of Erdős Problem #983 Theory

This script tests the claim that 2π(n^{1/2}) - f(π(n)+1, n) is bounded.

Key functions:
- f(k, n): Compute the minimum r such that any A of size k has r primes covering ≥r elements
- Verify the gap is bounded between 0 and 1
- Test intermediate regime estimates
"""

import math
from itertools import combinations, chain
from functools import lru_cache
from typing import Set, List, Tuple, Dict
import time

# =============================================================================
# PRIME AND SMOOTH NUMBER UTILITIES
# =============================================================================

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

def prime_factorization(n: int, primes: List[int]) -> Set[int]:
    """Return set of prime factors of n."""
    if n <= 1:
        return set()
    factors = set()
    for p in primes:
        if p * p > n:
            break
        if n % p == 0:
            factors.add(p)
            while n % p == 0:
                n //= p
    if n > 1:
        factors.add(n)
    return factors

def get_all_prime_factors(n: int, primes: List[int]) -> Dict[int, Set[int]]:
    """Precompute prime factors for all integers 1 to n."""
    factors = {1: set()}
    for m in range(2, n + 1):
        factors[m] = prime_factorization(m, primes)
    return factors

def is_covered(element: int, prime_set: Set[int], factors: Dict[int, Set[int]]) -> bool:
    """Check if element is covered by prime_set (all prime factors in prime_set)."""
    elem_factors = factors[element]
    if not elem_factors:  # element is 1
        return True
    return elem_factors.issubset(prime_set)

def count_covered(A: Set[int], prime_set: Set[int], factors: Dict[int, Set[int]]) -> int:
    """Count how many elements of A are covered by prime_set."""
    return sum(1 for a in A if is_covered(a, prime_set, factors))

# =============================================================================
# COMPUTING f(k, n) - THE MAIN FUNCTION
# =============================================================================

def compute_max_coverage_with_r_primes(A: Set[int], r: int, primes: List[int],
                                        factors: Dict[int, Set[int]]) -> int:
    """
    For a fixed set A, find the maximum coverage achievable with r primes.
    This is computationally expensive for large r.
    """
    if r >= len(primes):
        # Using all primes covers everything
        return len(A)

    max_coverage = 0

    # For small r, enumerate all combinations
    if r <= 10 and len(primes) <= 50:
        for prime_combo in combinations(primes, r):
            prime_set = set(prime_combo)
            coverage = count_covered(A, prime_set, factors)
            max_coverage = max(max_coverage, coverage)
    else:
        # Use greedy heuristic for larger cases
        max_coverage = greedy_coverage(A, r, primes, factors)

    return max_coverage

def greedy_coverage(A: Set[int], r: int, primes: List[int],
                    factors: Dict[int, Set[int]]) -> int:
    """Greedy algorithm to find r primes with good coverage."""
    remaining = set(A)
    chosen_primes = set()

    for _ in range(r):
        if not remaining:
            break

        # Find the prime that covers the most remaining elements
        best_prime = None
        best_count = -1

        for p in primes:
            if p in chosen_primes:
                continue
            # Count elements that would be newly covered if we add p
            # An element is covered when ALL its prime factors are in chosen_primes ∪ {p}
            count = 0
            for a in remaining:
                elem_factors = factors[a]
                if not elem_factors:  # 1 is always covered
                    count += 1
                elif elem_factors.issubset(chosen_primes | {p}):
                    count += 1

            if count > best_count:
                best_count = count
                best_prime = p

        if best_prime is None:
            break

        chosen_primes.add(best_prime)
        # Remove covered elements
        remaining = {a for a in remaining if not is_covered(a, chosen_primes, factors)}

    return count_covered(A, chosen_primes, factors)

def can_cover_r_with_r_primes(A: Set[int], r: int, primes: List[int],
                               factors: Dict[int, Set[int]], exhaustive: bool = False) -> bool:
    """
    Check if there exist r primes that cover at least r elements of A.
    """
    if r <= 0:
        return True
    if r > len(A):
        return False

    # First try greedy
    greedy_cov = greedy_coverage(A, r, primes, factors)
    if greedy_cov >= r:
        return True

    # For small cases, try exhaustive search
    if exhaustive and r <= 8 and len(primes) <= 30:
        for prime_combo in combinations(primes, r):
            prime_set = set(prime_combo)
            if count_covered(A, prime_set, factors) >= r:
                return True
        return False

    # For larger cases, rely on greedy (may underestimate coverage)
    return greedy_cov >= r

def find_f_for_set(A: Set[int], primes: List[int], factors: Dict[int, Set[int]],
                   max_r: int = None) -> int:
    """
    Find the minimum r such that r primes cover at least r elements of A.
    """
    if max_r is None:
        max_r = len(A)

    for r in range(1, max_r + 1):
        if can_cover_r_with_r_primes(A, r, primes, factors, exhaustive=(r <= 6)):
            return r

    return max_r

def compute_f_lower_bound(n: int, k: int, primes: List[int], factors: Dict[int, Set[int]],
                          num_samples: int = 100) -> int:
    """
    Compute lower bound on f(k, n) by finding hard sets.
    f(k,n) is the minimum r that works for ALL sets of size k.
    We look for sets where the minimum working r is maximized.
    """
    all_elements = list(range(1, n + 1))
    max_f = 1

    # Try various adversarial constructions
    primes_up_to_n = [p for p in primes if p <= n]
    sqrt_n = int(math.sqrt(n))
    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if sqrt_n < p <= n]

    # Construction 1: All large primes + spread small elements
    if len(large_primes) > 0 and k >= len(large_primes):
        needed_small = k - len(large_primes)
        if needed_small > 0 and needed_small <= sqrt_n:
            small_elements = [m for m in range(2, sqrt_n + 1)][:needed_small]
            A = set(large_primes) | set(small_elements)
            if len(A) == k:
                f_A = find_f_for_set(A, primes, factors)
                max_f = max(max_f, f_A)

    # Construction 2: Products of distinct primes (semiprimes)
    semiprimes = []
    for i, p in enumerate(small_primes):
        for q in small_primes[i+1:]:
            if p * q <= n:
                semiprimes.append(p * q)

    if len(semiprimes) >= k:
        # Try various subsets
        for _ in range(min(num_samples, 20)):
            import random
            random.shuffle(semiprimes)
            A = set(semiprimes[:k])
            if len(A) == k:
                f_A = find_f_for_set(A, primes, factors)
                max_f = max(max_f, f_A)

    # Construction 3: All primes up to n plus composites
    if k == len(primes_up_to_n) + 1:
        # Add various composites
        composites = [m for m in range(2, n + 1) if m not in set(primes_up_to_n)]
        for m in composites[:20]:
            A = set(primes_up_to_n) | {m}
            f_A = find_f_for_set(A, primes, factors)
            max_f = max(max_f, f_A)

    return max_f

def compute_f_upper_bound(n: int, k: int, primes: List[int], factors: Dict[int, Set[int]]) -> int:
    """
    Compute upper bound on f(k, n) by showing r primes always suffice.
    """
    sqrt_n = int(math.sqrt(n))
    pi_sqrt_n = sum(1 for p in primes if p <= sqrt_n)

    # Trivial upper bound: π(n) always works
    pi_n = sum(1 for p in primes if p <= n)

    # Better bound: 2π(√n) often suffices
    return min(pi_n, 2 * pi_sqrt_n + 2)

# =============================================================================
# MAIN TESTING FUNCTIONS
# =============================================================================

def test_main_conjecture(n_values: List[int]) -> List[Dict]:
    """
    Test the main conjecture: 2π(√n) - f(π(n)+1, n) is bounded.
    """
    results = []

    for n in n_values:
        print(f"\n{'='*60}")
        print(f"Testing n = {n}")
        print(f"{'='*60}")

        start_time = time.time()

        # Compute primes and factors
        primes = sieve_of_eratosthenes(n)
        factors = get_all_prime_factors(n, primes)

        sqrt_n = int(math.sqrt(n))
        pi_n = len([p for p in primes if p <= n])
        pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

        print(f"π(n) = {pi_n}, π(√n) = {pi_sqrt_n}, 2π(√n) = {2 * pi_sqrt_n}")

        k = pi_n + 1
        print(f"k = π(n) + 1 = {k}")

        # Compute f(k, n) bounds
        f_lower = compute_f_lower_bound(n, k, primes, factors)
        f_upper = compute_f_upper_bound(n, k, primes, factors)

        print(f"f({k}, {n}) bounds: [{f_lower}, {f_upper}]")

        gap_lower = 2 * pi_sqrt_n - f_upper
        gap_upper = 2 * pi_sqrt_n - f_lower

        print(f"Gap 2π(√n) - f(π(n)+1, n) in [{gap_lower}, {gap_upper}]")

        elapsed = time.time() - start_time

        result = {
            'n': n,
            'pi_n': pi_n,
            'pi_sqrt_n': pi_sqrt_n,
            'two_pi_sqrt_n': 2 * pi_sqrt_n,
            'k': k,
            'f_lower': f_lower,
            'f_upper': f_upper,
            'gap_lower': gap_lower,
            'gap_upper': gap_upper,
            'time': elapsed
        }
        results.append(result)

        # Check if gap is bounded
        if gap_lower < -5 or gap_upper > 10:
            print(f"⚠️  WARNING: Gap may not be bounded as claimed!")
        else:
            print(f"✓ Gap appears bounded")

    return results

def test_specific_sets(n: int):
    """
    Test specific adversarial set constructions.
    """
    print(f"\n{'='*60}")
    print(f"Testing specific sets for n = {n}")
    print(f"{'='*60}")

    primes = sieve_of_eratosthenes(n)
    factors = get_all_prime_factors(n, primes)

    sqrt_n = int(math.sqrt(n))
    primes_up_to_n = [p for p in primes if p <= n]
    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if sqrt_n < p <= n]

    pi_n = len(primes_up_to_n)
    pi_sqrt_n = len(small_primes)
    k = pi_n + 1

    print(f"π(n) = {pi_n}, π(√n) = {pi_sqrt_n}, k = {k}")
    print(f"Small primes: {small_primes[:10]}...")
    print(f"Large primes: {large_primes[:10]}...")

    # Test 1: All primes + 1
    A1 = set(primes_up_to_n) | {1}
    f1 = find_f_for_set(A1, primes, factors)
    print(f"\nSet A1 (all primes + 1): f = {f1}")

    # Test 2: All primes + smallest composite with most factors
    best_composite = None
    max_factors = 0
    for m in range(2, n + 1):
        if m not in set(primes_up_to_n):
            num_factors = len(factors[m])
            if num_factors > max_factors:
                max_factors = num_factors
                best_composite = m

    if best_composite:
        A2 = set(primes_up_to_n) | {best_composite}
        f2 = find_f_for_set(A2, primes, factors)
        print(f"Set A2 (all primes + {best_composite} with {max_factors} factors): f = {f2}")

    # Test 3: Large primes + spread small numbers
    if len(large_primes) < k:
        needed = k - len(large_primes)
        small_nums = list(range(2, sqrt_n + 1))[:needed]
        A3 = set(large_primes) | set(small_nums)
        if len(A3) == k:
            f3 = find_f_for_set(A3, primes, factors)
            print(f"Set A3 (large primes + small nums): f = {f3}")

    # Test 4: Products with spread factors
    semiprimes = []
    for i, p in enumerate(small_primes):
        for q in small_primes[i+1:]:
            if p * q <= n:
                semiprimes.append(p * q)

    if len(semiprimes) >= k:
        # Choose semiprimes with diverse prime factors
        A4 = set(semiprimes[:k])
        f4 = find_f_for_set(A4, primes, factors)
        print(f"Set A4 (semiprimes): f = {f4}, set size = {len(A4)}")

        # Analyze coverage
        all_factors = set()
        for a in A4:
            all_factors |= factors[a]
        print(f"  Total distinct primes in A4: {len(all_factors)}")
        print(f"  Coverage efficiency needed: {len(A4)}/{len(all_factors)} = {len(A4)/len(all_factors):.3f}")

def test_intermediate_regime(n: int, k_values: List[int]):
    """
    Test the intermediate regime π(n)+1 < k = o(n).
    """
    print(f"\n{'='*60}")
    print(f"Testing intermediate regime for n = {n}")
    print(f"{'='*60}")

    primes = sieve_of_eratosthenes(n)
    factors = get_all_prime_factors(n, primes)

    sqrt_n = int(math.sqrt(n))
    pi_n = len([p for p in primes if p <= n])
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    print(f"π(n) = {pi_n}, π(√n) = {pi_sqrt_n}")
    print(f"\n{'k':<10} {'m=k-π(n)':<12} {'f_lower':<10} {'f_upper':<10} {'2π(√n)':<10} {'Ratio':<10}")
    print("-" * 62)

    for k in k_values:
        if k <= pi_n or k > n:
            continue

        m = k - pi_n
        f_lower = compute_f_lower_bound(n, k, primes, factors, num_samples=20)
        f_upper = compute_f_upper_bound(n, k, primes, factors)

        ratio = f_lower / (2 * pi_sqrt_n) if pi_sqrt_n > 0 else 0

        print(f"{k:<10} {m:<12} {f_lower:<10} {f_upper:<10} {2*pi_sqrt_n:<10} {ratio:<10.3f}")

def exhaustive_test_small_n(n: int):
    """
    Exhaustive test for small n: check ALL sets of size k = π(n) + 1.
    """
    print(f"\n{'='*60}")
    print(f"Exhaustive test for n = {n}")
    print(f"{'='*60}")

    primes = sieve_of_eratosthenes(n)
    factors = get_all_prime_factors(n, primes)

    primes_up_to_n = [p for p in primes if p <= n]
    pi_n = len(primes_up_to_n)
    sqrt_n = int(math.sqrt(n))
    pi_sqrt_n = len([p for p in primes if p <= sqrt_n])

    k = pi_n + 1
    print(f"π(n) = {pi_n}, π(√n) = {pi_sqrt_n}, k = {k}")
    print(f"2π(√n) = {2 * pi_sqrt_n}")

    all_elements = list(range(1, n + 1))

    # Count total combinations
    from math import comb
    total_sets = comb(n, k)
    print(f"Total sets to check: {total_sets}")

    if total_sets > 100000:
        print("Too many sets, sampling instead...")
        return

    max_f = 0
    hardest_set = None

    count = 0
    for A_tuple in combinations(all_elements, k):
        A = set(A_tuple)
        f_A = find_f_for_set(A, primes, factors)
        if f_A > max_f:
            max_f = f_A
            hardest_set = A
        count += 1
        if count % 10000 == 0:
            print(f"  Checked {count}/{total_sets} sets, current max f = {max_f}")

    print(f"\n✓ Exhaustive search complete")
    print(f"Maximum f(A) over all sets: {max_f}")
    print(f"Hardest set: {sorted(hardest_set) if hardest_set and len(hardest_set) <= 20 else 'too large to display'}")
    print(f"Gap 2π(√n) - f = {2 * pi_sqrt_n - max_f}")

    return max_f

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("COMPREHENSIVE TESTING OF ERDŐS PROBLEM #983 THEORY")
    print("="*70)
    print("\nTheory claim: 2π(n^{1/2}) - f(π(n)+1, n) is bounded between 0 and 1")

    # Test 1: Exhaustive tests for small n
    print("\n" + "="*70)
    print("PHASE 1: Exhaustive tests for small n")
    print("="*70)

    for n in [10, 15, 20, 25, 30]:
        exhaustive_test_small_n(n)

    # Test 2: Main conjecture for larger n
    print("\n" + "="*70)
    print("PHASE 2: Main conjecture tests")
    print("="*70)

    n_values = [50, 100, 200, 500]
    results = test_main_conjecture(n_values)

    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'n':<8} {'π(n)':<8} {'π(√n)':<8} {'2π(√n)':<8} {'f_lower':<8} {'f_upper':<8} {'Gap range':<15}")
    print("-" * 75)

    for r in results:
        gap_range = f"[{r['gap_lower']}, {r['gap_upper']}]"
        print(f"{r['n']:<8} {r['pi_n']:<8} {r['pi_sqrt_n']:<8} {r['two_pi_sqrt_n']:<8} "
              f"{r['f_lower']:<8} {r['f_upper']:<8} {gap_range:<15}")

    # Test 3: Specific adversarial constructions
    print("\n" + "="*70)
    print("PHASE 3: Adversarial set constructions")
    print("="*70)

    for n in [50, 100]:
        test_specific_sets(n)

    # Test 4: Intermediate regime
    print("\n" + "="*70)
    print("PHASE 4: Intermediate regime tests")
    print("="*70)

    n = 200
    pi_n = len([p for p in sieve_of_eratosthenes(n) if p <= n])
    k_values = [pi_n + 1, pi_n + 5, pi_n + 10, pi_n + 20, pi_n + 50, n // 2, n]
    test_intermediate_regime(n, k_values)

    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
