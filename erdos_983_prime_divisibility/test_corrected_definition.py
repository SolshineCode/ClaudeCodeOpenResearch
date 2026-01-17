#!/usr/bin/env python3
"""
Test Erdős Problem #983 with the CORRECTED definition.

Per Woett's correction (Oct 2025) and Tao's confirmation (Jan 2026):
- Correct: r primes must cover STRICTLY MORE THAN r elements
- Incorrect: r primes cover "at least r" elements

Reference: [Er70b, p. 138] - "Some applications of graph theory to number theory" (1969)

This changes the problem fundamentally:
- With "at least r": r=1 works whenever A contains any prime (degenerate)
- With "strictly > r": r=1 requires covering >1 elements with 1 prime

f(k,n) = smallest r such that:
  FOR ANY A ⊆ {1,...,n} with |A| = k,
  THERE EXIST primes p₁,...,pᵣ such that
  STRICTLY MORE THAN r elements a ∈ A
  have all prime divisors in {p₁,...,pᵣ}
"""

import sys
from typing import List, Set, Dict, Tuple
from itertools import combinations
from utils import (
    sieve_of_eratosthenes, prime_factors, pi,
    count_covered, find_f_for_set
)


def compute_element_factors(elements: List[int], primes: List[int]) -> Dict[int, Set[int]]:
    """Pre-compute prime factors for all elements."""
    factors = {}
    for e in elements:
        factors[e] = prime_factors(e, primes)
    return factors


def find_f_for_set_corrected(elements: List[int], all_primes: List[int],
                              element_factors: Dict[int, Set[int]],
                              max_r: int = None, verbose: bool = False) -> Tuple[int, Set[int]]:
    """
    Find minimum r such that r primes cover STRICTLY MORE THAN r elements.

    Returns (r, best_prime_set) or (-1, set()) if not found.
    """
    if max_r is None:
        max_r = min(len(all_primes), len(elements))

    # Get primes that could be useful (factors of elements in A)
    relevant_primes = set()
    for e in elements:
        relevant_primes.update(element_factors.get(e, set()))
    relevant_primes = sorted(relevant_primes)

    if verbose:
        print(f"  Relevant primes: {len(relevant_primes)}")

    for r in range(1, max_r + 1):
        best_coverage = 0
        best_primes = set()

        # For small r, try exhaustive search
        if r <= 12 and len(relevant_primes) >= r:
            search_primes = relevant_primes[:min(40, len(relevant_primes))]
            for prime_combo in combinations(search_primes, r):
                prime_set = set(prime_combo)
                coverage = count_covered(elements, prime_set, element_factors)
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_primes = prime_set
                if coverage > r:  # STRICT inequality
                    if verbose:
                        print(f"  r={r}: {prime_set} covers {coverage} > {r} elements")
                    return r, best_primes

        # Also try greedy approach
        covered_elements = set()
        chosen_primes = set()

        for _ in range(r):
            best_prime = None
            best_gain = -1

            for p in relevant_primes:
                if p in chosen_primes:
                    continue
                test_set = chosen_primes | {p}
                new_coverage = count_covered(elements, test_set, element_factors)
                gain = new_coverage - len(covered_elements)
                if gain > best_gain:
                    best_gain = gain
                    best_prime = p

            if best_prime is not None:
                chosen_primes.add(best_prime)
                covered_elements = {e for e in elements
                                   if all(f in chosen_primes for f in element_factors.get(e, set()))}

        greedy_coverage = len(covered_elements)
        if greedy_coverage > best_coverage:
            best_coverage = greedy_coverage
            best_primes = chosen_primes

        if best_coverage > r:  # STRICT inequality
            if verbose:
                print(f"  r={r}: greedy found {best_primes} covers {best_coverage} > {r} elements")
            return r, best_primes

    return -1, set()


def test_prime_only_set(n: int):
    """
    Test: A = all primes ≤ n.

    With correct definition, f should be UNDEFINED for this set
    because r primes can only cover r elements (the primes themselves),
    never strictly more than r.
    """
    print(f"\n{'='*60}")
    print(f"Test: Prime-only set for n={n}")
    print(f"{'='*60}")

    primes = sieve_of_eratosthenes(n)
    A = primes.copy()  # All primes up to n

    print(f"|A| = {len(A)} (all primes ≤ {n})")
    print(f"π(n) = {len(primes)}")

    element_factors = compute_element_factors(A, primes)

    # For any r primes chosen from A, we cover exactly r elements
    # This is NOT > r, so f is undefined
    r, best_primes = find_f_for_set_corrected(A, primes, element_factors, max_r=20, verbose=True)

    if r == -1:
        print(f"Result: f is UNDEFINED for this set (as expected)")
        print("  Explanation: Any r primes cover exactly r prime elements, never > r")
        return True
    else:
        print(f"Result: f = {r} (UNEXPECTED - should be undefined)")
        return False


