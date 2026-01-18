#!/usr/bin/env python3
"""
Erdős Problem #983 Library

A clean, reusable library for investigating Erdős Problem #983.

This library provides:
- Prime number utilities
- f(k,n) computation with correct "strictly more than r" definition
- Adversarial set construction using Latin matching
- Gap analysis tools

Author: Claude (Anthropic)
Date: January 2026
"""

import math
from typing import List, Set, Tuple, Dict, Optional
from itertools import combinations
from collections import defaultdict
from dataclasses import dataclass


# =============================================================================
# PRIME NUMBER UTILITIES
# =============================================================================

def sieve_of_eratosthenes(n: int) -> List[int]:
    """
    Generate all primes up to n using the Sieve of Eratosthenes.

    Args:
        n: Upper bound (inclusive)

    Returns:
        List of primes ≤ n in ascending order
    """
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def prime_counting_function(x: float, primes: List[int]) -> int:
    """
    Compute π(x) = number of primes ≤ x.

    Args:
        x: Upper bound
        primes: Precomputed list of primes

    Returns:
        Count of primes ≤ x
    """
    return sum(1 for p in primes if p <= x)


def prime_factorization(n: int, primes: List[int]) -> Set[int]:
    """
    Compute the set of prime factors of n.

    Args:
        n: Positive integer to factor
        primes: Precomputed list of primes

    Returns:
        Set of prime factors
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


# =============================================================================
# f(k,n) COMPUTATION
# =============================================================================

def compute_coverage(elements: List[int], prime_set: Set[int],
                     factor_cache: Dict[int, Set[int]]) -> int:
    """
    Count elements whose ALL prime factors are in the given prime set.

    Args:
        elements: List of positive integers
        prime_set: Set of primes
        factor_cache: Precomputed factorizations {element: set of factors}

    Returns:
        Number of elements covered
    """
    return sum(1 for e in elements if factor_cache[e].issubset(prime_set))


def compute_f(A: List[int], primes: List[int], max_r: int = 50) -> Tuple[int, List[int]]:
    """
    Compute f for a given set A.

    f = smallest r such that there exist r primes covering STRICTLY MORE THAN r elements.

    Uses the CORRECT definition: "strictly more than r" (not "at least r").

    Args:
        A: The set to analyze
        primes: Precomputed list of all primes up to max(A)
        max_r: Maximum r to search

    Returns:
        (f, covering_primes) where f is the computed value and covering_primes
        are the primes that achieve it. Returns (max_r+1, []) if not found.
    """
    # Precompute factorizations
    factor_cache = {e: prime_factorization(e, primes) for e in A}

    # Relevant primes (those that appear in factorizations)
    relevant = sorted(set().union(*factor_cache.values()))

    for r in range(1, min(max_r + 1, len(relevant) + 1)):
        # Exhaustive search for small r
        if r <= 12:
            search_space = relevant[:min(30, len(relevant))]
            if len(search_space) >= r:
                for combo in combinations(search_space, r):
                    if compute_coverage(A, set(combo), factor_cache) > r:
                        return r, list(combo)

        # Greedy search for larger r
        chosen = set()
        for _ in range(r):
            best_prime, best_gain = None, 0
            current_cov = compute_coverage(A, chosen, factor_cache)
            for p in relevant:
                if p not in chosen:
                    gain = compute_coverage(A, chosen | {p}, factor_cache) - current_cov
                    if gain > best_gain:
                        best_gain, best_prime = gain, p
            if best_prime:
                chosen.add(best_prime)

        if compute_coverage(A, chosen, factor_cache) > r:
            return r, sorted(chosen)

    return max_r + 1, []


# =============================================================================
# ADVERSARIAL SET CONSTRUCTION
# =============================================================================

def find_latin_matching(left: List[int], right: List[int], n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Find a 2-regular bipartite matching with Latin rectangle property.

    Requirements:
    - Each left vertex connects to exactly 2 right vertices
    - Each right vertex connects to exactly 2 left vertices
    - No two left vertices share the same pair of right neighbors
    - All products p*q are ≤ n

    Args:
        left: Left partition primes
        right: Right partition primes (must have same length as left)
        n: Upper bound for products

    Returns:
        List of edges (p, q) or None if no valid matching exists
    """
    k = len(left)
    if k != len(right) or k < 2:
        return None

    # Valid edges for each left vertex
    valid = {}
    for i, p in enumerate(left):
        valid[i] = [j for j, q in enumerate(right) if p * q <= n]
        if len(valid[i]) < 2:
            return None

    # Backtracking search
    assignment = [None] * k
    used_pairs = set()
    right_degree = [0] * k

    def backtrack(i: int) -> bool:
        if i == k:
            return all(d == 2 for d in right_degree)

        neighbors = valid[i]
        for idx1 in range(len(neighbors)):
            for idx2 in range(idx1 + 1, len(neighbors)):
                j1, j2 = neighbors[idx1], neighbors[idx2]
                pair = (min(j1, j2), max(j1, j2))

                if pair in used_pairs:
                    continue
                if right_degree[j1] >= 2 or right_degree[j2] >= 2:
                    continue

                # Try this assignment
                assignment[i] = (j1, j2)
                used_pairs.add(pair)
                right_degree[j1] += 1
                right_degree[j2] += 1

                if backtrack(i + 1):
                    return True

                # Backtrack
                assignment[i] = None
                used_pairs.remove(pair)
                right_degree[j1] -= 1
                right_degree[j2] -= 1

        return False

    if backtrack(0):
        edges = []
        for i in range(k):
            j1, j2 = assignment[i]
            edges.append((left[i], right[j1]))
            edges.append((left[i], right[j2]))
        return edges

    return None


