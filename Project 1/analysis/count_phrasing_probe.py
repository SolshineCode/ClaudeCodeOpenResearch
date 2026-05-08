"""
Phrasing probe — does rewording the depth-count question recover Haiku 4.5's
performance at depths 5–6?

The depth-count curve showed a sharp 0% boundary at depths 5–6 with the
question "How many sections are at depth level d?" The model returns "1",
suggesting it misreads the question as "how many sections exist at this
single depth-level slot in the document spine" rather than "count siblings".

This probe holds the *document* identical to the failing trials and only
varies the question wording, isolating intent-misinterpretation from
counting capability per se.

Three phrasings:
  - 'level':  "How many sections are at depth level d?" (original)
  - 'hashes': "How many headings start with exactly d+1 '#' characters?"
  - 'children':"List the headings of all sections that are direct
                children of the [parent name] section, then count them."
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'analysis'))
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))

from live_harness import LiveTrial  # noqa: E402
from live_api_runner import _build_client, _run_one, DEFAULT_OUTPUT_DIR  # noqa: E402
from counting_curve import build_depth_count_doc  # noqa: E402


PHRASINGS = {
    'level': "How many sections are at depth level {d}? "
             "(Depth 0 = root with one #, depth 1 = ##, etc.) "
             "Provide a single integer.",
    'hashes': "How many headings in this document start with exactly "
              "{hashes} '#' characters? Provide a single integer.",
    'count_leaves': "Count the number of leaf-level headings (the deepest "
                    "level used in this document). Provide a single integer.",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--depths', default='3,4,5,6,7')
    parser.add_argument('--k', type=int, default=8)
    parser.add_argument('--reps', type=int, default=4)
    parser.add_argument('--phrasings', default='level,hashes,count_leaves')
    parser.add_argument('--model', default='claude-haiku-4-5')
    parser.add_argument('--concurrency', type=int, default=6)
    parser.add_argument('--max-tokens', type=int, default=128)
    args = parser.parse_args()

    depths = [int(x) for x in args.depths.split(',')]
    phrasings = [p.strip() for p in args.phrasings.split(',')]
    seed_start = 800000

    trials: List[LiveTrial] = []
    seed = seed_start
    for d in depths:
        for rep in range(args.reps):
            doc = build_depth_count_doc(d, args.k, seed)
            for phr in phrasings:
                tmpl = PHRASINGS[phr]
                question = tmpl.format(d=d, hashes='#' * (d + 1))
                trials.append(LiveTrial(
                    trial_id=f"PHR_{phr}_d{d}_r{rep}_s{seed}",
                    experiment_type="phrasing_probe",
                    stimulus=doc,
                    question=question,
                    expected_answer=args.k,
                    metadata={'phrasing': phr, 'target_depth': d, 'k': args.k, 'rep': rep},
                ))
            seed += 1

    print(f"Built {len(trials)} trials over depths {depths} x phrasings {phrasings}, "
          f"reps={args.reps}.")
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

    # Aggregate by (phrasing, depth)
    table = {}
    for r in results:
        key = (r.metadata['phrasing'], r.metadata['target_depth'])
        cell = table.setdefault(key, {'n': 0, 'correct': 0})
        cell['n'] += 1
        if r.is_correct:
            cell['correct'] += 1

    out_dir = DEFAULT_OUTPUT_DIR
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw = out_dir / f"phrasing_probe_{args.model}_{timestamp}.jsonl"
    with raw.open('w') as f:
        for r in results:
            f.write(json.dumps(asdict(r)) + '\n')
    summary = {
        'experiment': 'count_phrasing_probe',
        'model': args.model,
        'k': args.k,
        'reps': args.reps,
        'table': {f'{p}|d={d}': {'n': c['n'], 'correct': c['correct'],
                                  'accuracy': c['correct'] / c['n']}
                  for (p, d), c in sorted(table.items())},
    }
    (out_dir / f"phrasing_probe_{args.model}_{timestamp}_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    print()
    print(f"=== Count Phrasing Probe (k={args.k}, model={args.model}) ===")
    print(f"  {'depth':>6} | " + " | ".join(f"{p:>14s}" for p in phrasings))
    print(f"  {'-' * 6} | " + " | ".join('-' * 14 for _ in phrasings))
    for d in depths:
        cells = []
        for p in phrasings:
            cell = table.get((p, d), {'n': 0, 'correct': 0})
            if cell['n']:
                cells.append(f"{cell['correct']}/{cell['n']} ({cell['correct']/cell['n']:.0%})")
            else:
                cells.append("—")
        print(f"  d={d:>4d} | " + " | ".join(f"{c:>14s}" for c in cells))


if __name__ == '__main__':
    main()
