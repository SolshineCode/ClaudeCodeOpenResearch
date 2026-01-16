"""
Statistical Analysis Utilities

Tools for analyzing experimental results from interpretability experiments.
Designed to work without heavy dependencies - pure Python implementations
of essential statistical tests.
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class DescriptiveStats:
    """Basic descriptive statistics."""
    n: int
    mean: float
    std: float
    min_val: float
    max_val: float
    median: float

    def to_dict(self) -> Dict:
        return {
            'n': self.n,
            'mean': round(self.mean, 4),
            'std': round(self.std, 4),
            'min': round(self.min_val, 4),
            'max': round(self.max_val, 4),
            'median': round(self.median, 4)
        }


def compute_stats(values: List[float]) -> DescriptiveStats:
    """Compute descriptive statistics for a list of values."""
    if not values:
        return DescriptiveStats(0, 0, 0, 0, 0, 0)

    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0
    std = math.sqrt(variance)

    sorted_vals = sorted(values)
    if n % 2 == 0:
        median = (sorted_vals[n//2 - 1] + sorted_vals[n//2]) / 2
    else:
        median = sorted_vals[n//2]

    return DescriptiveStats(
        n=n,
        mean=mean,
        std=std,
        min_val=min(values),
        max_val=max(values),
        median=median
    )


def compute_accuracy(results: List[Dict], filter_fn: Optional[callable] = None) -> Dict:
    """
    Compute accuracy from results.

    Args:
        results: List of result dicts with 'is_correct' field
        filter_fn: Optional function to filter results

    Returns:
        Dict with accuracy metrics
    """
    filtered = results if filter_fn is None else [r for r in results if filter_fn(r)]

    if not filtered:
        return {'accuracy': 0, 'correct': 0, 'total': 0, 'ci_lower': 0, 'ci_upper': 0}

    correct = sum(1 for r in filtered if r.get('is_correct', False))
    total = len(filtered)
    accuracy = correct / total

    # Wilson score confidence interval (better for proportions)
    ci_lower, ci_upper = wilson_confidence_interval(correct, total)

    return {
        'accuracy': round(accuracy, 4),
        'correct': correct,
        'total': total,
        'ci_lower': round(ci_lower, 4),
        'ci_upper': round(ci_upper, 4)
    }


def wilson_confidence_interval(successes: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    """
    Compute Wilson score confidence interval for a proportion.

    Better than normal approximation for small samples or extreme proportions.
    """
    if total == 0:
        return (0, 0)

    p = successes / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator

    return (max(0, center - spread), min(1, center + spread))


def chi_square_test(contingency_table: List[List[int]]) -> Dict:
    """
    Perform chi-square test of independence.

    Args:
        contingency_table: 2D list of counts [[a, b], [c, d]]

    Returns:
        Dict with chi_square, df, and approximate p-value
    """
    rows = len(contingency_table)
    cols = len(contingency_table[0])

    # Calculate row and column totals
    row_totals = [sum(row) for row in contingency_table]
    col_totals = [sum(contingency_table[i][j] for i in range(rows)) for j in range(cols)]
    grand_total = sum(row_totals)

    if grand_total == 0:
        return {'chi_square': 0, 'df': 0, 'p_value_approx': 1.0}

    # Calculate expected values and chi-square
    chi_square = 0
    for i in range(rows):
        for j in range(cols):
            expected = (row_totals[i] * col_totals[j]) / grand_total
            if expected > 0:
                observed = contingency_table[i][j]
                chi_square += (observed - expected) ** 2 / expected

    df = (rows - 1) * (cols - 1)

    # Approximate p-value using chi-square distribution
    # This is a rough approximation; for precise values use scipy
    p_value = approximate_chi_square_p(chi_square, df)

    return {
        'chi_square': round(chi_square, 4),
        'df': df,
        'p_value_approx': round(p_value, 4)
    }


def approximate_chi_square_p(chi_sq: float, df: int) -> float:
    """
    Rough approximation of chi-square p-value.

    For precise values, use scipy.stats.chi2.sf()
    """
    if df <= 0 or chi_sq <= 0:
        return 1.0

    # Wilson-Hilferty approximation
    x = (chi_sq / df) ** (1/3) - (1 - 2 / (9 * df))
    x = x / math.sqrt(2 / (9 * df))

    # Standard normal CDF approximation
    p = 0.5 * (1 + math.erf(-x / math.sqrt(2)))
    return max(0, min(1, p))


def analyze_by_condition(
    results: List[Dict],
    condition_key: str
) -> Dict[str, Dict]:
    """
    Analyze results broken down by a condition variable.

    Args:
        results: List of result dicts
        condition_key: Key in metadata to group by

    Returns:
        Dict mapping condition values to accuracy metrics
    """
    grouped = defaultdict(list)

    for r in results:
        # Look in metadata or top level
        condition_value = r.get('metadata', {}).get(condition_key) or r.get(condition_key)
        if condition_value is not None:
            grouped[condition_value].append(r)

    analysis = {}
    for condition, group in grouped.items():
        analysis[str(condition)] = compute_accuracy(group)

    return analysis


def compare_conditions(
    results: List[Dict],
    condition_key: str,
    condition_a: Any,
    condition_b: Any
) -> Dict:
    """
    Compare accuracy between two conditions.

    Returns chi-square test results and effect size.
    """
    def filter_a(r):
        val = r.get('metadata', {}).get(condition_key) or r.get(condition_key)
        return val == condition_a

    def filter_b(r):
        val = r.get('metadata', {}).get(condition_key) or r.get(condition_key)
        return val == condition_b

    stats_a = compute_accuracy(results, filter_a)
    stats_b = compute_accuracy(results, filter_b)

    # Build contingency table
    table = [
        [stats_a['correct'], stats_a['total'] - stats_a['correct']],
        [stats_b['correct'], stats_b['total'] - stats_b['correct']]
    ]

    chi_sq_result = chi_square_test(table)

    # Effect size (phi coefficient for 2x2)
    n = stats_a['total'] + stats_b['total']
    phi = math.sqrt(chi_sq_result['chi_square'] / n) if n > 0 else 0

    return {
        'condition_a': {
            'value': condition_a,
            **stats_a
        },
        'condition_b': {
            'value': condition_b,
            **stats_b
        },
        'chi_square_test': chi_sq_result,
        'effect_size_phi': round(phi, 4),
        'difference': round(stats_a['accuracy'] - stats_b['accuracy'], 4)
    }


def generate_analysis_report(
    results: List[Dict],
    experiment_name: str,
    condition_keys: List[str]
) -> Dict:
    """
    Generate a comprehensive analysis report.

    Args:
        results: List of result dicts
        experiment_name: Name of experiment
        condition_keys: List of condition variables to analyze

    Returns:
        Complete analysis report dict
    """
    report = {
        'experiment_name': experiment_name,
        'total_trials': len(results),
        'overall_accuracy': compute_accuracy(results),
        'by_condition': {}
    }

    for key in condition_keys:
        report['by_condition'][key] = analyze_by_condition(results, key)

    # Response time analysis
    response_times = [r.get('response_time_ms') for r in results if r.get('response_time_ms')]
    if response_times:
        report['response_time_stats'] = compute_stats(response_times).to_dict()

    return report


def format_report_markdown(report: Dict) -> str:
    """Format analysis report as markdown."""
    lines = [f"# Analysis Report: {report['experiment_name']}\n"]

    lines.append("## Overall Results\n")
    overall = report['overall_accuracy']
    lines.append(f"- **Total Trials**: {overall['total']}")
    lines.append(f"- **Accuracy**: {overall['accuracy']:.1%} "
                f"(95% CI: [{overall['ci_lower']:.1%}, {overall['ci_upper']:.1%}])")
    lines.append(f"- **Correct**: {overall['correct']}/{overall['total']}")

    if 'response_time_stats' in report:
        rt = report['response_time_stats']
        lines.append(f"\n### Response Time")
        lines.append(f"- Mean: {rt['mean']:.1f}ms (SD: {rt['std']:.1f})")
        lines.append(f"- Range: {rt['min']:.1f} - {rt['max']:.1f}ms")

    lines.append("\n## Results by Condition\n")

    for condition_name, condition_data in report['by_condition'].items():
        lines.append(f"### {condition_name.replace('_', ' ').title()}\n")
        lines.append("| Condition | Accuracy | N | 95% CI |")
        lines.append("|-----------|----------|---|--------|")

        for value, stats in sorted(condition_data.items()):
            lines.append(f"| {value} | {stats['accuracy']:.1%} | {stats['total']} | "
                        f"[{stats['ci_lower']:.1%}, {stats['ci_upper']:.1%}] |")
        lines.append("")

    return '\n'.join(lines)


def load_results(filepath: Path) -> List[Dict]:
    """Load results from JSON file."""
    with open(filepath) as f:
        data = json.load(f)
    return data.get('results', data)


def demo_analysis():
    """Demonstrate analysis with synthetic data."""
    print("=" * 60)
    print("STATISTICAL ANALYSIS DEMO")
    print("=" * 60)

    # Create synthetic results
    import random
    random.seed(42)

    results = []
    for i in range(100):
        depth = random.choice([1, 2, 3, 4])
        format_type = random.choice(['markdown', 'json', 'xml'])

        # Accuracy decreases with depth, varies by format
        base_prob = 0.9 - (depth * 0.1)
        if format_type == 'json':
            base_prob += 0.1
        elif format_type == 'xml':
            base_prob += 0.05

        is_correct = random.random() < base_prob

        results.append({
            'trial_id': f'trial_{i:03d}',
            'is_correct': is_correct,
            'depth': depth,
            'format': format_type,
            'response_time_ms': random.gauss(500, 100)
        })

    # Generate report
    report = generate_analysis_report(
        results,
        'Synthetic Demo',
        ['depth', 'format']
    )

    # Print markdown report
    print(format_report_markdown(report))

    # Show comparison
    print("\n## Statistical Comparison: depth=1 vs depth=4\n")
    comparison = compare_conditions(results, 'depth', 1, 4)
    print(f"Depth 1: {comparison['condition_a']['accuracy']:.1%}")
    print(f"Depth 4: {comparison['condition_b']['accuracy']:.1%}")
    print(f"Difference: {comparison['difference']:.1%}")
    print(f"Chi-square: {comparison['chi_square_test']['chi_square']:.2f}, "
          f"p ≈ {comparison['chi_square_test']['p_value_approx']:.4f}")
    print(f"Effect size (φ): {comparison['effect_size_phi']:.3f}")


if __name__ == '__main__':
    demo_analysis()
