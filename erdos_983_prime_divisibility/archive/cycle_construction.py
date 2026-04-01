#!/usr/bin/env python3
"""
Corrected Woett Construction using Hamiltonian Cycles

KEY INSIGHT:
A 2-regular graph is a disjoint union of cycles. For maximum adversarial
strength, we want a single Hamiltonian cycle through all t primes.

For primes [p1, p2, ..., pt] with threshold T = (2-ε)√n:
- Form edges (p1,p2), (p2,p3), ..., (pt-1,pt), (pt,p1)
- Each prime appears in exactly 2 products
- Products are pi × pi+1

CHALLENGE: Some products pi × pj may exceed n. We need:
- pi × pi+1 ≤ n for all consecutive pairs
- This limits how large the primes can be

The construction works when the cycle can be formed.
"""

import math
from typing import List, Set, Dict, Tuple, Optional
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


def find_hamiltonian_cycle(primes: List[int], n: int) -> Optional[List[Tuple[int, int]]]:
    """
    Find a Hamiltonian cycle through primes where all products are ≤ n.

    Uses greedy heuristic: start from smallest prime, always connect to
    the largest available prime that keeps the product ≤ n.
    """
    t = len(primes)
    if t < 3:
        return None

    # Build adjacency list of valid edges
    adj = defaultdict(set)
    for i, p in enumerate(primes):
        for q in primes[i+1:]:
            if p * q <= n:
                adj[p].add(q)
                adj[q].add(p)

    # Check if cycle is possible (each vertex needs degree ≥ 2)
    for p in primes:
        if len(adj[p]) < 2:
            return None

    # Greedy Hamiltonian path: start from smallest, go to largest possible
    path = [primes[0]]
    used = {primes[0]}

    while len(path) < t:
        curr = path[-1]
        # Find next: largest unused neighbor
        candidates = [p for p in adj[curr] if p not in used]
        if not candidates:
            # Backtrack or fail
            return None
        # Prefer largest to maximize spread
        next_p = max(candidates)
        path.append(next_p)
        used.add(next_p)

    # Check if we can close the cycle
    if path[0] not in adj[path[-1]]:
        # Try alternative: find any valid cycle
        return find_cycle_backtrack(primes, n, adj)

    # Form edges
    edges = []
    for i in range(t):
        p, q = path[i], path[(i+1) % t]
        edges.append((min(p, q), max(p, q)))

    return edges


def find_cycle_backtrack(primes: List[int], n: int, adj: Dict[int, Set[int]]) -> Optional[List[Tuple[int, int]]]:
    """Backtracking search for Hamiltonian cycle."""
    t = len(primes)
    if t > 12:  # Too expensive for large t
        return None

    def dfs(path, used):
        if len(path) == t:
            # Check if we can close the cycle
            if path[0] in adj[path[-1]]:
                edges = []
                for i in range(t):
                    p, q = path[i], path[(i+1) % t]
                    edges.append((min(p, q), max(p, q)))
                return edges
            return None

        curr = path[-1]
        for next_p in sorted(adj[curr], reverse=True):
            if next_p not in used:
                result = dfs(path + [next_p], used | {next_p})
                if result:
                    return result
        return None

    # Try starting from each prime
    for start in primes:
        result = dfs([start], {start})
        if result:
            return result

    return None


def build_greedy_2regular(primes: List[int], n: int) -> List[Tuple[int, int]]:
    """
    Build a 2-regular graph greedily, prioritizing spread.

    If Hamiltonian cycle isn't possible, build union of smaller cycles.
    """
    t = len(primes)
    if t < 3:
        return []

    # Build valid edge set
    valid_edges = []
    for i, p in enumerate(primes):
        for q in primes[i+1:]:
            if p * q <= n:
                valid_edges.append((p, q))

    # Sort by product size descending (prefer larger products for spread)
    valid_edges.sort(key=lambda e: e[0] * e[1], reverse=True)

    deg = {p: 0 for p in primes}
    edges = []

    for p, q in valid_edges:
        if deg[p] < 2 and deg[q] < 2:
            edges.append((p, q))
            deg[p] += 1
            deg[q] += 1

    return edges


