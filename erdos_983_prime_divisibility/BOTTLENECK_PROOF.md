# Bottleneck Proof: Why f ≤ O(π(√n))

## The Key Theorem

**Theorem (Bottleneck Bound):** In any 2-regular bipartite matching on primes with all products ≤ n, the number of participating primes t satisfies:

$$t \leq 2\pi(\sqrt{n}) + O(1)$$

More precisely: $t \leq 2\pi(\sqrt{n})$ for $n \geq 4$.

**Corollary:** $f(\pi(n)+1, n) \leq 2\pi(\sqrt{n})$, and thus:
$$\text{gap} = 2\pi(\sqrt{n}) - f \geq 0$$

Wait - this only gives gap ≥ 0, not gap → ∞. We need a TIGHTER bound.

---

## Refined Analysis

Let's partition the primes into:
- **Small primes S:** primes ≤ √n
- **Large primes L:** primes with √n < p ≤ 2√n

Let |S| = s = π(√n) and |L| = ℓ.

### Observation 1: Large-Large Edges are Impossible

For p, q ∈ L with p, q > √n:
$$pq > \sqrt{n} \cdot \sqrt{n} = n$$

So no edge can connect two large primes.

### Observation 2: Edges Involving Large Primes

Every edge involving a large prime p ∈ L must connect to a small prime q ∈ S.

For p ∈ L to have degree 2 (required for 2-regularity), it needs TWO small prime partners.

### Observation 3: The Bottleneck

In a 2-regular matching:
- Each large prime needs 2 small prime partners
- Each small prime can have at most 2 partners total (from either S or L)

Let's count edges:
- Edges within S (small-small): call this $e_{SS}$
- Edges between S and L: call this $e_{SL}$

For 2-regularity:
- Total degree of S = 2s (each of s small primes has degree 2)
- Degree of S from within S = 2·$e_{SS}$ (each SS edge contributes 2 to S's total degree)
- Degree of S from L = $e_{SL}$

So: $2e_{SS} + e_{SL} = 2s$

For large primes:
- Total degree of L = 2ℓ (each large prime has degree 2)
- All edges from L go to S, so degree of L = $e_{SL}$

So: $e_{SL} = 2ℓ$

Substituting: $2e_{SS} + 2ℓ = 2s$

Therefore: $e_{SS} + ℓ = s$

And: $ℓ = s - e_{SS} \leq s$

### Conclusion from Observation 3

$$|L| \leq |S| = \pi(\sqrt{n})$$

The number of large primes participating is at most the number of small primes!

### Total Participating Primes

$$t = |S| + |L| \leq s + s = 2s = 2\pi(\sqrt{n})$$

This matches the Erdős-Straus bound. We haven't improved it yet.

---

## The Tighter Bound

The issue is that we assumed all small primes participate. But do they?

### Key Constraint: Small Primes Need Valid Partners

For a small prime p ∈ S to participate with degree 2, it needs 2 valid partners (primes q with pq ≤ n).

For the LARGEST small prime p = largest prime ≤ √n:
- Valid partners: q ≤ n/p ≈ √n (approximately)
- So the largest small prime can mostly only pair with OTHER small primes

### The Refined Argument

Consider primes in order: $p_1 < p_2 < \cdots < p_s < p_{s+1} < \cdots$

Where $p_s \leq \sqrt{n} < p_{s+1}$.

For large prime $p_i$ (i > s) to participate, it needs partners $q$ with $p_i \cdot q \leq n$, so $q \leq n/p_i$.

As $p_i$ increases toward $2\sqrt{n}$:
- $n/p_i$ decreases toward $\sqrt{n}/2$
- Fewer valid partners available

**Specific constraint:** The largest large prime $p$ with $p \leq 2\sqrt{n}$ needs partners $q \leq n/p \leq \sqrt{n}/2$.

There are only $\pi(\sqrt{n}/2) \approx \pi(\sqrt{n})/2$ such partners!

This creates a "squeeze" - large primes compete for a shrinking pool of valid partners.

---

## Computational Evidence for Tighter Bound

From our analysis:

| n | π(√n) | 2π(√n) | Max 2-regular | Ratio |
|---|-------|--------|---------------|-------|
| 100 | 4 | 8 | 8 | 2.00 |
| 225 | 6 | 12 | 10 | 1.67 |
| 400 | 8 | 16 | 12 | 1.50 |

The ratio is DECREASING! This suggests:

$$\text{Max 2-regular size} \sim c \cdot \pi(\sqrt{n}) \text{ for some } c < 2$$

If $c \to 1$ as $n \to \infty$, then gap → ∞.

---

## The Asymptotic Argument

**Claim:** As n → ∞, the maximum 2-regular matching size grows like $(1 + o(1))\pi(\sqrt{n})$, not $2\pi(\sqrt{n})$.

**Intuition:**
1. Large primes (√n < p ≤ 2√n) can only pair with small primes (≤ √n)
2. The largest large primes (near 2√n) can only pair with the SMALLEST small primes (≤ √n/2)
3. As n grows, this creates increasingly severe competition
4. The "middle" large primes get squeezed out

**Formal argument (sketch):**

Partition L into layers based on size:
- $L_1$: primes in $(\sqrt{n}, 1.2\sqrt{n}]$ - can pair with primes ≤ n/1.2√n = 0.83√n
- $L_2$: primes in $(1.2\sqrt{n}, 1.4\sqrt{n}]$ - can pair with primes ≤ 0.71√n
- $L_3$: primes in $(1.4\sqrt{n}, 1.6\sqrt{n}]$ - can pair with primes ≤ 0.625√n
- ...

Each layer $L_i$ has fewer valid partners than the previous. By counting arguments, most large primes CANNOT participate.

---

## Impact on f and the Gap

If max 2-regular matching size = $(1+\delta)\pi(\sqrt{n})$ for some $\delta < 1$:

$$f \leq (1+\delta)\pi(\sqrt{n}) + O(1)$$

$$\text{gap} = 2\pi(\sqrt{n}) - f \geq (1-\delta)\pi(\sqrt{n}) - O(1) \to \infty$$

**This would PROVE the answer is YES!**

---

## What Remains to Prove

1. **Rigorous bound on δ:** Show that δ < 1 (ideally δ → 0)
2. **Matching lower bound:** Show f ≥ (1+δ')π(√n) for some δ' > 0
3. **Asymptotic analysis:** Determine exact growth rate of max matching

---

## Updated Confidence

Based on this bottleneck analysis:
- The structural bound f ≤ O(π(√n)) is now **well-motivated**
- The computational evidence (ratio decreasing from 2.0 to 1.5) supports it
- **Confidence in YES: 70-75%** (up from 55-60%)

The remaining uncertainty is whether we can prove δ < 1 rigorously.
