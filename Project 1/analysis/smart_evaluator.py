"""
Smart evaluator with canonical-answer extraction.

The default LiveExperimentHarness evaluator does substring containment, which
falsely flags many correct adversarial responses as wrong. Adversarial probes
have ground-truth answers like 'Phase 1 (or arguably document-level/none)' —
the model legitimately answers 'Phase 1' and gets marked incorrect.

This module:
  - Strips parenthetical / qualifying tails from expected answers to recover
    the canonical short-form answer.
  - Re-evaluates a JSONL of trial results against the smarter rule.
  - Prints a re-scored summary with delta vs original.

Usage:
    python analysis/smart_evaluator.py data/results/live/adversarial_*.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, List, Tuple


_PAREN_TAIL = re.compile(r"\s*[\(\[].*$")
_TRAILING_NOTE = re.compile(r"\s+(?:or|but|unless|except|–|—|-)\s.*$", re.IGNORECASE)


def canonical(expected: Any) -> List[str]:
    """Return acceptable canonical short-form variants of an expected answer."""
    if expected is None:
        return [""]
    if isinstance(expected, (int, float)):
        return [str(expected)]
    if isinstance(expected, bool):
        return ["yes" if expected else "no"]
    if isinstance(expected, list):
        # For lists, each list element gets canonicalized; we keep them all.
        out: List[str] = []
        for item in expected:
            out.extend(canonical(item))
        return out
    s = str(expected).strip()
    candidates = {s}
    # Strip trailing parenthetical
    short = _PAREN_TAIL.sub("", s).strip()
    if short:
        candidates.add(short)
    # Strip trailing qualification clauses like "No (unless ...)" or "X — but ..."
    short2 = _TRAILING_NOTE.sub("", short).strip()
    if short2:
        candidates.add(short2)
    return [c for c in candidates if c]


def smart_match(expected: Any, response: str) -> bool:
    if response is None:
        return False
    resp = response.strip().lower()
    for variant in canonical(expected):
        v = variant.lower()
        if not v:
            continue
        if v in resp:
            return True
        # token-level match: every word in canonical answer appears
        toks = [t for t in re.split(r"\W+", v) if t]
        if toks and all(t in resp for t in toks):
            return True
    return False


def rescore(jsonl_path: Path) -> Tuple[List[dict], dict]:
    rows = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line.strip()]
    by_diff: dict = {}
    by_cat: dict = {}
    n = len(rows)
    orig_correct = sum(1 for r in rows if r["is_correct"])
    smart_correct = 0
    flips: List[dict] = []
    for r in rows:
        smart = smart_match(r["expected"], r["actual"])
        if smart:
            smart_correct += 1
        if smart != r["is_correct"]:
            flips.append({
                "trial_id": r["trial_id"],
                "expected": r["expected"],
                "actual_preview": r["actual"][:120],
                "original": r["is_correct"],
                "smart": smart,
            })
        meta = r.get("metadata", {}) or {}
        if "difficulty" in meta:
            cell = by_diff.setdefault(meta["difficulty"], {"n": 0, "orig": 0, "smart": 0})
            cell["n"] += 1
            cell["orig"] += int(r["is_correct"])
            cell["smart"] += int(smart)
        if "category" in meta:
            cell = by_cat.setdefault(meta["category"], {"n": 0, "orig": 0, "smart": 0})
            cell["n"] += 1
            cell["orig"] += int(r["is_correct"])
            cell["smart"] += int(smart)
    summary = {
        "file": jsonl_path.name,
        "n": n,
        "original_accuracy": orig_correct / n if n else 0.0,
        "smart_accuracy": smart_correct / n if n else 0.0,
        "flips": flips,
        "by_difficulty": by_diff,
        "by_category": by_cat,
    }
    return rows, summary


def main(argv: Iterable[str] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--write", action="store_true", help="Write *_smart.json next to source")
    args = parser.parse_args(argv)
    for p in args.paths:
        _, summary = rescore(p)
        print(json.dumps(summary, indent=2, default=str))
        if args.write:
            out = p.with_name(p.stem + "_smart.json")
            out.write_text(json.dumps(summary, indent=2, default=str))
            print(f"  -> wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
