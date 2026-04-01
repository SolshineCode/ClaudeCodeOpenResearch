"""
Experiment Runner Framework

Provides infrastructure for running interpretability experiments
against LLM APIs and collecting structured results.

This is a framework - actual API calls would require API keys
and would be implemented based on the specific model being tested.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod


@dataclass
class TrialResult:
    """Result of a single experimental trial."""
    trial_id: str
    experiment_name: str
    prompt: str
    expected_answer: Any
    model_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    response_time_ms: Optional[float] = None
    raw_response: Optional[str] = None
    metadata: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ExperimentRun:
    """Metadata for an experiment run."""
    run_id: str
    experiment_name: str
    model_name: str
    start_time: str
    end_time: Optional[str] = None
    total_trials: int = 0
    completed_trials: int = 0
    config: Optional[Dict] = None


class ModelInterface(ABC):
    """Abstract interface for model APIs."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response for the given prompt."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier."""
        pass


class MockModelInterface(ModelInterface):
    """Mock model for testing the framework."""

    def __init__(self, response_fn: Optional[Callable] = None):
        self.response_fn = response_fn or (lambda p: "MOCK_RESPONSE")
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        time.sleep(0.01)  # Simulate latency
        return self.response_fn(prompt)

    def get_model_name(self) -> str:
        return "mock-model-v1"


class ExperimentRunner:
    """
    Runs experiments and collects results.

    Usage:
        runner = ExperimentRunner(model_interface, output_dir)
        results = runner.run_experiment(
            name="hierarchy_perception",
            trials=trial_list,
            evaluator=eval_function
        )
    """

    def __init__(
        self,
        model: ModelInterface,
        output_dir: Optional[Path] = None,
        save_intermediate: bool = True
    ):
        self.model = model
        self.output_dir = output_dir or Path(__file__).parent.parent / 'data' / 'results'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.save_intermediate = save_intermediate

    def run_experiment(
        self,
        name: str,
        trials: List[Dict],
        evaluator: Callable[[Any, str], bool],
        max_trials: Optional[int] = None,
        config: Optional[Dict] = None
    ) -> List[TrialResult]:
        """
        Run an experiment.

        Args:
            name: Experiment name
            trials: List of trial dicts (must have 'prompt' and 'expected_answer')
            evaluator: Function(expected, actual) -> bool
            max_trials: Optional limit on trials to run
            config: Optional configuration metadata

        Returns:
            List of TrialResult objects
        """
        run_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run = ExperimentRun(
            run_id=run_id,
            experiment_name=name,
            model_name=self.model.get_model_name(),
            start_time=datetime.now().isoformat(),
            total_trials=len(trials) if max_trials is None else min(len(trials), max_trials),
            config=config
        )

        results = []
        trials_to_run = trials[:max_trials] if max_trials else trials

        for i, trial in enumerate(trials_to_run):
            trial_id = trial.get('trial_id', f"{name}_{i:04d}")

            try:
                start = time.time()
                response = self.model.generate(trial['prompt'])
                elapsed_ms = (time.time() - start) * 1000

                is_correct = evaluator(trial['expected_answer'], response)

                result = TrialResult(
                    trial_id=trial_id,
                    experiment_name=name,
                    prompt=trial['prompt'],
                    expected_answer=trial['expected_answer'],
                    model_answer=response,
                    is_correct=is_correct,
                    response_time_ms=elapsed_ms,
                    raw_response=response,
                    metadata={k: v for k, v in trial.items()
                             if k not in ['prompt', 'expected_answer']}
                )

            except Exception as e:
                result = TrialResult(
                    trial_id=trial_id,
                    experiment_name=name,
                    prompt=trial['prompt'],
                    expected_answer=trial['expected_answer'],
                    error=str(e)
                )

            results.append(result)
            run.completed_trials = len(results)

            # Progress update
            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{len(trials_to_run)} trials")

            # Intermediate save
            if self.save_intermediate and (i + 1) % 50 == 0:
                self._save_intermediate(run, results)

        run.end_time = datetime.now().isoformat()
        self._save_final(run, results)

        return results

    def _save_intermediate(self, run: ExperimentRun, results: List[TrialResult]):
        """Save intermediate results."""
        path = self.output_dir / f"{run.run_id}_intermediate.json"
        self._save_results(path, run, results)

    def _save_final(self, run: ExperimentRun, results: List[TrialResult]):
        """Save final results."""
        path = self.output_dir / f"{run.run_id}_final.json"
        self._save_results(path, run, results)

        # Also save summary
        summary = self._compute_summary(run, results)
        summary_path = self.output_dir / f"{run.run_id}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

    def _save_results(self, path: Path, run: ExperimentRun, results: List[TrialResult]):
        """Save results to file."""
        data = {
            'run': asdict(run),
            'results': [asdict(r) for r in results]
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def _compute_summary(self, run: ExperimentRun, results: List[TrialResult]) -> Dict:
        """Compute summary statistics."""
        correct = sum(1 for r in results if r.is_correct)
        total = len(results)
        errors = sum(1 for r in results if r.error)

        response_times = [r.response_time_ms for r in results if r.response_time_ms]

        return {
            'run_id': run.run_id,
            'experiment_name': run.experiment_name,
            'model_name': run.model_name,
            'total_trials': total,
            'correct': correct,
            'accuracy': correct / total if total > 0 else 0,
            'errors': errors,
            'mean_response_time_ms': sum(response_times) / len(response_times) if response_times else None,
            'start_time': run.start_time,
            'end_time': run.end_time
        }


# Standard evaluators for different probe types

def exact_match_evaluator(expected: Any, actual: str) -> bool:
    """Check for exact string match (case-insensitive)."""
    return str(expected).lower().strip() == actual.lower().strip()


def contains_evaluator(expected: Any, actual: str) -> bool:
    """Check if expected value is contained in actual."""
    return str(expected).lower() in actual.lower()


def numeric_evaluator(expected: Any, actual: str) -> bool:
    """Extract and compare numeric values."""
    try:
        expected_num = int(expected)
        # Extract first number from actual
        import re
        numbers = re.findall(r'\d+', actual)
        if numbers:
            return int(numbers[0]) == expected_num
        return False
    except (ValueError, TypeError):
        return False


def list_evaluator(expected: List, actual: str) -> bool:
    """Check if all expected items appear in actual."""
    actual_lower = actual.lower()
    return all(str(item).lower() in actual_lower for item in expected)


def yes_no_evaluator(expected: str, actual: str) -> bool:
    """Evaluate yes/no answers."""
    actual_lower = actual.lower().strip()
    if expected.lower() == 'yes':
        return actual_lower in ['yes', 'true', '1', 'correct', 'affirmative']
    else:
        return actual_lower in ['no', 'false', '0', 'incorrect', 'negative']


class EvaluatorFactory:
    """Factory for creating appropriate evaluators."""

    @staticmethod
    def get_evaluator(probe_type: str) -> Callable:
        """Get evaluator based on probe type."""
        evaluators = {
            'depth_probe': numeric_evaluator,
            'count_probe': numeric_evaluator,
            'parent_probe': contains_evaluator,
            'sibling_probe': list_evaluator,
            'leaf_probe': yes_no_evaluator,
            'path_probe': list_evaluator,
            'entity_property': contains_evaluator,
            'relation': contains_evaluator,
            'aggregate': contains_evaluator,
            'comparison': contains_evaluator,
            'count_filter': numeric_evaluator,
        }
        return evaluators.get(probe_type, exact_match_evaluator)


def demo_run():
    """Demonstrate the experiment runner with mock model."""
    print("=" * 60)
    print("EXPERIMENT RUNNER DEMO")
    print("=" * 60)

    # Create mock model that returns random-ish responses
    import random
    def mock_response(prompt):
        if "depth" in prompt.lower():
            return str(random.randint(0, 5))
        elif "how many" in prompt.lower():
            return str(random.randint(1, 20))
        elif "yes or no" in prompt.lower():
            return random.choice(["yes", "no"])
        else:
            return "mock_answer_123"

    mock_model = MockModelInterface(response_fn=mock_response)

    # Create sample trials
    trials = [
        {
            'trial_id': 'demo_001',
            'prompt': 'What is the depth of node X?',
            'expected_answer': 2,
            'probe_type': 'depth_probe'
        },
        {
            'trial_id': 'demo_002',
            'prompt': 'How many nodes are at level 1?',
            'expected_answer': 5,
            'probe_type': 'count_probe'
        },
        {
            'trial_id': 'demo_003',
            'prompt': 'Does node Y have children? Answer yes or no.',
            'expected_answer': 'no',
            'probe_type': 'leaf_probe'
        },
    ]

    # Run experiment
    runner = ExperimentRunner(mock_model, save_intermediate=False)

    def smart_evaluator(expected, actual):
        # In real use, would inspect trial metadata for probe_type
        return contains_evaluator(expected, actual)

    results = runner.run_experiment(
        name='demo_experiment',
        trials=trials,
        evaluator=smart_evaluator,
        config={'description': 'Demo run'}
    )

    print("\nResults:")
    for r in results:
        print(f"  {r.trial_id}: expected={r.expected_answer}, "
              f"got={r.model_answer}, correct={r.is_correct}")


if __name__ == '__main__':
    demo_run()
