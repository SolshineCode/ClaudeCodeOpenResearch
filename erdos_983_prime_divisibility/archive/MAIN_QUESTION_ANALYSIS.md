# Analysis: Does 2π(√n) - f(π(n)+1, n) → ∞?

## The Core Question

Erdős Problem #983 asks whether:

$$2\pi(n^{1/2}) - f(\pi(n)+1, n) \to \infty \text{ as } n \to \infty$$

## Known Bounds from [Er70b]

### Upper Bound (Erdős-Straus)

$$f(\pi(n)+1, n) \leq 2\pi(\sqrt{n}) + 1$$

### Lower Bound (Woett's Construction)

For any ε > 0:

$$f(\pi(n)+1, n) \geq \pi((2-\varepsilon)\sqrt{n}) + 1$$

### The Stated Asymptotic

Erdős-Straus claim:

$$f(\pi(n)+1, n) = 2\pi(n^{1/2}) + o_A\left(\frac{n^{1/2}}{(\log n)^A}\right)$$

for any A > 0.

---

## Asymptotic Analysis

Using the Prime Number Theorem: π(x) ~ x/log(x)

### Upper Bound Asymptotics

$$2\pi(\sqrt{n}) \sim 2 \cdot \frac{\sqrt{n}}{\log(\sqrt{n})} = 2 \cdot \frac{\sqrt{n}}{\frac{1}{2}\log n} = \frac{4\sqrt{n}}{\log n}$$

### Lower Bound Asymptotics

$$\pi((2-\varepsilon)\sqrt{n}) \sim \frac{(2-\varepsilon)\sqrt{n}}{\log((2-\varepsilon)\sqrt{n})}$$

For large n:
$$\approx \frac{(2-\varepsilon)\sqrt{n}}{\frac{1}{2}\log n} = \frac{2(2-\varepsilon)\sqrt{n}}{\log n} = \frac{(4-2\varepsilon)\sqrt{n}}{\log n}$$

### Gap Between Bounds

Upper bound: $\frac{4\sqrt{n}}{\log n} + 1$

Lower bound: $\frac{(4-2\varepsilon)\sqrt{n}}{\log n} + 1$

Gap: $\frac{2\varepsilon\sqrt{n}}{\log n}$

---

## The Answer Depends on Which Bound is Tight

### Case 1: f is close to the Upper Bound

If $f = 2\pi(\sqrt{n}) + O(1)$, then:

$$2\pi(\sqrt{n}) - f = O(1)$$

**Answer: NO**, the gap remains bounded.

### Case 2: f is close to the Lower Bound

If $f = \pi((2-\varepsilon)\sqrt{n}) + O(1)$ for fixed ε > 0, then:

$$2\pi(\sqrt{n}) - f \sim \frac{2\varepsilon\sqrt{n}}{\log n} \to \infty$$

**Answer: YES**, the gap tends to infinity.

---

## What Does the Erdős-Straus Asymptotic Mean?

The statement $f = 2\pi(\sqrt{n}) + o_A(\sqrt{n}/(\log n)^A)$ is very strong:

- The error term goes to zero faster than $\sqrt{n}/(\log n)^A$ for ANY A
- This means the error is "superpolynomially small" in log n
- Specifically, it's smaller than $\sqrt{n}/(\log n)^{100}$, $\sqrt{n}/(\log n)^{1000}$, etc.

This suggests:

$$|f - 2\pi(\sqrt{n})| = o\left(\frac{\sqrt{n}}{(\log n)^A}\right) \text{ for all } A$$

If this is a two-sided bound (f could be above or below 2π(√n)), then:

$$|2\pi(\sqrt{n}) - f| = o\left(\frac{\sqrt{n}}{(\log n)^A}\right) \to 0 \text{ (relative to any polynomial in log n)}$$

**But this doesn't tell us whether the gap is positive, negative, bounded, or growing to ±∞!**

---

## Possible Interpretations

### Interpretation 1: The Gap is Bounded

If the Erdős-Straus asymptotic implies $|f - 2\pi(\sqrt{n})| = O(1)$, then the answer is **NO**.

### Interpretation 2: The Gap Grows but Slowly

If $f = 2\pi(\sqrt{n}) - \omega(1)$ but the growth is slower than any power of log n, then technically **YES** but the growth is imperceptibly slow.

### Interpretation 3: We Need the Exact Error Term

The question can only be definitively answered by determining:
1. The sign of the error term (is f above or below 2π(√n)?)
2. The magnitude (is it O(1), o(1), ω(1), or something else?)

---

## Evidence from Computational Testing

At n = 100:
- 2π(√100) = 2π(10) = 8
- f (from Woett's construction) = 9
- Gap = 8 - 9 = -1

This suggests f > 2π(√n) for small n, meaning the gap is **negative**!

If this persists for large n, then:
$$2\pi(\sqrt{n}) - f < 0$$

And the question "Does 2π(√n) - f → ∞?" would have answer **NO** (it goes to -∞ or stays bounded below).

---

## Verified Result for n=100

With the CORRECT Woett construction (manually verified):

**A₀ semiprimes:** {26=2·13, 33=3·11, 38=2·19, 51=3·17, 77=7·11, 85=5·17, 91=7·13, 95=5·19}

Each small prime {2,3,5,7,11,13,17,19} appears in exactly 2 products.

**Results:**
- 8 small primes {2,3,5,7,11,13,17,19} cover exactly 8 elements (A₀)
- 9 primes (adding 23) cover 10 > 9 elements (A₀ + {46, 69})
- **f = 9 = t + 1** as predicted by Woett

**Key insight:** The 2-regular graph must be "well-spread" - no short cycles.
Products like 6=2·3 would allow 2 primes to cover an element, breaking the construction.

## Conclusion

Given:
- Lower bound: f ≥ t + 1 = π((2-ε)√n) + 1
- Upper bound: f ≤ 2π(√n) + 1
- Verified: f = 9 = t + 1 for n = 100 (matching 2π(√10) + 1 = 9)

**CORRECTION:** The bounds are NOT tight for large n!

Using PNT:
- Lower bound ≈ (4-2ε)√n/ln n
- Upper bound ≈ 4√n/ln n
- Gap between bounds ≈ 2ε√n/ln n → ∞ for fixed ε

**Answer: UNCERTAIN**

The answer depends on WHERE f lies between the bounds:
- If f tracks upper bound: gap ≈ O(1), answer is NO
- If f tracks lower bound: gap ≈ 2ε√n/ln n → ∞, answer is YES

The n=100 case is special (bounds coincide). For large n, more analysis is needed.

---

## Open Questions

1. **Sign of the gap:** Is f typically above or below 2π(√n)?

2. **Magnitude:** Is $|f - 2\pi(\sqrt{n})| = O(1)$, $\Theta(\log n)$, or something else?

3. **Existence of better bounds:** Can the lower bound be improved beyond Woett's construction?

4. **Original proof:** What does [Er70b, p. 138] say about the error term structure?

---

## Recommendation

To definitively answer the question:

1. **Obtain [Er70b]** and study the proof of $f = 2\pi(\sqrt{n}) + o(\cdot)$
2. **Determine the sign** of f - 2π(√n) from the proof
3. **Verify computationally** for n = 10^4, 10^5, 10^6 if feasible

The question may be more subtle than it appears, and the answer likely hinges on the exact structure of the error term in the Erdős-Straus theorem.
