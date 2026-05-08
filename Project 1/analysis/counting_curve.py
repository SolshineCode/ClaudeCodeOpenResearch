"""
Counting Magnitude Dose-Response Curve

Tests hypothesis H1.4 ("Counting follows Weber's law") by varying the
*magnitude* of the count to be performed at *fixed* depth. The default
hierarchy generator gives whatever depth+magnitude land randomly; this
script forces a sweep.

Approach: build documents with a single root and exactly k leaf children
(k ∈ {3, 5, 10, 20, 40, 80}), all at depth 1. Ask the model to count
the leaves. The structure-recognition load is identical across k; the
only varying factor is the magnitude of the count.

If H1.4 holds (Weber's law), accuracy should degrade smoothly with
log(k) and errors should scale proportionally with magnitude.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'analysis'))
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))

from live_harness import LiveTrial  # noqa: E402
from live_api_runner import _build_client, _run_one, _summarize, DEFAULT_OUTPUT_DIR  # noqa: E402


def build_count_doc(k: int, seed: int) -> str:
    """A simple document with exactly k labeled leaf sections under one root."""
    import random
    rng = random.Random(seed)
    lines = ["# Root Document", ""]
    lines.append("This document describes several components. Each component has a brief paragraph.")
    lines.append("")
    for i in range(k):
        section_id = f"sec-{seed:05d}-{i:03d}"
        topic = rng.choice([
            "configuration", "deployment", "monitoring", "logging",
            "authentication", "caching", "indexing", "scheduling",
            "validation", "metrics", "throttling", "diagnostics",
        ])
        lines.append(f"## Section {i + 1} [{section_id}]")
        lines.append("")
        # ~30 token filler per section
        lines.append(
            f"This section covers {topic} concerns and outlines the relevant procedures. "
            f"It establishes the {topic} contract used elsewhere."
        )
        lines.append("")
    return "\n".join(lines)


def build_depth_count_doc(target_depth: int, k_at_target: int, seed: int) -> str:
    """A document where the COUNT-AT-DEPTH question has answer k_at_target.

    Builds a deterministic spine of depth `target_depth` with exactly
    `k_at_target` sibling sections at depth `target_depth`. Other depths
    have a single chain of headings — so the only level with multiple
    siblings is the target.
    """
    import random
    rng = random.Random(seed)
    lines = []

    def heading(level: int, label: str) -> str:
        return f"{'#' * (level + 1)} {label}"

    # Build chain from depth 0 down to target_depth - 1 (single child each)
    lines.append(heading(0, f"Root [r-{seed:05d}]"))
    lines.append("Top-level overview paragraph providing brief introduction.")
    lines.append("")
    for d in range(1, target_depth):
        topic = rng.choice(["alpha", "beta", "gamma", "delta", "epsilon", "zeta"])
        lines.append(heading(d, f"{topic.capitalize()} branch [{topic}-{seed:05d}-{d}]"))
        lines.append(f"Intermediate {topic} discussion at depth {d}, paragraph filler.")
        lines.append("")
    # At target depth: k_at_target sibling sections, all leaves
    for i in range(k_at_target):
        topic = rng.choice([
            "configuration", "deployment", "monitoring", "logging",
            "authentication", "caching", "indexing", "scheduling",
        ])
        lines.append(heading(target_depth, f"{topic.capitalize()} [t-{seed:05d}-{i:03d}]"))
        lines.append(
            f"Leaf section about {topic}. Brief description of role and scope."
        )
        lines.append("")
    return "\n".join(lines)


def build_count_trials(magnitudes: List[int], reps_per_mag: int, seed_start: int = 600000) -> List[LiveTrial]:
    trials = []
    seed = seed_start
    for k in magnitudes:
        for rep in range(reps_per_mag):
            doc = build_count_doc(k, seed)
            trials.append(LiveTrial(
                trial_id=f"COUNT_k{k}_r{rep}_s{seed}",
                experiment_type="count_curve",
                stimulus=doc,
                question="How many top-level sections are in this document? (Sections beginning with `## Section N`. Provide a single integer.)",
                expected_answer=k,
                metadata={'magnitude': k, 'rep': rep},
            ))
            seed += 1
    return trials


def build_depth_count_trials(target_depths: List[int], k: int, reps: int,
                              seed_start: int = 700000) -> List[LiveTrial]:
    trials = []
    seed = seed_start
    for d in target_depths:
        for rep in range(reps):
            doc = build_depth_count_doc(d, k, seed)
            trials.append(LiveTrial(
                trial_id=f"DEPTHCOUNT_d{d}_k{k}_r{rep}_s{seed}",
                experiment_type="depth_count_curve",
                stimulus=doc,
                question=f"How many sections are at depth level {d}? "
                         f"(Depth 0 = root with one #, depth 1 = ##, etc.) "
                         f"Provide a single integer.",
                expected_answer=k,
                metadata={'target_depth': d, 'k': k, 'rep': rep},
            ))
            seed += 1
    return trials


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['magnitude', 'depth'], default='magnitude')
    parser.add_argument('--magnitudes', default='3,5,10,20,40,80,160',
                        help='comma-separated counts to test (magnitude mode)')
    parser.add_argument('--depths', default='1,2,3,4,5,6,7',
                        help='comma-separated target depths to test (depth mode)')
    parser.add_argument('--k-at-depth', type=int, default=8,
                        help='number of siblings at the target depth (depth mode)')
    parser.add_argument('--reps', type=int, default=4)
    parser.add_argument('--model', default='claude-haiku-4-5')
    parser.add_argument('--concurrency', type=int, default=6)
    parser.add_argument('--max-tokens', type=int, default=64)
    args = parser.parse_args()

    if args.mode == 'magnitude':
        mags = [int(x) for x in args.magnitudes.split(',')]
        trials = build_count_trials(mags, args.reps)
        print(f"Built {len(trials)} magnitude-mode trials over k={mags}, {args.reps} reps each.")
        sweep_axis_name = 'magnitude'
        sweep_values = mags
    else:
        depths = [int(x) for x in args.depths.split(',')]
        trials = build_depth_count_trials(depths, args.k_at_depth, args.reps)
        print(f"Built {len(trials)} depth-mode trials over depths {depths}, k={args.k_at_depth}, "
              f"{args.reps} reps each.")
        sweep_axis_name = 'target_depth'
        sweep_values = depths

    client = _build_client()
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(_run_one, client, t, args.model, args.max_tokens): t for t in trials}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            mark = "OK " if r.is_correct else ("ERR" if r.error else "MIS")
            preview = r.actual[:60].encode('ascii', 'replace').decode('ascii')
            print(f"  [{mark}] {r.trial_id} -> {preview!r} (expected {r.expected})")

    import re
    by_axis = {}
    for r in results:
        axis_val = r.metadata.get(sweep_axis_name) or r.metadata.get('magnitude')
        by_axis.setdefault(axis_val, {'n': 0, 'correct': 0, 'errors': []})
        by_axis[axis_val]['n'] += 1
        if r.is_correct:
            by_axis[axis_val]['correct'] += 1
        else:
            m = re.search(r'-?\d+', r.actual)
            if m:
                guess = int(m.group())
                expected = r.expected if isinstance(r.expected, int) else 0
                by_axis[axis_val]['errors'].append(guess - expected)

    summary = {
        'experiment': f'counting_curve_{args.mode}',
        'model': args.model,
        'timestamp': datetime.now().isoformat(),
        'sweep_axis': sweep_axis_name,
        'sweep_values': sweep_values,
        'reps': args.reps,
        'overall_accuracy': sum(1 for r in results if r.is_correct) / len(results),
        f'by_{sweep_axis_name}': {
            str(k): {
                'n': v['n'],
                'correct': v['correct'],
                'accuracy': v['correct'] / v['n'],
                'mean_signed_error': (sum(v['errors']) / len(v['errors'])) if v['errors'] else None,
                'errors': v['errors'],
            }
            for k, v in sorted(by_axis.items())
        },
    }
    out_dir = DEFAULT_OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw = out_dir / f"count_curve_{args.mode}_{args.model}_{timestamp}.jsonl"
    with raw.open('w') as f:
        for r in results:
            f.write(json.dumps(asdict(r)) + '\n')
    (out_dir / f"count_curve_{args.mode}_{args.model}_{timestamp}_summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    print()
    print(f"=== Counting curve ({args.mode} mode) ===")
    cells = summary[f'by_{sweep_axis_name}']
    for k in sweep_values:
        cell = cells[str(k)]
        bar = '#' * int(cell['accuracy'] * 20)
        label = f"k={k:4d}" if args.mode == 'magnitude' else f"depth={k:2d}"
        print(f"  {label}  acc={cell['accuracy']:5.1%}  mean_err={cell['mean_signed_error']!s:>7}   |{bar:<20}|")


if __name__ == '__main__':
    main()
