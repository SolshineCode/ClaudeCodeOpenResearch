#!/usr/bin/env python3
"""
Debug: Compare my automated construction with the manual one that worked.
"""

from woett_proper import sieve, factors, build_spread_2regular, construct_woett_set, compute_f_exhaustive

def manual_n100():
    """The CORRECT manual construction for n=100 that gives f=9."""
    # A₀: 2-regular with good spread
    # Each prime in {2,3,5,7,11,13,17,19} appears exactly twice
    A0_manual = [
        26,  # 2 × 13
        38,  # 2 × 19
        33,  # 3 × 11
        51,  # 3 × 17
        77,  # 7 × 11
        85,  # 5 × 17
        91,  # 7 × 13
        95,  # 5 × 19
    ]

    # Extra: 2×23, 3×23
    extra = [46, 69]

    # Large primes
    large_primes = [29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    A = sorted(set(A0_manual + extra + large_primes))
    return A, A0_manual


def automated_n100():
    """My automated construction."""
    A, info = construct_woett_set(100, epsilon=0.1, verbose=False)
    return A, info.get('A0', []), info.get('edges', [])


def analyze_coverage(A0, small_primes, n):
    """Analyze how efficiently small prime sets cover A0."""
    primes = sieve(n)
    facs = {e: factors(e, primes) for e in A0}

    from itertools import combinations

    print(f"\nA0 = {A0}")
    print(f"Products and their factors:")
    for e in A0:
        print(f"  {e} = {' × '.join(map(str, sorted(facs[e])))}")

    print(f"\nCoverage analysis:")

    # Check how many elements each small prime set covers
    for r in range(1, min(9, len(small_primes) + 1)):
        best_cov = 0
        best_combo = None

        for combo in combinations(small_primes, r):
            pset = set(combo)
            cov = sum(1 for e in A0 if facs[e].issubset(pset))
            if cov > best_cov:
                best_cov = cov
                best_combo = combo

        print(f"  r={r}: best {r} primes cover {best_cov} of {len(A0)} elements")
        if best_cov == len(A0):
            print(f"       → All covered by {best_combo}")
            break


def main():
    n = 100
    primes = sieve(n)
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19]  # primes ≤ 19

    print("="*60)
    print("COMPARISON: Manual vs Automated Construction for n=100")
    print("="*60)

    # Manual construction
    print("\n" + "="*40)
    print("MANUAL CONSTRUCTION (known to give f=9)")
    print("="*40)

    A_manual, A0_manual = manual_n100()
    print(f"|A| = {len(A_manual)}")
    analyze_coverage(A0_manual, small_primes, n)

    f_manual, _, _ = compute_f_exhaustive(A_manual, primes, 15, verbose=False)
    print(f"\nComputed f = {f_manual}")

    # Automated construction
    print("\n" + "="*40)
    print("AUTOMATED CONSTRUCTION")
    print("="*40)

    A_auto, A0_auto, edges = automated_n100()
    print(f"|A| = {len(A_auto)}")
    print(f"Edges: {edges}")
    analyze_coverage(A0_auto, small_primes, n)

    f_auto, _, _ = compute_f_exhaustive(A_auto, primes, 15, verbose=False)
    print(f"\nComputed f = {f_auto}")

    # Compare A0
    print("\n" + "="*40)
    print("COMPARISON OF A0")
    print("="*40)

    print(f"Manual A0: {sorted(A0_manual)}")
    print(f"Auto A0:   {sorted(A0_auto)}")

    common = set(A0_manual) & set(A0_auto)
    only_manual = set(A0_manual) - set(A0_auto)
    only_auto = set(A0_auto) - set(A0_manual)

    print(f"Common: {sorted(common)}")
    print(f"Only in manual: {sorted(only_manual)}")
    print(f"Only in auto: {sorted(only_auto)}")

    # Key insight
    print("\n" + "="*40)
    print("KEY INSIGHT")
    print("="*40)

    print("""
The manual construction pairs:
  2 with 13, 19 (medium-large primes)
  3 with 11, 17 (medium-large primes)
  5 with 17, 19 (large primes)
  7 with 11, 13 (medium primes)

This creates a "bipartite-like" structure where small primes (2,3,5,7)
are paired with larger primes (11,13,17,19), maximizing spread.

The key property: No 3 products share more than 1 prime.
This prevents efficient coverage by small prime sets.
""")


if __name__ == "__main__":
    main()
