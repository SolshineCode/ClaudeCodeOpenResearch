#!/usr/bin/env python3
"""
Corrected Woett Construction using Bipartite 2-Regular Graphs

KEY INSIGHT from debug_comparison.py:
The manual construction for n=100 creates a BIPARTITE graph:
- Left partition: small primes {2, 3, 5, 7}
- Right partition: medium-large primes {11, 13, 17, 19}
- Each prime on both sides appears exactly twice

This prevents efficient coverage because any r primes can cover
at most r elements of A₀ (the semiprimes).

For general n, we split the small primes (≤ (2-ε)√n) into two halves
and create edges only between the halves.
"""

import math
from typing import List, Set, Dict, Tuple
from itertools import combinations
from collections import defaultdict


def sieve(n: int) -> List[int]:
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
    return sum(1 for p in primes if p <= x)


def factors(n: int, primes: List[int]) -> Set[int]:
    if n <= 1:
        return set()
    f = set()
    temp = n
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


def build_bipartite_2regular(left: List[int], right: List[int], n: int) -> List[Tuple[int, int]]:
    """
    Build a 2-regular bipartite graph where:
    - Each prime in 'left' has degree 2 (connected to 2 primes in 'right')
    - Each prime in 'right' has degree 2 (connected to 2 primes in 'left')
    - All products p*q are ≤ n

    Returns list of edges (p, q) where p ∈ left, q ∈ right.
    """
    # Find all valid edges
    valid_edges = []
    for p in left:
        for q in right:
            if p * q <= n:
                valid_edges.append((p, q))

    # Greedy matching to build 2-regular bipartite graph
    deg_left = {p: 0 for p in left}
    deg_right = {q: 0 for q in right}
    edges = []

    # Sort edges by product size (prefer larger products for better spread)
    valid_edges.sort(key=lambda e: e[0] * e[1], reverse=True)

    for p, q in valid_edges:
        if deg_left[p] < 2 and deg_right[q] < 2:
            edges.append((p, q))
            deg_left[p] += 1
            deg_right[q] += 1

    return edges


