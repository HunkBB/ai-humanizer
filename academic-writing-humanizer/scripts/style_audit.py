#!/usr/bin/env python3
"""Find local editorial review candidates; never infer AI use or rewrite input."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, urlsplit


WORD_RE = re.compile(r"\b[^\W_]+(?:[’'\-][^\W_]+)*\b", re.UNICODE)
PLACEHOLDER_RE = re.compile(
    r"\[(?:VERIFY|CONFIRM|CHECK|TODO|TBD|PENDING|DATE|URL)(?:[ :/_\-][^\]\n]*)?\]"
    r"|\[INSERT(?:[ :/_\-][^\]\n]*)?\]|\{\{[^{}\n]+\}\}"
    r"|\b(?:TODO|TBD|YYYY[-/]MM[-/]DD|DD[-/]MM[-/]YYYY)\b"
    r"|\b\d{4}[-/](?:XX[-/](?:XX|\d{2})|\d{2}[-/]XX)\b", re.I)
URL_PLACEHOLDER_RE = re.compile(r"\bINSERT_(?:SOURCE|WEBSITE)_URL_(?:\d+|HERE)\b", re.I)
ARTIFACT_RE = re.compile(
    r"\bturn\d+(?:search|view|fetch|news|image)\d+\b"
    r"|contentReference\[|oaicite:|oai_citation|\battributableIndex\b"
    r"|\[cite:\s*\d+(?:\s*,\s*\d+)*\]|\[span_\d+\]\((?:start|end)_span\)"
    r"|<grok-card\b|grok_render_citation_card_json|〖\d+[†‡][^〗\n]+〗"
    r"|\[(?:attached_file|web):\d+\]|ppl-ai-file-upload|:::writing(?=\s*\{|\s*$)"
    r"|[\ue200\ue202\ue201]", re.M)
CHAT_RE = re.compile(
    r"\b(?:(?:here is|here's)\s+your\s+(?:revised|polished|edited|updated)\s+"
    r"(?:(?:research|outreach)\s+)?(?:draft|proposal|text|version)|let me know if|"
    r"I hope this helps|as an AI(?: language model)?)\b", re.I)
RHETORIC_RE = re.compile(
    r"\bnot only\b[^.!?\n]{0,180}?\bbut also\b"
    r"|\bnot\b[^.!?\n]{0,100}?\bbut\b|\brather than\b", re.I)
STOCK_RE = re.compile(
    r"\b(?:a testament to|pivotal role|ever[- ]evolving landscape|"
    r"unlock the potential|delve into|a comprehensive and holistic|"
    r"valuable insights|underscores the importance)\b", re.I)
URL_RE = re.compile(r'https?://[^\s<>"\]\)]+', re.I)
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def masks(text: str) -> tuple[str, str]:
    """Retain offsets/newlines while excluding fenced code and reference prose."""
    artifact_lines, prose_lines = [], []
    fence = None
    reference_level = None
    for line in text.splitlines(keepends=True):
        blank = re.sub(r"[^\r\n]", " ", line)
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        is_code = fence is not None or marker is not None
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        heading = HEADING_RE.match(line.rstrip("\r\n")) if not is_code else None
        if heading:
            level = len(heading.group(1))
            if reference_level is not None and level <= reference_level:
                reference_level = None
            if re.fullmatch(r"(?:\d+[.)]?\s+)?(?:references|bibliography|works cited)",
                            heading.group(2), re.I):
                reference_level = level
        # Also support plain-text reference headings at the end of a document.
        elif not is_code and re.fullmatch(r"(?:references|bibliography|works cited):?", line.strip(), re.I):
            reference_level = 6
        artifact_lines.append(blank if is_code else line)
        prose_lines.append(blank if is_code or reference_level is not None or heading else line)
    return "".join(artifact_lines), "".join(prose_lines)


def audit_text(text: str, raw: bytes, source: str,
               sentence_review_words: int = 45, paragraph_review_words: int = 180) -> dict:
    if min(sentence_review_words, paragraph_review_words) < 1:
        raise ValueError("Review lengths must be positive integers.")
    artifacts, prose = masks(text)
    findings = []
    # Quote/code examples and genuine URL paths must not become delivery residue
    # or bare URL-placeholder findings solely because they contain these words.
    chat_prose = re.sub(r'"[^"\n]*"|“[^”\n]*”',
                       lambda match: " " * len(match.group()), prose)
    url_free_artifacts = URL_RE.sub(lambda match: " " * len(match.group()), artifacts)

    def add(category: str, start: int, end: int, instruction: str, **extra) -> None:
        findings.append({"category": category, "line": text.count("\n", 0, start) + 1,
                         "excerpt": text[start:end].strip()[:220],
                         "review_instruction": instruction, **extra})

    rules = [
        (artifacts, PLACEHOLDER_RE, "unresolved_placeholder", "Resolve from evidence or mark it explicitly in review notes; never invent missing content."),
        (url_free_artifacts, URL_PLACEHOLDER_RE, "unresolved_placeholder", "Replace the bare URL placeholder with a verified source URL; never invent a reference."),
        (artifacts, ARTIFACT_RE, "tool_citation_artifact", "Check the source, then convert a genuine citation to the required document format. Keep literal examples if intended."),
        (chat_prose, CHAT_RE, "assistant_residue", "Remove conversational delivery text from the manuscript if it is not an intentional quotation."),
        (prose, RHETORIC_RE, "rhetorical_contrast", "Context required: retain a necessary scientific distinction; simplify a decorative contrast without changing scope."),
        (prose, STOCK_RE, "stock_phrase", "Context required: state the supported action or finding, or delete an empty claim. This phrase is not automatically wrong."),
    ]
    for content, pattern, category, instruction in rules:
        for match in pattern.finditer(content):
            add(category, match.start(), match.end(), instruction)
    for match in URL_RE.finditer(artifacts):
        try:
            keys = [key for key, _ in parse_qsl(urlsplit(match.group()).query)]
        except ValueError:
            continue
        tracking = [key for key in keys if key.lower().startswith("utm_")
                    or key.lower() in {"fbclid", "gclid", "msclkid"}]
        if tracking:
            add("tracking_parameter", match.start(), match.end(),
                "Review only listed tracking keys. Verify the canonical destination; preserve functional parameters, DOI paths and access tokens.",
                tracking_keys=tracking)
    paragraphs = []
    for match in re.finditer(r"\S[\s\S]*?(?=\r?\n[ \t]*\r?\n|\Z)", prose):
        content = match.group()
        count = len(WORD_RE.findall(content))
        paragraphs.append((match, count))
        if count > paragraph_review_words:
            add("paragraph_load", match.start(), match.end(),
                "Review purpose and conceptual load; split only at a real change of task. Length alone is not a fault.", words=count)
    # Approximate splitting is deliberately described as such in the report.
    sentences = list(re.finditer(r"\S[\s\S]*?(?:[.!?。！？](?=\s|$)|\Z)", prose))
    for match in sentences:
        count = len(WORD_RE.findall(match.group()))
        if count > sentence_review_words:
            add("sentence_load", match.start(), match.end(),
                "Review the actor, action, qualification and embedded clauses. Keep a long sentence when its structure is clear.", words=count)
    openings = {}
    for match, count in paragraphs:
        first = WORD_RE.findall(match.group())[:3]
        if len(first) == 3:
            openings.setdefault(" ".join(first).casefold(), []).append(match)
    for opening, matches in openings.items():
        if len(matches) > 1:
            for match in matches:
                add("repeated_opening", match.start(), match.start() + min(len(match.group()), 100),
                    "Review repetition across paragraphs; retain useful parallel structure and stable technical labels.", opening=opening)
    findings.sort(key=lambda item: (item["line"], item["category"]))
    return {
        "schema_version": "1.0", "status": "not_ai_detector",
        "purpose": "Candidate locations for editorial review, not errors, a score, or an authorship verdict.",
        "source": {"path": source, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "encoding": "UTF-8"},
        "counts": {"prose_words": len(WORD_RE.findall(prose)), "prose_paragraphs": len(paragraphs), "prose_sentences_heuristic": len(sentences)},
        "review_lengths": {"sentence_words": sentence_review_words, "paragraph_words": paragraph_review_words,
                           "basis": "Adjustable editorial prompts, not empirically validated cutoffs or writing targets."},
        "artifact_pattern_reference": "https://en.wikipedia.org/w/index.php?oldid=1383317735&title=Wikipedia:Signs_of_AI_writing/Markup",
        "findings_by_category": dict(Counter(item["category"] for item in findings)),
        "findings": findings,
        "limitations": [
            "No network calls, citation verification, text changes, detector run or inference of AI contribution.",
            "Fenced code is excluded from all scans. References and headings are excluded from prose scans, but checked for placeholders, citation artifacts and tracking parameters.",
            "Markdown reference headings and plain-text References/Bibliography/Works cited are recognized; unmarked reference sections may require manual review.",
            "English phrase patterns and approximate sentence/word segmentation are incomplete; abbreviation, markup and non-English text affect counts.",
            "Same-line straight-double or curly-double quotations are excluded from assistant-residue checks. Bare URL placeholders inside actual HTTP(S) URLs are excluded; no URL is rewritten.",
            "No universal ban on punctuation, contrasts, lists, passive voice or vocabulary. Significant and associated with are not treated as suspect terms.",
            "Zero findings does not mean natural, accurate, human-written, submission-ready or undetectable text. More findings need not mean worse writing.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sentence-review-words", type=int, default=45)
    parser.add_argument("--paragraph-review-words", type=int, default=180)
    args = parser.parse_args(argv)
    try:
        if args.output.resolve() == args.input.resolve() or (args.output.exists() and args.output.samefile(args.input)):
            raise ValueError("Output must not overwrite an input file or its hard link.")
        raw = args.input.read_bytes()
        report = audit_text(raw.decode("utf-8-sig"), raw, str(args.input.resolve()),
                            args.sentence_review_words, args.paragraph_review_words)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(args.output.resolve()), "status": "not_ai_detector"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
