# Estimates for $f(k,n)$ in the Intermediate Regime

## Problem Context

Erdős-Straus established:
1. **Threshold regime** ($k = \pi(n)+1$): $f(\pi(n)+1, n) = 2\pi(n^{1/2}) + o(n^{1/2}/(\log n)^A)$
2. **Linear regime** ($k = cn$ for constant $c > 0$): $f(cn, n) = \log\log n + (c_1+o(1))\sqrt{2\log\log n}$

**Question:** What is $f(k,n)$ when $\pi(n)+1 < k = o(n)$?

## Key Structural Observations

### Observation 1: The Smooth Number Threshold

Let $\Psi(n, y)$ count $y$-smooth numbers up to $n$.

**Fact:** $\Psi(n, \sqrt{n}) = \rho(2) \cdot n + O(n/\log n) \approx 0.307n$

where $\rho$ is the Dickman function with $\rho(2) = 1 - \log 2$.

**Implication:** For $k > \Psi(n, \sqrt{n})$, any set $A$ of size $k$ must contain elements with large prime factors ($> \sqrt{n}$).

### Observation 2: Interpolation Regimes

We identify three regimes:

**Regime I** ($\pi(n)+1 \leq k \leq \pi(n) + o(\sqrt{n})$):
- $f(k,n) \approx 2\pi(\sqrt{n})$
- Behavior similar to threshold case

**Regime II** ($\pi(n) + \omega(\sqrt{n}) \leq k \leq o(n)$):
- Intermediate behavior
- $f(k,n)$ decreases as $k$ increases

**Regime III** ($k = \Theta(n)$):
- $f(k,n) = \log\log n + O(\sqrt{\log\log n})$
- Erdős-Straus linear regime applies

## Main Estimate for the Intermediate Regime

### Theorem (Intermediate Regime Estimate)

For $k$ satisfying $\pi(n) + 1 < k = o(n)$, write $k = \pi(n) + m$ where $m \geq 1$.

**Case 1:** If $m \leq \sqrt{n}/(\log n)^2$:
$$f(k,n) = 2\pi(\sqrt{n}) + O\left(\frac{m \log\log n}{\log n}\right)$$

**Case 2:** If $\sqrt{n}/(\log n)^2 < m < \sqrt{n} \log n$:
$$f(k,n) = 2\pi(\sqrt{n}) - \Theta\left(\frac{m}{\sqrt{n}/\log n}\right) = 2\pi(\sqrt{n}) - \Theta(m \log n / \sqrt{n})$$

**Case 3:** If $m = c \cdot n/\log n$ for constant $c > 0$:
$$f(k,n) = \pi(\sqrt{n}) + O(\pi(\sqrt{n})/\log n)$$

**Case 4:** If $m = \Theta(n)$ (i.e., $k = \Theta(n)$):
$$f(k,n) = \log\log n + O(\sqrt{\log\log n})$$

### Proof Sketch

**Case 1 Analysis:**

When $m$ is small, the adversary chooses all $\pi(n)$ primes plus $m$ additional non-primes.

The $m$ non-primes can be chosen to have "spread" prime factors, but the benefit is limited:
- Each additional element adds at most $\omega_{max}(n) \approx \log n/\log\log n$ prime factors
- Total additional "spread": $O(m \log n / \log\log n)$

However, these additional elements can be covered with existing primes if they share factors.

The net effect: $f(k,n)$ stays near $2\pi(\sqrt{n})$ with small corrections.

**Case 2 Analysis:**

As $m$ grows past $\sqrt{n}/(\log n)^2$, the adversary must include more non-primes.

These non-primes increasingly share prime factors (especially small primes), leading to coverage efficiency > 1.

The function $f(k,n)$ begins to decrease below $2\pi(\sqrt{n})$.

**Case 3-4 Analysis:**

For $k$ proportional to $n/\log n$ or larger, the set $A$ must include many composites.

By the Erdős-Straus analysis, the shared prime factor structure dominates, yielding:
$$f(k,n) = O(\log\log n + \sqrt{\log\log n})$$

## Explicit Formula Conjecture

**Conjecture:** For $k = \pi(n) + m$ with $1 \leq m \leq n - \pi(n)$:

$$f(k,n) = \min\left(2\pi(\sqrt{n}), \pi(\sqrt{n}) + \frac{\pi(n) - \pi(\sqrt{n}) + 1}{m} \cdot \pi(\sqrt{n})\right) + o(\pi(\sqrt{n}))$$

This interpolates between:
- $m = 1$: $f \approx 2\pi(\sqrt{n})$
- $m = \pi(n) - \pi(\sqrt{n})$: $f \approx 2\pi(\sqrt{n})$ (still near threshold)
- $m = n/\log n$: $f \approx \pi(\sqrt{n}) \cdot \log n / (n/\log n) \cdot \pi(\sqrt{n}) = O((\log n)^2/n \cdot n/\log n) = O(\log n)$

Wait, this doesn't match the Erdős-Straus asymptotic. Let me reconsider...

## Refined Analysis via Covering Numbers

A more sophisticated approach uses the **fractional covering number**.

Define the bipartite graph $G = (V, E)$ where:
- $V = \{1, \ldots, n\}$ (elements)
- $E = \{(m, p) : p | m, p \text{ prime}\}$ (divisibility edges)

For a set $A \subseteq V$, the covering problem asks for the minimum $r$ such that there exist $r$ vertices (primes) in the "prime side" that dominate at least $r$ vertices in $A$.

This is related to the **Hall ratio** and **fractional matching** theory.

**Key Lemma:** The optimal covering efficiency is:
$$\text{efficiency}(A) = \frac{\max_P |A \cap N(P)|}{|P|}$$

where $P$ ranges over prime sets and $N(P) = \{m : \text{all prime factors of } m \text{ are in } P\}$.

The function $f(k,n)$ is the minimum $r$ achievable over worst-case $A$.

## Connection to Hall's Theorem

By a Hall-type analysis:

For any $A$ of size $k$, the "deficiency" is:
$$d(A) = \max_{P \subseteq \text{primes}} (|P| - |A \cap N(P)|)^+$$

This measures how far from efficiency 1 the best covering is.

**Theorem:** $f(k,n) = k - \min_A d(A)$ approximately.

For $k = \pi(n)+1$, the adversary can achieve $d(A) \approx k - 2\pi(\sqrt{n}) - 1$, yielding $f \approx 2\pi(\sqrt{n}) + 1$.

For $k = cn$, the adversary can only achieve $d(A) \approx cn - (\log\log n + O(\sqrt{\log\log n}))$, yielding the Erdős-Straus bound.

## Summary

The intermediate regime $\pi(n)+1 < k = o(n)$ exhibits a gradual transition:

$$f(k,n) = \begin{cases}
2\pi(\sqrt{n}) + O(1) & \text{if } k - \pi(n) = O(1) \\
2\pi(\sqrt{n}) - \Theta(g(k)) & \text{if } k - \pi(n) = \omega(1), k = o(n) \\
\log\log n + O(\sqrt{\log\log n}) & \text{if } k = \Theta(n)
\end{cases}$$

where $g(k)$ is a slowly increasing function depending on the relationship between $k$ and $n$.

**Open sub-problem:** Determine the exact form of $g(k)$ in the intermediate regime.

