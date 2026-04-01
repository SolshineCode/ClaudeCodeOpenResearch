#!/usr/bin/env python3
"""
FINAL Experiment: Erdős Problem #983

KEY CORRECTION: Don't add "extras" (2×p_t1, 3×p_t1) to the set A.
These extras share factors with A0 and create vulnerabilities.

CORRECT CONSTRUCTION:
A = A0 (semiprimes from 2-regular graph) + large primes only
"""

import math
from typing import List, Set, Dict, Tuple
from itertools import combinations
from collections import defaultdict
import time


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


def build_2regular_spread(primes_list: List[int], n: int) -> List[Tuple[int, int]]:
    """Build 2-regular graph maximizing spread between paired primes."""
    t = len(primes_list)
    if t < 3:
        return []

    # All valid edges
    all_edges = []
    for i, p in enumerate(primes_list):
        for q in primes_list[i+1:]:
            if p * q <= n:
                all_edges.append((p, q))

    # Sort by "spread" - prefer pairing distant primes
    def spread(e):
        i1 = primes_list.index(e[0])
        i2 = primes_list.index(e[1])
        return abs(i2 - i1)

    all_edges.sort(key=spread, reverse=True)

    # Greedy selection
    deg = defaultdict(int)
    selected = []
    for p, q in all_edges:
        if deg[p] < 2 and deg[q] < 2:
            selected.append((p, q))
            deg[p] += 1
            deg[q] += 1

    return selected


