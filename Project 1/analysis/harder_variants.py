"""
Harder Variants — push the experiment difficulty past where Haiku 4.5
saturates. Default suites mostly hit the ceiling on Haiku, masking real
capability boundaries. These variants:

  - Hierarchy: deeper trees (depths 5-6) with count probes only — the
    weakest sub-type observed in baseline.
  - Needle: needle placed at depth 1 (subsection) with 3 high-similarity
    distractors at multiple depths.
  - Multihop: 5-hop chains using implicit / mixed link styles. The
    underlying generator silently caps at len(domain['entities'])
    distinct entity types (5 in the default domain), so 6+ hops produce
    broken trials; we run 5 to stay within that cap and lift difficulty
    via the link-style choice instead.
  - Format: comparison + aggregate probes only (entity_property too easy)
    over 6 entities (vs default 4).

Writes results in the same shape as live_api_runner so the analysis
pipeline can ingest them.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'structural'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'attention'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'format'))
sys.path.insert(0, str(PROJECT_ROOT / 'experiments' / 'reasoning'))
sys.path.insert(0, str(PROJECT_ROOT / 'analysis'))

from live_harness import LiveTrial  # noqa: E402
from live_api_runner import _build_client, _run_one, _summarize, DEFAULT_OUTPUT_DIR  # noqa: E402
from concurrent.futures import ThreadPoolExecutor, as_completed  # noqa: E402


def hard_hierarchy_trials(n: int, seed_start: int = 60000) -> List[LiveTrial]:
    """Deep trees (depth 5 or 6) with count_probe only (weakest sub-type)."""
    from document_generator import HierarchicalDocumentGenerator, DocumentRenderer, ProbeGenerator
    rng = random.Random(seed_start)
    trials = []
    seed = seed_start
    while len(trials) < n:
        depth = rng.choice([5, 6])
        gen = HierarchicalDocumentGenerator(seed=seed)
        # Tighter branching to keep documents under ~30k tokens
        root, ground_truth = gen.generate_tree(max_depth=depth, branching_factor=(1, 2))
        renderer = DocumentRenderer()
        doc = renderer.to_markdown(root)
        probe = ProbeGenerator.count_probe(ground_truth)
        if probe is None:
            seed += 1
            continue
        trials.append(LiveTrial(
            trial_id=f"HARD_HP_{seed}_d{depth}",
            experiment_type="hierarchy_hard",
            stimulus=doc,
            question=probe['question'],
            expected_answer=probe['answer'],
            metadata={
                'depth': depth,
                'probe_type': probe['type'],
                'variant': 'hard_count',
                'total_nodes': ground_truth.to_dict()['total_nodes'],
            },
        ))
        seed += 1
    return trials


def hard_needle_trials(n: int, seed_start: int = 70000) -> List[LiveTrial]:
    """Needle placed at depth 1 (subsection) with high-similarity distractors."""
    from needle_in_structure import (
        NeedleInStructureGenerator, StructuralPosition, DistractorConfig,
    )
    rng = random.Random(seed_start)
    trials = []
    for i in range(n):
        seed = seed_start + i
        g = NeedleInStructureGenerator(seed=seed)
        template = rng.choice(g.FACT_TEMPLATES)
        ctx = f"Project-{seed:04d}"
        needle = g._fill_template(template, ctx)
        # Place at depth 1 (subsection)
        needle_pos = StructuralPosition(depth=1, section_index=rng.randint(2, 6),
                                         local_position=rng.choice(['start', 'middle', 'end']))
        # High-similarity distractors at multiple depths
        dist_positions = [
            StructuralPosition(depth=0, section_index=1, local_position='end'),
            StructuralPosition(depth=1, section_index=4, local_position='middle'),
            StructuralPosition(depth=0, section_index=7, local_position='start'),
        ]
        dist_cfg = DistractorConfig(num_distractors=3, similarity_level='high', positions=dist_positions)
        doc = g.generate_structured_document(
            needle=needle, needle_position=needle_pos, distractor_config=dist_cfg,
            total_sections=10, format='markdown',
        )
        trials.append(LiveTrial(
            trial_id=f"HARD_NIS_{seed}",
            experiment_type="needle_hard",
            stimulus=doc['document'],
            question=f"What is the {needle.needle_key}?",
            expected_answer=needle.needle_value,
            metadata={
                'similarity': 'high',
                'needle_depth': 1,
                'num_distractors': 3,
                'local_position': needle_pos.local_position,
            },
        ))
    return trials


def hard_multihop_trials(n: int, seed_start: int = 80000) -> List[LiveTrial]:
    """5-hop chains with implicit (and mixed) linking — pushes the upper end
    of what the generator supports."""
    from multi_hop_document import MultiHopDocumentGenerator
    rng = random.Random(seed_start)
    trials = []
    for i in range(n):
        seed = seed_start + i
        hops = 5
        chain_type = rng.choice(['implicit', 'mixed'])
        g = MultiHopDocumentGenerator(seed=seed)
        doc, chain = g.generate_reasoning_chain(num_hops=hops, chain_type=chain_type)
        rendered = g.render_markdown(doc)
        trials.append(LiveTrial(
            trial_id=f"HARD_MH_{seed}_{hops}h_{chain_type}",
            experiment_type="multihop_hard",
            stimulus=rendered,
            question=chain.question,
            expected_answer=chain.answer,
            metadata={'num_hops': hops, 'chain_type': chain_type, 'variant': f'hard_{chain_type}'},
        ))
    return trials


def hard_format_trials(n: int, seed_start: int = 90000) -> List[LiveTrial]:
    """Comparison + aggregate probes across all 6 formats."""
    from isomorphic_content import IsomorphicContentGenerator, IsomorphicProbeGenerator
    rng = random.Random(seed_start)
    fmts = ["markdown_prose", "markdown_table", "json", "xml", "yaml", "plain_text"]
    probe_kinds = ["comparison", "aggregate"]
    trials = []
    for i in range(n):
        seed = seed_start + i
        g = IsomorphicContentGenerator(seed=seed)
        content = g.generate_semantic_content(num_entities=6)  # bigger
        fmt = rng.choice(fmts)
        renderer = {
            "markdown_prose": g.render_markdown_prose,
            "markdown_table": g.render_markdown_table,
            "json": g.render_json,
            "xml": g.render_xml,
            "yaml": g.render_yaml,
            "plain_text": g.render_plain_text,
        }[fmt]
        rendered = renderer(content)
        pg = IsomorphicProbeGenerator()
        kind = rng.choice(probe_kinds)
        probe = pg.comparison_probe(content) if kind == "comparison" else pg.aggregate_probe(content)
        trials.append(LiveTrial(
            trial_id=f"HARD_ISO_{seed}_{fmt}_{kind}",
            experiment_type="format_hard",
            stimulus=rendered,
            question=probe['question'],
            expected_answer=probe['answer'],
            metadata={'format': fmt, 'probe_type': probe['type'], 'num_entities': 6},
        ))
    return trials


BUILDERS = {
    'hierarchy_hard': hard_hierarchy_trials,
    'needle_hard': hard_needle_trials,
    'multihop_hard': hard_multihop_trials,
    'format_hard': hard_format_trials,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment', '-e', required=True,
                        choices=list(BUILDERS) + ['all'])
    parser.add_argument('--trials', '-n', type=int, default=20)
    parser.add_argument('--model', '-m', default='claude-haiku-4-5')
    parser.add_argument('--max-tokens', type=int, default=512)
    parser.add_argument('--concurrency', type=int, default=6)
    args = parser.parse_args()

    suites = list(BUILDERS) if args.experiment == 'all' else [args.experiment]
    client = _build_client()
    DEFAULT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for s in suites:
        print(f"\n=== {s} (n={args.trials}, model={args.model}) ===")
        trials = BUILDERS[s](args.trials)
        results = []
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(_run_one, client, t, args.model, args.max_tokens): t for t in trials}
            for fut in as_completed(futures):
                r = fut.result()
                results.append(r)
                mark = "OK " if r.is_correct else ("ERR" if r.error else "MIS")
                preview = r.actual[:80].encode('ascii', 'replace').decode('ascii')
                print(f"  [{mark}] {r.trial_id} ({r.latency_ms}ms) -> {preview!r}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ordered = {r.trial_id: r for r in results}
        ordered = [ordered[t.trial_id] for t in trials if t.trial_id in ordered]
        raw = DEFAULT_OUTPUT_DIR / f"{s}_{args.model}_{timestamp}.jsonl"
        with raw.open('w') as f:
            for r in ordered:
                f.write(json.dumps(asdict(r)) + "\n")
        summary = _summarize(s, args.model, ordered)
        (DEFAULT_OUTPUT_DIR / f"{s}_{args.model}_{timestamp}_summary.json").write_text(
            json.dumps(summary, indent=2)
        )
        print(f"[{s}] accuracy: {summary['overall']['accuracy']:.1%} ({summary['overall']['n']} trials)")


if __name__ == '__main__':
    main()
