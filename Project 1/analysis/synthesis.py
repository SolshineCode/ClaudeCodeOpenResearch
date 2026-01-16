"""
Cross-Experiment Synthesis Analysis

Analyzes patterns and findings across all experiment types to build
a unified model of document understanding capabilities.

This module:
1. Aggregates results across experiment types
2. Identifies common patterns and divergences
3. Tests meta-hypotheses about document processing
4. Generates capability maps
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
import math


@dataclass
class CapabilityProfile:
    """Profile of a capability dimension."""
    name: str
    description: str
    experiments_testing: List[str]
    accuracy_by_condition: Dict[str, float]
    boundary_conditions: List[str]  # Where capability breaks down
    confidence: str  # 'low', 'medium', 'high'


@dataclass
class MetaFinding:
    """A finding that spans multiple experiments."""
    finding_id: str
    title: str
    description: str
    supporting_evidence: List[Dict]
    confidence: float
    implications: List[str]


class CrossExperimentAnalyzer:
    """Analyzes results across multiple experiments."""

    def __init__(self):
        self.experiment_results: Dict[str, List[Dict]] = {}
        self.capability_profiles: List[CapabilityProfile] = []
        self.meta_findings: List[MetaFinding] = []

    def load_results(self, experiment_name: str, results: List[Dict]):
        """Load results from an experiment."""
        self.experiment_results[experiment_name] = results

    def compute_accuracy(self, results: List[Dict], filter_fn: Optional[callable] = None) -> float:
        """Compute accuracy for a set of results."""
        filtered = results if filter_fn is None else [r for r in results if filter_fn(r)]
        if not filtered:
            return 0.0
        correct = sum(1 for r in filtered if r.get('is_correct', False))
        return correct / len(filtered)

    def analyze_format_effects(self) -> Dict:
        """Analyze format effects across experiments."""
        format_results = defaultdict(lambda: {'correct': 0, 'total': 0, 'by_experiment': {}})

        for exp_name, results in self.experiment_results.items():
            for r in results:
                fmt = r.get('metadata', {}).get('format') or r.get('format')
                if fmt:
                    format_results[fmt]['total'] += 1
                    if r.get('is_correct', False):
                        format_results[fmt]['correct'] += 1

                    if exp_name not in format_results[fmt]['by_experiment']:
                        format_results[fmt]['by_experiment'][exp_name] = {'correct': 0, 'total': 0}
                    format_results[fmt]['by_experiment'][exp_name]['total'] += 1
                    if r.get('is_correct', False):
                        format_results[fmt]['by_experiment'][exp_name]['correct'] += 1

        # Compute accuracies
        summary = {}
        for fmt, data in format_results.items():
            summary[fmt] = {
                'overall_accuracy': data['correct'] / data['total'] if data['total'] > 0 else 0,
                'total_trials': data['total'],
                'by_experiment': {
                    exp: d['correct'] / d['total'] if d['total'] > 0 else 0
                    for exp, d in data['by_experiment'].items()
                }
            }

        return summary

    def analyze_depth_effects(self) -> Dict:
        """Analyze depth effects across experiments."""
        depth_results = defaultdict(lambda: {'correct': 0, 'total': 0})

        for exp_name, results in self.experiment_results.items():
            for r in results:
                depth = r.get('metadata', {}).get('depth') or r.get('depth')
                if depth is not None:
                    depth_results[depth]['total'] += 1
                    if r.get('is_correct', False):
                        depth_results[depth]['correct'] += 1

        summary = {}
        for depth, data in sorted(depth_results.items()):
            summary[depth] = {
                'accuracy': data['correct'] / data['total'] if data['total'] > 0 else 0,
                'total_trials': data['total']
            }

        return summary

    def analyze_complexity_scaling(self) -> Dict:
        """Analyze how performance scales with various complexity measures."""
        metrics = {}

        # Analyze different complexity dimensions
        complexity_dims = [
            ('depth', 'Nesting depth'),
            ('total_nodes', 'Document size'),
            ('num_hops', 'Reasoning steps'),
            ('num_distractors', 'Distractor count')
        ]

        for dim_key, dim_name in complexity_dims:
            dim_results = defaultdict(lambda: {'correct': 0, 'total': 0})

            for exp_name, results in self.experiment_results.items():
                for r in results:
                    val = r.get('metadata', {}).get(dim_key) or r.get(dim_key)
                    if val is not None:
                        dim_results[val]['total'] += 1
                        if r.get('is_correct', False):
                            dim_results[val]['correct'] += 1

            if dim_results:
                # Compute correlation (simplified)
                points = [(k, v['correct'] / v['total'] if v['total'] > 0 else 0)
                         for k, v in sorted(dim_results.items())]

                if len(points) >= 2:
                    x_vals = [p[0] for p in points]
                    y_vals = [p[1] for p in points]
                    correlation = self._compute_correlation(x_vals, y_vals)

                    metrics[dim_key] = {
                        'name': dim_name,
                        'correlation': correlation,
                        'trend': 'decreasing' if correlation < -0.3 else ('increasing' if correlation > 0.3 else 'stable'),
                        'data_points': len(points)
                    }

        return metrics

    def _compute_correlation(self, x: List[float], y: List[float]) -> float:
        """Compute Pearson correlation coefficient."""
        n = len(x)
        if n < 2:
            return 0.0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denom_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        denom_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

        if denom_x == 0 or denom_y == 0:
            return 0.0

        return numerator / (denom_x * denom_y)

    def identify_capability_boundaries(self) -> List[Dict]:
        """Identify where capabilities break down."""
        boundaries = []

        # Check for sharp accuracy drops
        for exp_name, results in self.experiment_results.items():
            condition_keys = ['depth', 'num_hops', 'similarity']

            for key in condition_keys:
                by_condition = defaultdict(lambda: {'correct': 0, 'total': 0})

                for r in results:
                    val = r.get('metadata', {}).get(key) or r.get(key)
                    if val is not None:
                        by_condition[val]['total'] += 1
                        if r.get('is_correct', False):
                            by_condition[val]['correct'] += 1

                if len(by_condition) >= 2:
                    accuracies = sorted([
                        (k, v['correct'] / v['total'] if v['total'] > 0 else 0)
                        for k, v in by_condition.items()
                    ])

                    # Look for drops
                    for i in range(len(accuracies) - 1):
                        drop = accuracies[i][1] - accuracies[i + 1][1]
                        if drop > 0.2:  # 20% drop
                            boundaries.append({
                                'experiment': exp_name,
                                'dimension': key,
                                'boundary_value': accuracies[i + 1][0],
                                'accuracy_drop': drop,
                                'before': accuracies[i][1],
                                'after': accuracies[i + 1][1]
                            })

        return boundaries

    def generate_capability_map(self) -> Dict:
        """Generate a comprehensive capability map."""
        capability_map = {
            'structural_understanding': {
                'description': 'Ability to perceive and reason about document hierarchy',
                'components': {}
            },
            'information_retrieval': {
                'description': 'Ability to locate and extract specific information',
                'components': {}
            },
            'format_processing': {
                'description': 'Ability to handle different document formats',
                'components': {}
            },
            'multi_step_reasoning': {
                'description': 'Ability to chain reasoning across document sections',
                'components': {}
            }
        }

        # Map experiments to capabilities
        exp_to_cap = {
            'hierarchy_perception': 'structural_understanding',
            'needle_in_structure': 'information_retrieval',
            'isomorphic_content': 'format_processing',
            'multi_hop': 'multi_step_reasoning'
        }

        for exp_name, results in self.experiment_results.items():
            cap_name = None
            for exp_key, cap in exp_to_cap.items():
                if exp_key in exp_name.lower():
                    cap_name = cap
                    break

            if cap_name and results:
                overall_acc = self.compute_accuracy(results)
                capability_map[cap_name]['components'][exp_name] = {
                    'accuracy': overall_acc,
                    'trials': len(results),
                    'status': 'strong' if overall_acc > 0.85 else ('moderate' if overall_acc > 0.70 else 'weak')
                }

        return capability_map

    def synthesize_findings(self) -> List[MetaFinding]:
        """Synthesize meta-findings from cross-experiment analysis."""
        findings = []

        # Finding 1: Format effects
        format_analysis = self.analyze_format_effects()
        if format_analysis:
            accuracies = {fmt: data['overall_accuracy'] for fmt, data in format_analysis.items()}
            best_format = max(accuracies, key=accuracies.get) if accuracies else None
            worst_format = min(accuracies, key=accuracies.get) if accuracies else None

            if best_format and worst_format and accuracies.get(best_format, 0) - accuracies.get(worst_format, 0) > 0.1:
                findings.append(MetaFinding(
                    finding_id="MF_001",
                    title="Format Performance Gap",
                    description=f"Significant performance difference between formats: {best_format} ({accuracies[best_format]:.1%}) vs {worst_format} ({accuracies[worst_format]:.1%})",
                    supporting_evidence=[{'format_analysis': format_analysis}],
                    confidence=0.8,
                    implications=[
                        f"Prefer {best_format} format for critical operations",
                        "Format choice impacts reliability",
                        "Consider format-specific fine-tuning"
                    ]
                ))

        # Finding 2: Complexity scaling
        scaling = self.analyze_complexity_scaling()
        for dim, data in scaling.items():
            if data.get('trend') == 'decreasing' and data.get('correlation', 0) < -0.5:
                findings.append(MetaFinding(
                    finding_id=f"MF_SCALE_{dim}",
                    title=f"Performance Degrades with {data['name']}",
                    description=f"Strong negative correlation (r={data['correlation']:.2f}) between {data['name']} and accuracy",
                    supporting_evidence=[{'scaling_analysis': {dim: data}}],
                    confidence=0.7,
                    implications=[
                        f"Limit {data['name']} where possible",
                        "Consider chunking or decomposition strategies",
                        "Monitor performance at high complexity"
                    ]
                ))

        # Finding 3: Capability boundaries
        boundaries = self.identify_capability_boundaries()
        if boundaries:
            findings.append(MetaFinding(
                finding_id="MF_BOUNDARIES",
                title="Capability Boundaries Identified",
                description=f"Found {len(boundaries)} points where performance drops sharply",
                supporting_evidence=[{'boundaries': boundaries}],
                confidence=0.75,
                implications=[
                    "Design systems to stay within capability boundaries",
                    "Add fallbacks when approaching limits",
                    "Use boundary conditions for risk assessment"
                ]
            ))

        self.meta_findings = findings
        return findings

    def generate_synthesis_report(self) -> str:
        """Generate comprehensive synthesis report."""
        lines = [
            "╔══════════════════════════════════════════════════════════════════════╗",
            "║              CROSS-EXPERIMENT SYNTHESIS REPORT                       ║",
            "╚══════════════════════════════════════════════════════════════════════╝",
            "",
        ]

        # Overview
        total_experiments = len(self.experiment_results)
        total_trials = sum(len(r) for r in self.experiment_results.values())
        lines.append(f"Experiments analyzed: {total_experiments}")
        lines.append(f"Total trials: {total_trials}")
        lines.append("")

        # Format analysis
        lines.append("FORMAT EFFECTS")
        lines.append("-" * 40)
        format_analysis = self.analyze_format_effects()
        for fmt, data in sorted(format_analysis.items(), key=lambda x: -x[1]['overall_accuracy']):
            lines.append(f"  {fmt:15} : {data['overall_accuracy']:.1%} (n={data['total_trials']})")
        lines.append("")

        # Complexity scaling
        lines.append("COMPLEXITY SCALING")
        lines.append("-" * 40)
        scaling = self.analyze_complexity_scaling()
        for dim, data in scaling.items():
            arrow = "↓" if data['trend'] == 'decreasing' else ("↑" if data['trend'] == 'increasing' else "→")
            lines.append(f"  {data['name']:20} : {arrow} (r={data['correlation']:.2f})")
        lines.append("")

        # Capability boundaries
        lines.append("CAPABILITY BOUNDARIES")
        lines.append("-" * 40)
        boundaries = self.identify_capability_boundaries()
        for b in boundaries[:5]:  # Top 5
            lines.append(f"  {b['experiment']}: {b['dimension']}={b['boundary_value']} → {b['accuracy_drop']:.1%} drop")
        lines.append("")

        # Meta-findings
        findings = self.synthesize_findings()
        lines.append("META-FINDINGS")
        lines.append("-" * 40)
        for f in findings:
            lines.append(f"\n  [{f.finding_id}] {f.title}")
            lines.append(f"  Confidence: {f.confidence:.0%}")
            lines.append(f"  {f.description}")
            lines.append("  Implications:")
            for imp in f.implications:
                lines.append(f"    • {imp}")
        lines.append("")

        # Capability map
        lines.append("CAPABILITY MAP")
        lines.append("-" * 40)
        cap_map = self.generate_capability_map()
        for cap_name, cap_data in cap_map.items():
            if cap_data['components']:
                lines.append(f"\n  {cap_name.replace('_', ' ').title()}")
                lines.append(f"  {cap_data['description']}")
                for comp_name, comp_data in cap_data['components'].items():
                    status_emoji = {'strong': '●', 'moderate': '◐', 'weak': '○'}
                    lines.append(f"    {status_emoji.get(comp_data['status'], '?')} {comp_name}: {comp_data['accuracy']:.1%}")

        return "\n".join(lines)


def demo():
    """Demonstrate synthesis analysis with synthetic data."""
    import random
    random.seed(42)

    analyzer = CrossExperimentAnalyzer()

    # Generate synthetic results for each experiment type
    experiments = {
        'hierarchy_perception': {'depth': [1, 2, 3, 4], 'format': ['markdown', 'json', 'xml']},
        'needle_in_structure': {'similarity': ['none', 'low', 'medium', 'high'], 'format': ['markdown', 'xml']},
        'isomorphic_content': {'format': ['json', 'xml', 'yaml', 'plain_text']},
        'multi_hop': {'num_hops': [2, 3, 4, 5]}
    }

    for exp_name, conditions in experiments.items():
        results = []
        for _ in range(50):  # 50 trials per experiment
            # Create trial with random conditions
            metadata = {}
            base_acc = 0.85

            for key, values in conditions.items():
                val = random.choice(values)
                metadata[key] = val

                # Adjust accuracy based on conditions
                if key == 'depth':
                    base_acc -= val * 0.05
                elif key == 'num_hops':
                    base_acc -= val * 0.07
                elif key == 'similarity' and val == 'high':
                    base_acc -= 0.15
                elif key == 'format':
                    if val == 'json':
                        base_acc += 0.05
                    elif val == 'plain_text':
                        base_acc -= 0.10

            results.append({
                'trial_id': f"{exp_name}_{len(results):03d}",
                'is_correct': random.random() < base_acc,
                'metadata': metadata
            })

        analyzer.load_results(exp_name, results)

    # Generate report
    print(analyzer.generate_synthesis_report())


if __name__ == '__main__':
    demo()