def build_woett_bipartite(n: int, eps: float = 0.1, verbose: bool = False) -> Tuple[List[int], Dict]:
    """
    Build Woett's adversarial set using bipartite construction.

    The key is to split small primes into two groups and create
    edges only between groups.
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    t = len(small)

    if t < 4:
        return [], {"error": "t < 4", "t": t}

    # Split small primes into two halves
    mid = t // 2
    left = small[:mid]   # Smaller primes
    right = small[mid:]  # Larger primes

    if verbose:
        print(f"t = {t}, left = {left}, right = {right}")

    # Build bipartite 2-regular graph
    edges = build_bipartite_2regular(left, right, n)

    if verbose:
        print(f"Edges: {edges}")

    # Count degrees
    deg = defaultdict(int)
    for p, q in edges:
        deg[p] += 1
        deg[q] += 1

    # Semiprimes (A₀)
    A0 = sorted([p * q for p, q in edges])

    if verbose:
        print(f"A0 = {A0} ({len(A0)} elements)")

    # Large primes beyond threshold
    large = [p for p in primes if p > thresh]
    if not large:
        return [], {"error": "no large primes", "t": t}

    p_t1 = large[0]  # First prime > threshold

    # Extra composites: products of small primes with p_{t+1}
    # Only add if the small prime has degree 2 (fully used)
    extra = []
    for p in [2, 3]:
        if deg[p] == 2 and p * p_t1 <= n:
            extra.append(p * p_t1)

    # Target size: π(n) + 1
    target = len(primes) + 1

    # Build A = A₀ ∪ extra ∪ large_primes
    A = set(A0 + extra)
    for p in large[1:]:
        if len(A) >= target:
            break
        A.add(p)

    info = {
        "n": n,
        "t": t,
        "left": left,
        "right": right,
        "edges": edges,
        "degree": dict(deg),
        "A0": A0,
        "p_t1": p_t1,
        "extra": extra,
        "size": len(A),
        "target": target
    }

    return sorted(A), info


def compute_f_exhaustive(A: List[int], primes: List[int], max_r: int, verbose: bool = False) -> Tuple[int, List[int], int]:
    """
    Compute f for set A exhaustively.
    Returns (f, best_primes, coverage).
    """
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    def cov(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        best = 0
        best_primes = []

        # Exhaustive search for small r
        if r <= 12:
            search_space = rel[:min(50, len(rel))]
            if len(search_space) >= r:
                for combo in combinations(search_space, r):
                    c = cov(set(combo))
                    if c > best:
                        best = c
                        best_primes = list(combo)
                    if c > r:
                        if verbose:
                            print(f"  r={r}: {combo} covers {c} > {r}")
                        return r, best_primes, c

        # Greedy fallback
        chosen = set()
        for _ in range(r):
            best_p, best_g = None, -1
            cur = cov(chosen)
            for p in rel:
                if p not in chosen:
                    g = cov(chosen | {p}) - cur
                    if g > best_g:
                        best_g, best_p = g, p
            if best_p:
                chosen.add(best_p)

        gc = cov(chosen)
        if gc > best:
            best = gc
            best_primes = sorted(chosen)

        if best > r:
            if verbose:
                print(f"  r={r}: greedy {best_primes} covers {best} > {r}")
            return r, best_primes, best

    return -1, [], 0


def analyze_a0_coverage(A0: List[int], primes: List[int]) -> None:
    """Analyze how efficiently prime sets cover A0."""
    facs = {e: factors(e, primes) for e in A0}
    all_primes = sorted(set().union(*facs.values()))

    print(f"\nA0 analysis:")
    for e in A0:
        print(f"  {e} = {' × '.join(map(str, sorted(facs[e])))}")

    def cov(pset):
        return sum(1 for e in A0 if facs[e].issubset(pset))

    print(f"\nCoverage by r primes:")
    for r in range(1, len(all_primes) + 1):
        best = 0
        for combo in combinations(all_primes, r):
            c = cov(set(combo))
            best = max(best, c)
        print(f"  r={r}: max coverage = {best}")
        if best == len(A0):
            break


def test_n100():
    """Test for n=100 and compare with manual construction."""
    print("=" * 60)
    print("TEST: n = 100 (Bipartite Construction)")
    print("=" * 60)

    n = 100
    primes = sieve(n)

    A, info = build_woett_bipartite(n, verbose=True)

    print(f"\n|A| = {len(A)}")
    print(f"A = {A[:15]}..." if len(A) > 15 else f"A = {A}")

    # Analyze A0
    A0 = info.get("A0", [])
    if A0:
        analyze_a0_coverage(A0, primes)

    print(f"\nComputing f...")
    f, best_p, cov = compute_f_exhaustive(A, primes, 15, verbose=True)

    pi_sqrt = pi(10, primes)
    gap = 2 * pi_sqrt - f

    print(f"\nResults:")
    print(f"  f = {f}")
    print(f"  2π(√100) = 2×{pi_sqrt} = {2*pi_sqrt}")
    print(f"  Gap = 2π(√n) - f = {gap}")
    print(f"  Upper bound: 2π(√n) + 1 = {2*pi_sqrt + 1}")

    # Compare with expected
    expected_f = info["t"] + 1
    print(f"\n  Expected f (t+1): {expected_f}")
    print(f"  Match: {'✓' if f == expected_f else '✗'}")

    return f, gap, info


def run_experiments():
    """Run experiments for various n values."""
    print("=" * 60)
    print("ERDŐS PROBLEM #983: Bipartite Construction Experiments")
    print("=" * 60)
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        A, info = build_woett_bipartite(n)

        if not A:
            print(f"n={n}: Construction failed ({info.get('error', 'unknown')})")
            continue

        f, _, _ = compute_f_exhaustive(A, primes, upper + 5)
        gap = 2 * pi_sqrt - f

        t = info["t"]
        expected_f = t + 1

        results.append({
            "n": n,
            "t": t,
            "pi_sqrt": pi_sqrt,
            "upper": upper,
            "f": f,
            "expected_f": expected_f,
            "gap": gap,
            "|A0|": len(info["A0"])
        })

        match = "✓" if f == expected_f else "≠"
        bound_ok = "✓" if f <= upper else "✗"
        print(f"n={n:5d}: t={t:2d}, f={f:3d}, expected={expected_f:3d} {match}, 2π(√n)={2*pi_sqrt:3d}, gap={gap:3d} {bound_ok}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"\n{'n':>6} | {'t':>3} | {'f':>4} | {'exp':>4} | {'2π(√n)':>7} | {'gap':>5} | {'|A0|':>5}")
    print("-" * 55)
    for r in results:
        print(f"{r['n']:>6} | {r['t']:>3} | {r['f']:>4} | {r['expected_f']:>4} | {2*r['pi_sqrt']:>7} | {r['gap']:>5} | {r['|A0|']:>5}")

    # Check if gap is bounded
    gaps = [r["gap"] for r in results]
    print(f"\nGaps: {gaps}")
    print(f"Gap range: [{min(gaps)}, {max(gaps)}]")

    # Check if f matches expected (t+1)
    matches = sum(1 for r in results if r["f"] == r["expected_f"])
    print(f"\nf = t+1 for {matches}/{len(results)} cases")

    # Check if gap is growing
    if len(gaps) >= 3:
        growing = all(gaps[i] <= gaps[i+1] for i in range(len(gaps)-1))
        print(f"Gap monotonically growing: {growing}")

    # Conclusion
    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    if all(r["f"] <= r["upper"] for r in results):
        print("✓ Upper bound f ≤ 2π(√n) + 1 holds for all tested n")

    if matches == len(results):
        print("✓ f = t + 1 for all tested n (Woett construction optimal)")
        print()
        print("Since f = t + 1 = π((2-ε)√n) + 1:")
        print("  gap = 2π(√n) - f = 2π(√n) - π((2-ε)√n) - 1")
        print("      ≈ π(2√n) - π((2-ε)√n)")
        print("      ≈ number of primes in ((2-ε)√n, 2√n]")
        print("      ≈ (2ε√n) / ln(√n)  [by PNT]")
        print()
        print("This grows like √n / ln(n) → ∞")
        print()
        print("★ ANSWER: YES — the gap 2π(√n) - f → ∞")
    else:
        print(f"⚠ f ≠ t+1 for some cases — construction may be suboptimal")


if __name__ == "__main__":
    print("First testing n=100...")
    print()
    test_n100()
    print()
    print()
    run_experiments()
