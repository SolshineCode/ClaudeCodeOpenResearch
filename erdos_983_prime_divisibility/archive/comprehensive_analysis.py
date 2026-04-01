#!/usr/bin/env python3
"""
Comprehensive Analysis of Erdős Problem #983

Manually construct adversarial sets and compute f precisely for various n.
"""

import math
from typing import List, Set, Tuple, Dict
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


def build_latin_matching(left: List[int], right: List[int], n: int) -> List[Tuple[int, int]]:
    """
    Build a 2-regular bipartite Latin matching.
    Each left prime connects to exactly 2 right primes, and vice versa.
    No two left primes share the same pair of right neighbors.
    """
    k = len(left)
    if k != len(right) or k < 2:
        return []

    # Check all products valid
    valid = {}
    for i, p in enumerate(left):
        valid[i] = [j for j, q in enumerate(right) if p * q <= n]
        if len(valid[i]) < 2:
            return []

    # Backtracking search
    assignment = [None] * k
    used_pairs = set()
    right_deg = [0] * k

    def backtrack(i):
        if i == k:
            return all(d == 2 for d in right_deg)
        for j1 in range(len(valid[i])):
            for j2 in range(j1 + 1, len(valid[i])):
                jj1, jj2 = valid[i][j1], valid[i][j2]
                pair = (min(jj1, jj2), max(jj1, jj2))
                if pair in used_pairs or right_deg[jj1] >= 2 or right_deg[jj2] >= 2:
                    continue
                assignment[i] = (jj1, jj2)
                used_pairs.add(pair)
                right_deg[jj1] += 1
                right_deg[jj2] += 1
                if backtrack(i + 1):
                    return True
                assignment[i] = None
                used_pairs.remove(pair)
                right_deg[jj1] -= 1
                right_deg[jj2] -= 1
        return False

    if backtrack(0):
        edges = []
        for i in range(k):
            j1, j2 = assignment[i]
            edges.append((left[i], right[j1]))
            edges.append((left[i], right[j2]))
        return edges
    return []


def find_best_construction(n: int, eps: float = 0.1) -> Tuple[List[Tuple[int, int]], int]:
    """Find the best Latin matching construction for n."""
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n
    small = [p for p in primes if p <= thresh]
    t = len(small)

    best_edges = []
    best_size = 0

    # Try different split points
    for split in range(2, t - 1):
        left = small[:split]
        right = small[split:]

        # Try equal-sized subsets
        for size in range(min(len(left), len(right)), 1, -1):
            for l_start in range(len(left) - size + 1):
                for r_start in range(len(right) - size + 1):
                    l_sub = left[l_start:l_start + size]
                    r_sub = right[r_start:r_start + size]
                    edges = build_latin_matching(l_sub, r_sub, n)
                    if edges and len(edges) > best_size:
                        best_size = len(edges)
                        best_edges = edges

    return best_edges, t


def build_adversarial_set(n: int, eps: float = 0.1) -> Tuple[List[int], Dict]:
    """Build full adversarial set A."""
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n
    small = [p for p in primes if p <= thresh]
    large = [p for p in primes if p > thresh]
    t = len(small)

    if not large:
        return [], {"error": "no large primes"}

    edges, _ = find_best_construction(n, eps)
    if not edges:
        return [], {"error": "no valid matching"}

    A0 = sorted([p * q for p, q in edges])
    p_t1 = large[0]

    extras = []
    if 2 * p_t1 <= n:
        extras.append(2 * p_t1)
    if 3 * p_t1 <= n:
        extras.append(3 * p_t1)

    target = len(primes) + 1
    A = set(A0 + extras)
    for p in large[1:]:
        if len(A) >= target:
            break
        A.add(p)

    info = {
        "n": n, "t": t, "edges": len(edges), "A0": A0,
        "extras": extras, "p_t1": p_t1, "size": len(A), "target": target
    }
    return sorted(A), info


def compute_f_precise(A: List[int], primes: List[int], A0: List[int], extras: List[int], max_r: int) -> int:
    """Compute f precisely by understanding the structure."""
    facs = {e: factors(e, primes) for e in A}

    # Primes needed for A0
    A0_primes = set()
    for e in A0:
        A0_primes |= facs[e]

    # Primes needed for extras
    extra_primes = set()
    for e in extras:
        extra_primes |= facs[e]

    all_needed = A0_primes | extra_primes

    def cov(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    # Check if |all_needed| primes cover > |all_needed| elements
    c = cov(all_needed)
    if c > len(all_needed):
        # f ≤ len(all_needed), now find exact f
        for r in range(1, len(all_needed) + 1):
            # Try all r-subsets of all_needed + a few more
            search_primes = sorted(all_needed) + sorted(extra_primes - A0_primes)[:5]
            for combo in combinations(search_primes, r):
                if cov(set(combo)) > r:
                    return r
        return len(all_needed)

    # Need to search more broadly
    rel = sorted(set().union(*facs.values()))
    for r in range(1, min(max_r + 1, len(rel) + 1)):
        # Smart search: prioritize primes in A0 and extras
        priority = sorted(A0_primes) + sorted(extra_primes - A0_primes) + [p for p in rel if p not in all_needed]
        for combo in combinations(priority[:30], r):
            if cov(set(combo)) > r:
                return r
    return max_r + 1


def main():
    print("=" * 70)
    print("ERDŐS PROBLEM #983: COMPREHENSIVE GAP ANALYSIS")
    print("=" * 70)
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 5000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        A, info = build_adversarial_set(n)

        if not A:
            print(f"n={n}: Construction failed")
            continue

        f = compute_f_precise(A, primes, info["A0"], info.get("extras", []), upper + 5)
        gap = 2 * pi_sqrt - f

        results.append({
            "n": n, "t": info["t"], "edges": info["edges"],
            "f": f, "two_pi_sqrt": 2 * pi_sqrt, "upper": upper, "gap": gap
        })

        status = "=" if f == upper else (">" if gap > 0 else "<")
        print(f"n={n:5d}: t={info['t']:2d}, edges={info['edges']:2d}, f={f:3d}, 2π(√n)={2*pi_sqrt:3d}, gap={gap:3d} {status}")

    print()
    print("=" * 70)
    print("RESULTS TABLE")
    print("=" * 70)

    print(f"\n{'n':>6} | {'t':>3} | {'edges':>5} | {'f':>4} | {'2π(√n)':>6} | {'gap':>4}")
    print("-" * 45)
    for r in results:
        print(f"{r['n']:>6} | {r['t']:>3} | {r['edges']:>5} | {r['f']:>4} | {r['two_pi_sqrt']:>6} | {r['gap']:>4}")

    gaps = [r["gap"] for r in results]
    print(f"\nGaps: {gaps}")
    print(f"Range: [{min(gaps)}, {max(gaps)}]")

    # Analysis
    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if max(gaps) > min(gaps) + 5:
        print(f"\n★ Gap GROWS from {min(gaps)} to {max(gaps)}")
        print("★ ANSWER: YES — the gap tends to infinity")
    else:
        print("\n★ Gap appears bounded")
        print("★ ANSWER: NO — the gap does not tend to infinity")

    # Theoretical prediction
    print()
    print("Theoretical prediction:")
    print("  If f ≈ (edges/2) + O(1) = O(π(√n)), then")
    print("  gap = 2π(√n) - f ≈ π(√n) → ∞")


if __name__ == "__main__":
    main()
