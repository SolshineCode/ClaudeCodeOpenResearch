"""
Multi-hop depth sweep — using the ExtendedMultiHopGenerator, run trials
at hop counts 3, 5, 7, 9, 11 to find where multi-hop accuracy actually
breaks. Baseline runs in PR #4 saturated through 5 hops because the
shipped generator caps there silently.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'analysis'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'reasoning'))

from live_harness import LiveTrial  # noqa: E402
from live_api_runner import _build_client, _run_one, _summarize, DEFAULT_OUTPUT_DIR  # noqa: E402
from extended_multihop import ExtendedMultiHopGenerator  # noqa: E402


def build(hops_list: List[int], reps: int, seed_start: int = 900000,
          chain_type: str = 'explicit') -> List[LiveTrial]:
    trials = []
    seed = seed_start
    for h in hops_list:
        for rep in range(reps):
            g = ExtendedMultiHopGenerator(seed=seed, domain='organization')
            doc, chain = g.generate_reasoning_chain(num_hops=h, chain_type=chain_type)
            rendered = g.render_markdown(doc)
            trials.append(LiveTrial(
                trial_id=f"MHX_h{h:02d}_r{rep}_s{seed}",
                experiment_type="multihop_extended",
                stimulus=rendered,
                question=chain.question,
                expected_answer=chain.answer,
                metadata={'num_hops': h, 'chain_type': chain_type, 'rep': rep},
            ))
            seed += 1
    return trials


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hops', default='3,5,7,9,11')
    parser.add_argument('--reps', type=int, default=4)
    parser.add_argument('--chain-type', default='explicit',
                        choices=['explicit', 'implicit', 'mixed'])
    parser.add_argument('--model', default='claude-haiku-4-5')
    parser.add_argument('--max-tokens', type=int, default=512)
    parser.add_argument('--concurrency', type=int, default=6)
    args = parser.parse_args()

    hops = [int(x) for x in args.hops.split(',')]
    trials = build(hops, args.reps, chain_type=args.chain_type)
    print(f"Built {len(trials)} trials over hops={hops}, "
          f"chain_type={args.chain_type}, reps={args.reps}.")

    client = _build_client()
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(_run_one, client, t, args.model, args.max_tokens): t
                   for t in trials}
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            mark = "OK " if r.is_correct else ("ERR" if r.error else "MIS")
            preview = r.actual[:50].encode('ascii', 'replace').decode('ascii')
            print(f"  [{mark}] {r.trial_id} -> {preview!r} (expected {r.expected})")

    by_hops = {}
    for r in results:
        h = r.metadata['num_hops']
        cell = by_hops.setdefault(h, {'n': 0, 'correct': 0})
        cell['n'] += 1
        if r.is_correct:
            cell['correct'] += 1

    out_dir = DEFAULT_OUTPUT_DIR
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw = out_dir / f"multihop_extended_{args.model}_{args.chain_type}_{timestamp}.jsonl"
    with raw.open('w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(asdict(r)) + '\n')
    summary = {
        'experiment': 'multihop_extended',
        'model': args.model,
        'chain_type': args.chain_type,
        'hops': hops,
        'reps': args.reps,
        'overall_accuracy': sum(1 for r in results if r.is_correct) / len(results),
        'by_hops': {str(h): {**c, 'accuracy': c['correct'] / c['n']}
                    for h, c in sorted(by_hops.items())},
    }
    (out_dir / f"multihop_extended_{args.model}_{args.chain_type}_{timestamp}_summary.json"
     ).write_text(json.dumps(summary, indent=2), encoding='utf-8')

    print()
    print(f"=== Multi-hop depth sweep ({args.chain_type} chains, "
          f"model={args.model}) ===")
    for h in hops:
        cell = by_hops.get(h, {'n': 0, 'correct': 0})
        if cell['n']:
            bar = '#' * int(cell['correct'] / cell['n'] * 20)
            print(f"  hops={h:>2d}  {cell['correct']}/{cell['n']} "
                  f"({cell['correct']/cell['n']:.0%})   |{bar:<20}|")


if __name__ == '__main__':
    main()
