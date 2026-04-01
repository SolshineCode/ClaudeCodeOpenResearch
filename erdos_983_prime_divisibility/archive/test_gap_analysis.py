#!/usr/bin/env python3
"""
Analyze the gap 2π(√n) - f for various n.

The main question: Does 2π(√n) - f(π(n)+1, n) → ∞?

We test Woett's adversarial construction to get lower bounds on f.
"""

from typing import List, Set, Dict, Tuple
from itertools import combinations
from utils import sieve_of_eratosthenes, prime_factors, pi, count_covered


def find_2_regular_subgraph_greedy(nodes: List[int], valid_edges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Find a 2-regular subgraph greedily (may not cover all nodes)."""
    degree = {node: 0 for node in nodes}
    chosen = []

    # Sort edges by product to prefer smaller semiprimes
    for u, v in sorted(valid_edges, key=lambda e: e[0] * e[1]):
        if degree[u] < 2 and degree[v] < 2:
            chosen.append((u, v))
            degree[u] += 1
            degree[v] += 1

    return chosen


def construct_adversarial_set(n: int, epsilon: float = 0.1) -> Tuple[List[int], int]:
    """
    Construct Woett's adversarial set.
    Returns (A, t) where t = π((2-ε)√n).
    """
    primes = sieve_of_eratosthenes(n)
    sqrt_n = n ** 0.5
    threshold = (2 - epsilon) * sqrt_n

    small_primes = [p for p in primes if p <= threshold]
    t = len(small_primes)

    if t < 3:
        return [], t

    # Valid edges
    valid_edges = [(p, q) for i, p in enumerate(small_primes)
                   for q in small_primes[i+1:] if p * q <= n]

    # Find 2-regular subgraph
    edges = find_2_regular_subgraph_greedy(small_primes, valid_edges)

    # A₀ = products
    A0 = [p * q for p, q in edges]

    # Remaining primes
    remaining = [p for p in primes if p > threshold]

    if not remaining:
        return [], t

    p_t1 = remaining[0]

    # Extra composites
    extra = []
    if 2 * p_t1 <= n:
        extra.append(2 * p_t1)
    if 3 * p_t1 <= n:
        extra.append(3 * p_t1)

    # Fill to π(n) + 1
    target = len(primes) + 1
    current = set(A0 + extra)

    for p in remaining[1:]:
        if len(current) >= target:
            break
        current.add(p)

    return sorted(current), t


def compute_f_for_set(A: List[int], primes: List[int], max_r: int = 50) -> int:
    """
    Find minimum r such that r primes cover > r elements of A.
    """
    # Pre-compute factors
    factors = {}
    relevant_primes = set()
    for e in A:
        f = set()
        temp = e
        for p in primes:
            if p * p > temp:
                break
            if temp % p == 0:
                f.add(p)
                while temp % p == 0:
                    temp //= p
        if temp > 1:
            f.add(temp)
        factors[e] = f
        relevant_primes.update(f)

    relevant_primes = sorted(relevant_primes)

    for r in range(1, min(max_r + 1, len(relevant_primes) + 1)):
        best_cov = 0

        # Exhaustive for small r
        if r <= 12:
            search = relevant_primes[:min(35, len(relevant_primes))]
            if len(search) >= r:
                for combo in combinations(search, r):
                    pset = set(combo)
                    cov = sum(1 for e in A if factors[e].issubset(pset))
                    if cov > r:
                        return r
                    best_cov = max(best_cov, cov)

        # Greedy
        chosen = set()
        for _ in range(r):
            best_p, best_gain = None, -1
            current_cov = sum(1 for e in A if factors[e].issubset(chosen))

            for p in relevant_primes:
                if p in chosen:
                    continue
                new_cov = sum(1 for e in A if factors[e].issubset(chosen | {p}))
                if new_cov - current_cov > best_gain:
                    best_gain = new_cov - current_cov
                    best_p = p

            if best_p:
                chosen.add(best_p)

        greedy_cov = sum(1 for e in A if factors[e].issubset(chosen))
        if greedy_cov > r:
            return r

    return -1


def main():
    print("=" * 70)
    print("GAP ANALYSIS: 2π(√n) - f(π(n)+1, n)")
    print("=" * 70)
    print()
    print("Testing Woett's construction to estimate f for various n.")
    print("Question: Does 2π(√n) - f → ∞?")
    print()

    results = []

    for n in [50, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 2000]:
        primes = sieve_of_eratosthenes(n)
        sqrt_n = int(n ** 0.5)
        two_pi_sqrt = 2 * pi(sqrt_n, primes)

        A, t = construct_adversarial_set(n)

        if not A:
            print(f"n={n}: Construction failed")
            continue

        f = compute_f_for_set(A, primes, max_r=two_pi_sqrt + 10)

        if f == -1:
            f_str = ">max"
            gap = "N/A"
        else:
            f_str = str(f)
            gap = two_pi_sqrt - f

        expected_lower = t + 1

        results.append((n, t, expected_lower, f, two_pi_sqrt, gap))

        print(f"n={n:5d}: t={t:3d}, f≥{expected_lower:3d}, computed_f={f_str:>4}, 2π(√n)={two_pi_sqrt:3d}, gap={gap}")

    print()
    print("=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'n':>6} | {'t':>4} | {'f_lower':>7} | {'f_computed':>10} | {'2π(√n)':>7} | {'Gap':>6}")
    print("-" * 55)

    for n, t, expected, f, two_pi, gap in results:
        f_str = str(f) if f != -1 else ">max"
        gap_str = str(gap) if gap != "N/A" else "N/A"
        print(f"{n:>6} | {t:>4} | {expected:>7} | {f_str:>10} | {two_pi:>7} | {gap_str:>6}")

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # Check if gaps are growing or bounded
    valid_gaps = [(n, g) for n, _, _, _, _, g in results if isinstance(g, int)]

    if valid_gaps:
        gaps_only = [g for _, g in valid_gaps]
        print(f"Gaps observed: {gaps_only}")

        if all(g <= 0 for g in gaps_only):
            print("All gaps ≤ 0: f ≥ 2π(√n)")
            print("This suggests 2π(√n) - f does NOT → +∞")
        elif all(g >= 0 for g in gaps_only):
            print("All gaps ≥ 0: f ≤ 2π(√n)")
            if max(gaps_only) - min(gaps_only) < 5:
                print("Gaps appear BOUNDED: Answer likely NO")
            else:
                print("Gaps may be GROWING: Need larger n to confirm")
        else:
            print("Mixed signs: More analysis needed")


if __name__ == "__main__":
    main()
