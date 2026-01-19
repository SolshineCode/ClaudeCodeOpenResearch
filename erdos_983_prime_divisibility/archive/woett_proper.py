#!/usr/bin/env python3
"""
Proper implementation of Woett's adversarial construction.

The key insight: For the construction to achieve f = t+1, the 2-regular graph
must be "well-spread". Each small prime should be paired with primes that are
far from it in the list, preventing efficient coverage.

Strategy: Use a "bipartite-like" matching where we pair primes from the first
half with primes from the second half of the small primes list.
"""

import math
from typing import List, Set, Dict, Tuple, Optional
from itertools import combinations
from collections import defaultdict


def sieve(n: int) -> List[int]:
    """Sieve of Eratosthenes."""
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(2, n + 1) if is_prime[i]]


def pi(x: int, primes: List[int]) -> int:
    """Prime counting function."""
    return sum(1 for p in primes if p <= x)


def factors(m: int, primes: List[int]) -> Set[int]:
    """Get prime factors of m."""
    if m <= 1:
        return set()
    f = set()
    temp = m
    for p in primes:
        if p * p > temp:
            break
        if temp % p == 0:
            f.add(p)
            while temp % p == 0:
                temp //= p
    if temp > 1:
        f.add(temp)
    return f


def build_spread_2regular(small_primes: List[int], n: int) -> List[Tuple[int, int]]:
    """
    Build a 2-regular graph with "spread" pairings.

    Strategy: Split primes into two halves (small and large within threshold).
    Pair primes from different halves to maximize spread.
    This prevents any small set of primes from covering multiple products.
    """
    t = len(small_primes)
    if t < 4:
        return []

    # Valid edges (products ≤ n)
    valid = set()
    for i, p in enumerate(small_primes):
        for j in range(i+1, t):
            q = small_primes[j]
            if p * q <= n:
                valid.add((p, q))

    # Split into two halves
    mid = t // 2
    first_half = small_primes[:mid]
    second_half = small_primes[mid:]

    edges = []
    degree = {p: 0 for p in small_primes}

    # Phase 1: Pair primes across halves
    # For each prime in first half, find 2 partners in second half
    for p in first_half:
        partners_needed = 2 - degree[p]
        for q in reversed(second_half):  # Start from largest
            if partners_needed <= 0:
                break
            if degree[q] < 2 and (min(p,q), max(p,q)) in valid:
                edge = (min(p,q), max(p,q))
                if edge not in edges:
                    edges.append(edge)
                    degree[p] += 1
                    degree[q] += 1
                    partners_needed -= 1

    # Phase 2: Fill remaining within second half (if needed)
    for i, p in enumerate(second_half):
        if degree[p] >= 2:
            continue
        for q in second_half[i+1:]:
            if degree[p] >= 2:
                break
            if degree[q] < 2 and (min(p,q), max(p,q)) in valid:
                edge = (min(p,q), max(p,q))
                if edge not in edges:
                    edges.append(edge)
                    degree[p] += 1
                    degree[q] += 1

    # Phase 3: Fill remaining within first half (if needed)
    for i, p in enumerate(first_half):
        if degree[p] >= 2:
            continue
        for q in first_half[i+1:]:
            if degree[p] >= 2:
                break
            if degree[q] < 2 and (min(p,q), max(p,q)) in valid:
                edge = (min(p,q), max(p,q))
                if edge not in edges:
                    edges.append(edge)
                    degree[p] += 1
                    degree[q] += 1

    # Phase 4: Any remaining connections
    for p in small_primes:
        if degree[p] >= 2:
            continue
        for q in small_primes:
            if p >= q:
                continue
            if degree[p] >= 2:
                break
            if degree[q] < 2:
                edge = (p, q)
                if edge in valid and edge not in edges:
                    edges.append(edge)
                    degree[p] += 1
                    degree[q] += 1

    return edges


