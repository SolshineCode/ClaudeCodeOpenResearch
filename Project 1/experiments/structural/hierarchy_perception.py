"""
Experiment 1: Hierarchy Perception

Tests whether LLMs can accurately perceive and report hierarchical
structure in documents across different depths and formats.

Key Questions:
1. Can models accurately count nesting depth?
2. Do models understand parent-child relationships?
3. Is structural perception format-dependent?
4. Where are the capability boundaries?
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'tools'))
from document_generator import (
    HierarchicalDocumentGenerator,
    DocumentRenderer,
    ProbeGenerator,
    generate_experiment_stimulus
)


@dataclass
class ExperimentConfig:
    """Configuration for a hierarchy perception experiment."""
    name: str
    description: str
    seed_range: Tuple[int, int]  # Range of seeds to use
    depth_range: Tuple[int, int]  # (min_depth, max_depth) to test
    formats: List[str]  # Formats to test
    probes_per_stimulus: int
    branching_factor: Tuple[int, int]


@dataclass
class TrialResult:
    """Result of a single experimental trial."""
    trial_id: str
    config_name: str
    seed: int
    format: str
    depth: int
    probe_type: str
    question: str
    expected_answer: any
    model_answer: Optional[any] = None
    is_correct: Optional[bool] = None
    response_time_ms: Optional[float] = None
    raw_response: Optional[str] = None
    error: Optional[str] = None


class HierarchyPerceptionExperiment:
    """
    Runs hierarchy perception experiments.

    This experiment tests a model's ability to:
    1. Count levels of nesting (depth perception)
    2. Identify parent-child relationships
    3. Find siblings at the same level
    4. Trace paths through the hierarchy
    5. Count nodes at various levels
    """

    # Standard experiment configurations
    CONFIGS = {
        'shallow': ExperimentConfig(
            name='shallow',
            description='Test hierarchy perception on shallow documents (depth 1-2)',
            seed_range=(1000, 1020),
            depth_range=(1, 2),
            formats=['markdown', 'json', 'xml', 'text'],
            probes_per_stimulus=5,
            branching_factor=(2, 3)
        ),
        'medium': ExperimentConfig(
            name='medium',
            description='Test hierarchy perception on medium documents (depth 2-4)',
            seed_range=(2000, 2020),
            depth_range=(2, 4),
            formats=['markdown', 'json', 'xml', 'text'],
            probes_per_stimulus=5,
            branching_factor=(2, 3)
        ),
        'deep': ExperimentConfig(
            name='deep',
            description='Test hierarchy perception on deep documents (depth 4-6)',
            seed_range=(3000, 3020),
            depth_range=(4, 6),
            formats=['markdown', 'json', 'xml', 'text'],
            probes_per_stimulus=5,
            branching_factor=(2, 3)
        ),
        'wide': ExperimentConfig(
            name='wide',
            description='Test hierarchy perception on wide documents (high branching)',
            seed_range=(4000, 4020),
            depth_range=(2, 3),
            formats=['markdown', 'json', 'xml', 'text'],
            probes_per_stimulus=5,
            branching_factor=(4, 6)
        )
    }

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).parent.parent.parent / 'data' / 'results'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_trial_stimuli(self, config: ExperimentConfig) -> List[Dict]:
        """Generate all stimuli for a configuration."""
        stimuli = []

        for seed in range(config.seed_range[0], config.seed_range[1]):
            for depth in range(config.depth_range[0], config.depth_range[1] + 1):
                for fmt in config.formats:
                    stimulus = generate_experiment_stimulus(
                        seed=seed,
                        max_depth=depth,
                        branching=config.branching_factor,
                        format=fmt,
                        num_probes=config.probes_per_stimulus
                    )
                    stimulus['config_name'] = config.name
                    stimulus['target_depth'] = depth
                    stimuli.append(stimulus)

        return stimuli

    def create_prompt(self, stimulus: Dict, probe: Dict) -> str:
        """Create a prompt for a single trial."""
        return f"""I'm going to show you a structured document, then ask you a question about its structure.

