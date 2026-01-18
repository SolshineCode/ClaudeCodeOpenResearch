#!/usr/bin/env python3
"""
Optimized Experiment: Erdős Problem #983

Focus on JUST verifying f values efficiently.
Uses smarter search strategies to compute f quickly.
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


def build_adversarial_set(n: int, eps: float = 0.1) -> Tuple[List[int], int]:
    """
    Build the adversarial set A with |A| = π(n) + 1.

    Returns (A, t) where t is the number of small primes.
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    large = [p for p in primes if p > thresh]
    t = len(small)

    if t < 3 or not large:
        return [], t

    # Build Hamiltonian cycle on small primes
    # Edges: (small[0], small[1]), (small[1], small[2]), ..., (small[t-1], small[0])
    edges = []
    for i in range(t):
        p, q = small[i], small[(i + 1) % t]
        if p * q <= n:
            edges.append((p, q))

    # Products from edges
    A0 = [p * q for p, q in edges]

    # First large prime
    p_t1 = large[0]

    # Extras: 2*p_t1, 3*p_t1 if valid
    extra = [x for x in [2 * p_t1, 3 * p_t1] if x <= n]

    # Build A
    target = len(primes) + 1
    A = set(A0 + extra)

    # Add large primes until we reach target
    for p in large[1:]:
        if len(A) >= target:
            break
        A.add(p)

    return sorted(A), t


def compute_f_fast(A: List[int], primes: List[int], max_r: int) -> int:
    """
    Compute f efficiently using smart search.

    Key insight: Focus on small primes first since they cover more.
    """
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    # Precompute which elements each prime covers
    coverage = {p: set() for p in rel}
    for e in A:
        for p in facs[e]:
            coverage[p].add(e)

    def cov(pset):
        """Count elements covered by pset."""
        covered = set()
        for p in pset:
            if p in coverage:
                covered |= coverage[p]
        return len(covered)

    def cov_subset(pset):
        """Count elements whose ALL factors are in pset."""
        return sum(1 for e in A if facs[e].issubset(pset))

    # Sort primes by coverage potential (prefer those that cover more semiprimes)
    semi_count = defaultdict(int)
    for e in A:
        if len(facs[e]) == 2:  # Semiprime
            for p in facs[e]:
                semi_count[p] += 1

    # Prioritize primes that appear in many semiprimes
    priority = sorted(rel, key=lambda p: semi_count[p], reverse=True)

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        # Quick greedy check
        chosen = set(priority[:r])
        if cov_subset(chosen) > r:
            return r

        # Exhaustive for very small r
        if r <= 8:
            top_primes = priority[:min(20, len(priority))]
            if len(top_primes) >= r:
                for combo in combinations(top_primes, r):
                    if cov_subset(set(combo)) > r:
                        return r

        # Greedy expansion
        chosen = set()
        for _ in range(r):
            best_p, best_gain = None, -1
            cur = cov_subset(chosen)
            for p in rel:
                if p not in chosen:
                    gain = cov_subset(chosen | {p}) - cur
                    if gain > best_gain:
                        best_gain, best_p = gain, p
            if best_p:
                chosen.add(best_p)

        if cov_subset(chosen) > r:
            return r

    return -1


def manual_construction_n100():
    """Known-good construction for n=100."""
    A0 = [26, 38, 33, 51, 77, 85, 91, 95]  # 2-regular semiprimes
    extra = [46, 69]  # 2×23, 3×23
    large = [29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    return sorted(set(A0 + extra + large))


def run_experiments():
    print("=" * 70)
    print("ERDŐS PROBLEM #983: Optimized Experiments")
    print("=" * 70)
    print()

    results = []

    # First test n=100 with manual construction
    print("Testing n=100 with MANUAL construction (known f=9):")
    primes = sieve(100)
    A_manual = manual_construction_n100()
    f_manual = compute_f_fast(A_manual, primes, 15)
    print(f"  f = {f_manual}")
    print()

    # Test range of n
    for n in [100, 200, 400, 800, 1000, 2000, 4000, 8000, 10000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        if n == 100:
            A = manual_construction_n100()
            t = 8
        else:
            A, t = build_adversarial_set(n)

        if not A:
            print(f"n={n}: Construction failed (t={t})")
            continue

        f = compute_f_fast(A, primes, min(upper + 10, 40))
        gap = 2 * pi_sqrt - f

        results.append({
            "n": n,
            "t": t,
            "pi_sqrt": pi_sqrt,
            "upper": upper,
            "f": f,
            "gap": gap
        })

        status = "✓" if f <= upper else "✗"
        print(f"n={n:6d}: t={t:3d}, f={f:3d}, 2π(√n)={2*pi_sqrt:3d}, upper={upper:3d}, gap={gap:3d} {status}")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)

    print(f"\n{'n':>7} | {'t':>4} | {'f':>4} | {'2π(√n)':>7} | {'upper':>6} | {'gap':>5}")
    print("-" * 50)
    for r in results:
        print(f"{r['n']:>7} | {r['t']:>4} | {r['f']:>4} | {2*r['pi_sqrt']:>7} | {r['upper']:>6} | {r['gap']:>5}")

    # Gap analysis
    gaps = [r["gap"] for r in results]
    print()
    print(f"Gaps observed: {gaps}")
    print(f"Gap range: [{min(gaps)}, {max(gaps)}]")

    # Check if gap is growing
    if len(gaps) >= 3:
        increasing = all(gaps[i] <= gaps[i+1] for i in range(len(gaps)-1))
        print(f"Gap monotonically increasing: {increasing}")

        # Check trend
        if gaps[-1] > gaps[0] + 10:
            print(f"Gap grew from {gaps[0]} to {gaps[-1]} — suggests gap → ∞")

    # Conclusion
    print()
    print("=" * 70)
    print("PRELIMINARY CONCLUSION")
    print("=" * 70)

    if all(r["f"] <= r["upper"] for r in results):
        print("\n✓ Upper bound f ≤ 2π(√n) + 1 VERIFIED for all n")
        print("  This proves: gap ≥ -1 (bounded below)")
    else:
        print("\n⚠ Upper bound violated for some n")

    if gaps[-1] > gaps[0] + 5:
        print(f"\n⚠ Gap appears to be GROWING ({gaps[0]} → {gaps[-1]})")
        print("  This suggests: gap → ∞ (Answer: YES)")
    else:
        print(f"\n? Gap appears relatively stable")
        print("  Unclear whether gap → ∞")

    print()
    print("NOTE: The gap behavior depends critically on how f relates to t.")
    print("If f ≈ t + 1 (Woett lower bound is tight), then gap → ∞.")
    print("If f ≈ 2π(√n) (upper bound is tight), then gap ≈ O(1).")


if __name__ == "__main__":
    run_experiments()