def build_woett_cycle(n: int, eps: float = 0.1, verbose: bool = False) -> Tuple[List[int], Dict]:
    """
    Build Woett's adversarial set using cycle-based 2-regular graph.
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    thresh = (2 - eps) * sqrt_n

    small = [p for p in primes if p <= thresh]
    t = len(small)

    if t < 3:
        return [], {"error": "t < 3", "t": t}

    # Try Hamiltonian cycle first
    edges = find_hamiltonian_cycle(small, n)

    if not edges:
        # Fall back to greedy 2-regular
        if verbose:
            print(f"  Hamiltonian cycle not found, using greedy")
        edges = build_greedy_2regular(small, n)

    # Count degrees
    deg = defaultdict(int)
    for p, q in edges:
        deg[p] += 1
        deg[q] += 1

    # Check coverage
    covered = [p for p in small if deg[p] == 2]
    uncovered = [p for p in small if deg[p] < 2]

    if verbose:
        print(f"  t={t}, edges={len(edges)}, covered={len(covered)}, uncovered={len(uncovered)}")

    # Semiprimes (A₀)
    A0 = sorted([p * q for p, q in edges])

    # Large primes beyond threshold
    large = [p for p in primes if p > thresh]
    if not large:
        return [], {"error": "no large primes", "t": t}

    p_t1 = large[0]

    # Extra composites
    extra = []
    for p in [2, 3]:
        if p in deg and deg[p] == 2 and p * p_t1 <= n:
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
        "small": small,
        "edges": edges,
        "degree": dict(deg),
        "covered": len(covered),
        "uncovered": uncovered,
        "A0": A0,
        "p_t1": p_t1,
        "extra": extra,
        "size": len(A),
        "target": target
    }

    return sorted(A), info


def compute_f_exhaustive(A: List[int], primes: List[int], max_r: int, verbose: bool = False) -> Tuple[int, List[int], int]:
    """Compute f for set A exhaustively."""
    facs = {e: factors(e, primes) for e in A}
    rel = sorted(set().union(*facs.values()))

    def cov(pset):
        return sum(1 for e in A if facs[e].issubset(pset))

    for r in range(1, min(max_r + 1, len(rel) + 1)):
        best = 0
        best_primes = []

        # Exhaustive for small r
        if r <= 10:
            search_space = rel[:min(40, len(rel))]
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
                print(f"  r={r}: greedy covers {best} > {r}")
            return r, best_primes, best

    return -1, [], 0


def verify_2regularity(edges: List[Tuple[int, int]], primes: List[int]) -> Dict:
    """Verify 2-regularity of edge set."""
    deg = defaultdict(int)
    for p, q in edges:
        deg[p] += 1
        deg[q] += 1

    deg0 = [p for p in primes if deg[p] == 0]
    deg1 = [p for p in primes if deg[p] == 1]
    deg2 = [p for p in primes if deg[p] == 2]

    return {
        "deg0": deg0,
        "deg1": deg1,
        "deg2": deg2,
        "is_2regular": len(deg0) == 0 and len(deg1) == 0
    }


def run_experiments():
    """Run experiments with cycle construction."""
    print("=" * 70)
    print("ERDŐS PROBLEM #983: Cycle-Based 2-Regular Construction")
    print("=" * 70)
    print()

    results = []

    for n in [100, 200, 400, 600, 800, 1000, 2000, 5000]:
        primes = sieve(n)
        sqrt_n = int(math.sqrt(n))
        pi_sqrt = pi(sqrt_n, primes)
        upper = 2 * pi_sqrt + 1

        A, info = build_woett_cycle(n)

        if not A:
            print(f"n={n}: Construction failed ({info.get('error', 'unknown')})")
            continue

        # Verify 2-regularity
        reg = verify_2regularity(info["edges"], info["small"])

        f, _, _ = compute_f_exhaustive(A, primes, min(upper + 5, 25))
        gap = 2 * pi_sqrt - f

        t = info["t"]
        num_edges = len(info["edges"])
        expected_f = num_edges + 1  # Should be t edges in a Hamiltonian cycle

        results.append({
            "n": n,
            "t": t,
            "edges": num_edges,
            "pi_sqrt": pi_sqrt,
            "upper": upper,
            "f": f,
            "expected_f": expected_f,
            "gap": gap,
            "is_2reg": reg["is_2regular"],
            "uncovered": len(reg["deg0"]) + len(reg["deg1"])
        })

        reg_str = "✓" if reg["is_2regular"] else f"✗({info['uncovered']})"
        bound_ok = "✓" if f <= upper else "✗"
        print(f"n={n:5d}: t={t:2d}, edges={num_edges:2d}, f={f:3d}, 2π(√n)={2*pi_sqrt:3d}, gap={gap:3d} {bound_ok} 2-reg:{reg_str}")

    print()
    print("=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70)

    print(f"\n{'n':>6} | {'t':>3} | {'edges':>5} | {'f':>4} | {'2π(√n)':>7} | {'gap':>5} | {'2-reg':>5}")
    print("-" * 55)
    for r in results:
        reg = "Y" if r["is_2reg"] else f"N-{r['uncovered']}"
        print(f"{r['n']:>6} | {r['t']:>3} | {r['edges']:>5} | {r['f']:>4} | {2*r['pi_sqrt']:>7} | {r['gap']:>5} | {reg:>5}")

    # Analysis
    print()
    print("=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    gaps = [r["gap"] for r in results]
    print(f"\nGaps: {gaps}")
    print(f"Gap range: [{min(gaps)}, {max(gaps)}]")

    # Key question: does gap grow?
    if len(gaps) >= 2:
        trend = "INCREASING" if gaps[-1] > gaps[0] else "STABLE/DECREASING"
        print(f"Gap trend: {trend}")

    # Check upper bound
    if all(r["f"] <= r["upper"] for r in results):
        print("\n✓ Upper bound f ≤ 2π(√n) + 1 VERIFIED for all tested n")
        print("  This means: gap = 2π(√n) - f ≥ -1 (bounded below)")
    else:
        print("\n✗ Upper bound violated for some n — check construction")

    # The key insight
    print()
    print("KEY OBSERVATION:")
    print("-" * 50)
    print("If the 2-regular graph has k edges (each prime has degree 2),")
    print("then f should be approximately k+1 (or k+2 accounting for extras).")
    print()
    print("For a perfect Hamiltonian cycle on t primes: k = t edges")
    print("So f ≈ t + 1 = π((2-ε)√n) + 1")
    print()
    print("Gap = 2π(√n) - f ≈ 2π(√n) - π((2-ε)√n) - 1")
    print("    ≈ π(2√n) - π((2-ε)√n)  [primes in the interval]")
    print()
    print("By PNT, this is approximately:")
    print("    2ε√n / ln(2√n) → ∞ as n → ∞")

    return results


if __name__ == "__main__":
    run_experiments()