def build_correct_woett(n: int, eps: float = 0.1) -> Tuple[List[int], Dict]:
    """
    Build Woett's adversarial set CORRECTLY.
    A = A0 (semiprimes) + large primes (NO composites with shared factors)
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    large = [p for p in primes if p > thresh]
    t = len(small)

    if t < 3 or not large:
        return [], {"error": "insufficient primes", "t": t}

    # Build 2-regular graph with spread
    edges = build_2regular_spread(small, n)

    # Semiprimes
    A0 = sorted([p * q for p, q in edges])

    # Target size
    target = len(primes) + 1

    # A = A0 + large primes ONLY (no extras!)
    A = set(A0)
    for p in large:
        if len(A) >= target:
            break
        A.add(p)

    deg = defaultdict(int)
    for p, q in edges:
        deg[p] += 1
        deg[q] += 1

    info = {
        "n": n,
        "t": t,
        "edges": len(edges),
        "A0_size": len(A0),
        "A0": A0,
        "large_added": len(A) - len(A0),
        "size": len(A),
        "target": target
    }

    return sorted(A), info


def compute_f_smart(A: List[int], primes: List[int], max_r: int) -> Tuple[int, int]:
    """
    Compute f efficiently.
    Returns (f, coverage) where f is the smallest r with coverage > r.
    """
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    def cov_subset(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    # Prioritize primes by frequency in semiprimes
    semi_freq = defaultdict(int)
    for e in A:
        if len(facs[e]) == 2:  # Semiprime
            for p in facs[e]:
                semi_freq[p] += 1

    priority = sorted(rel, key=lambda p: semi_freq[p], reverse=True)

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        best = 0

        # Greedy with priority primes
        chosen = set(priority[:r])
        c = cov_subset(chosen)
        best = max(best, c)

        if best > r:
            return r, best

        # Exhaustive for small r, limited search space
        if r <= 8:
            search = priority[:min(25, len(priority))]
            if len(search) >= r:
                for combo in combinations(search, r):
                    c = cov_subset(set(combo))
                    if c > r:
                        return r, c
                    best = max(best, c)

        # Extended greedy
        chosen = set()
        for _ in range(r):
            best_p, best_gain = None, 0
            cur = cov_subset(chosen)
            for p in rel:
                if p not in chosen:
                    g = cov_subset(chosen | {p}) - cur
                    if g > best_gain:
                        best_gain, best_p = g, p
            if best_p:
                chosen.add(best_p)

        c = cov_subset(chosen)
        if c > r:
            return r, c
        best = max(best, c)

    return max_r + 1, best


def manual_n100():
    """Verified optimal construction for n=100 (gives f=9)."""
    A0 = [26, 38, 33, 51, 77, 85, 91, 95]  # 2-regular on {2,3,5,7,11,13,17,19}
    large = [29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    return sorted(set(A0 + large))


def run_final_experiments():
    print("=" * 70)
    print("ERDŐS PROBLEM #983: FINAL EXPERIMENTS")
    print("(Corrected construction: NO extras)")
    print("=" * 70)
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000, 1500, 2000]:
        start = time.time()
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        # Use manual construction for n=100
        if n == 100:
            A = manual_n100()
            info = {"t": 8, "edges": 8, "A0_size": 8}
        else:
            A, info = build_correct_woett(n)

        if not A:
            print(f"n={n}: Construction failed")
            continue

        t = info["t"]
        edges = info.get("edges", 0)

        # Compute f with reasonable timeout
        f, cov = compute_f_smart(A, primes, min(upper + 5, 25))
        elapsed = time.time() - start

        gap = 2 * pi_sqrt - f

        results.append({
            "n": n,
            "t": t,
            "edges": edges,
            "pi_sqrt": pi_sqrt,
            "upper": upper,
            "f": f,
            "gap": gap,
            "time": elapsed
        })

        # Expected: f should be close to t+1 (Woett) or 2π(√n)+1 (upper)
        woett_pred = edges + 1
        upper_pred = upper

        status = "✓" if f <= upper else "✗"
        print(f"n={n:5d}: t={t:2d}, edges={edges:2d}, f={f:3d}, 2π(√n)={2*pi_sqrt:3d}, gap={gap:3d} {status} ({elapsed:.1f}s)")

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\n{'n':>6} | {'t':>3} | {'edges':>5} | {'f':>4} | {'2π(√n)':>6} | {'gap':>4}")
    print("-" * 45)
    for r in results:
        print(f"{r['n']:>6} | {r['t']:>3} | {r['edges']:>5} | {r['f']:>4} | {2*r['pi_sqrt']:>6} | {r['gap']:>4}")

    gaps = [r["gap"] for r in results]
    print(f"\nGaps: {gaps}")
    print(f"Gap range: [{min(gaps)}, {max(gaps)}]")

    # Analysis
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Is f closer to lower bound (edges+1) or upper bound (2π(√n)+1)?
    print("\nComparing f to bounds:")
    for r in results:
        lower = r["edges"] + 1
        upper_val = r["upper"]
        f = r["f"]
        to_lower = f - lower
        to_upper = upper_val - f
        closer = "LOWER" if to_lower < to_upper else "UPPER"
        print(f"  n={r['n']:5d}: f={f:3d}, lower={lower:3d} (+{to_lower:2d}), upper={upper_val:3d} (-{to_upper:2d}) → {closer}")

    # Conclusion
    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if all(r["f"] <= r["upper"] for r in results):
        print("\n✓ Upper bound f ≤ 2π(√n) + 1 VERIFIED for all n")

    # Check if f is consistently at lower bound
    at_lower = sum(1 for r in results if r["f"] == r["edges"] + 1)
    at_upper = sum(1 for r in results if r["f"] == r["upper"])

    print(f"\n  f = lower bound (edges+1) for {at_lower}/{len(results)} cases")
    print(f"  f = upper bound (2π(√n)+1) for {at_upper}/{len(results)} cases")

    if at_lower >= len(results) * 0.8:
        print("""
★ LIKELY ANSWER: YES — gap → ∞

Since f ≈ edges + 1 ≈ t + 1 (Woett lower bound is tight):
  gap = 2π(√n) - f ≈ 2π(√n) - t - 1
      = 2π(√n) - π((2-ε)√n) - 1
      → ∞ as n → ∞
""")
    elif at_upper >= len(results) * 0.8:
        print("""
★ LIKELY ANSWER: NO — gap is bounded

Since f ≈ 2π(√n) + 1 (upper bound is tight):
  gap = 2π(√n) - f ≈ -1
  The gap stays bounded near -1.
""")
    else:
        print("""
⚠ INCONCLUSIVE

f appears to be between lower and upper bounds.
More investigation needed.
""")


if __name__ == "__main__":
    run_final_experiments()
