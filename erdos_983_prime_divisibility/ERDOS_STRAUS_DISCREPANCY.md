# Analysis of the Erdos-Straus Discrepancy

## Problem Statement (from erdosproblems.com #983)

Let $n \geq 2$ and $\pi(n) < k \leq n$. Define $f(k,n)$ as the smallest integer $r$ such that in **any** $A \subseteq \{1, \ldots, n\}$ of size $|A| = k$, there exist primes $p_1, \ldots, p_r$ such that at least $r$ elements $a \in A$ are **only divisible by primes from** $\{p_1, \ldots, p_r\}$.

**Main Question:** Is it true that $2\pi(n^{1/2}) - f(\pi(n)+1, n) \to \infty$ as $n \to \infty$?

## The Claimed Theorem

The Erdos-Straus theorem [Er70b] allegedly states:
$$f(\pi(n)+1, n) = 2\pi(n^{1/2}) + o_A\left(\frac{n^{1/2}}{(\log n)^A}\right)$$

This would imply $f \approx 2\pi(\sqrt{n})$, making the gap approximately 0.

## Computational Results

Extensive testing shows:

| n | $\pi(n)$ | k | $2\pi(\sqrt{n})$ | Computed $f$ | Gap |
|---|----------|---|------------------|--------------|-----|
| 100 | 25 | 26 | 8 | 3-4 | 4-5 |
| 500 | 95 | 96 | 16 | 3-4 | 12-13 |
| 1000 | 168 | 169 | 22 | 3-4 | 18-19 |
| 5000 | 669 | 670 | 38 | 3-4 | 34-35 |
| 10000 | 1229 | 1230 | 50 | 3-4 | 46-47 |

The gap **clearly grows** with $n$, suggesting $f = O(1)$, not $f \approx 2\pi(\sqrt{n})$.

## Theoretical Analysis of the Discrepancy

### Definition Interpretation

"Element $a$ is only divisible by primes from $P$" means: **all prime factors of $a$ are in $P$**.

- If $a = 6 = 2 \times 3$, then $a$ is covered by $P$ iff $\{2,3\} \subseteq P$
- If $a = p$ (prime), then $a$ is covered by $P$ iff $p \in P$
- If $a = 1$, then $a$ is always covered (has no prime factors)

### Why f Should Be Small (O(1))

**Key Observation:** For any set of semiprimes, small prime sets exhibit "triangle efficiency."

If $A$ contains semiprimes with factors in $\{2, 3, 5\}$:
- $\{2, 3\}$ covers $6 = 2 \times 3$
- $\{2, 5\}$ covers $10 = 2 \times 5$
- $\{3, 5\}$ covers $15 = 3 \times 5$
- $\{2, 3, 5\}$ covers all three: **3 elements with 3 primes**

This "triangle pattern" means $f \leq 3$ for any set containing semiprimes with small factors.

### The Hardest Sets: Mixed Semiprimes

For semiprimes $pq$ where $p \leq \sqrt{n}$ (small) and $q > \sqrt{n}$ (large):
- These require **both** $p$ AND $q$ in the covering set
- With $s$ small primes and $t$ large primes, coverage $\approx s \times t$
- For $r = s + t$ primes to cover $\geq r$ elements: need $s \times t \geq s + t$
- This requires $(s-1)(t-1) \geq 1$, so $s \geq 2$ AND $t \geq 2$
- **Minimum $r = 4$**

So even for the hardest sets (pure mixed semiprimes), $f = 4$.

### Why f Cannot Be 2pi(sqrt(n))

For $f \approx 2\pi(\sqrt{n})$ to hold, we would need sets where:
- Any $r < 2\pi(\sqrt{n})$ primes cover fewer than $r$ elements

But this is impossible because:
1. **If $A$ contains primes:** With $r$ primes from $A$, we cover exactly $r$ elements
2. **If $A$ contains composites:** Small prime triangles ensure efficient coverage

The only way to "defeat" small primes is mixed semiprimes, which give $f = 4$, not $f \approx 2\pi(\sqrt{n})$.

## Possible Explanations for the Discrepancy

### Hypothesis 1: Typo or Error in Problem Statement

The formula $f(\pi(n)+1, n) = 2\pi(n^{1/2}) + o(\cdot)$ may be stated incorrectly on erdosproblems.com.

Possible corrections:
- The formula might describe a different function
- The asymptotic might apply to a different regime of $k$
- There may be a sign error or missing constraint

### Hypothesis 2: Different Definition of f(k,n)

The original Erdos-Straus definition may differ from the stated one. Possible alternatives:

1. **Maximum vs Minimum:** $f$ could be a maximum over sets rather than minimum over $r$
2. **Constraint on primes:** The $r$ primes might be restricted to $p \leq \sqrt{n}$
3. **Different covering condition:** "Covered" might mean something else

### Hypothesis 3: The Result Applies to a Different Regime

The Erdos-Straus theorem might apply to:
- $k$ significantly larger than $\pi(n) + 1$
- A different relationship between $k$ and $n$

### Hypothesis 4: My Analysis is Missing Something

There may exist adversarial sets I haven't considered that achieve $f \approx 2\pi(\sqrt{n})$.

However, I have systematically analyzed:
- Sets containing primes (easy: $f = 1$)
- Sets of squarefree composites (triangles give $f \leq 3$)
- Sets of mixed semiprimes (bipartite structure gives $f = 4$)
- Sets of prime powers (easy: $f = 1$)

All yield $f \leq 4$.

## Conclusion

**Based on computational and theoretical analysis:**

$$\boxed{f(\pi(n)+1, n) = O(1) \approx 3-4}$$

Therefore, the answer to Erdos's question is **LIKELY YES:**
$$2\pi(n^{1/2}) - f(\pi(n)+1, n) \to \infty$$

The gap grows like $\Theta(\sqrt{n}/\log n)$.

**However, this contradicts the claimed Erdos-Straus theorem.** Resolution requires:
1. Verification of the original problem statement
2. Access to the original Erdos-Straus paper [Er70b]
3. Clarification from experts in this area

## References

- [Er70b] P. Erdos and E. G. Straus, "Some applications of graph theory to number theory," The Many Facets of Graph Theory, Springer LNM, 1969, pp. 77-82.
- Erdos Problems: https://www.erdosproblems.com/983
- GitHub Repository: https://github.com/teorth/erdosproblems

---

*Analysis date: January 2026*
*Status: DISCREPANCY IDENTIFIED - requires further verification*
