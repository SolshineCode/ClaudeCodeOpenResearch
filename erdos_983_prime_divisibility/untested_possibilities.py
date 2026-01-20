#!/usr/bin/env python3
"""
Untested Possibilities for Erdős Problem #983

This script explores approaches we haven't fully tested.
"""

import math
from collections import defaultdict
from itertools import combinations

def sieve(n):
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
    return sum(1 for p in primes if p <= x)

def factorize(n, primes):
    if n <= 1:
        return set()
    factors = set()
    temp = n
    for p in primes:
        if p * p > temp:
            break
        if temp % p == 0:
            factors.add(p)
            while temp % p == 0:
                temp //= p
    if temp > 1:
        factors.add(temp)
    return factors

print("=" * 70)
print("UNTESTED POSSIBILITIES")
print("=" * 70)

# =============================================================================
# TEST 1: What if we DON'T use semiprimes?
# =============================================================================
print("\n" + "=" * 70)
print("TEST 1: Non-semiprime adversarial sets")
print("=" * 70)
print("""
The Woett construction uses semiprimes pq. But what if we use:
- Prime powers (p^k)?
- Products of 3+ primes?
- Mixed sets?
""")

n = 100
primes = sieve(n)
pi_n = len(primes)
target = pi_n + 1  # = 26

# Alternative construction: use smooth numbers instead of semiprimes
# Smooth numbers have ALL prime factors ≤ some bound

def get_smooth_numbers(n, bound):
    """Get all numbers ≤ n that are B-smooth (all prime factors ≤ bound)."""
    smooth = []
    for x in range(2, n + 1):
        factors = factorize(x, primes)
        if factors and max(factors) <= bound:
            smooth.append(x)
    return smooth

# Try different smoothness bounds
for bound in [5, 7, 10, 13]:
    smooth = get_smooth_numbers(n, bound)
    print(f"  {bound}-smooth numbers ≤ {n}: {len(smooth)}")
    if len(smooth) >= 10:
        print(f"    First 10: {smooth[:10]}")

print("\n  Could a smooth-number based adversarial set give different f?")

# =============================================================================
# TEST 2: What happens right after n=100?
# =============================================================================
print("\n" + "=" * 70)
print("TEST 2: Phase transition around n=100")
print("=" * 70)
print("""
At n=100, gap = -1 (minimum possible).
At n=200, gap = 3.
What happens in between?
""")

for n in [100, 110, 120, 130, 140, 150, 160, 180, 200]:
    primes = sieve(n)
    sqrt_n = int(math.sqrt(n))
    pi_sqrt = pi(sqrt_n, primes)
    two_pi_sqrt = 2 * pi_sqrt

    # Upper bound on f
    upper = two_pi_sqrt + 1

    # Woett lower bound (eps=1)
    woett_lower = pi_sqrt + 1

    print(f"  n={n}: sqrt={sqrt_n}, pi(sqrt)={pi_sqrt}, 2pi(sqrt)={two_pi_sqrt}")
    print(f"         bounds: {woett_lower} <= f <= {upper}, gap in [{two_pi_sqrt - upper}, {two_pi_sqrt - woett_lower}]")

# =============================================================================
# TEST 3: What if gap stays bounded?
# =============================================================================
print("\n" + "=" * 70)
print("TEST 3: Devil's advocate - what if answer is NO?")
print("=" * 70)
print("""
For answer to be NO, we need f ~ 2*pi(sqrt(n)), so gap ~ constant.

This would require:
- A construction where 2*pi(sqrt(n)) primes are NEEDED
- No bottleneck effect

Let's check: how many small primes are "wasted" in typical constructions?
""")

for n in [100, 400, 900]:
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    small = [p for p in primes if p <= sqrt_n]
    large = [p for p in primes if sqrt_n < p <= 2 * sqrt_n]

    # In Woett construction, each small prime appears in 2 semiprimes
    # Total edges = 2 * |small| = 2 * pi(sqrt)
    # But we also need |small| = |large| for perfect matching

    print(f"  n={n}:")
    print(f"    Small primes (≤ sqrt): {len(small)}")
    print(f"    Large primes (sqrt < p ≤ 2sqrt): {len(large)}")
    print(f"    Imbalance: {len(large) - len(small)}")
    print(f"    If balanced, max matching = 2 * {len(small)} = {2 * len(small)} primes")

