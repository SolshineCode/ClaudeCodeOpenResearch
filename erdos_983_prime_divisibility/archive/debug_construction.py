#!/usr/bin/env python3
"""
Debug why the adversarial construction isn't achieving f = t+1.
"""

from utils import sieve_of_eratosthenes, prime_factors, pi


def debug_n100():
    """Detailed analysis for n=100."""
    n = 100
    epsilon = 0.1
    primes = sieve_of_eratosthenes(n)
    sqrt_n = n ** 0.5
    threshold = (2 - epsilon) * sqrt_n  # 19

    small_primes = [p for p in primes if p <= threshold]
    t = len(small_primes)

    print(f"n = {n}")
    print(f"Small primes (≤ {threshold:.1f}): {small_primes}")
    print(f"t = {t}")
    print()

    # According to Woett, we need a 2-regular graph on small_primes
    # where each prime appears in exactly 2 products

    # Valid pairs with product ≤ n
    valid = []
    for i, p in enumerate(small_primes):
        for q in small_primes[i+1:]:
            if p * q <= n:
                valid.append((p, q, p*q))
                print(f"  {p} * {q} = {p*q}")

    print(f"\nValid pairs: {len(valid)}")
    print()

    # Manual construction of 2-regular graph
    # Each of 2,3,5,7,11,13,17,19 must appear exactly twice
    #
    # One valid pairing:
    # 2-19: 38
    # 2-13: 26
    # 3-17: 51
    # 3-11: 33
    # 5-17: 85
    # 5-19: 95
    # 7-11: 77
    # 7-13: 91

    A0 = [38, 26, 51, 33, 85, 95, 77, 91]
    print(f"A₀ (manual 2-regular): {sorted(A0)}")

    # Verify each small prime appears exactly twice
    count = {p: 0 for p in small_primes}
    for prod in A0:
        for p in small_primes:
            if prod % p == 0:
                count[p] += 1

    print(f"Prime counts in A₀: {count}")
    print()

    # Rest of construction
    large_primes = [p for p in primes if p > threshold]
    p_t1 = large_primes[0]  # 23

    print(f"p_(t+1) = {p_t1}")

    extra = []
    if 2 * p_t1 <= n:
        extra.append(2 * p_t1)
    if 3 * p_t1 <= n:
        extra.append(3 * p_t1)

    print(f"Extra composites: {extra}")

    # Fill with large primes
    target_size = len(primes) + 1  # 26
    current = set(A0 + extra)

    for p in large_primes[1:]:
        if len(current) >= target_size:
            break
        current.add(p)

    A = sorted(current)
    print(f"\nA = {A}")
    print(f"|A| = {len(A)}, target = {target_size}")
    print()

    # Now compute f for this set
    print("Computing f...")
    print()

    # Get factors for each element
    factors = {}
    for e in A:
        f = set()
        temp = e
        for p in primes:
            if p * p > temp:
                break
            if temp % p == 0:
                f.add(p)
                while temp % p == 0:
                    temp //= p
        if temp > 1:
            f.add(temp)
        factors[e] = f

    print("Elements and their factors:")
    for e in sorted(A):
        print(f"  {e}: {factors[e]}")
    print()

    # Test small r values
    from itertools import combinations

    all_relevant_primes = set()
    for f in factors.values():
        all_relevant_primes.update(f)
    all_relevant_primes = sorted(all_relevant_primes)

    print(f"Relevant primes: {all_relevant_primes}")
    print(f"Count: {len(all_relevant_primes)}")
    print()

    for r in range(1, 15):
        best_cov = 0
        best_primes = None

        for combo in combinations(all_relevant_primes, r):
            pset = set(combo)
            covered = [e for e in A if factors[e].issubset(pset)]
            if len(covered) > best_cov:
                best_cov = len(covered)
                best_primes = combo

            if len(covered) > r:
                print(f"r = {r}: {combo} covers {len(covered)} > {r} elements: {covered}")
                break
        else:
            print(f"r = {r}: best coverage = {best_cov} (need > {r}), best primes = {best_primes}")
            continue
        break

    print()
    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print()
    print("For Woett's construction to achieve f = t+1 = 9:")
    print("- We need: for r = 1..8, no r primes cover > r elements")
    print("- We need: for r = 9, the 9 primes {2,3,5,7,11,13,17,19,23} cover > 9 = 10 elements")
    print()
    print("Let's verify the claim with the 8 small primes:")

    small_set = set(small_primes)
    covered_by_small = [e for e in A if factors[e].issubset(small_set)]
    print(f"8 small primes cover: {len(covered_by_small)} elements")
    print(f"Elements: {covered_by_small}")
    print()

    # This should be exactly 8 (the A₀ semiprimes), not > 8
    # If it's > 8, then r = 8 works and f ≤ 8

    print("Adding p_(t+1) = 23:")
    small_plus_23 = small_set | {23}
    covered_by_9 = [e for e in A if factors[e].issubset(small_plus_23)]
    print(f"9 primes cover: {len(covered_by_9)} elements")
    print(f"Elements: {covered_by_9}")


if __name__ == "__main__":
    debug_n100()
