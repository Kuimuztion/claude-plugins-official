# SPDX-License-Identifier: Apache-2.0
"""Unit tests for hookify config_loader and rule_engine."""

import os
import sys
import tempfile
import unittest

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PLUGIN_DIR not in sys.path:
        sys.path.insert(0, PLUGIN_DIR)

from core.config_loader import Condition, Rule, extract_frontmatter
from core.rule_engine import RuleEngine


class TestHookifyConfigLoader(unittest.TestCase):
        """Tests for YAML frontmatter and condition parsing."""

        def test_inline_dict_with_regex_quantifier_commas(self):
                """Ensure regex quantifiers like {1,3} are not split."""
                md = (
                        "---\n"
                        "name: ip-check\n"
                        "enabled: true\n"
                        "event: bash\n"
                        "conditions:\n"
                        "  - field: command, operator: regex_match, "
                        'pattern: "\\b\\d{1,3}\\.\\d{1,3}\\b"\n'
                        "---\n"
                        "IP address matched.\n"
                )
                fm, msg = extract_frontmatter(md)
                rule = Rule.from_dict(fm, msg)
                self.assertEqual(len(rule.conditions), 1)
                cond = rule.conditions[0]
                self.assertEqual(cond.field, "command")
                self.assertEqual(cond.operator, "regex_match")
                self.assertEqual(cond.pattern, r"\b\d{1,3}\.\d{1,3}\b")

        def test_multiline_dict_starting_with_comma_pattern(self):
                """Ensure multiline condition with comma in first line works."""
                md = (
                        "---\n"
                        "name: quantifier-first\n"
                        "enabled: true\n"
                        "event: bash\n"
                        "conditions:\n"
                        '  - pattern: "a{1,2}"\n'
                        "    field: command\n"
                        "    operator: regex_match\n"
                        "---\n"
                        "Matched quantifier.\n"
                )
                fm, msg = extract_frontmatter(md)
                rule = Rule.from_dict(fm, msg)
                self.assertEqual(len(rule.conditions), 1)
                self.assertEqual(rule.conditions[0].pattern, "a{1,2}")
                self.assertEqual(rule.conditions[0].field, "command")


class TestHookifyRuleEngine(unittest.TestCase):
        """Tests for rule evaluation and hook output format."""

        def test_pre_vs_post_tool_use_blocking_format(self):
                """Verify PreToolUse denies and PostToolUse blocks."""
                rule = Rule(
                        name="no-rm",
                        enabled=True,
                        event="bash",
                        action="block",
                        conditions=[
                                Condition(
                                        field="command",
                                        operator="regex_match",
                                        pattern=r"rm\s+-rf",
                                )
                        ],
                        message="Blocked rm.",
                )
                engine = RuleEngine()
                pre_input = {
                        "hook_event_name": "PreToolUse",
                        "tool_name": "Bash",
                        "tool_input": {"command": "rm -rf /tmp/x"},
                }
                pre_res = engine.evaluate_rules([rule], pre_input)
                self.assertEqual(
                        pre_res["hookSpecificOutput"]["permissionDecision"],
                        "deny",
                )

                post_input = {
                        "hook_event_name": "PostToolUse",
                        "tool_name": "Bash",
                        "tool_input": {"command": "rm -rf /tmp/x"},
                }
                post_res = engine.evaluate_rules([rule], post_input)
                self.assertEqual(post_res.get("decision"), "block")
                self.assertIn("Blocked rm.", post_res.get("reason", ""))

        def test_transcript_read_is_cached(self):
                """Verify transcript file is read once per engine instance."""
                with tempfile.NamedTemporaryFile(
                        mode="w", encoding="utf-8", delete=False
                ) as tmp:
                        tmp.write("some transcript content")
                        tmp_path = tmp.name

                try:
                        r1 = Rule(
                                name="r1",
                                enabled=True,
                                event="stop",
                                conditions=[
                                        Condition(
                                                field="transcript",
                                                operator="contains",
                                                pattern="pytest",
                                        )
                                ],
                                message="m1",
                        )
                        r2 = Rule(
                                name="r2",
                                enabled=True,
                                event="stop",
                                conditions=[
                                        Condition(
                                                field="transcript",
                                                operator="not_contains",
                                                pattern="pytest",
                                        )
                                ],
                                message="m2",
                        )
                        engine = RuleEngine()
                        os.unlink(tmp_path)
                        engine._transcript_cache[tmp_path] = "cached text"
                        res = engine.evaluate_rules(
                                [r1, r2],
                                {
                                        "hook_event_name": "Stop",
                                        "transcript_path": tmp_path,
                                },
                        )
                        self.assertIn("m2", res.get("systemMessage", ""))
                finally:
                        if os.path.exists(tmp_path):
                                os.unlink(tmp_path)


if __name__ == "__main__":
        unittest.main()