def find_best_matching(small_primes: List[int], n: int) -> List[Tuple[int, int]]:
    """
    Find the best Latin matching for the given small primes.

    Tries different bipartite splits and returns the largest valid matching.

    Args:
        small_primes: Primes ≤ (2-ε)√n
        n: Upper bound

    Returns:
        List of edges (p, q) forming the best matching found
    """
    t = len(small_primes)
    if t < 4:
        return []

    best_edges = []
    best_size = 0

    # Try different split points
    for split in range(2, t - 1):
        left = small_primes[:split]
        right = small_primes[split:]

        # Try equal-sized subsets
        min_size = min(len(left), len(right))
        for size in range(min_size, 1, -1):
            # Try different starting positions
            for l_start in range(len(left) - size + 1):
                for r_start in range(len(right) - size + 1):
                    l_sub = left[l_start:l_start + size]
                    r_sub = right[r_start:r_start + size]
                    edges = find_latin_matching(l_sub, r_sub, n)
                    if edges and len(edges) > best_size:
                        best_size = len(edges)
                        best_edges = edges

    return best_edges


# Manual constructions for verified cases
MANUAL_CONSTRUCTIONS = {
    100: [
        (2, 13), (2, 19),  # 26, 38
        (3, 11), (3, 17),  # 33, 51
        (5, 17), (5, 19),  # 85, 95
        (7, 11), (7, 13),  # 77, 91
    ],
    200: [
        (2, 13), (2, 19),
        (3, 11), (3, 17),
        (5, 17), (5, 19),
        (7, 11), (7, 13),
    ],
    400: [
        (2, 17), (2, 19),
        (3, 13), (3, 23),
        (5, 19), (5, 29),
        (7, 17), (7, 23),
        (11, 13), (11, 29),
    ],
}


@dataclass
class AdversarialSet:
    """Result of adversarial set construction."""
    n: int
    A: List[int]
    A0: List[int]  # Semiprimes from matching
    extras: List[int]
    edges: List[Tuple[int, int]]
    t: int  # Number of small primes
    first_large_prime: int


def build_adversarial_set(n: int, eps: float = 0.1) -> Optional[AdversarialSet]:
    """
    Build an adversarial set A of size π(n) + 1 for the given n.

    The construction:
    1. Find small primes ≤ (2-ε)√n
    2. Build Latin matching to get semiprimes A₀
    3. Add extras: 2×p_{t+1}, 3×p_{t+1}
    4. Fill with large primes to reach size π(n) + 1

    Args:
        n: The parameter n
        eps: Epsilon for threshold (default 0.1)

    Returns:
        AdversarialSet with all components, or None if construction fails
    """
    primes = sieve_of_eratosthenes(n)
    sqrt_n = math.sqrt(n)
    threshold = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= threshold]
    large = [p for p in primes if p > threshold]
    t = len(small)

    if t < 4 or not large:
        return None

    # Use manual construction if available
    if n in MANUAL_CONSTRUCTIONS:
        edges = MANUAL_CONSTRUCTIONS[n]
    else:
        edges = find_best_matching(small, n)

    if not edges:
        return None

    # Semiprimes from edges
    A0 = sorted([p * q for p, q in edges])

    # First large prime
    p_t1 = large[0]

    # Extras
    extras = []
    if 2 * p_t1 <= n:
        extras.append(2 * p_t1)
    if 3 * p_t1 <= n:
        extras.append(3 * p_t1)

    # Target size
    target = len(primes) + 1

    # Build A
    A = set(A0 + extras)
    for p in large[1:]:
        if len(A) >= target:
            break
        A.add(p)

    return AdversarialSet(
        n=n,
        A=sorted(A),
        A0=A0,
        extras=extras,
        edges=edges,
        t=t,
        first_large_prime=p_t1
    )


