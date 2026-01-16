# Erdős Problem #983: Prime Divisibility Coverage

## Problem Statement

Let $n \geq 2$ and $\pi(n) < k \leq n$. Define $f(k,n)$ as the smallest integer $r$ such that in **any** subset $A \subseteq \{1, \ldots, n\}$ of size $|A| = k$, there exist primes $p_1, \ldots, p_r$ such that at least $r$ elements $a \in A$ are divisible **only** by primes from $\{p_1, \ldots, p_r\}$.

**Main Question:** Is it true that
$$2\pi(n^{1/2}) - f(\pi(n)+1, n) \to \infty \quad \text{as } n \to \infty?$$

**Secondary Question:** Estimate $f(k,n)$ in general, particularly when $\pi(n)+1 < k = o(n)$.

## Known Results (Erdős-Straus 1970)

1. **Trivial bound:** $f(k,n) \leq \pi(n)$

2. **At the threshold $k = \pi(n)+1$:**
$$f(\pi(n)+1, n) = 2\pi(n^{1/2}) + o_A\left(\frac{n^{1/2}}{(\log n)^A}\right)$$
for any $A > 0$.

3. **Linear regime $k = cn$ for constant $c > 0$:**
$$f(cn, n) = \log\log n + (c_1 + o(1))\sqrt{2\log\log n}$$
where $c = \Phi(c_1) = \frac{1}{\sqrt{2\pi}}\int_{-\infty}^{c_1} e^{-x^2/2} dx$.

## Key Definitions and Notation

- $\pi(x)$: the prime counting function
- $\Psi(x,y)$: count of $y$-smooth numbers up to $x$ (numbers with all prime factors $\leq y$)
- $S(P)$ for a set of primes $P$: the set of positive integers whose prime factors all lie in $P$
- An element $a$ is **covered** by primes $\{p_1, \ldots, p_r\}$ if all prime factors of $a$ are in this set

## Interpretation of $f(k,n)$

The function $f(k,n)$ measures a min-max quantity:
$$f(k,n) = \min_r \left\{ r : \forall A \subseteq \{1,\ldots,n\}, |A|=k, \exists p_1,\ldots,p_r \text{ s.t. } |A \cap S(\{p_1,\ldots,p_r\})| \geq r \right\}$$

Equivalently, $f(k,n) - 1$ is the largest $r$ such that there exists a "hard" set $A$ of size $k$ where no choice of $r$ primes covers $r$ elements.

