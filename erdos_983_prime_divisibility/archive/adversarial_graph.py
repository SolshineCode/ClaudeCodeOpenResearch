#!/usr/bin/env python3
"""
Adversarial 2-Regular Graph Construction

KEY INSIGHT:
The Woett construction requires a 2-regular graph where NO two primes
share the same pair of neighbors. This maximizes the number of primes
needed to cover all semiprimes.

BAD construction (n=100):
- 2 paired with (17, 19)
- 3 paired with (17, 19)  ← SAME pair!
→ {2, 3, 17, 19} covers 4 semiprimes, vulnerability exists

GOOD construction (n=100):
- 2 paired with (13, 19)
- 3 paired with (11, 17)
- 5 paired with (17, 19)
- 7 paired with (11, 13)
→ Each small prime has UNIQUE large partners

This is equivalent to finding a 2-regular bipartite graph where
the two partitions are "small" primes {2,3,5,7} and "large" primes
{11,13,17,19}, and each vertex has degree exactly 2.
"""

import math
from typing import List, Set, Tuple, Dict, Optional
from itertools import combinations, permutations
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


def build_adversarial_bipartite(left: List[int], right: List[int], n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Build a 2-regular bipartite graph where:
    - Each left vertex has degree 2
    - Each right vertex has degree 2
    - No two left vertices share the same pair of right neighbors

    This is a Latin rectangle constraint!
    """
    l = len(left)
    r = len(right)

    if l != r:
        # For unequal sizes, some vertices can't have degree 2
        return None

    # Valid edges (product ≤ n)
    valid = set()
    for p in left:
        for q in right:
            if p * q <= n:
                valid.add((p, q))

    # We need each left vertex to connect to 2 right vertices
    # and vice versa, with no overlapping pairs

    # Brute force for small cases
    if l <= 4:
        # Try all possible 2-regular matchings
        for perm1 in permutations(right):
            for perm2 in permutations(right):
                # left[i] connects to perm1[i] and perm2[i]
                valid_match = True
                edges = []

                for i in range(l):
                    p = left[i]
                    q1, q2 = perm1[i], perm2[i]

                    if q1 == q2:
                        valid_match = False
                        break

                    if (p, q1) not in valid or (p, q2) not in valid:
                        valid_match = False
                        break

                    edges.append((p, q1))
                    edges.append((p, q2))

                if not valid_match:
                    continue

                # Check degree on right side
                deg_right = defaultdict(int)
                for _, q in edges:
                    deg_right[q] += 1

                if all(deg_right[q] == 2 for q in right):
                    # Check no two left vertices share same pair
                    pairs = []
                    for i in range(l):
                        pair = tuple(sorted([perm1[i], perm2[i]]))
                        if pair in pairs:
                            valid_match = False
                            break
                        pairs.append(pair)

                    if valid_match:
                        return edges

    return None


def build_adversarial_2regular(primes_list: List[int], n: int) -> List[Tuple[int, int]]:
    """
    Build adversarial 2-regular graph on all small primes.

    Strategy:
    1. Split primes into two equal halves
    2. Build bipartite 2-regular between halves
    3. If not possible, fall back to general construction
    """
    t = len(primes_list)
    if t < 4:
        return []

    # Even split
    if t % 2 == 0:
        mid = t // 2
        left = primes_list[:mid]
        right = primes_list[mid:]
    else:
        # Odd case: make left one smaller
        mid = t // 2
        left = primes_list[:mid]
        right = primes_list[mid:]  # One more in right

    # Try bipartite construction
    edges = build_adversarial_bipartite(left, right, n)

    if edges:
        return edges

    # Fallback: greedy with diversity constraint
    return build_diverse_2regular(primes_list, n)


def build_diverse_2regular(primes_list: List[int], n: int) -> List[Tuple[int, int]]:
    """
    Build 2-regular graph trying to maximize diversity of neighbor pairs.
    """
    t = len(primes_list)

    # All valid edges
    valid_edges = [(p, q) for i, p in enumerate(primes_list)
                   for q in primes_list[i+1:] if p * q <= n]

    # Track neighbors
    neighbors = defaultdict(set)
    deg = defaultdict(int)
    edges = []

    # Greedy: prioritize edges that don't create shared pairs
    def score(p, q):
        # Higher score = better edge
        # Penalize if adding this edge would create shared neighbor pairs
        penalty = 0
        for other in primes_list:
            if other == p or other == q:
                continue
            # Check if other already has q as neighbor
            if q in neighbors[other] and p in neighbors[other]:
                penalty += 100  # Both already neighbors of other
            elif q in neighbors[other] or p in neighbors[other]:
                penalty += 1
        return -penalty + abs(primes_list.index(p) - primes_list.index(q))

    valid_edges.sort(key=lambda e: score(e[0], e[1]), reverse=True)

    for p, q in valid_edges:
        if deg[p] < 2 and deg[q] < 2:
            edges.append((p, q))
            deg[p] += 1
            deg[q] += 1
            neighbors[p].add(q)
            neighbors[q].add(p)

    return edges


def manual_n100_construction():
    """
    The verified adversarial construction for n=100.

    Small primes: {2,3,5,7}
    Large primes: {11,13,17,19}

    Pairings (bipartite 2-regular):
    - 2 with (13, 19)
    - 3 with (11, 17)
    - 5 with (17, 19)
    - 7 with (11, 13)
    """
    A0 = [
        2*13, 2*19,  # 26, 38
        3*11, 3*17,  # 33, 51
        5*17, 5*19,  # 85, 95
        7*11, 7*13,  # 77, 91
    ]
    return sorted(A0)


def build_woett_adversarial(n: int, eps: float = 0.1) -> Tuple[List[int], dict]:
    """Build Woett's adversarial set with proper 2-regular graph."""
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    large = [p for p in primes if p > thresh]
    t = len(small)

    if t < 3 or not large:
        return [], {"error": "insufficient primes", "t": t}

    # Special case: n=100
    if n == 100:
        A0 = manual_n100_construction()
        p_t1 = large[0]  # 23
        extras = [2 * p_t1, 3 * p_t1]  # 46, 69
        A = set(A0 + extras)
        for p in large[1:]:
            if len(A) >= len(primes) + 1:
                break
            A.add(p)
        return sorted(A), {"n": n, "t": t, "A0": A0, "extras": extras, "edges": 8}

    # General case: build adversarial 2-regular
    edges = build_adversarial_2regular(small, n)
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

    return sorted(A), {"n": n, "t": t, "A0": A0, "extras": extras, "edges": len(edges)}


def compute_f(A: List[int], primes: List[int], max_r: int) -> int:
    """Compute f: smallest r with r primes covering > r elements."""
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    def cov(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        if r <= 10:
            search = rel[:min(25, len(rel))]
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


def run_tests():
    print("=" * 70)
    print("ERDŐS PROBLEM #983: Adversarial Graph Construction")
    print("=" * 70)
    print()

    # Test n=100 first
    print("Testing n=100 (manual adversarial construction):")
    n = 100
    primes = sieve(n)
    A, info = build_woett_adversarial(n)
    print(f"A0 = {info['A0']}")
    print(f"|A| = {len(A)}, target = {len(primes) + 1}")

    f = compute_f(A, primes, 15)
    pi_sqrt = pi(10, primes)
    gap = 2 * pi_sqrt - f
    print(f"f = {f}, upper = {2*pi_sqrt + 1}, gap = {gap}")
    print()

    # Run for multiple n
    print("Full experiments:")
    results = []

    for n in [100, 200, 400, 800, 1000, 2000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        A, info = build_woett_adversarial(n)
        if not A:
            print(f"n={n}: Failed")
            continue

        f = compute_f(A, primes, min(upper + 5, 25))
        gap = 2 * pi_sqrt - f

        results.append({"n": n, "t": info["t"], "f": f, "upper": upper, "gap": gap})
        print(f"n={n:5d}: t={info['t']:2d}, f={f:3d}, upper={upper:3d}, gap={gap:3d}")

    # Summary
    print()
    gaps = [r["gap"] for r in results]
    print(f"Gaps: {gaps}")

    # Conclusion
    print()
    if all(r["f"] == r["upper"] for r in results):
        print("★ f = upper bound for all n → gap ≈ -1 → Answer: NO")
    elif gaps[-1] > gaps[0] + 5:
        print(f"★ Gap appears to grow ({gaps[0]} → {gaps[-1]}) → Answer: LIKELY YES")
    else:
        print("⚠ Results inconclusive")


if __name__ == "__main__":
    run_tests()
