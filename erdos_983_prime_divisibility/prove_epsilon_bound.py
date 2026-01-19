#!/usr/bin/env python3
"""
Rigorous analysis of the epsilon constraint in Woett's construction.

Key Question: What is the maximum number of primes t that can participate
in a valid 2-regular bipartite matching where all products pq ≤ n?

If we can prove t ≤ c·π(√n) for some c < 2, then:
- f ≤ t + O(1) ≈ c·π(√n)
- gap = 2π(√n) - f ≥ (2-c)π(√n) → ∞

This would PROVE the answer is YES.
"""

import math
from itertools import combinations
from collections import defaultdict

def sieve(n):
    """Generate primes up to n."""
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):
                is_prime[j] = False
    return [i for i in range(n + 1) if is_prime[i]]

def pi(x, primes):
    """Prime counting function."""
    return sum(1 for p in primes if p <= x)

def max_matching_size(primes_list, n):
    """
    Find the maximum number of primes that can participate in a
    2-regular bipartite matching where all products are ≤ n.

    A 2-regular bipartite matching on t vertices (each side) has:
    - t vertices on left, t vertices on right
    - Each vertex has degree exactly 2
    - Total edges = 2t (since sum of left degrees = 2t)
    - Each edge (p,q) must satisfy p*q ≤ n

    Returns: (max_t, edges) where max_t is the maximum t achievable
    """
    t = len(primes_list)
    if t < 2:
        return 0, []

    # Build adjacency: which pairs (i,j) have primes[i]*primes[j] ≤ n?
    valid_edges = []
    for i in range(t):
        for j in range(i+1, t):
            if primes_list[i] * primes_list[j] <= n:
                valid_edges.append((i, j))

    # For a 2-regular matching, we need each prime to appear in exactly 2 edges
    # This is equivalent to finding a 2-regular spanning subgraph

    # Greedy approach: find maximum subset of primes with this property
    # Start with all primes, compute degree of each

    degree = defaultdict(int)
    for i, j in valid_edges:
        degree[i] += 1
        degree[j] += 1

    # Primes with degree < 2 cannot participate
    usable = [i for i in range(t) if degree[i] >= 2]

    # The maximum matching size is limited by the minimum degree constraint
    # For a perfect 2-regular matching on k primes, we need 2k edges
    # Each prime must have degree ≥ 2 in the edge graph

    return len(usable), degree

def analyze_matching_constraint(n):
    """
    Analyze how many primes can participate in a valid Woett construction.
    """
    primes = sieve(n)
    sqrt_n = math.sqrt(n)

    results = []

    for threshold_mult in [1.0, 1.2, 1.4, 1.5, 1.6, 1.8, 1.9, 2.0]:
        threshold = threshold_mult * sqrt_n
        small = [p for p in primes if p <= threshold]
        t = len(small)

        if t < 2:
            continue

        # Count valid pairs
        valid_pairs = 0
        min_degree = float('inf')
        max_degree = 0
        degrees = defaultdict(int)

        for i, p in enumerate(small):
            for j, q in enumerate(small):
                if i < j and p * q <= n:
                    valid_pairs += 1
                    degrees[p] += 1
                    degrees[q] += 1

        if degrees:
            min_degree = min(degrees.values())
            max_degree = max(degrees.values())

        # Primes with degree ≥ 2 can potentially participate
        usable = sum(1 for d in degrees.values() if d >= 2)

        # For 2-regular matching, we need exactly t edges with each vertex having degree 2
        # Maximum t is limited by: 2t ≤ 2 * valid_pairs, so t ≤ valid_pairs
        # But also each vertex needs degree ≥ 2

        results.append({
            'mult': threshold_mult,
            'threshold': threshold,
            't': t,
            'valid_pairs': valid_pairs,
            'usable': usable,
            'min_deg': min_degree if degrees else 0,
            'max_deg': max_degree if degrees else 0,
        })

    return results

def find_max_2regular(primes_list, n):
    """
    Find the maximum size 2-regular bipartite matching.

    Uses backtracking to find the largest subset of primes that can
    form a valid 2-regular structure.
    """
    t = len(primes_list)
    if t < 4:
        return 0, []

    # Valid edges
    edges = []
    for i in range(t):
        for j in range(i+1, t):
            if primes_list[i] * primes_list[j] <= n:
                edges.append((i, j))

    # For each subset size k (from t down to 4), check if 2-regular matching exists
    for k in range(t, 3, -1):
        for subset in combinations(range(t), k):
            subset_set = set(subset)
            # Get edges within this subset
            subset_edges = [(i,j) for i,j in edges if i in subset_set and j in subset_set]

            # Check if we can select exactly k edges forming a 2-regular graph
            # Each vertex in subset must have degree exactly 2
            if len(subset_edges) >= k:
                # Try to find k edges covering all vertices with degree 2 each
                if try_2regular(list(subset_set), subset_edges, k):
                    return k, subset

    return 0, []