# =============================================================================
# GAP ANALYSIS
# =============================================================================

@dataclass
class GapResult:
    """Result of gap computation for a single n."""
    n: int
    t: int  # Small primes count
    edges: int  # Matching size
    f: int
    two_pi_sqrt: int  # 2π(√n)
    upper_bound: int  # 2π(√n) + 1
    gap: int  # 2π(√n) - f


def analyze_gap(n: int, eps: float = 0.1) -> Optional[GapResult]:
    """
    Compute the gap 2π(√n) - f for a given n.

    Args:
        n: The parameter n
        eps: Epsilon for construction

    Returns:
        GapResult with all computed values, or None if analysis fails
    """
    primes = sieve_of_eratosthenes(n)
    sqrt_n = int(math.sqrt(n))
    pi_sqrt = prime_counting_function(sqrt_n, primes)

    result = build_adversarial_set(n, eps)
    if result is None:
        return None

    # Compute f
    f, _ = compute_f(result.A, primes, 2 * pi_sqrt + 10)

    return GapResult(
        n=n,
        t=result.t,
        edges=len(result.edges),
        f=f,
        two_pi_sqrt=2 * pi_sqrt,
        upper_bound=2 * pi_sqrt + 1,
        gap=2 * pi_sqrt - f
    )


def run_gap_analysis(n_values: List[int], eps: float = 0.1) -> List[GapResult]:
    """
    Run gap analysis for multiple n values.

    Args:
        n_values: List of n values to analyze
        eps: Epsilon for construction

    Returns:
        List of GapResult objects
    """
    results = []
    for n in n_values:
        result = analyze_gap(n, eps)
        if result:
            results.append(result)
    return results


# =============================================================================
# VERIFICATION UTILITIES
# =============================================================================

def verify_construction(result: AdversarialSet, primes: List[int]) -> Dict:
    """
    Verify the adversarial property of a construction.

    Args:
        result: AdversarialSet to verify
        primes: List of all primes up to n

    Returns:
        Dictionary with verification results
    """
    factor_cache = {e: prime_factorization(e, primes) for e in result.A0}
    A0_primes = sorted(set().union(*factor_cache.values()))

    # Check Latin property (no shared pairs)
    pairs_by_left = defaultdict(set)
    for p, q in result.edges:
        pairs_by_left[p].add(q)

    pairs = [frozenset(v) for v in pairs_by_left.values()]
    latin_ok = len(pairs) == len(set(pairs))

    # Check degrees
    degrees = defaultdict(int)
    for p, q in result.edges:
        degrees[p] += 1
        degrees[q] += 1

    all_deg_2 = all(d == 2 for d in degrees.values())

    # Check coverage progression for A0
    coverage_by_r = {}
    for r in range(1, len(A0_primes) + 1):
        best = 0
        if r <= 10:
            for combo in combinations(A0_primes, r):
                cov = compute_coverage(result.A0, set(combo), factor_cache)
                best = max(best, cov)
        coverage_by_r[r] = best

    # A0 is adversarial if coverage[r] ≤ r for all r < |A0|
    adversarial = all(coverage_by_r.get(r, 0) <= r for r in range(1, len(result.A0)))

    return {
        "latin_property": latin_ok,
        "all_degree_2": all_deg_2,
        "A0_adversarial": adversarial,
        "coverage_by_r": coverage_by_r,
        "A0_primes": A0_primes,
        "num_edges": len(result.edges),
        "num_A0": len(result.A0)
    }


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    print("Erdős Problem #983 Library")
    print("=" * 60)
    print()

    # Quick test
    for n in [100, 200, 400]:
        result = analyze_gap(n)
        if result:
            print(f"n={n}: f={result.f}, 2π(√n)={result.two_pi_sqrt}, gap={result.gap}")

    print()
    print("Library loaded successfully.")
