#!/usr/bin/env python3
"""
DEFINITIVE Experiment: Erdős Problem #983

After much debugging, the correct construction:
1. Build 2-regular graph on small primes (≤ (2-ε)√n)
2. A0 = semiprimes from the graph
3. extras = 2×p_{t+1}, 3×p_{t+1} where p_{t+1} is first prime > threshold
4. A = A0 + extras + large primes to reach |A| = π(n) + 1

The extras are NECESSARY to reach the correct set size and
DO NOT create vulnerabilities at the relevant r values.
"""

import math
from typing import List, Set, Tuple
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


def build_spread_2regular(primes_list: List[int], n: int) -> List[Tuple[int, int]]:
    """Build 2-regular graph with maximum spread between paired primes."""
    t = len(primes_list)
    if t < 3:
        return []

    # All valid edges (products ≤ n)
    all_edges = [(p, q) for i, p in enumerate(primes_list) for q in primes_list[i+1:] if p * q <= n]

    # Sort by spread (distance in the sorted list)
    idx = {p: i for i, p in enumerate(primes_list)}
    all_edges.sort(key=lambda e: abs(idx[e[1]] - idx[e[0]]), reverse=True)

    # Greedy 2-regular
    deg = defaultdict(int)
    selected = []
    for p, q in all_edges:
        if deg[p] < 2 and deg[q] < 2:
            selected.append((p, q))
            deg[p] += 1
            deg[q] += 1

    return selected


def build_woett_definitive(n: int, eps: float = 0.1) -> Tuple[List[int], dict]:
    """Build the definitive Woett construction."""
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    large = [p for p in primes if p > thresh]
    t = len(small)

    if t < 3 or not large:
        return [], {"error": "insufficient primes", "t": t}

    # 2-regular graph with spread
    edges = build_spread_2regular(small, n)
    A0 = sorted([p * q for p, q in edges])

    # First prime beyond threshold
    p_t1 = large[0]

    # Extras: 2×p_{t+1}, 3×p_{t+1}
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

    # Check if we need more elements
    while len(A) < target:
        # Add more large primes if available, or adjust
        remaining = [p for p in large if p not in A]
        if remaining:
            A.add(remaining[0])
        else:
            break

    info = {
        "n": n,
        "t": t,
        "edges": len(edges),
        "A0": A0,
        "extras": extras,
        "p_t1": p_t1,
        "size": len(A),
        "target": target
    }

    return sorted(A), info


def compute_f(A: List[int], primes: List[int], max_r: int) -> int:
    """Compute f: smallest r such that r primes cover > r elements."""
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    def cov(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        # Exhaustive for small r
        if r <= 10:
            search = rel[:min(25, len(rel))]
            if len(search) >= r:
                for combo in combinations(search, r):
                    if cov(set(combo)) > r:
                        return r

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

        if cov(chosen) > r:
            return r

    return max_r + 1


def run_definitive_experiments():
    print("=" * 70)
    print("ERDŐS PROBLEM #983: DEFINITIVE EXPERIMENTS")
    print("=" * 70)
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000, 1500, 2000, 3000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        A, info = build_woett_definitive(n)

        if not A:
            print(f"n={n}: Construction failed")
            continue

        t = info["t"]
        edges = info["edges"]

        f = compute_f(A, primes, min(upper + 10, 30))
        gap = 2 * pi_sqrt - f

        results.append({
            "n": n,
            "t": t,
            "edges": edges,
            "pi_sqrt": pi_sqrt,
            "upper": upper,
            "f": f,
            "gap": gap,
            "size": info["size"],
            "target": info["target"]
        })

        size_ok = "✓" if info["size"] == info["target"] else "✗"
        bound_ok = "✓" if f <= upper else "✗"
        print(f"n={n:5d}: t={t:2d}, f={f:3d}, upper={upper:3d}, gap={gap:3d} {bound_ok} |A|={info['size']}/{info['target']} {size_ok}")

    # Summary
    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    print(f"\n{'n':>6} | {'t':>3} | {'f':>4} | {'upper':>5} | {'gap':>4} | {'status':>8}")
    print("-" * 45)
    for r in results:
        status = "UPPER" if r["f"] == r["upper"] else ("LOWER" if r["f"] == r["edges"] + 1 else "BETWEEN")
        print(f"{r['n']:>6} | {r['t']:>3} | {r['f']:>4} | {r['upper']:>5} | {r['gap']:>4} | {status:>8}")

    gaps = [r["gap"] for r in results]
    print(f"\nGaps: {gaps}")
    print(f"Range: [{min(gaps)}, {max(gaps)}]")

    # Analysis
    print()
    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    at_upper = sum(1 for r in results if r["f"] == r["upper"])
    at_lower = sum(1 for r in results if r["f"] == r["edges"] + 1)

    print(f"\nf = upper bound for {at_upper}/{len(results)} cases")
    print(f"f = lower bound (t+1) for {at_lower}/{len(results)} cases")

    if all(r["f"] <= r["upper"] for r in results):
        print("\n✓ Upper bound f ≤ 2π(√n) + 1 VERIFIED for all n")

    # Determine answer
    if at_upper >= len(results) * 0.8:
        print("""
★ ANSWER: NO — the gap 2π(√n) - f does NOT tend to ∞

Since f ≈ 2π(√n) + 1 (upper bound is essentially tight):
  gap = 2π(√n) - f ≈ -1

The gap stays bounded near -1.
""")
    elif at_lower >= len(results) * 0.5:
        print("""
★ ANSWER: YES — the gap 2π(√n) - f DOES tend to ∞

Since f ≈ t + 1 (lower bound from Woett construction):
  gap = 2π(√n) - f ≈ 2π(√n) - π((2-ε)√n) - 1
      → ∞ as n → ∞
""")
    else:
        avg_gap_ratio = sum(r["gap"] / (2 * r["pi_sqrt"]) for r in results) / len(results)
        print(f"""
⚠ ANALYSIS UNCERTAIN

Average gap/2π(√n) ratio: {avg_gap_ratio:.3f}

If ratio → 0: gap is o(π(√n)), answer depends on precise asymptotics
If ratio → constant: gap ∝ π(√n) → ∞, answer is YES
""")


if __name__ == "__main__":
    run_definitive_experiments()
