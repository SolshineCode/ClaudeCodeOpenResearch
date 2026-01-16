"""
Live Experiment Harness

A framework for running interpretability experiments in real-time,
designed to work within conversation context for self-evaluation.

This module enables:
1. Generating experiment trials on-the-fly
2. Collecting responses for analysis
3. Real-time evaluation and scoring
4. Building behavioral profiles
"""

import json
import random
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import sys

# Add project modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'experiments' / 'structural'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'experiments' / 'attention'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'experiments' / 'format'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'experiments' / 'reasoning'))


@dataclass
class LiveTrial:
    """A trial ready for live execution."""
    trial_id: str
    experiment_type: str
    stimulus: str
    question: str
    expected_answer: Any
    metadata: Dict = field(default_factory=dict)

    def format_prompt(self) -> str:
        """Format as a clean prompt for model consumption."""
        return f"""{self.stimulus}

---

**Question**: {self.question}

**Instructions**: Provide your answer concisely. If the answer is a number, give just the number. If it's a list, separate items with commas. If yes/no, answer only "yes" or "no"."""


@dataclass
class LiveResult:
    """Result from a live trial."""
    trial_id: str
    expected: Any
    actual: str
    is_correct: bool
    confidence: Optional[str] = None
    reasoning: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class LiveExperimentHarness:
    """
    Harness for running live experiments.

    Designed for self-evaluation scenarios where the model
    being tested is also the one running the experiments.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).parent.parent / 'data' / 'results' / 'live'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.results: List[LiveResult] = []

    def generate_hierarchy_trial(self, seed: int, depth: int = 2) -> LiveTrial:
        """Generate a hierarchy perception trial."""
        from document_generator import generate_experiment_stimulus

        stimulus = generate_experiment_stimulus(
            seed=seed,
            max_depth=depth,
            format='markdown',
            num_probes=1
        )

        probe = stimulus['probes'][0]

        return LiveTrial(
            trial_id=f"HP_{seed}_{depth}",
            experiment_type='hierarchy_perception',
            stimulus=stimulus['document'],
            question=probe['question'],
            expected_answer=probe['answer'],
            metadata={
                'depth': depth,
                'probe_type': probe['type'],
                'total_nodes': stimulus['ground_truth']['total_nodes']
            }
        )

    def generate_needle_trial(self, seed: int, similarity: str = 'low') -> LiveTrial:
        """Generate a needle-in-structure trial."""
        from needle_in_structure import NeedleInStructureGenerator, StructuralPosition, DistractorConfig

        generator = NeedleInStructureGenerator(seed=seed)

        # Create needle
        template = random.choice(generator.FACT_TEMPLATES)
        context = f"Project-{seed:04d}"
        needle = generator._fill_template(template, context)

        # Position configuration
        needle_pos = StructuralPosition(depth=0, section_index=3, local_position='middle')

        # Distractor configuration
        num_dist = 2 if similarity != 'none' else 0
        dist_positions = [
            StructuralPosition(depth=0, section_index=1, local_position='end'),
            StructuralPosition(depth=1, section_index=5, local_position='end')
        ][:num_dist]

        dist_config = DistractorConfig(
            num_distractors=num_dist,
            similarity_level=similarity,
            positions=dist_positions
        )

        # Generate document
        doc_data = generator.generate_structured_document(
            needle=needle,
            needle_position=needle_pos,
            distractor_config=dist_config,
            format='markdown'
        )

        return LiveTrial(
            trial_id=f"NIS_{seed}_{similarity}",
            experiment_type='needle_in_structure',
            stimulus=doc_data['document'],
            question=f"What is the {needle.needle_key}?",
            expected_answer=needle.needle_value,
            metadata={
                'similarity': similarity,
                'needle_depth': needle_pos.depth,
                'num_distractors': num_dist
            }
        )

    def generate_format_trial(self, seed: int, format_type: str = 'json') -> LiveTrial:
        """Generate an isomorphic content trial."""
        from isomorphic_content import IsomorphicContentGenerator, IsomorphicProbeGenerator

        generator = IsomorphicContentGenerator(seed=seed)
        content = generator.generate_semantic_content(num_entities=4)

        # Render in requested format
        format_map = {
            'markdown_prose': generator.render_markdown_prose,
            'markdown_table': generator.render_markdown_table,
            'json': generator.render_json,
            'xml': generator.render_xml,
            'yaml': generator.render_yaml,
            'plain_text': generator.render_plain_text,
        }

        rendered = format_map.get(format_type, generator.render_json)(content)

        # Generate probe
        probe_gen = IsomorphicProbeGenerator()
        probe = probe_gen.entity_property_probe(content)

        return LiveTrial(
            trial_id=f"ISO_{seed}_{format_type}",
            experiment_type='isomorphic_content',
            stimulus=rendered,
            question=probe['question'],
            expected_answer=probe['answer'],
            metadata={
                'format': format_type,
                'probe_type': probe['type'],
                'num_entities': len(content.entities)
            }
        )

    def generate_multihop_trial(self, seed: int, num_hops: int = 3) -> LiveTrial:
        """Generate a multi-hop reasoning trial."""
        from multi_hop_document import MultiHopDocumentGenerator

        generator = MultiHopDocumentGenerator(seed=seed)
        document, chain = generator.generate_reasoning_chain(
            num_hops=num_hops,
            chain_type='explicit'
        )

        rendered = generator.render_markdown(document)

        return LiveTrial(
            trial_id=f"MH_{seed}_{num_hops}hop",
            experiment_type='multi_hop',
            stimulus=rendered,
            question=chain.question,
            expected_answer=chain.answer,
            metadata={
                'num_hops': num_hops,
                'chain_type': chain.chain_type,
                'hops': [h['fact'][:50] + '...' for h in chain.hops]
            }
        )

    def evaluate_response(self, trial: LiveTrial, response: str) -> LiveResult:
        """Evaluate a response against expected answer."""
        response_clean = response.strip().lower()
        expected_str = str(trial.expected_answer).lower()

        # Type-specific evaluation
        if isinstance(trial.expected_answer, int):
            # Numeric comparison
            try:
                import re
                numbers = re.findall(r'\d+', response_clean)
                is_correct = any(int(n) == trial.expected_answer for n in numbers)
            except:
                is_correct = False
        elif isinstance(trial.expected_answer, list):
            # List comparison - all items must appear
            is_correct = all(str(item).lower() in response_clean
                           for item in trial.expected_answer)
        elif trial.expected_answer in ['yes', 'no']:
            # Yes/no comparison
            if trial.expected_answer == 'yes':
                is_correct = response_clean in ['yes', 'true', 'correct']
            else:
                is_correct = response_clean in ['no', 'false', 'incorrect']
        else:
            # String containment
            is_correct = expected_str in response_clean

        result = LiveResult(
            trial_id=trial.trial_id,
            expected=trial.expected_answer,
            actual=response,
            is_correct=is_correct
        )

        self.results.append(result)
        return result

    def generate_trial_batch(
        self,
        experiment_types: List[str],
        trials_per_type: int = 3,
        seed_start: int = 10000
    ) -> List[LiveTrial]:
        """Generate a batch of trials across experiment types."""
        trials = []
        seed = seed_start

        generators = {
            'hierarchy': lambda s: self.generate_hierarchy_trial(s, depth=random.randint(1, 3)),
            'needle': lambda s: self.generate_needle_trial(s, random.choice(['none', 'low', 'medium'])),
            'format': lambda s: self.generate_format_trial(s, random.choice(['json', 'xml', 'yaml'])),
            'multihop': lambda s: self.generate_multihop_trial(s, random.randint(2, 4))
        }

        for exp_type in experiment_types:
            if exp_type in generators:
                for _ in range(trials_per_type):
                    try:
                        trial = generators[exp_type](seed)
                        trials.append(trial)
                    except Exception as e:
                        print(f"Error generating {exp_type} trial: {e}")
                    seed += 1

        return trials

    def get_session_summary(self) -> Dict:
        """Get summary of current session."""
        if not self.results:
            return {'message': 'No results yet'}

        correct = sum(1 for r in self.results if r.is_correct)
        total = len(self.results)

        # By experiment type
        by_type = {}
        for r in self.results:
            exp_type = r.trial_id.split('_')[0]
            if exp_type not in by_type:
                by_type[exp_type] = {'correct': 0, 'total': 0}
            by_type[exp_type]['total'] += 1
            if r.is_correct:
                by_type[exp_type]['correct'] += 1

        for exp_type in by_type:
            data = by_type[exp_type]
            data['accuracy'] = data['correct'] / data['total'] if data['total'] > 0 else 0

        return {
            'session_id': self.session_id,
            'total_trials': total,
            'correct': correct,
            'accuracy': correct / total if total > 0 else 0,
            'by_experiment_type': by_type
        }

    def save_session(self):
        """Save session results to file."""
        output_file = self.output_dir / f"session_{self.session_id}.json"

        data = {
            'session_id': self.session_id,
            'summary': self.get_session_summary(),
            'results': [asdict(r) for r in self.results]
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        return output_file


def create_quick_trial(experiment_type: str, seed: int = None) -> LiveTrial:
    """Quick helper to create a single trial."""
    if seed is None:
        seed = random.randint(10000, 99999)

    harness = LiveExperimentHarness()

    generators = {
        'hierarchy': harness.generate_hierarchy_trial,
        'needle': harness.generate_needle_trial,
        'format': harness.generate_format_trial,
        'multihop': harness.generate_multihop_trial
    }

    return generators.get(experiment_type, harness.generate_hierarchy_trial)(seed)


def demo():
    """Demonstrate the live harness."""
    print("=" * 70)
    print("LIVE EXPERIMENT HARNESS DEMO")
    print("=" * 70)

    harness = LiveExperimentHarness()

    # Generate one trial of each type
    trial_types = ['hierarchy', 'needle', 'format', 'multihop']

    for exp_type in trial_types:
        print(f"\n{'='*70}")
        print(f"EXPERIMENT TYPE: {exp_type.upper()}")
        print(f"{'='*70}")

        trial = create_quick_trial(exp_type, seed=42)

        print(f"\nTrial ID: {trial.trial_id}")
        print(f"Metadata: {trial.metadata}")
        print(f"\n--- STIMULUS (truncated) ---")
        print(trial.stimulus[:500] + "..." if len(trial.stimulus) > 500 else trial.stimulus)
        print(f"\n--- QUESTION ---")
        print(trial.question)
        print(f"\n--- EXPECTED ANSWER ---")
        print(trial.expected_answer)


if __name__ == '__main__':
    demo()