## Document

{stimulus['document']}

## Question

{probe['question']}

## Instructions

Answer the question precisely and concisely. If the answer is a list, provide it as a comma-separated list. If it's a number, provide just the number. If it's yes/no, answer only "yes" or "no".

Your answer:"""

    def evaluate_response(self, expected: any, actual: str, probe_type: str) -> Tuple[bool, any]:
        """
        Evaluate whether a response is correct.

        Returns (is_correct, parsed_answer)
        """
        actual = actual.strip().lower()

        if probe_type == 'depth_probe' or probe_type == 'count_probe':
            try:
                parsed = int(''.join(filter(str.isdigit, actual)))
                return parsed == expected, parsed
            except ValueError:
                return False, actual

        elif probe_type == 'leaf_probe':
            return actual in ['no', 'false', '0'], actual

        elif probe_type == 'parent_probe':
            # Check if expected ID appears in response
            return str(expected).lower() in actual, actual

        elif probe_type in ['sibling_probe', 'path_probe']:
            # For list answers, check if all expected items are mentioned
            if isinstance(expected, list):
                found = [str(item).lower() in actual for item in expected]
                return all(found), actual
            return str(expected).lower() in actual, actual

        return False, actual

    def format_trial_for_model(self, stimulus: Dict) -> List[Dict]:
        """
        Format a stimulus into a list of trial dicts ready for model evaluation.

        Each trial dict contains:
            - prompt: The full prompt to send to the model
            - probe: The probe metadata
            - stimulus_metadata: Info about the stimulus
        """
        trials = []

        for probe in stimulus['probes']:
            trial = {
                'prompt': self.create_prompt(stimulus, probe),
                'probe': probe,
                'stimulus_metadata': {
                    'seed': stimulus['seed'],
                    'format': stimulus['format'],
                    'target_depth': stimulus.get('target_depth'),
                    'config_name': stimulus.get('config_name'),
                    'total_nodes': stimulus['ground_truth']['total_nodes'],
                    'max_depth': stimulus['ground_truth']['max_depth']
                }
            }
            trials.append(trial)

        return trials

    def save_stimuli(self, stimuli: List[Dict], config_name: str):
        """Save generated stimuli to file."""
        output_file = self.output_dir / f'hierarchy_stimuli_{config_name}.json'

        # Remove tree data to reduce file size (can regenerate from seed)
        slim_stimuli = []
        for s in stimuli:
            slim = {k: v for k, v in s.items() if k != 'tree'}
            slim_stimuli.append(slim)

        with open(output_file, 'w') as f:
            json.dump(slim_stimuli, f, indent=2)

        return output_file

    def save_results(self, results: List[TrialResult], experiment_name: str):
        """Save experiment results."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'hierarchy_results_{experiment_name}_{timestamp}.json'

        with open(output_file, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)

        return output_file


