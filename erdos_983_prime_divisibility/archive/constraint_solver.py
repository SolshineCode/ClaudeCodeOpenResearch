#!/usr/bin/env python3
"""
Constraint-Based Adversarial Construction

Implements a proper constraint solver for finding 2-regular bipartite
matchings where no two vertices share the same pair of neighbors.

This is the key to building correct adversarial sets for Erdős Problem #983.
"""

import math
from typing import List, Set, Tuple, Optional, Dict
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


def find_latin_matching(left: List[int], right: List[int], n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Find a 2-regular bipartite matching with Latin rectangle property.

    Each left vertex connects to exactly 2 right vertices.
    Each right vertex connects to exactly 2 left vertices.
    No two left vertices share the same pair of right neighbors.
    All products are ≤ n.
    """
    k = len(left)
    if k != len(right):
        return None

    if k == 0:
        return []

    # Build valid edge set
    valid = {}
    for i, p in enumerate(left):
        valid[i] = []
        for j, q in enumerate(right):
            if p * q <= n:
                valid[i].append(j)

    # Check if each left vertex has at least 2 valid right neighbors
    for i in range(k):
        if len(valid[i]) < 2:
            return None

    # Backtracking search
    # assignment[i] = (j1, j2) means left[i] connects to right[j1] and right[j2]
    assignment = [None] * k
    used_pairs = set()  # Track used (j1, j2) pairs
    right_deg = [0] * k  # Degree of each right vertex

    def backtrack(i: int) -> bool:
        if i == k:
            # Check all right vertices have degree 2
            return all(d == 2 for d in right_deg)

        # Try all pairs of valid neighbors for left[i]
        neighbors = valid[i]
        for idx1 in range(len(neighbors)):
            for idx2 in range(idx1 + 1, len(neighbors)):
                j1, j2 = neighbors[idx1], neighbors[idx2]
                pair = (min(j1, j2), max(j1, j2))

                # Check constraints
                if pair in used_pairs:
                    continue  # Pair already used
                if right_deg[j1] >= 2 or right_deg[j2] >= 2:
                    continue  # Would exceed degree 2

                # Try this assignment
                assignment[i] = (j1, j2)
                used_pairs.add(pair)
                right_deg[j1] += 1
                right_deg[j2] += 1

                if backtrack(i + 1):
                    return True

                # Backtrack
                assignment[i] = None
                used_pairs.remove(pair)
                right_deg[j1] -= 1
                right_deg[j2] -= 1

        return False

    if backtrack(0):
        # Convert to edges
        edges = []
        for i in range(k):
            j1, j2 = assignment[i]
            edges.append((left[i], right[j1]))
            edges.append((left[i], right[j2]))
        return edges

    return None


def find_adversarial_2regular(primes_list: List[int], n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Find an adversarial 2-regular graph on the given primes.

    Strategy:
    1. Split primes into two equal halves (or near-equal for odd count)
    2. Find Latin matching between halves
    3. Handle remaining primes if odd count
    """
    t = len(primes_list)
    if t < 4:
        return None

    # Try splitting at different points
    for split in range(t // 4, 3 * t // 4 + 1):
        if split < 2 or t - split < 2:
            continue

        left = primes_list[:split]
        right = primes_list[split:]

        # For Latin matching, need equal sizes
        if len(left) == len(right):
            edges = find_latin_matching(left, right, n)
            if edges:
                return edges

        # Try with smaller subset
        if len(left) > len(right):
            edges = find_latin_matching(left[:len(right)], right, n)
            if edges:
                return edges
        else:
            edges = find_latin_matching(left, right[:len(left)], n)
            if edges:
                return edges

    return None


def build_adversarial_woett(n: int, eps: float = 0.1) -> Tuple[List[int], Dict]:
    """
    Build Woett's adversarial set using constraint-based construction.
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    large = [p for p in primes if p > thresh]
    t = len(small)

    if t < 4 or not large:
        return [], {"error": "insufficient primes", "t": t}

    # Find adversarial 2-regular graph
    edges = find_adversarial_2regular(small, n)

    if not edges:
        return [], {"error": "no valid matching found", "t": t}

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

    # Verify construction quality
    deg = defaultdict(int)
    for p, q in edges:
        deg[p] += 1
        deg[q] += 1

    # Check no shared pairs
    pairs_by_prime = defaultdict(set)
    for p, q in edges:
        pairs_by_prime[p].add(q)
        pairs_by_prime[q].add(p)

    info = {
        "n": n,
        "t": t,
        "edges": len(edges),
        "A0": A0,
        "extras": extras,
        "p_t1": p_t1,
        "size": len(A),
        "target": target,
        "primes_used": len(deg),
        "all_deg_2": all(d == 2 for d in deg.values())
    }

    return sorted(A), info


def compute_f_correct(A: List[int], primes: List[int], max_r: int) -> Tuple[int, List[int]]:
    """
    Compute f correctly: smallest r such that r primes cover > r elements.
    Returns (f, covering_primes).
    """
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    def cov(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        # Exhaustive search for small r
        if r <= 12:
            search = rel[:min(30, len(rel))]
            if len(search) >= r:
                for combo in combinations(search, r):
                    c = cov(set(combo))
                    if c > r:
                        return r, list(combo)

        # Greedy for larger r
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
            return r, sorted(chosen)

    return max_r + 1, []


def verify_adversarial_property(A: List[int], A0: List[int], primes: List[int]) -> Dict:
    """
    Verify that the construction is properly adversarial.

    For a good construction:
    - r primes should cover at most r elements of A0 for all r < t
    - Only when r = t should we cover > t elements
    """
    facs = {e: factors(e, primes) for e in A0}
    rel = sorted(set().union(*facs.values()))
    t = len(rel)

    def cov(pset):
        return sum(1 for e in A0 if facs[e].issubset(pset))

    results = {}
    for r in range(1, t + 1):
        best = 0
        if r <= 10:
            for combo in combinations(rel, r):
                c = cov(set(combo))
                best = max(best, c)
        else:
            # Greedy
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
            best = cov(chosen)

        results[r] = best

    # Check adversarial property: coverage should equal r for r < |A0|
    is_adversarial = all(results[r] == r for r in range(1, len(A0)))

    return {
        "coverage_by_r": results,
        "is_adversarial": is_adversarial,
        "num_primes": t,
        "num_semiprimes": len(A0)
    }


def run_comprehensive_test():
    print("=" * 70)
    print("ERDŐS PROBLEM #983: Constraint-Based Adversarial Construction")
    print("=" * 70)
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000, 1500, 2000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        print(f"n = {n}")
        print("-" * 40)

        A, info = build_adversarial_woett(n)

        if not A:
            print(f"  Construction failed: {info.get('error', 'unknown')}")
            print()
            continue

        t = info["t"]
        num_edges = info["edges"]

        print(f"  t = {t}, edges = {num_edges}")
        print(f"  A0 = {info['A0'][:6]}..." if len(info['A0']) > 6 else f"  A0 = {info['A0']}")
        print(f"  |A| = {info['size']}, target = {info['target']}")
        print(f"  All primes degree 2: {info['all_deg_2']}")

        # Verify adversarial property on A0
        adv = verify_adversarial_property(A, info["A0"], primes)
        print(f"  A0 is adversarial: {adv['is_adversarial']}")

        if not adv['is_adversarial']:
            print(f"  Coverage pattern: {adv['coverage_by_r']}")

        # Compute f
        f, covering = compute_f_correct(A, primes, min(upper + 5, 30))
        gap = 2 * pi_sqrt - f

        print(f"  f = {f}, covering primes = {covering[:5]}..." if len(covering) > 5 else f"  f = {f}, covering primes = {covering}")
        print(f"  Upper bound = {upper}")
        print(f"  Gap = 2π(√n) - f = {2*pi_sqrt} - {f} = {gap}")

        status = "UPPER" if f == upper else ("LOWER" if f == num_edges // 2 + 1 else "BETWEEN")
        print(f"  Status: f is at {status} bound")
        print()

        results.append({
            "n": n,
            "t": t,
            "edges": num_edges,
            "f": f,
            "upper": upper,
            "gap": gap,
            "adversarial": adv['is_adversarial']
        })

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\n{'n':>6} | {'t':>3} | {'f':>4} | {'upper':>5} | {'gap':>4} | {'adv':>3}")
    print("-" * 40)
    for r in results:
        adv_str = "Y" if r["adversarial"] else "N"
        print(f"{r['n']:>6} | {r['t']:>3} | {r['f']:>4} | {r['upper']:>5} | {r['gap']:>4} | {adv_str:>3}")

    gaps = [r["gap"] for r in results]
    print(f"\nGaps: {gaps}")

    # Analysis
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    at_upper = sum(1 for r in results if r["f"] == r["upper"])
    adversarial_count = sum(1 for r in results if r["adversarial"])

    print(f"\nf = upper bound for {at_upper}/{len(results)} cases")
    print(f"Construction adversarial for {adversarial_count}/{len(results)} cases")

    if at_upper == len(results):
        print("\n★ ANSWER: NO — gap is bounded at approximately -1")
    elif adversarial_count == len(results) and max(gaps) > min(gaps) + 10:
        print(f"\n★ ANSWER: YES — gap grows from {min(gaps)} to {max(gaps)}")
    else:
        print("\n⚠ Results require more analysis")


if __name__ == "__main__":
    run_comprehensive_test()
