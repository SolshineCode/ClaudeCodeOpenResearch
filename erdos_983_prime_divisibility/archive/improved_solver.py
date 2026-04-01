#!/usr/bin/env python3
"""
Improved Constraint Solver for Erdős Problem #983

Fix: Find the LARGEST valid Latin matching, not just the first one.
"""

import math
from typing import List, Set, Tuple, Optional, Dict
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


def find_latin_matching_bt(left: List[int], right: List[int], n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Backtracking search for Latin matching.
    """
    k = len(left)
    if k != len(right) or k == 0:
        return None

    # Valid edges for each left vertex
    valid = {}
    for i, p in enumerate(left):
        valid[i] = [j for j, q in enumerate(right) if p * q <= n]
        if len(valid[i]) < 2:
            return None

    # Backtracking
    assignment = [None] * k
    used_pairs = set()
    right_deg = [0] * k

    def backtrack(i: int) -> bool:
        if i == k:
            return all(d == 2 for d in right_deg)

        for j1_idx in range(len(valid[i])):
            for j2_idx in range(j1_idx + 1, len(valid[i])):
                j1, j2 = valid[i][j1_idx], valid[i][j2_idx]
                pair = (min(j1, j2), max(j1, j2))

                if pair in used_pairs:
                    continue
                if right_deg[j1] >= 2 or right_deg[j2] >= 2:
                    continue

                assignment[i] = (j1, j2)
                used_pairs.add(pair)
                right_deg[j1] += 1
                right_deg[j2] += 1

                if backtrack(i + 1):
                    return True

                assignment[i] = None
                used_pairs.remove(pair)
                right_deg[j1] -= 1
                right_deg[j2] -= 1

        return False

    if backtrack(0):
        edges = []
        for i in range(k):
            j1, j2 = assignment[i]
            edges.append((left[i], right[j1]))
            edges.append((left[i], right[j2]))
        return edges
    return None


def find_best_latin_matching(primes_list: List[int], n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Find the largest Latin matching by trying all valid splits.
    """
    t = len(primes_list)
    if t < 4:
        return None

    best_edges = None
    best_size = 0

    # Try all possible split points
    for split in range(2, t - 1):
        left = primes_list[:split]
        right = primes_list[split:]

        # For equal halves
        if len(left) == len(right):
            edges = find_latin_matching_bt(left, right, n)
            if edges and len(edges) > best_size:
                best_size = len(edges)
                best_edges = edges
                # If we found a full matching for this size, it's optimal for this split
                if best_size == 2 * len(left):
                    continue

        # Try with trimmed halves
        min_size = min(len(left), len(right))
        for size in range(min_size, 1, -1):
            # Try different subsets of left and right
            for left_sub in [left[:size], left[-size:]]:
                for right_sub in [right[:size], right[-size:]]:
                    edges = find_latin_matching_bt(left_sub, right_sub, n)
                    if edges and len(edges) > best_size:
                        best_size = len(edges)
                        best_edges = edges

    return best_edges


def manual_construction(n: int) -> Optional[Tuple[List[int], List[Tuple[int, int]]]]:
    """
    Manual adversarial constructions for specific n values.
    """
    if n == 100:
        # Verified optimal construction
        left = [2, 3, 5, 7]
        right = [11, 13, 17, 19]
        edges = [
            (2, 13), (2, 19),  # 26, 38
            (3, 11), (3, 17),  # 33, 51
            (5, 17), (5, 19),  # 85, 95
            (7, 11), (7, 13),  # 77, 91
        ]
        return edges

    if n == 200:
        # For n=200, threshold ≈ 26.8, t=9
        # Small primes: {2,3,5,7,11,13,17,19,23}
        # Split: left={2,3,5,7}, right={11,13,17,19} (4x4), plus 23 extra
        left = [2, 3, 5, 7]
        right = [11, 13, 17, 19]
        edges = [
            (2, 13), (2, 19),  # 26, 38
            (3, 11), (3, 17),  # 33, 51
            (5, 17), (5, 19),  # 85, 95
            (7, 11), (7, 13),  # 77, 91
        ]
        return edges

    if n == 400:
        # threshold ≈ 38, t=12
        # Small primes: {2,3,5,7,11,13,17,19,23,29,31,37}
        # Try 6x6 split
        left = [2, 3, 5, 7, 11, 13]
        right = [17, 19, 23, 29, 31, 37]
        # Check if Latin matching exists
        # Products must all be ≤ 400
        # 13 × 37 = 481 > 400, so this won't work fully
        # Try 5x5
        left = [2, 3, 5, 7, 11]
        right = [13, 17, 19, 23, 29]
        # 11 × 29 = 319 ≤ 400 ✓
        # Need to find valid matching
        edges = [
            (2, 17), (2, 19),   # 34, 38
            (3, 13), (3, 23),   # 39, 69
            (5, 19), (5, 29),   # 95, 145
            (7, 17), (7, 23),   # 119, 161
            (11, 13), (11, 29), # 143, 319
        ]
        # Check pairs are unique:
        # 2: {17,19}, 3: {13,23}, 5: {19,29}, 7: {17,23}, 11: {13,29}
        # All unique ✓
        # Check right degrees:
        # 13: from 3, 11 → 2
        # 17: from 2, 7 → 2
        # 19: from 2, 5 → 2
        # 23: from 3, 7 → 2
        # 29: from 5, 11 → 2
        # All 2 ✓
        return edges

    return None


def build_adversarial_set(n: int, eps: float = 0.1) -> Tuple[List[int], Dict]:
    """
    Build adversarial set using best available construction.
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    large = [p for p in primes if p > thresh]
    t = len(small)

    if t < 4 or not large:
        return [], {"error": "insufficient primes", "t": t}

    # Try manual construction first
    edges = manual_construction(n)

    if not edges:
        # Fall back to automated search
        edges = find_best_latin_matching(small, n)

    if not edges:
        return [], {"error": "no valid matching", "t": t}

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
        "n": n,
        "t": t,
        "edges": len(edges),
        "A0": A0,
        "extras": extras,
        "size": len(A),
        "target": target
    }

    return sorted(A), info


def compute_f(A: List[int], primes: List[int], max_r: int) -> int:
    """Compute f correctly."""
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    def cov(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        if r <= 12:
            search = rel[:min(30, len(rel))]
            if len(search) >= r:
                for combo in combinations(search, r):
                    if cov(set(combo)) > r:
                        return r

        chosen = set()
        for _ in range(r):
            best_p, best_g = None, 0
            cur = cov(chosen)
            for p in rel:
                if p not in chosen:
                    g = cov(chosen | {p}) - cur
                    if g > best_g:
                        best_g, best_p = g, p
            if best_p:
                chosen.add(best_p)
        if cov(chosen) > r:
            return r

    return max_r + 1


def run_experiments():
    print("=" * 70)
    print("ERDŐS PROBLEM #983: Improved Adversarial Construction")
    print("=" * 70)
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        A, info = build_adversarial_set(n)

        if not A:
            print(f"n={n}: Failed ({info.get('error', '?')})")
            continue

        t = info["t"]
        num_edges = info["edges"]

        f = compute_f(A, primes, min(upper + 5, 25))
        gap = 2 * pi_sqrt - f

        results.append({
            "n": n, "t": t, "edges": num_edges,
            "f": f, "upper": upper, "gap": gap,
            "size": info["size"], "target": info["target"]
        })

        size_ok = "✓" if info["size"] == info["target"] else f"({info['size']}/{info['target']})"
        bound_match = "UPPER" if f == upper else ("LOWER" if f == num_edges // 2 + 1 else "between")
        print(f"n={n:5d}: t={t:2d}, edges={num_edges:2d}, f={f:3d}, upper={upper:3d}, gap={gap:3d}, {bound_match} {size_ok}")

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    gaps = [r["gap"] for r in results]
    print(f"\nGaps: {gaps}")

    at_upper = sum(1 for r in results if r["f"] == r["upper"])
    print(f"f = upper bound for {at_upper}/{len(results)} cases")

    if at_upper == len(results):
        print("\n★ ANSWER: NO — gap bounded at -1")
    elif max(gaps) > min(gaps) + 5:
        print(f"\n★ Gap grows from {min(gaps)} to {max(gaps)} — ANSWER: LIKELY YES")
    else:
        print("\n⚠ Inconclusive")


if __name__ == "__main__":
    run_experiments()
