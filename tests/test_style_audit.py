"""Regression checks for candidate diagnostics; no external packages or models."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "academic-writing-humanizer/scripts/style_audit.py"
SPEC = importlib.util.spec_from_file_location("style_audit", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class StyleAuditTests(unittest.TestCase):
    def report(self, text, **kwargs):
        return audit.audit_text(text, text.encode(), "fixture.md", **kwargs)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, check=False)

    def test_technical_terms_and_normal_markdown_not_banned(self):
        text = ("# Analysis\n\nThe estimate was not significant. Exposure was associated with age. "
                "We used three models—each used the same sample.\n\n"
                "- The sample included 12 plans.\n- Follow-up lasted four quarters.\n\n"
                "See [source](https://doi.org/10.1000/test?download=true).")
        result = self.report(text)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["status"], "not_ai_detector")
        self.assertNotIn("score", result)

    def test_artifacts_have_locations_and_actionable_instructions(self):
        text = ("Here is your revised draft.\n\n[VERIFY] (data) [CHECK][TODO] [DATE] [URL] YYYY-MM-DD\n\n"
                "A finding. citeturn0search1 :contentReference[oaicite:0] [cite: 2]\n\n"
                "Let me know if you need edits. I hope this helps. As an AI, I cannot verify it.")
        result = self.report(text)
        categories = result["findings_by_category"]
        self.assertEqual(categories["assistant_residue"], 4)
        self.assertEqual(categories["unresolved_placeholder"], 6)
        self.assertGreaterEqual(categories["tool_citation_artifact"], 4)
        placeholders = [f for f in result["findings"] if f["category"] == "unresolved_placeholder"]
        self.assertTrue(all(f["line"] == 3 for f in placeholders))
        self.assertTrue(all(f["review_instruction"] for f in result["findings"]))

    def test_documented_tool_marker_families_and_literal_math(self):
        text = ('[span_1](start_span) [span_1](end_span) <grok-card data-id="a"> '
                'grok_render_citation_card_json 〖85†L261-269〗 [attached_file:1] '
                '[web:1] https://ppl-ai-file-upload.s3.amazonaws.com/test '
                ':::writing{variant="document"} oai_citation attributableIndex\n'
                'The result is x+1; an HTML <mark> can highlight text.')
        result = self.report(text)
        findings = [f for f in result["findings"] if f["category"] == "tool_citation_artifact"]
        self.assertEqual(len(findings), 11)
        self.assertTrue(all(f["line"] == 1 for f in findings))

    def test_partial_dates_bare_writing_blocks_and_url_placeholders(self):
        text = ("Due 2026-XX-XX, then 2026-11-XX or 2026-XX-07.\n"
                "INSERT_SOURCE_URL_01 INSERT_WEBSITE_URL_HERE\n"
                ":::writing\nThe proposal follows.\n")
        result = self.report(text)
        placeholders = [f["excerpt"] for f in result["findings"] if f["category"] == "unresolved_placeholder"]
        self.assertEqual(placeholders, ["2026-XX-XX", "2026-11-XX", "2026-XX-07",
                                        "INSERT_SOURCE_URL_01", "INSERT_WEBSITE_URL_HERE"])
        artifact = next(f for f in result["findings"] if f["category"] == "tool_citation_artifact")
        self.assertEqual(artifact["line"], 3)
        self.assertEqual(artifact["excerpt"], ":::writing")

    def test_genuine_dates_url_paths_and_quoted_prose_are_preserved(self):
        text = ('We collected observations on 2026-11-07 and 2025/06/03.\n\n'
                'The respondent wrote, “Here is your polished research proposal.”\n\n'
                'The protocol quotes "Let me know if symptoms persist".\n\n'
                'See https://example.org/docs/INSERT_SOURCE_URL_01 '
                'or https://example.org/help?term=INSERT_WEBSITE_URL_HERE .')
        self.assertEqual(self.report(text)["findings"], [])

    def test_delivery_phrasing_supports_polished_or_revised_proposals(self):
        text = ("Here is your polished research proposal.\n\n"
                "Here's your revised draft.\n\nHere is your edited proposal.\n\n"
                "Here is your updated text.")
        result = self.report(text)
        self.assertEqual(result["findings_by_category"]["assistant_residue"], 4)

    def test_reference_prose_excluded_but_reference_artifacts_scanned(self):
        text = ("# Draft\n\nWe will study 12 plans.\n\n## References\n\n"
                "A. Not only evidence but also valuable insights. [VERIFY]\n"
                "https://example.org/paper?download=1&utm_source=chatgpt.com&token=abc\n"
                "[cite: 3] turn2view4\n\n## Appendix\n\nWe will compare quarters.")
        result = self.report(text)
        self.assertEqual(result["counts"]["prose_words"], 9)
        categories = result["findings_by_category"]
        self.assertNotIn("stock_phrase", categories)
        self.assertNotIn("rhetorical_contrast", categories)
        self.assertEqual(categories["unresolved_placeholder"], 1)
        finding = next(f for f in result["findings"] if f["category"] == "tracking_parameter")
        self.assertEqual(finding["tracking_keys"], ["utm_source"])
        self.assertIn("download=1", finding["excerpt"])
        self.assertIn("token=abc", finding["excerpt"])

    def test_fenced_code_is_not_treated_as_submission_prose(self):
        text = ("We will compare plans.\n\n```python\n"
                "print('Let me know if [VERIFY] turn0search1 https://example.org/?utm_source=x')\n"
                "```\n\n~~~text\nNot only one but also two. [cite: 2]\n~~~\n")
        result = self.report(text)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["counts"]["prose_words"], 4)

    def test_contrasts_are_context_required_candidates_not_errors(self):
        result = self.report("We estimate association rather than causation. Not only A but also B changed. "
                             "This is not an effect but a descriptive difference.")
        findings = result["findings"]
        self.assertEqual(len(findings), 3)
        self.assertTrue(all(f["category"] == "rhetorical_contrast" for f in findings))
        self.assertTrue(all("Context required" in f["review_instruction"] for f in findings))

    def test_lengths_and_repeated_openings_only_prompt_review(self):
        text = ("I will compare the same clinicians across quarters and separately inspect inconsistent records.\n\n"
                "I will compare counts across networks, with a denominator fixed before analysis.")
        result = self.report(text, sentence_review_words=8, paragraph_review_words=10)
        self.assertEqual(result["findings_by_category"]["sentence_load"], 2)
        self.assertEqual(result["findings_by_category"]["paragraph_load"], 2)
        self.assertEqual(result["findings_by_category"]["repeated_opening"], 2)
        self.assertIn("not empirically validated", result["review_lengths"]["basis"])

    def test_exact_bytes_hash_and_readonly_input_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "中文.md", Path(directory) / "out/report.json"
            raw = b"\xef\xbb\xbf" + "研究。\r\n\r\n[VERIFY]\r\n".encode()
            source.write_bytes(raw)
            source.chmod(0o444)
            process = self.run_cli(source, "--output", output)
            self.assertEqual(process.returncode, 0, process.stderr)
            result = json.loads(output.read_text())
            self.assertEqual(result["source"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["findings"][0]["line"], 3)
            self.assertEqual(source.read_bytes(), raw)

    def test_no_input_overwrite_hardlink_or_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.md"
            source.write_text("Preserve this text.")
            hard, symlink = Path(directory) / "hard.md", Path(directory) / "symlink.md"
            hard.hardlink_to(source)
            symlink.symlink_to(source)
            for output in (source, hard, symlink):
                with self.subTest(output=output.name):
                    process = self.run_cli(source, "--output", output)
                    self.assertEqual(process.returncode, 2)
                    self.assertIn("must not overwrite", process.stderr)
                    self.assertEqual(source.read_text(), "Preserve this text.")

    def test_invalid_utf8_or_length_writes_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "bad.md", Path(directory) / "audit.json"
            source.write_bytes(b"\xffinvalid")
            process = self.run_cli(source, "--output", output)
            self.assertEqual(process.returncode, 2)
            self.assertFalse(output.exists())
            source.write_text("Readable prose.")
            process = self.run_cli(source, "--output", output, "--sentence-review-words", "0")
            self.assertEqual(process.returncode, 2)
            self.assertFalse(output.exists())

    def test_empty_input_and_plaintext_references(self):
        empty = self.report("")
        self.assertEqual(empty["findings"], [])
        self.assertEqual(empty["counts"]["prose_words"], 0)
        result = self.report("The study is descriptive.\n\nReferences\nAn ever-evolving landscape. [URL]")
        self.assertEqual(result["counts"]["prose_words"], 4)
        self.assertEqual(result["findings_by_category"], {"unresolved_placeholder": 1})


if __name__ == "__main__":
    unittest.main()
