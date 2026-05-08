"""
Live API Runner

Runs the Project 1 experiment suites against the Anthropic API and
records concrete behavioral data. Supersedes synthetic-mock predictions
in FINDINGS_LOG.md with measured baselines.

Usage:
    ANTHROPIC_API_KEY=sk-ant-... python analysis/live_api_runner.py \
        --experiment hierarchy --trials 30 --model claude-haiku-4-5

The runner:
  1. Builds trials via the existing live_harness + experiment generators
  2. Calls the Anthropic Messages API for each trial
  3. Evaluates responses against ground truth
  4. Saves per-trial JSONL + a session summary JSON to data/results/live/

Design notes:
  - We use Haiku 4.5 by default for cost (Caleb's standing pref).
  - max_tokens kept tight (~256) — these probes have short answers.
  - Threaded concurrency for bulk runs; the API tolerates ~5-10 in-flight.
  - All trial seeds are deterministic for reproducibility.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'structural'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'attention'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'format'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'reasoning'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'adversarial'))
sys.path.insert(0, str(PROJECT_ROOT / 'analysis'))

from live_harness import LiveExperimentHarness, LiveTrial  # noqa: E402

DEFAULT_MODEL = "claude-haiku-4-5"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "results" / "live"


@dataclass
class APIResult:
    trial_id: str
    experiment_type: str
    expected: Any
    actual: str
    is_correct: bool
    metadata: Dict[str, Any]
    latency_ms: int
    input_tokens: int = 0
    output_tokens: int = 0
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


def _build_client():
    import anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        for candidate in [
            Path.home() / "ChatFiller" / "voice" / "env.txt",
            Path("C:/Users/caleb/ChatFiller/voice/env.txt"),
        ]:
            if candidate.exists():
                for line in candidate.read_text().splitlines():
                    if line.startswith("ANTHROPIC_API_KEY"):
                        api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
                if api_key:
                    break
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not found")
    return anthropic.Anthropic(api_key=api_key)


def _run_one(client, trial: LiveTrial, model: str, max_tokens: int) -> APIResult:
    prompt = trial.format_prompt()
    start = time.time()
    try:
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = int((time.time() - start) * 1000)
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text").strip()
        in_tok = msg.usage.input_tokens
        out_tok = msg.usage.output_tokens
        is_correct = _evaluate(trial, text)
        return APIResult(
            trial_id=trial.trial_id,
            experiment_type=trial.experiment_type,
            expected=trial.expected_answer,
            actual=text,
            is_correct=is_correct,
            metadata=trial.metadata,
            latency_ms=latency_ms,
            input_tokens=in_tok,
            output_tokens=out_tok,
        )
    except Exception as e:
        return APIResult(
            trial_id=trial.trial_id,
            experiment_type=trial.experiment_type,
            expected=trial.expected_answer,
            actual="",
            is_correct=False,
            metadata=trial.metadata,
            latency_ms=int((time.time() - start) * 1000),
            error=str(e)[:300],
        )


def _evaluate(trial: LiveTrial, response: str) -> bool:
    """Reproduce LiveExperimentHarness.evaluate_response with a few extras."""
    cleaned = response.strip().lower()
    expected = trial.expected_answer

    if isinstance(expected, bool):
        return ("yes" in cleaned and expected) or ("no" in cleaned and not expected)

    if isinstance(expected, int):
        nums = re.findall(r"-?\d+", cleaned)
        return any(int(n) == expected for n in nums)

    if isinstance(expected, list):
        if not expected:
            return cleaned in {"none", "no siblings", "[]", ""}
        return all(str(item).lower() in cleaned for item in expected)

    if isinstance(expected, str):
        if expected.lower() in {"yes", "no"}:
            yes_words = {"yes", "true", "correct", "y"}
            no_words = {"no", "false", "incorrect", "n"}
            tokens = set(re.findall(r"[a-z]+", cleaned))
            if expected.lower() == "yes":
                return bool(tokens & yes_words) and not bool(tokens & no_words - {"none"})
            return bool(tokens & no_words)
        return expected.lower() in cleaned

    return str(expected).lower() in cleaned


def build_hierarchy_trials(n: int, seed_start: int = 20000) -> List[LiveTrial]:
    h = LiveExperimentHarness()
    trials = []
    rng = random.Random(seed_start)
    for i in range(n):
        seed = seed_start + i
        depth = rng.choice([1, 2, 3, 4])
        trials.append(h.generate_hierarchy_trial(seed=seed, depth=depth))
    return trials


def build_needle_trials(n: int, seed_start: int = 30000) -> List[LiveTrial]:
    h = LiveExperimentHarness()
    trials = []
    rng = random.Random(seed_start)
    sims = ["none", "low", "medium", "high"]
    for i in range(n):
        seed = seed_start + i
        sim = rng.choice(sims)
        trials.append(h.generate_needle_trial(seed=seed, similarity=sim))
    return trials


def build_format_trials(n: int, seed_start: int = 40000) -> List[LiveTrial]:
    h = LiveExperimentHarness()
    trials = []
    rng = random.Random(seed_start)
    formats = ["markdown_prose", "markdown_table", "json", "xml", "yaml", "plain_text"]
    for i in range(n):
        seed = seed_start + i
        fmt = rng.choice(formats)
        trials.append(h.generate_format_trial(seed=seed, format_type=fmt))
    return trials


def build_multihop_trials(n: int, seed_start: int = 50000) -> List[LiveTrial]:
    h = LiveExperimentHarness()
    trials = []
    rng = random.Random(seed_start)
    for i in range(n):
        seed = seed_start + i
        hops = rng.choice([2, 3, 4, 5])
        trials.append(h.generate_multihop_trial(seed=seed, num_hops=hops))
    return trials


def build_adversarial_trials() -> List[LiveTrial]:
    """Adversarial set is fixed (12 hand-crafted probes)."""
    from edge_case_probes import generate_all_probes  # noqa: WPS433
    probes = generate_all_probes()
    out: List[LiveTrial] = []
    for p in probes:
        out.append(LiveTrial(
            trial_id=f"ADV_{p.probe_id}",
            experiment_type="adversarial",
            stimulus=p.document,
            question=p.question,
            expected_answer=p.correct_answer,
            metadata={
                "category": p.category,
                "difficulty": p.difficulty,
                "target_weakness": p.target_weakness,
                "trap_answer": p.trap_answer,
            },
        ))
    return out


EXPERIMENT_BUILDERS: Dict[str, Callable[[int], List[LiveTrial]]] = {
    "hierarchy": lambda n: build_hierarchy_trials(n),
    "needle": lambda n: build_needle_trials(n),
    "format": lambda n: build_format_trials(n),
    "multihop": lambda n: build_multihop_trials(n),
    "adversarial": lambda n: build_adversarial_trials(),
}


def run_suite(
    experiment: str,
    n: int,
    model: str,
    max_tokens: int = 256,
    concurrency: int = 6,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    builder = EXPERIMENT_BUILDERS[experiment]
    trials = builder(n)
    print(f"[{experiment}] Built {len(trials)} trials. Running on {model} with {concurrency}x concurrency...")
    client = _build_client()
    results: List[APIResult] = []
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(_run_one, client, t, model, max_tokens): t for t in trials}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            mark = "OK " if r.is_correct else ("ERR" if r.error else "MIS")
            preview = r.actual[:80].encode("ascii", "replace").decode("ascii")
            print(f"  [{mark}] {r.trial_id} ({r.latency_ms}ms) -> {preview!r}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    by_id = {r.trial_id: r for r in results}
    ordered = [by_id[t.trial_id] for t in trials if t.trial_id in by_id]

    raw_path = output_dir / f"{experiment}_{model}_{timestamp}.jsonl"
    with raw_path.open("w") as f:
        for r in ordered:
            f.write(json.dumps(asdict(r)) + "\n")

    summary = _summarize(experiment, model, ordered)
    summary_path = output_dir / f"{experiment}_{model}_{timestamp}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"[{experiment}] Saved {raw_path.name} + summary. Accuracy: {summary['overall']['accuracy']:.1%}")
    return summary


def _summarize(experiment: str, model: str, results: List[APIResult]) -> Dict[str, Any]:
    n = len(results)
    correct = sum(1 for r in results if r.is_correct)
    errors = sum(1 for r in results if r.error)
    total_in = sum(r.input_tokens for r in results)
    total_out = sum(r.output_tokens for r in results)
    avg_latency = sum(r.latency_ms for r in results) / max(n, 1)

    # Stratified breakdowns
    strata: Dict[str, Dict[str, Dict[str, int]]] = {}
    for r in results:
        for key, val in r.metadata.items():
            if not isinstance(val, (str, int, float, bool)):
                continue
            bucket = strata.setdefault(key, {})
            cell = bucket.setdefault(str(val), {"n": 0, "correct": 0})
            cell["n"] += 1
            if r.is_correct:
                cell["correct"] += 1
    for key, bucket in strata.items():
        for val, cell in bucket.items():
            cell["accuracy"] = cell["correct"] / cell["n"] if cell["n"] else 0.0

    return {
        "experiment": experiment,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "overall": {
            "n": n,
            "correct": correct,
            "errors": errors,
            "accuracy": correct / n if n else 0.0,
            "avg_latency_ms": round(avg_latency, 1),
            "total_input_tokens": total_in,
            "total_output_tokens": total_out,
        },
        "strata": strata,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live experiments against the Anthropic API.")
    parser.add_argument("--experiment", "-e", required=True,
                        choices=list(EXPERIMENT_BUILDERS.keys()) + ["all"],
                        help="Which suite to run")
    parser.add_argument("--trials", "-n", type=int, default=20,
                        help="Trials per suite (ignored for adversarial — fixed at 12)")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    suites = list(EXPERIMENT_BUILDERS) if args.experiment == "all" else [args.experiment]
    summaries: List[Dict[str, Any]] = []
    for suite in suites:
        summaries.append(run_suite(
            experiment=suite,
            n=args.trials,
            model=args.model,
            max_tokens=args.max_tokens,
            concurrency=args.concurrency,
            output_dir=Path(args.output_dir),
        ))

    # Cross-suite roll-up
    if len(summaries) > 1:
        roll = {
            "model": args.model,
            "timestamp": datetime.now().isoformat(),
            "suites": [s["overall"] | {"experiment": s["experiment"]} for s in summaries],
        }
        rollup_path = Path(args.output_dir) / f"rollup_{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        rollup_path.write_text(json.dumps(roll, indent=2))
        print(f"\nRoll-up saved to {rollup_path.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
