"""
Visualization and Reporting Tools

ASCII-based visualizations for experiment results that work in
terminal environments without graphics dependencies.

Includes:
- Accuracy bar charts
- Confusion matrices
- Trend plots
- Summary tables
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import math


class ASCIIChart:
    """ASCII-based chart renderer."""

    @staticmethod
    def horizontal_bar(
        data: Dict[str, float],
        title: str = "",
        width: int = 50,
        show_values: bool = True,
        max_val: float = 1.0
    ) -> str:
        """
        Create horizontal bar chart.

        Args:
            data: Dict of label -> value
            title: Chart title
            width: Width of bar area
            show_values: Whether to show numeric values
            max_val: Maximum value for scaling
        """
        lines = []

        if title:
            lines.append(title)
            lines.append("=" * (width + 20))

        # Find longest label for alignment
        max_label = max(len(str(k)) for k in data.keys()) if data else 0

        for label, value in data.items():
            bar_width = int((value / max_val) * width)
            bar = "█" * bar_width + "░" * (width - bar_width)

            if show_values:
                value_str = f"{value:.1%}" if max_val == 1.0 else f"{value:.2f}"
                lines.append(f"{str(label):>{max_label}} │{bar}│ {value_str}")
            else:
                lines.append(f"{str(label):>{max_label}} │{bar}│")

        return "\n".join(lines)

    @staticmethod
    def grouped_bar(
        data: Dict[str, Dict[str, float]],
        title: str = "",
        width: int = 40
    ) -> str:
        """
        Create grouped horizontal bar chart.

        Args:
            data: Dict of group -> {category -> value}
        """
        lines = []

        if title:
            lines.append(title)
            lines.append("=" * (width + 30))

        all_categories = set()
        for group_data in data.values():
            all_categories.update(group_data.keys())

        symbols = ['█', '▓', '▒', '░', '▄', '▀']
        cat_symbols = {cat: symbols[i % len(symbols)] for i, cat in enumerate(sorted(all_categories))}

        # Legend
        lines.append("\nLegend: " + " ".join(f"{sym} {cat}" for cat, sym in cat_symbols.items()))
        lines.append("")

        max_label = max(len(str(k)) for k in data.keys()) if data else 0

        for group, group_data in data.items():
            lines.append(f"\n{group}:")
            for cat, value in group_data.items():
                bar_width = int(value * width)
                bar = cat_symbols[cat] * bar_width
                lines.append(f"  {cat:>12} │{bar:<{width}}│ {value:.1%}")

        return "\n".join(lines)

    @staticmethod
    def table(
        data: List[Dict],
        columns: List[str],
        title: str = ""
    ) -> str:
        """Create ASCII table."""
        lines = []

        if title:
            lines.append(title)
            lines.append("")

        # Calculate column widths
        col_widths = {}
        for col in columns:
            max_width = len(col)
            for row in data:
                val = str(row.get(col, ""))
                max_width = max(max_width, len(val))
            col_widths[col] = max_width + 2

        # Header
        header = "│".join(f" {col:^{col_widths[col]-2}} " for col in columns)
        separator = "┼".join("─" * col_widths[col] for col in columns)

        lines.append("┌" + separator.replace("┼", "┬") + "┐")
        lines.append("│" + header + "│")
        lines.append("├" + separator + "┤")

        # Rows
        for row in data:
            row_str = "│".join(
                f" {str(row.get(col, '')):^{col_widths[col]-2}} "
                for col in columns
            )
            lines.append("│" + row_str + "│")

        lines.append("└" + separator.replace("┼", "┴") + "┘")

        return "\n".join(lines)

    @staticmethod
    def confusion_matrix(
        matrix: Dict[str, Dict[str, int]],
        title: str = "Confusion Matrix"
    ) -> str:
        """Create confusion matrix visualization."""
        lines = [title, ""]

        labels = sorted(matrix.keys())
        max_label = max(len(l) for l in labels)
        cell_width = 8

        # Header row
        header = " " * (max_label + 1) + "│ " + " │ ".join(f"{l:^{cell_width}}" for l in labels) + " │"
        lines.append(header)
        lines.append("─" * len(header))

        # Data rows
        for row_label in labels:
            row_data = matrix.get(row_label, {})
            cells = []
            for col_label in labels:
                val = row_data.get(col_label, 0)
                cells.append(f"{val:^{cell_width}}")
            lines.append(f"{row_label:>{max_label}} │ " + " │ ".join(cells) + " │")

        return "\n".join(lines)

    @staticmethod
    def sparkline(values: List[float], width: int = 20) -> str:
        """Create a sparkline (mini inline chart)."""
        if not values:
            return "─" * width

        chars = "▁▂▃▄▅▆▇█"
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val if max_val > min_val else 1

        # Resample to width
        step = len(values) / width
        resampled = []
        for i in range(width):
            idx = int(i * step)
            resampled.append(values[min(idx, len(values) - 1)])

        # Map to characters
        result = ""
        for v in resampled:
            normalized = (v - min_val) / range_val
            char_idx = min(int(normalized * len(chars)), len(chars) - 1)
            result += chars[char_idx]

        return result

    @staticmethod
    def heatmap(
        data: List[List[float]],
        row_labels: List[str],
        col_labels: List[str],
        title: str = ""
    ) -> str:
        """Create ASCII heatmap."""
        lines = []
        if title:
            lines.append(title)
            lines.append("")

        # Characters for intensity
        chars = " ░▒▓█"

        # Normalize data
        flat = [v for row in data for v in row]
        min_val = min(flat) if flat else 0
        max_val = max(flat) if flat else 1
        range_val = max_val - min_val if max_val > min_val else 1

        max_row_label = max(len(l) for l in row_labels) if row_labels else 0
        cell_width = max(len(l) for l in col_labels) + 1 if col_labels else 3

        # Header
        header = " " * (max_row_label + 1) + "".join(f"{l:^{cell_width}}" for l in col_labels)
        lines.append(header)

        # Rows
        for i, row_label in enumerate(row_labels):
            row_chars = ""
            for j, val in enumerate(data[i] if i < len(data) else []):
                normalized = (val - min_val) / range_val
                char_idx = min(int(normalized * (len(chars) - 1)), len(chars) - 1)
                row_chars += f"{chars[char_idx] * (cell_width)}"
            lines.append(f"{row_label:>{max_row_label}} {row_chars}")

        # Legend
        lines.append("")
        lines.append(f"Scale: {min_val:.2f} " + "".join(chars) + f" {max_val:.2f}")

        return "\n".join(lines)


class ReportGenerator:
    """Generates comprehensive experiment reports."""

    def __init__(self, results: List[Dict]):
        self.results = results
        self.chart = ASCIIChart()

    def overall_summary(self) -> str:
        """Generate overall summary section."""
        total = len(self.results)
        correct = sum(1 for r in self.results if r.get('is_correct', False))
        accuracy = correct / total if total > 0 else 0

        lines = [
            "╔══════════════════════════════════════════════════════════════════╗",
            "║                     EXPERIMENT SUMMARY                           ║",
            "╠══════════════════════════════════════════════════════════════════╣",
            f"║  Total Trials:     {total:>6}                                     ║",
            f"║  Correct:          {correct:>6}                                     ║",
            f"║  Accuracy:         {accuracy:>6.1%}                                     ║",
            "╚══════════════════════════════════════════════════════════════════╝"
        ]

        return "\n".join(lines)

    def accuracy_by_condition(self, condition_key: str) -> str:
        """Generate accuracy breakdown by condition."""
        grouped = defaultdict(lambda: {'correct': 0, 'total': 0})

        for r in self.results:
            cond = r.get('metadata', {}).get(condition_key) or r.get(condition_key)
            if cond is not None:
                grouped[cond]['total'] += 1
                if r.get('is_correct', False):
                    grouped[cond]['correct'] += 1

        accuracies = {}
        for cond, data in grouped.items():
            acc = data['correct'] / data['total'] if data['total'] > 0 else 0
            accuracies[f"{cond} (n={data['total']})"] = acc

        return self.chart.horizontal_bar(
            accuracies,
            title=f"Accuracy by {condition_key}",
            width=40
        )

    def error_analysis(self) -> str:
        """Analyze error patterns."""
        errors = [r for r in self.results if not r.get('is_correct', False)]

        if not errors:
            return "No errors to analyze."

        lines = ["ERROR ANALYSIS", "=" * 50, ""]

        # Errors by condition
        error_conditions = defaultdict(int)
        for e in errors:
            for key in ['format', 'depth', 'probe_type', 'num_hops']:
                val = e.get('metadata', {}).get(key) or e.get(key)
                if val is not None:
                    error_conditions[f"{key}={val}"] += 1

        lines.append("Most common error conditions:")
        for cond, count in sorted(error_conditions.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  {cond}: {count} errors")

        return "\n".join(lines)

    def generate_full_report(self, experiment_name: str) -> str:
        """Generate complete report."""
        sections = [
            f"{'='*70}",
            f"EXPERIMENT REPORT: {experiment_name}",
            f"{'='*70}",
            "",
            self.overall_summary(),
            "",
        ]

        # Add condition breakdowns
        condition_keys = ['format', 'depth', 'probe_type', 'num_hops', 'similarity']
        for key in condition_keys:
            # Check if this condition exists in data
            has_key = any(
                r.get('metadata', {}).get(key) or r.get(key)
                for r in self.results
            )
            if has_key:
                sections.append("")
                sections.append(self.accuracy_by_condition(key))

        sections.append("")
        sections.append(self.error_analysis())

        return "\n".join(sections)


class ProgressTracker:
    """Track experiment progress in real-time."""

    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.correct = 0

    def update(self, is_correct: bool) -> str:
        """Update progress and return status line."""
        self.completed += 1
        if is_correct:
            self.correct += 1

        accuracy = self.correct / self.completed if self.completed > 0 else 0
        pct_complete = self.completed / self.total

        bar_width = 30
        filled = int(pct_complete * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        return f"Progress: [{bar}] {self.completed}/{self.total} | Accuracy: {accuracy:.1%}"


def demo():
    """Demonstrate visualization tools."""
    print("=" * 70)
    print("VISUALIZATION DEMO")
    print("=" * 70)

    chart = ASCIIChart()

    # Bar chart demo
    print("\n--- HORIZONTAL BAR CHART ---\n")
    accuracy_data = {
        'markdown': 0.75,
        'json': 0.88,
        'xml': 0.82,
        'yaml': 0.79,
        'plain_text': 0.65
    }
    print(chart.horizontal_bar(accuracy_data, "Accuracy by Format", width=40))

    # Table demo
    print("\n\n--- TABLE ---\n")
    table_data = [
        {'Experiment': 'Hierarchy', 'Trials': 100, 'Accuracy': '78%', 'p-value': '0.001'},
        {'Experiment': 'Needle', 'Trials': 72, 'Accuracy': '85%', 'p-value': '0.003'},
        {'Experiment': 'Isomorphic', 'Trials': 140, 'Accuracy': '82%', 'p-value': '0.012'},
        {'Experiment': 'Multi-hop', 'Trials': 72, 'Accuracy': '71%', 'p-value': '0.001'},
    ]
    print(chart.table(table_data, ['Experiment', 'Trials', 'Accuracy', 'p-value'], "Experiment Results"))

    # Sparkline demo
    print("\n\n--- SPARKLINES ---\n")
    accuracy_over_time = [0.70, 0.72, 0.75, 0.73, 0.78, 0.80, 0.82, 0.79, 0.85, 0.88]
    print(f"Accuracy trend: {chart.sparkline(accuracy_over_time, width=30)} ({accuracy_over_time[-1]:.0%})")

    depth_performance = [0.95, 0.88, 0.75, 0.60, 0.45]
    print(f"By depth (1-5): {chart.sparkline(depth_performance, width=20)}")

    # Heatmap demo
    print("\n\n--- HEATMAP ---\n")
    heatmap_data = [
        [0.95, 0.88, 0.72, 0.58],
        [0.92, 0.85, 0.68, 0.52],
        [0.88, 0.78, 0.62, 0.45],
        [0.82, 0.70, 0.55, 0.38],
    ]
    print(chart.heatmap(
        heatmap_data,
        row_labels=['depth=1', 'depth=2', 'depth=3', 'depth=4'],
        col_labels=['low', 'med', 'high', 'v.high'],
        title="Accuracy: Depth × Complexity"
    ))

    # Progress tracker demo
    print("\n\n--- PROGRESS TRACKER ---\n")
    tracker = ProgressTracker(total=50)
    import random
    for _ in range(25):
        status = tracker.update(random.random() > 0.3)
    print(status)


if __name__ == '__main__':
    demo()