def test_primes_plus_one(n: int):
    """
    Test: A = {1} ∪ all primes ≤ n.

    With |A| = π(n) + 1, this is the degenerate case.
    Element 1 is covered by any prime set (has no prime factors).
    But r primes still only cover r+1 elements total (1 plus r primes).
    For r=1: cover 1 and one prime = 2 elements > 1. So f=1!
    """
    print(f"\n{'='*60}")
    print(f"Test: Primes plus 1 for n={n}")
    print(f"{'='*60}")

    primes = sieve_of_eratosthenes(n)
    A = [1] + primes  # 1 plus all primes

    print(f"|A| = {len(A)} = π(n) + 1 = {len(primes)} + 1")

    element_factors = compute_element_factors(A, primes)

    r, best_primes = find_f_for_set_corrected(A, primes, element_factors, max_r=20, verbose=True)

    print(f"Result: f = {r}")
    if r == 1:
        print("  Explanation: 1 prime p covers {1, p} = 2 elements > 1")
    return r


def woett_lower_bound_construction(n: int, epsilon: float = 0.1):
    """
    Implement Woett's lower bound construction from [Er70b].

    Let p₁ < p₂ < ... < pₜ be primes ≤ (2-ε)√n.

    A₀: t pairs of products pᵢpⱼ < n where each pᵢ appears in exactly 2 products.

    A := A₀ ∪ {2·p_{t+1}, 3·p_{t+1}} ∪ ⋃_{i=t+2}^{π(n)} {pᵢ}

    For this set, r = t+1, giving lower bound f(π(n)+1, n) > t = π((2-ε)√n).
    """
    print(f"\n{'='*60}")
    print(f"Woett's Lower Bound Construction for n={n}, ε={epsilon}")
    print(f"{'='*60}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = n ** 0.5
    threshold = (2 - epsilon) * sqrt_n

    # Primes ≤ (2-ε)√n
    small_primes = [p for p in primes if p <= threshold]
    t = len(small_primes)

    print(f"√n = {sqrt_n:.2f}")
    print(f"(2-ε)√n = {threshold:.2f}")
    print(f"t = π((2-ε)√n) = {t}")
    print(f"Small primes: {small_primes[:10]}{'...' if t > 10 else ''}")

    # Build A₀: pairs of products where each prime appears exactly twice
    # This is the tricky part - need to pair up primes carefully
    A0 = []
    used_count = {p: 0 for p in small_primes}

    # Simple approach: pair consecutive primes
    for i in range(0, t - 1, 2):
        p, q = small_primes[i], small_primes[i + 1]
        if p * q <= n:
            A0.append(p * q)
            used_count[p] += 1
            used_count[q] += 1

    # Also pair primes to ensure each appears twice
    for i in range(len(small_primes)):
        if used_count[small_primes[i]] < 2:
            for j in range(i + 1, len(small_primes)):
                if used_count[small_primes[j]] < 2:
                    p, q = small_primes[i], small_primes[j]
                    if p * q <= n and p * q not in A0:
                        A0.append(p * q)
                        used_count[p] += 1
                        used_count[q] += 1
                        if used_count[small_primes[i]] >= 2:
                            break

    print(f"|A₀| = {len(A0)} (semiprimes from small primes)")

    # Get remaining primes
    remaining_primes = [p for p in primes if p > threshold]

    if len(remaining_primes) < 2:
        print("Not enough large primes for construction")
        return None

    # {2·p_{t+1}, 3·p_{t+1}}
    p_t1 = remaining_primes[0]
    extra_composites = []
    if 2 * p_t1 <= n:
        extra_composites.append(2 * p_t1)
    if 3 * p_t1 <= n:
        extra_composites.append(3 * p_t1)

    print(f"p_{{t+1}} = {p_t1}")
    print(f"Extra composites: {extra_composites}")

    # Remaining primes to fill up to π(n) + 1
    # A = A₀ ∪ extra_composites ∪ remaining_primes[1:]
    current_size = len(A0) + len(extra_composites)
    target_size = len(primes) + 1  # π(n) + 1

    primes_to_add = []
    for p in remaining_primes[1:]:
        if current_size + len(primes_to_add) >= target_size:
            break
        primes_to_add.append(p)

    # Construct A
    A = list(set(A0 + extra_composites + primes_to_add))
    A.sort()

    print(f"Target |A| = π(n) + 1 = {target_size}")
    print(f"Actual |A| = {len(A)}")

    # Compute f for this set
    element_factors = compute_element_factors(A, primes)

    print(f"\nComputing f for Woett's construction...")
    r, best_primes = find_f_for_set_corrected(A, primes, element_factors,
                                               max_r=t + 10, verbose=True)

    print(f"\nResult: f = {r}")
    print(f"Expected lower bound: r > t = {t}")
    print(f"2π(√n) = {2 * pi(int(sqrt_n), primes)}")

    return r, t


def test_adversarial_semiprimes(n: int):
    """
    Test an adversarial set of semiprimes designed to maximize f.

    Strategy: Choose semiprimes p·q where p ≤ √n and q > √n.
    Each such semiprime requires BOTH its factors to be covered.
    Since q > √n, each large prime q can only appear in one semiprime ≤ n.
    """
    print(f"\n{'='*60}")
    print(f"Adversarial Semiprimes for n={n}")
    print(f"{'='*60}")

    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(n ** 0.5)

    small_primes = [p for p in primes if p <= sqrt_n]
    large_primes = [p for p in primes if p > sqrt_n]

    print(f"Small primes (≤ √n): {len(small_primes)}")
    print(f"Large primes (> √n): {len(large_primes)}")

    # Create semiprimes p·q with p small, q large
    semiprimes = []
    for p in small_primes:
        for q in large_primes:
            if p * q <= n:
                semiprimes.append(p * q)

    semiprimes = sorted(set(semiprimes))
    print(f"Semiprimes p·q (p≤√n, q>√n): {len(semiprimes)}")

    # Take first k = π(n) + 1 semiprimes
    k = len(primes) + 1
    if len(semiprimes) < k:
        print(f"Not enough semiprimes for k = {k}")
        A = semiprimes
    else:
        A = semiprimes[:k]

    print(f"|A| = {len(A)}")

    element_factors = compute_element_factors(A, primes)

    r, best_primes = find_f_for_set_corrected(A, primes, element_factors,
                                               max_r=50, verbose=True)

    print(f"\nResult: f = {r}")
    print(f"2π(√n) = {2 * pi(sqrt_n, primes)}")

    return r


def compute_f_worst_case(n: int, k: int, sample_size: int = 100):
    """
    Estimate f(k, n) by sampling many sets and taking the maximum.

    f(k, n) = min r such that for ALL A, r primes cover > r elements.

    Equivalently: max over all A of (min r for that A).
    """
    print(f"\n{'='*60}")
    print(f"Estimating f({k}, {n}) via sampling")
    print(f"{'='*60}")

    import random

    primes = sieve_of_eratosthenes(n)

    # Get all possible elements
    all_elements = list(range(1, n + 1))

    # Pre-compute factors for all elements
    all_factors = compute_element_factors(all_elements, primes)

    max_f = 0
    hardest_set = None

    for trial in range(sample_size):
        # Random subset of size k
        A = random.sample(all_elements, k)

        # Extract factors for this set
        element_factors = {e: all_factors[e] for e in A}

        r, _ = find_f_for_set_corrected(A, primes, element_factors, max_r=30)

        if r > max_f:
            max_f = r
            hardest_set = A

    print(f"Max f found over {sample_size} random samples: {max_f}")
    print(f"2π(√n) = {2 * pi(int(n**0.5), primes)}")

    return max_f, hardest_set


def main():
    print("="*60)
    print("Erdős Problem #983 - CORRECTED DEFINITION")
    print("="*60)
    print()
    print("Definition: r primes must cover STRICTLY MORE THAN r elements")
    print("Reference: [Er70b, p. 138], Woett (Oct 2025), Tao (Jan 2026)")
    print()

    # Test 1: Prime-only set (should be undefined)
    test_prime_only_set(100)

    # Test 2: Primes plus 1
    test_primes_plus_one(100)

    # Test 3: Woett's construction
    for n in [100, 500, 1000]:
        woett_lower_bound_construction(n)

    # Test 4: Adversarial semiprimes
    for n in [100, 500, 1000]:
        test_adversarial_semiprimes(n)

    # Test 5: Random sampling to estimate worst case
    for n in [100, 200, 500]:
        k = pi(n, sieve_of_eratosthenes(n)) + 1
        compute_f_worst_case(n, k, sample_size=50)

    print("\n" + "="*60)
    print("Testing complete")
    print("="*60)


if __name__ == "__main__":
    main()
