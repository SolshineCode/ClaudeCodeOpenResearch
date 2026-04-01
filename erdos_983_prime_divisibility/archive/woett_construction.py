#!/usr/bin/env python3
"""
Correct implementation of Woett's lower bound construction from [Er70b].

This constructs the adversarial set A that achieves f(π(n)+1, n) ≥ t+1
where t = π((2-ε)√n).

The key insight is that A₀ must be a 2-regular graph on the small primes,
meaning each prime appears in EXACTLY 2 products.
"""

from typing import List, Set, Dict, Tuple, Optional
from itertools import combinations
from utils import sieve_of_eratosthenes, prime_factors, pi, count_covered


def find_2_regular_subgraph(nodes: List[int], valid_edges: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
    """
    Find a 2-regular subgraph on all nodes using only valid edges.

    A 2-regular graph has every vertex with degree exactly 2.
    For n vertices, this means n edges forming disjoint cycles covering all vertices.

    Uses backtracking to find a valid 2-regular subgraph.
    """
    n = len(nodes)
    if n < 3:
        return None

    # Build adjacency information
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    adj = {node: [] for node in nodes}
    for u, v in valid_edges:
        if u in node_to_idx and v in node_to_idx:
            adj[u].append(v)
            adj[v].append(u)

    # Check if degree at least 2 for all nodes
    for node in nodes:
        if len(adj[node]) < 2:
            return None

    # Backtracking search for 2-regular subgraph
    degree = {node: 0 for node in nodes}
    chosen_edges = []

    def backtrack(edge_idx: int) -> bool:
        # Check if we have a valid 2-regular graph
        if all(d == 2 for d in degree.values()):
            return True

        if edge_idx >= len(valid_edges):
            return False

        u, v = valid_edges[edge_idx]
        if u not in node_to_idx or v not in node_to_idx:
            return backtrack(edge_idx + 1)

        # Try including this edge
        if degree[u] < 2 and degree[v] < 2:
            degree[u] += 1
            degree[v] += 1
            chosen_edges.append((u, v))

            if backtrack(edge_idx + 1):
                return True

            # Backtrack
            degree[u] -= 1
            degree[v] -= 1
            chosen_edges.pop()

        # Try not including this edge
        return backtrack(edge_idx + 1)

    if backtrack(0):
        return chosen_edges
    return None


def construct_woett_set(n: int, epsilon: float = 0.1, verbose: bool = True) -> Tuple[List[int], int, int]:
    """
    Construct Woett's adversarial set A for n.

    Returns: (A, t, expected_r) where:
        - A is the adversarial set with |A| = π(n) + 1
        - t = π((2-ε)√n) (number of small primes)
        - expected_r = t + 1 (the expected value of f for this set)
    """
    primes = sieve_of_eratosthenes(n)
    sqrt_n = n ** 0.5
    threshold = (2 - epsilon) * sqrt_n

    # Small primes: p ≤ (2-ε)√n
    small_primes = [p for p in primes if p <= threshold]
    t = len(small_primes)

    if verbose:
        print(f"\nn = {n}")
        print(f"√n = {sqrt_n:.2f}")
        print(f"(2-ε)√n = {threshold:.2f}")
        print(f"t = π((2-ε)√n) = {t}")
        print(f"Small primes: {small_primes}")

    # Find valid edges: pairs (p, q) with p*q ≤ n
    valid_edges = []
    for i, p in enumerate(small_primes):
        for q in small_primes[i+1:]:
            if p * q <= n:
                valid_edges.append((p, q))

    if verbose:
        print(f"Valid pairs (product ≤ n): {len(valid_edges)}")

    # Find 2-regular subgraph
    edges = find_2_regular_subgraph(small_primes, valid_edges)

    if edges is None:
        if verbose:
            print("WARNING: Could not find 2-regular subgraph!")
            print("Falling back to greedy construction...")

        # Fallback: use as many edges as possible
        degree = {p: 0 for p in small_primes}
        edges = []
        for p, q in sorted(valid_edges, key=lambda e: e[0] * e[1]):
            if degree[p] < 2 and degree[q] < 2:
                edges.append((p, q))
                degree[p] += 1
                degree[q] += 1

    # A₀ = products from the 2-regular subgraph
    A0 = [p * q for p, q in edges]

    if verbose:
        print(f"|A₀| = {len(A0)}")
        print(f"A₀ = {sorted(A0)}")

        # Verify each small prime appears exactly twice
        prime_count = {p: 0 for p in small_primes}
        for p, q in edges:
            prime_count[p] += 1
            prime_count[q] += 1
        print(f"Prime occurrence counts: {prime_count}")

    # Get remaining primes (larger than threshold)
    remaining_primes = [p for p in primes if p > threshold]

    if len(remaining_primes) < 1:
        if verbose:
            print("Not enough large primes!")
        return [], t, t + 1

    p_t1 = remaining_primes[0]  # First prime after threshold

    # Extra composites: {2·p_{t+1}, 3·p_{t+1}} if ≤ n
    extra = []
    if 2 * p_t1 <= n:
        extra.append(2 * p_t1)
    if 3 * p_t1 <= n:
        extra.append(3 * p_t1)

    if verbose:
        print(f"p_{{t+1}} = {p_t1}")
        print(f"Extra composites: {extra}")

    # Fill with remaining large primes to reach |A| = π(n) + 1
    target_size = len(primes) + 1
    current = set(A0 + extra)

    for p in remaining_primes[1:]:
        if len(current) >= target_size:
            break
        current.add(p)

    A = sorted(current)

    if verbose:
        print(f"Target |A| = π(n) + 1 = {target_size}")
        print(f"Actual |A| = {len(A)}")
        print(f"A = {A[:15]}{'...' if len(A) > 15 else ''}")

    return A, t, t + 1


def compute_element_factors(elements: List[int], primes: List[int]) -> Dict[int, Set[int]]:
    """Pre-compute prime factors for all elements."""
    factors = {}
    for e in elements:
        factors[e] = prime_factors(e, primes)
    return factors


def find_minimum_r(elements: List[int], primes: List[int],
                   element_factors: Dict[int, Set[int]],
                   max_r: int = None, verbose: bool = False) -> Tuple[int, Set[int]]:
    """
    Find minimum r such that r primes cover STRICTLY MORE THAN r elements.

    Uses more exhaustive search for accuracy.
    """
    if max_r is None:
        max_r = min(len(primes), len(elements))

    # Get relevant primes
    relevant_primes = set()
    for e in elements:
        relevant_primes.update(element_factors.get(e, set()))
    relevant_primes = sorted(relevant_primes)

    if verbose:
        print(f"Relevant primes: {len(relevant_primes)}")
        print(f"Testing r from 1 to {max_r}")

    for r in range(1, max_r + 1):
        best_coverage = 0
        best_primes = set()

        # Limit search space for large r
        search_limit = min(len(relevant_primes), r + 20)
        search_primes = relevant_primes[:search_limit]

        if len(search_primes) < r:
            continue

        # For small r, exhaustive search
        if r <= 15:
            for prime_combo in combinations(search_primes, r):
                prime_set = set(prime_combo)
                coverage = count_covered(elements, prime_set, element_factors)
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_primes = prime_set
                if coverage > r:
                    if verbose:
                        print(f"  r={r}: {prime_set} covers {coverage} > {r}")
                    return r, best_primes

        # Also try greedy
        chosen = set()
        for _ in range(r):
            best_p = None
            best_gain = -1
            current_cov = count_covered(elements, chosen, element_factors)

            for p in relevant_primes:
                if p in chosen:
                    continue
                new_cov = count_covered(elements, chosen | {p}, element_factors)
                gain = new_cov - current_cov
                if gain > best_gain:
                    best_gain = gain
                    best_p = p

            if best_p:
                chosen.add(best_p)

        greedy_cov = count_covered(elements, chosen, element_factors)
        if greedy_cov > best_coverage:
            best_coverage = greedy_cov
            best_primes = chosen

        if best_coverage > r:
            if verbose:
                print(f"  r={r}: greedy {best_primes} covers {best_coverage} > {r}")
            return r, best_primes

        if verbose and r % 5 == 0:
            print(f"  r={r}: best coverage = {best_coverage} (need > {r})")

    return -1, set()


def analyze_woett_construction(n: int, epsilon: float = 0.1):
    """
    Construct Woett's adversarial set and compute f.
    """
    print("=" * 70)
    print(f"WOETT'S LOWER BOUND CONSTRUCTION: n = {n}")
    print("=" * 70)

    A, t, expected_r = construct_woett_set(n, epsilon, verbose=True)

    if not A:
        print("Construction failed!")
        return None

    primes = sieve_of_eratosthenes(n)
    element_factors = compute_element_factors(A, primes)

    print(f"\nComputing f for this set (expecting r ≥ {expected_r})...")
    r, best_primes = find_minimum_r(A, primes, element_factors,
                                     max_r=expected_r + 5, verbose=True)

    sqrt_n = int(n ** 0.5)
    two_pi_sqrt_n = 2 * pi(sqrt_n, primes)

    print(f"\n{'='*40}")
    print(f"RESULTS for n = {n}:")
    print(f"  t = π((2-ε)√n) = {t}")
    print(f"  Expected r = t + 1 = {expected_r}")
    print(f"  Computed r = {r}")
    print(f"  2π(√n) = {two_pi_sqrt_n}")
    print(f"{'='*40}")

    return r, t, expected_r, two_pi_sqrt_n


def main():
    print("=" * 70)
    print("ERDŐS PROBLEM #983 - WOETT'S CONSTRUCTION")
    print("=" * 70)
    print()
    print("Testing the lower bound construction from [Er70b]")
    print("Expected: f(π(n)+1, n) ≥ t + 1 where t = π((2-ε)√n)")
    print()

    results = []

    for n in [100, 200, 500, 1000, 2000]:
        result = analyze_woett_construction(n)
        if result:
            results.append((n, *result))
        print()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'n':>6} | {'t':>4} | {'Expected':>8} | {'Computed':>8} | {'2π(√n)':>8}")
    print("-" * 50)
    for n, r, t, expected, two_pi in results:
        print(f"{n:>6} | {t:>4} | {expected:>8} | {r:>8} | {two_pi:>8}")


if __name__ == "__main__":
    main()
