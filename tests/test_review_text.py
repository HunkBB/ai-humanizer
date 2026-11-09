"""Behavioral checks for the local review helper; no external packages or services."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "academic-writing-humanizer/scripts/review_text.py"
SPEC = importlib.util.spec_from_file_location("review_text", SCRIPT)
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class ReviewTextTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, check=False)

    def test_audit_extracts_placeholders_dois_and_repeated_starts(self):
        text = ("I propose to study access. [VERIFY/data permission]\n\n"
                "I propose to compare plans. TODO: resolve [TBD] and {{sample_size}}.\n\n"
                "See https://doi.org/10.1000/example(foo). DOI: 10.1000/example(foo); "
                "and [source](https://doi.org/10.1016/j.test.2024.123). 中文研究。")
        result = review.audit_text(text, text.encode(), "fixture.md")
        self.assertEqual([p["text"] for p in result["unresolved_placeholders"]],
                         ["[VERIFY/data permission]", "TODO", "[TBD]", "{{sample_size}}"])
        self.assertEqual(result["unresolved_placeholders"][1]["line"], 3)
        self.assertEqual([d["text"] for d in result["doi_occurrences"]],
                         ["10.1000/example(foo)", "10.1000/example(foo)", "10.1016/j.test.2024.123"])
        self.assertEqual(result["doi_unique_count"], 2)
        self.assertEqual(result["repeated_paragraph_starts"],
                         [{"opening_words": "i propose to", "paragraph_numbers": [1, 2], "count": 2}])
        self.assertEqual(result["external_detector_test"], "Not performed by this program.")

    def test_review_markers_survive_parenthetical_notes_and_adjacency(self):
        text = ("[VERIFY] (check actual year)\n[VERIFY][CHECK]\n"
                "[CONFIRM: permission] (with data owner) [PENDING][INSERT: result]")
        result = review.audit_text(text, text.encode(), "markers.md")
        self.assertEqual([p["text"] for p in result["unresolved_placeholders"]],
                         ["[VERIFY]", "[VERIFY]", "[CHECK]", "[CONFIRM: permission]",
                          "[PENDING]", "[INSERT: result]"])

    def test_source_links_are_not_placeholders_but_unresolved_labels_are(self):
        text = ("Read [source](https://example.org) or [citation][paper].\n"
                "Still unresolved: [SOURCE] and [CITATION: page number].")
        result = review.audit_text(text, text.encode(), "links.md")
        self.assertEqual([p["text"] for p in result["unresolved_placeholders"]],
                         ["[SOURCE]", "[CITATION: page number]"])

    def test_cli_audit_preserves_utf8_bom_crlf_and_exact_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "中文.md"
            output = Path(directory) / "nested/audit.json"
            raw = b"\xef\xbb\xbf" + "研究 🧪.\r\n\r\n[VERIFY: source]\r\n".encode()
            source.write_bytes(raw)
            process = self.run_cli("audit", source, "--output", output)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(output.read_text())
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(result["source"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["counts"]["paragraphs"], 2)
            self.assertEqual(result["unresolved_placeholders"][0]["text"], "[VERIFY: source]")

    def test_cli_diff_escapes_html_and_reports_real_change(self):
        with tempfile.TemporaryDirectory() as directory:
            before = Path(directory) / '<img onerror="bad">.md'
            after = Path(directory) / "after.md"
            output = Path(directory) / "comparison.html"
            left = '<script>alert("x")</script> & 原文\nunchanged\n'.encode()
            right = '<img src=x onerror=alert(1)> 改稿 🧪\nunchanged\nadded\n'.encode()
            before.write_bytes(left)
            after.write_bytes(right)
            process = self.run_cli("diff", before, after, "--output", output)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = output.read_text()
            self.assertNotIn("<script>", result)
            self.assertNotIn("<img", result)
            self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; &amp; 原文", result)
            self.assertIn("&lt;img src=x onerror=alert(1)&gt; 改稿 🧪", result)
            self.assertIn("<del>", result)
            self.assertIn("<ins>", result)
            self.assertIn("1 removed; 2 added", result)
            self.assertIn(hashlib.sha256(left).hexdigest(), result)
            self.assertIn(hashlib.sha256(right).hexdigest(), result)
            self.assertIn('scope="col"', result)
            self.assertIn('Content-Security-Policy', result)
            self.assertEqual(before.read_bytes(), left)
            self.assertEqual(after.read_bytes(), right)

    def test_output_cannot_overwrite_input_or_hard_link(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.md"
            source.write_text("Do not modify.\n")
            link = Path(directory) / "linked.md"
            link.hardlink_to(source)
            for output in (source, link):
                with self.subTest(output=output.name):
                    process = self.run_cli("audit", source, "--output", output)
                    self.assertEqual(process.returncode, 2)
                    self.assertIn("must not overwrite", process.stderr)
                    self.assertEqual(source.read_text(), "Do not modify.\n")

    def test_empty_input_and_identical_diff(self):
        result = review.audit_text("", b"", "empty.txt")
        self.assertEqual(result["counts"]["words"], 0)
        self.assertEqual(result["sentence_word_lengths_heuristic"]["mean"], None)
        self.assertEqual(result["unresolved_placeholders"], [])
        report = review.diff_html("Same.\n", "Same.\n", b"Same.\n", b"Same.\n", "a", "b")
        self.assertIn("0 removed; 0 added", report)
        self.assertNotIn("<del>", report)
        self.assertNotIn("<ins>", report)

    def test_invalid_encoding_fails_without_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bad.txt"
            output = Path(directory) / "report.json"
            source.write_bytes(b"\xff\xfeinvalid")
            process = self.run_cli("audit", source, "--output", output)
            self.assertEqual(process.returncode, 2)
            self.assertFalse(output.exists())
            self.assertEqual(source.read_bytes(), b"\xff\xfeinvalid")


if __name__ == "__main__":
    unittest.main()
