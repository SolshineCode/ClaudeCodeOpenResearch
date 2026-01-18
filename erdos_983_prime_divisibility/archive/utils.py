"""
Shared utility functions for Erdős Problem #983 analysis.

This module provides common mathematical functions used across all test files.
"""

from typing import List, Set, Dict, Tuple
from itertools import combinations


def sieve_of_eratosthenes(n: int) -> List[int]:
    """Return list of all primes up to n using the Sieve of Eratosthenes."""
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
    """
    Return set of prime factors of n.

    Args:
        n: The integer to factorize
        primes: List of primes to use for factorization (must include all primes up to sqrt(n))

    Returns:
        Set of prime factors of n
    """
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


def is_covered(element: int, prime_set: Set[int], element_factors: Dict[int, Set[int]]) -> bool:
    """
    Check if an element is covered by a set of primes.

    An element is covered if ALL its prime factors are in the prime set.
    Element 1 is always covered (has no prime factors).

    Args:
        element: The element to check
        prime_set: Set of primes to check coverage against
        element_factors: Pre-computed mapping of elements to their prime factors

    Returns:
        True if element is covered by prime_set
    """
    factors = element_factors.get(element, set())
    if not factors:  # Element 1 or any with no factors
        return True
    return factors.issubset(prime_set)


def count_covered(elements: List[int], prime_set: Set[int],
                  element_factors: Dict[int, Set[int]]) -> int:
    """
    Count how many elements are covered by a set of primes.

    Args:
        elements: List of elements to check
        prime_set: Set of primes to check coverage against
        element_factors: Pre-computed mapping of elements to their prime factors

    Returns:
        Number of elements covered by prime_set
    """
    return sum(1 for e in elements if is_covered(e, prime_set, element_factors))


def find_f_for_set(elements: List[int], all_primes: List[int],
                   element_factors: Dict[int, Set[int]],
                   max_r: int = None,
                   strict: bool = True) -> int:
    """
    Find the minimum r such that r primes cover the required number of elements.

    IMPORTANT: Per Woett's correction (Oct 2025), the correct Erdős definition
    requires STRICTLY MORE THAN r elements (coverage > r), not "at least r".

    Args:
        elements: The set A to analyze
        all_primes: List of all available primes
        element_factors: Pre-computed mapping of elements to their prime factors
        max_r: Maximum r to try (defaults to len(all_primes))
        strict: If True, require coverage > r (correct Erdős definition)
                If False, require coverage >= r (incorrect, for comparison only)

    Returns:
        The minimum r achieving the required coverage, or -1 if not found
    """
    if max_r is None:
        max_r = min(len(all_primes), len(elements))

    # Get primes that could be useful (factors of elements in A)
    relevant_primes = set()
    for e in elements:
        relevant_primes.update(element_factors.get(e, set()))
    relevant_primes = sorted(relevant_primes)

    # Determine the coverage threshold based on strict mode
    # strict=True: need coverage > r (strictly more than r)
    # strict=False: need coverage >= r (at least r) - INCORRECT but for comparison
    def meets_threshold(coverage: int, r: int) -> bool:
        return coverage > r if strict else coverage >= r

    for r in range(1, max_r + 1):
        # Try to find r primes covering the required number of elements
        # First try greedy approach with relevant primes
        best_coverage = 0

        # Greedy: iteratively pick the prime that covers the most uncovered elements
        if r <= 10:  # For small r, try exhaustive search on relevant primes
            search_primes = relevant_primes[:min(30, len(relevant_primes))]
            if len(search_primes) >= r:
                for prime_combo in combinations(search_primes, r):
                    prime_set = set(prime_combo)
                    coverage = count_covered(elements, prime_set, element_factors)
                    best_coverage = max(best_coverage, coverage)
                    if meets_threshold(coverage, r):
                        break

        # Also try greedy approach
        if best_coverage < r:
            covered_elements = set()
            chosen_primes = set()

            for _ in range(r):
                best_prime = None
                best_gain = -1

                for p in relevant_primes:
                    if p in chosen_primes:
                        continue
                    # Count new elements covered if we add p
                    test_set = chosen_primes | {p}
                    new_coverage = count_covered(elements, test_set, element_factors)
                    gain = new_coverage - len(covered_elements)
                    if gain > best_gain:
                        best_gain = gain
                        best_prime = p

                if best_prime is not None:
                    chosen_primes.add(best_prime)
                    covered_elements = {e for e in elements
                                       if is_covered(e, chosen_primes, element_factors)}

            best_coverage = max(best_coverage, len(covered_elements))

        if meets_threshold(best_coverage, r):
            return r

    return -1


def get_squarefree_composites(n: int, primes: List[int]) -> List[Tuple[int, Set[int]]]:
    """
    Generate all squarefree composite numbers up to n with their prime factors.

    Args:
        n: Upper bound
        primes: List of primes to use

    Returns:
        List of (number, factors) tuples, sorted by number of factors (descending)
    """
    composites = []
    prime_set = set(primes)

    for m in range(2, n + 1):
        if m in prime_set:
            continue
        factors = prime_factors(m, primes)
        if len(factors) >= 2:
            # Check squarefree
            product = 1
            for p in factors:
                product *= p
            if product == m:
                composites.append((m, factors))

    # Sort by number of prime factors (descending) to prioritize semiprimes
    composites.sort(key=lambda x: len(x[1]))
    return composites


def pi(n: int, primes: List[int] = None) -> int:
    """
    Return the prime counting function pi(n).

    Args:
        n: Upper bound
        primes: Optional pre-computed list of primes

    Returns:
        Number of primes <= n
    """
    if primes is None:
        primes = sieve_of_eratosthenes(n)
    return sum(1 for p in primes if p <= n)