# =============================================================================
# TEST 4: Exact max 2-regular matching for small n
# =============================================================================
print("\n" + "=" * 70)
print("TEST 4: Exact max 2-regular matching (brute force)")
print("=" * 70)

def find_exact_max_2regular(n, timeout_edges=100):
    """Find exact maximum 2-regular matching."""
    primes = sieve(n)
    sqrt_n = math.sqrt(n)
    candidates = [p for p in primes if p <= 2 * sqrt_n]

    # Build edge list
    edges = []
    for i, p in enumerate(candidates):
        for j, q in enumerate(candidates):
            if i < j and p * q <= n:
                edges.append((i, j))

    if len(edges) > timeout_edges:
        return None, "too many edges"

    t = len(candidates)

    # Try to find 2-regular subgraph with maximum vertices
    for k in range(t, 1, -1):
        for vertex_subset in combinations(range(t), k):
            vs = set(vertex_subset)
            sub_edges = [(i,j) for i,j in edges if i in vs and j in vs]

            # Check if we can pick exactly k edges with each vertex having degree 2
            if len(sub_edges) >= k:
                # Need to find k edges covering k vertices, each with degree 2
                for edge_subset in combinations(sub_edges, k):
                    degree = [0] * t
                    for i, j in edge_subset:
                        degree[i] += 1
                        degree[j] += 1
                    if all(degree[v] == 2 for v in vertex_subset):
                        return k, [candidates[v] for v in vertex_subset]

    return 0, []

print("  Computing exact max 2-regular matching (slow)...")
for n in [49, 64, 81, 100]:
    primes = sieve(n)
    pi_sqrt = pi(int(math.sqrt(n)), primes)

    max_k, primes_used = find_exact_max_2regular(n, timeout_edges=50)
    if max_k is None:
        print(f"  n={n}: too complex")
    else:
        ratio = max_k / pi_sqrt if pi_sqrt > 0 else 0
        print(f"  n={n}: max 2-regular = {max_k}, pi(sqrt) = {pi_sqrt}, ratio = {ratio:.2f}")

# =============================================================================
# TEST 5: Are there adversarial sets we haven't considered?
# =============================================================================
print("\n" + "=" * 70)
print("TEST 5: Alternative adversarial constructions")
print("=" * 70)
print("""
The Woett construction uses:
  A = semiprimes + {2*p_{t+1}, 3*p_{t+1}} + large primes

What about:
  - All primes (no semiprimes)?
  - All semiprimes?
  - Prime powers?
""")

n = 100
primes = sieve(n)
pi_n = len(primes)
target = pi_n + 1

# Construction A: All large primes
A_primes = primes[-target:]
print(f"  A = {target} largest primes: {A_primes[:5]}...{A_primes[-3:]}")

# What's the minimum covering set?
# For primes, each prime p needs prime p in the covering set
# So f = target (each element needs its own prime)
print(f"    f = {target} (each prime needs itself)")
print(f"    gap = 2*pi(sqrt) - f = {2*pi(int(math.sqrt(n)), primes)} - {target} = {2*pi(int(math.sqrt(n)), primes) - target}")

print()
print("KEY INSIGHT: Using all primes makes f very large (bad for adversary)")
print("Semiprimes are good because multiple semiprimes share primes")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY OF UNTESTED POSSIBILITIES")
print("=" * 70)
print("""
1. NON-SEMIPRIME CONSTRUCTIONS: Could give different f values
   Status: Partially tested - semiprimes seem optimal

2. PHASE TRANSITION: Gap jumps from -1 to positive between n=100-200
   Status: UNTESTED - worth investigating

3. DEVIL'S ADVOCATE: Could f track 2*pi(sqrt)?
   Status: Bottleneck argument suggests no, but not proven

4. EXACT MAX 2-REGULAR: Computed for small n, confirms ratios
   Status: Done for n ≤ 100

5. ALTERNATIVE ADVERSARIAL SETS: All-prime set gives huge f
   Status: Tested - semiprimes are better for adversary

MOST PROMISING UNTESTED: Phase transition analysis around n=100-200
""")
