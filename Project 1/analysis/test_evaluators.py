"""
Regression tests for the evaluator helpers.

Run from `Project 1/`:
    python -m analysis.test_evaluators
or:
    python analysis/test_evaluators.py

These tests target the false-positive risks that motivated the
lexical-edge guards: substring matches on short identifiers and short
numeric answers. They also lock in correct behavior on dollar amounts
and other answers that begin/end with non-word characters — those
break under a naive ``\\b`` boundary check.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'analysis'))

from live_api_runner import _word_in, _evaluate  # noqa: E402
from live_harness import LiveTrial  # noqa: E402
from smart_evaluator import smart_match, _lex_edge_in, canonical  # noqa: E402


class WordInTests(unittest.TestCase):
    """Substring search must reject 'inside-a-word' false positives but
    accept matches whose edges fall on non-word characters like '$'."""

    def test_short_int_no_subword(self):
        self.assertFalse(_word_in("1", "answer is 10"))
        self.assertFalse(_word_in("2", "version 23 of the spec"))

    def test_short_int_match(self):
        self.assertTrue(_word_in("1", "answer is 1"))
        self.assertTrue(_word_in("1", "answer is 1."))

    def test_node_id_no_subword(self):
        self.assertFalse(_word_in("node_1", "node_10 here"))

    def test_node_id_match(self):
        self.assertTrue(_word_in("node_1", "see node_1, ok"))

    def test_dollar_amount_match(self):
        self.assertTrue(_word_in("$82,000", "received $82,000 today"))
        self.assertTrue(_word_in("$82,000", "received $82,000."))
        self.assertTrue(_word_in("$540,891", "the total is $540,891."))

    def test_yes_inside_word(self):
        self.assertFalse(_word_in("yes", "eyes are open"))
        self.assertTrue(_word_in("yes", "yes that is correct"))

    def test_three_letter_no_subword(self):
        self.assertFalse(_word_in("foo", "foobar"))
        self.assertTrue(_word_in("foo", "foo bar"))


class EvaluateTests(unittest.TestCase):
    """End-to-end on _evaluate — same trial shape used by the live runner."""

    def _t(self, expected, response, want):
        trial = LiveTrial("T", "test", "", "", expected)
        self.assertEqual(_evaluate(trial, response), want, (expected, response))

    def test_int(self):
        self._t(1, "Answer: 1", True)
        self._t(1, "Answer: 10", False)
        self._t(8, "8 sections", True)

    def test_string(self):
        self._t("yes", "Yes, that is right", True)
        self._t("yes", "eyes wide open", False)

    def test_list(self):
        self._t(["node_1"], "Result: node_1", True)
        self._t(["node_1"], "Result: node_10", False)
        self._t(["a", "b"], "Both a and b are valid", True)

    def test_dollar(self):
        self._t("$82,000", "received $82,000.", True)
        self._t("$540,891", "total is $540,891 in profit", True)


class SmartMatchTests(unittest.TestCase):

    def test_canonical_strips_paren_tail(self):
        variants = canonical("Phase 1 (or arguably document-level/none)")
        self.assertIn("Phase 1", variants)

    def test_canonical_strips_qualifier(self):
        variants = canonical("No (unless senior with approval)")
        self.assertIn("No", variants)

    def test_smart_matches_short_form(self):
        self.assertTrue(smart_match("Phase 1 (or arguably document-level/none)", "Phase 1"))
        self.assertTrue(smart_match("$1.3M (corrected value)", "$1.3M"))
        self.assertTrue(smart_match("Q3 (her corrected statement)", "Q3"))

    def test_smart_does_not_match_substring_inside_word(self):
        # 'foo' should not match 'food' even with smart relaxation
        self.assertFalse(smart_match("foo", "food court"))

    def test_smart_lex_edge_helper(self):
        self.assertTrue(_lex_edge_in("$82,000", "received $82,000 today"))
        self.assertFalse(_lex_edge_in("1", "version 10"))


if __name__ == '__main__':
    unittest.main(verbosity=2)