def construct_woett_set(n: int, epsilon: float = 0.1, verbose: bool = False) -> Tuple[List[int], Dict]:
    """
    Construct Woett's adversarial set for n.

    Returns (A, info) where A is the set and info contains construction details.
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    threshold = (2 - epsilon) * sqrt_n

    # Small primes
    small_primes = [p for p in primes if p <= threshold]
    t = len(small_primes)

    if verbose:
        print(f"n = {n}")
        print(f"threshold = (2-{epsilon})√{n} = {threshold:.2f}")
        print(f"t = {t} small primes")

    if t < 4:
        return [], {"error": "t < 4", "t": t}

    # Build 2-regular graph
    edges = build_spread_2regular(small_primes, n)

    # Check degree
    degree = defaultdict(int)
    for p, q in edges:
        degree[p] += 1
        degree[q] += 1

    covered = [p for p in small_primes if degree[p] == 2]
    uncovered = [p for p in small_primes if degree[p] != 2]

    if verbose:
        print(f"Edges: {len(edges)}")
        print(f"Covered primes (deg=2): {len(covered)}")
        if uncovered:
            print(f"Uncovered primes: {uncovered}")

    # A₀ = products from edges
    A0 = sorted([p * q for p, q in edges])

    if verbose:
        print(f"|A₀| = {len(A0)}")

    # Large primes
    large_primes = [p for p in primes if p > threshold]
    if not large_primes:
        return [], {"error": "no large primes", "t": t}

    p_t1 = large_primes[0]

    # Extra composites
    extra = []
    if 2 in covered and 2 * p_t1 <= n:
        extra.append(2 * p_t1)
    if 3 in covered and 3 * p_t1 <= n:
        extra.append(3 * p_t1)

    if verbose:
        print(f"p_{{t+1}} = {p_t1}")
        print(f"Extra composites: {extra}")

    # Build A
    target = len(primes) + 1
    A = set(A0 + extra)

    for p in large_primes[1:]:
        if len(A) >= target:
            break
        A.add(p)

    A = sorted(A)

    info = {
        "n": n,
        "epsilon": epsilon,
        "t": t,
        "small_primes": small_primes,
        "edges": edges,
        "degree": dict(degree),
        "covered": covered,
        "uncovered": uncovered,
        "A0": A0,
        "p_t1": p_t1,
        "extra": extra,
        "size": len(A),
        "target": target,
    }

    return A, info


def compute_f_exhaustive(A: List[int], primes: List[int], max_r: int, verbose: bool = False) -> Tuple[int, Set[int], int]:
    """
    Compute f for set A using exhaustive search up to max_r.
    Returns (f, best_primes, coverage).
    """
    # Get factors
    facs = {e: factors(e, primes) for e in A}

    # Relevant primes
    rel = sorted(set().union(*facs.values()))

    if verbose:
        print(f"  {len(rel)} relevant primes")

    def coverage(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        best_cov = 0
        best_primes = set()

        # Exhaustive for small r
        if r <= 15:
            search_primes = rel[:min(50, len(rel))]
            if len(search_primes) >= r:
                for combo in combinations(search_primes, r):
                    pset = set(combo)
                    cov = coverage(pset)
                    if cov > best_cov:
                        best_cov = cov
                        best_primes = pset
                    if cov > r:  # STRICT inequality
                        if verbose:
                            print(f"  r={r}: {pset} covers {cov} > {r}")
                        return r, best_primes, cov

        # Greedy for larger r
        chosen = set()
        for _ in range(r):
            best_p, best_gain = None, -1
            cur_cov = coverage(chosen)
            for p in rel:
                if p in chosen:
                    continue
                new_cov = coverage(chosen | {p})
                gain = new_cov - cur_cov
                if gain > best_gain:
                    best_gain = gain
                    best_p = p
            if best_p:
                chosen.add(best_p)

        greedy_cov = coverage(chosen)
        if greedy_cov > best_cov:
            best_cov = greedy_cov
            best_primes = chosen

        if best_cov > r:
            if verbose:
                print(f"  r={r}: greedy covers {best_cov} > {r}")
            return r, best_primes, best_cov

        if verbose and r % 5 == 0:
            print(f"  r={r}: best = {best_cov}")

    return -1, set(), 0


def analyze_n(n: int, epsilon: float = 0.1, verbose: bool = True):
    """Analyze f for a specific n."""
    print(f"\n{'='*60}")
    print(f"ANALYZING n = {n}")
    print(f"{'='*60}")

    primes = sieve(n)
    sqrt_n = int(math.sqrt(n))
    pi_sqrt = pi(sqrt_n, primes)
    upper_bound = 2 * pi_sqrt + 1

    print(f"π(n) = {len(primes)}")
    print(f"π(√n) = π({sqrt_n}) = {pi_sqrt}")
    print(f"Upper bound: 2π(√n) + 1 = {upper_bound}")
    print()

    # Construct Woett set
    A, info = construct_woett_set(n, epsilon, verbose=verbose)

    if not A:
        print(f"Construction failed: {info.get('error', 'unknown')}")
        return None

    print()
    print(f"Set A: |A| = {len(A)}, target = {info['target']}")
    print()

    # Compute f
    print("Computing f...")
    f, best_primes, cov = compute_f_exhaustive(A, primes, upper_bound + 5, verbose=verbose)

    # Results
    gap = 2 * pi_sqrt - f
    expected_f = info['t'] + 1  # Woett's prediction

    print()
    print(f"{'='*40}")
    print(f"RESULTS for n = {n}")
    print(f"{'='*40}")
    print(f"  t = {info['t']}")
    print(f"  Expected f (Woett): t + 1 = {expected_f}")
    print(f"  Computed f: {f}")
    print(f"  2π(√n) = {2 * pi_sqrt}")
    print(f"  Upper bound = {upper_bound}")
    print(f"  Gap = 2π(√n) - f = {gap}")

    if f == expected_f:
        print(f"  ✓ f matches Woett's prediction!")
    elif f == upper_bound:
        print(f"  ✓ f equals upper bound!")
    else:
        print(f"  ⚠ f differs from prediction")

    return {
        "n": n,
        "t": info["t"],
        "expected_f": expected_f,
        "f": f,
        "pi_sqrt": pi_sqrt,
        "upper_bound": upper_bound,
        "gap": gap,
    }


def main():
    print("="*60)
    print("WOETT CONSTRUCTION: PROPER IMPLEMENTATION")
    print("="*60)
    print()
    print("Goal: Compute f for various n to determine if gap → ∞")
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000]:
        result = analyze_n(n, epsilon=0.1, verbose=True)
        if result:
            results.append(result)

    # Summary
    print()
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print()
    print(f"{'n':>6} | {'t':>4} | {'f_exp':>6} | {'f':>4} | {'2π(√n)':>7} | {'upper':>6} | {'gap':>5}")
    print("-" * 55)

    for r in results:
        print(f"{r['n']:>6} | {r['t']:>4} | {r['expected_f']:>6} | {r['f']:>4} | {2*r['pi_sqrt']:>7} | {r['upper_bound']:>6} | {r['gap']:>5}")

    print()

    # Analysis
    gaps = [r['gap'] for r in results]
    print(f"Gaps: {gaps}")

    if len(set(gaps)) == 1:
        print(f"Gap is constant = {gaps[0]}")
        print("→ Suggests answer is NO (gap bounded)")
    elif all(g >= gaps[0] for g in gaps):
        if gaps[-1] > gaps[0]:
            print(f"Gap is increasing: {gaps[0]} → {gaps[-1]}")
            print("→ Suggests answer might be YES (gap growing)")
        else:
            print("Gap appears stable")

    return results


if __name__ == "__main__":
    main()