def try_2regular(vertices, edges, target_edges):
    """Try to find a 2-regular subgraph using exactly target_edges edges."""
    n_v = len(vertices)
    v_to_idx = {v: i for i, v in enumerate(vertices)}

    # Need to select target_edges edges such that each vertex has degree 2
    # This means 2 * n_v = 2 * target_edges, so n_v = target_edges

    if len(vertices) != target_edges:
        return False

    # Backtracking search
    def backtrack(edge_idx, selected, degree):
        if len(selected) == target_edges:
            return all(d == 2 for d in degree)

        if edge_idx >= len(edges):
            return False

        # Remaining edges needed
        remaining_needed = target_edges - len(selected)
        remaining_edges = len(edges) - edge_idx
        if remaining_edges < remaining_needed:
            return False

        # Check if any vertex already has degree > 2
        if any(d > 2 for d in degree):
            return False

        i, j = edges[edge_idx]
        ii, jj = v_to_idx[i], v_to_idx[j]

        # Try including this edge
        if degree[ii] < 2 and degree[jj] < 2:
            degree[ii] += 1
            degree[jj] += 1
            selected.append((i, j))
            if backtrack(edge_idx + 1, selected, degree):
                return True
            selected.pop()
            degree[ii] -= 1
            degree[jj] -= 1

        # Try excluding this edge
        if backtrack(edge_idx + 1, selected, degree):
            return True

        return False

    return backtrack(0, [], [0] * n_v)

print("=" * 70)
print("RIGOROUS ANALYSIS OF EPSILON CONSTRAINT")
print("=" * 70)
print()

print("PART 1: Degree Analysis")
print("-" * 50)
print()

for n in [100, 400, 900, 1600, 2500]:
    sqrt_n = math.sqrt(n)
    primes = sieve(n)
    pi_sqrt = pi(int(sqrt_n), primes)

    print(f"n = {n}, √n = {sqrt_n:.1f}, π(√n) = {pi_sqrt}")

    results = analyze_matching_constraint(n)

    print(f"  {'mult':>4} {'thresh':>7} {'t':>4} {'pairs':>6} {'usable':>6} {'min_d':>5} {'max_d':>5} {'ratio':>6}")
    for r in results:
        ratio = r['usable'] / pi_sqrt if pi_sqrt > 0 else 0
        print(f"  {r['mult']:>4.1f} {r['threshold']:>7.1f} {r['t']:>4} {r['valid_pairs']:>6} {r['usable']:>6} {r['min_deg']:>5} {r['max_deg']:>5} {ratio:>6.2f}")
    print()

print()
print("PART 2: Maximum 2-Regular Matching Size")
print("-" * 50)
print()

for n in [100, 225, 400]:
    sqrt_n = math.sqrt(n)
    primes = sieve(n)
    pi_sqrt = pi(int(sqrt_n), primes)

    # Use primes up to 2√n
    threshold = 2 * sqrt_n
    small = [p for p in primes if p <= threshold]

    print(f"n = {n}: √n = {sqrt_n:.0f}, π(√n) = {pi_sqrt}, primes ≤ 2√n: {len(small)}")

    max_k, best_subset = find_max_2regular(small, n)

    print(f"  Maximum 2-regular matching: {max_k} primes")
    print(f"  Ratio to π(√n): {max_k / pi_sqrt:.2f}")
    if max_k > 0 and max_k <= 10:
        subset_primes = [small[i] for i in best_subset]
        print(f"  Primes used: {subset_primes}")
    print()

print()
print("PART 3: Key Insight")
print("-" * 50)
print("""
The degree constraint is crucial:

For a prime p close to √n to participate in a 2-regular matching,
it needs degree ≥ 2, meaning at least 2 other primes q₁, q₂ with:
  p * q₁ ≤ n  AND  p * q₂ ≤ n

This means q₁, q₂ ≤ n/p ≈ √n (when p ≈ √n).

So large primes (near √n) can only pair with small primes (≤ √n).
But small primes have many options, creating an ASYMMETRY.

This asymmetry limits the effective matching size!
""")

print()
print("PART 4: Theoretical Bound")
print("-" * 50)
print("""
Claim: The maximum 2-regular matching size is O(π(√n)), not O(π(2√n)).

Argument:
1. Primes p with √n < p ≤ 2√n can only pair with primes q ≤ n/p < √n
2. There are π(√n) primes ≤ √n
3. Each small prime can appear in at most 2 edges (2-regular constraint)
4. So at most 2·π(√n) edges involve large primes
5. With 2-regularity, this limits large prime participation

If this bound holds: f ≤ π(√n) + O(1), so gap ≥ π(√n) - O(1) → ∞
""")