def create_experiment_protocol() -> Dict:
    """
    Create a documented experiment protocol.

    Returns a dict describing the full experimental protocol
    that can be saved and shared.
    """
    return {
        'experiment_name': 'Hierarchy Perception',
        'version': '1.0',
        'date_created': datetime.now().isoformat(),
        'description': '''
            This experiment tests LLM ability to perceive and reason about
            hierarchical document structure. It uses procedurally generated
            documents with known ground truth to probe specific structural
            understanding capabilities.
        ''',
        'hypotheses': [
            'H1: Accuracy decreases with document depth',
            'H2: JSON format yields highest accuracy due to explicit structure',
            'H3: Parent/child relationships are easier than sibling relationships',
            'H4: Path tracing accuracy depends on path length',
            'H5: Counting accuracy depends on total count (Weber\'s law)',
        ],
        'independent_variables': [
            {'name': 'document_depth', 'levels': [1, 2, 3, 4, 5, 6]},
            {'name': 'format', 'levels': ['markdown', 'json', 'xml', 'text']},
            {'name': 'branching_factor', 'levels': ['narrow (2-3)', 'wide (4-6)']},
            {'name': 'probe_type', 'levels': [
                'depth_probe', 'parent_probe', 'sibling_probe',
                'leaf_probe', 'path_probe', 'count_probe'
            ]},
        ],
        'dependent_variables': [
            {'name': 'accuracy', 'type': 'binary', 'description': 'Whether response was correct'},
            {'name': 'response', 'type': 'string', 'description': 'Raw model response'},
        ],
        'controls': [
            'Randomized node IDs prevent memorization',
            'Multiple seeds per condition ensure reliability',
            'Ground truth derived programmatically',
        ],
        'procedure': '''
            1. Generate document with specified parameters
            2. Render document in target format
            3. Generate probing questions with ground truth
            4. Present document + question to model
            5. Parse and evaluate response
            6. Record all data for analysis
        ''',
        'analysis_plan': '''
            Primary analyses:
            - Accuracy by depth (test H1)
            - Accuracy by format (test H2)
            - Accuracy by probe type (test H3, H4)
            - Counting accuracy vs magnitude (test H5)

            Secondary analyses:
            - Interaction effects (depth x format)
            - Error pattern analysis
            - Confidence calibration (if available)
        ''',
        'configurations': {
            name: asdict(config) if hasattr(config, '__dataclass_fields__')
            else {
                'name': config.name,
                'description': config.description,
                'seed_range': config.seed_range,
                'depth_range': config.depth_range,
                'formats': config.formats,
                'probes_per_stimulus': config.probes_per_stimulus,
                'branching_factor': config.branching_factor
            }
            for name, config in HierarchyPerceptionExperiment.CONFIGS.items()
        }
    }


def generate_sample_trials(config_name: str = 'shallow', num_samples: int = 3) -> List[Dict]:
    """Generate sample trials for inspection/testing."""
    experiment = HierarchyPerceptionExperiment()
    config = experiment.CONFIGS[config_name]

    # Modify config for sample generation
    sample_config = ExperimentConfig(
        name=config.name + '_sample',
        description='Sample trials for inspection',
        seed_range=(config.seed_range[0], config.seed_range[0] + num_samples),
        depth_range=(config.depth_range[0], config.depth_range[0]),
        formats=['markdown'],  # Just one format for samples
        probes_per_stimulus=3,
        branching_factor=config.branching_factor
    )

    stimuli = experiment.generate_trial_stimuli(sample_config)

    all_trials = []
    for stimulus in stimuli:
        trials = experiment.format_trial_for_model(stimulus)
        all_trials.extend(trials)

    return all_trials


if __name__ == '__main__':
    # Generate and display sample trials
    print("=" * 70)
    print("HIERARCHY PERCEPTION EXPERIMENT - SAMPLE TRIALS")
    print("=" * 70)

    trials = generate_sample_trials('shallow', num_samples=2)

    for i, trial in enumerate(trials[:3]):  # Show first 3
        print(f"\n{'='*70}")
        print(f"TRIAL {i+1}")
        print(f"{'='*70}")
        print(f"\nMetadata: {trial['stimulus_metadata']}")
        print(f"\nProbe Type: {trial['probe']['type']}")
        print(f"\nExpected Answer: {trial['probe']['answer']}")
        print(f"\n{'-'*70}")
        print("PROMPT:")
        print(f"{'-'*70}")
        print(trial['prompt'])

    # Save protocol
    protocol = create_experiment_protocol()
    protocol_path = Path(__file__).parent.parent.parent / 'data' / 'stimuli'
    protocol_path.mkdir(parents=True, exist_ok=True)

    with open(protocol_path / 'hierarchy_perception_protocol.json', 'w') as f:
        json.dump(protocol, f, indent=2)

    print(f"\n\nProtocol saved to: {protocol_path / 'hierarchy_perception_protocol.json'}")
