#!/usr/bin/env python3
"""Local writing diagnostics and readable diffs; Python standard library only.

Inputs are UTF-8 plain text or Markdown. This program does not detect AI,
predict detector scores, verify citations, or determine authorship.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import difflib
import hashlib
import html
import json
from pathlib import Path
import re
import statistics
import sys


WORD_RE = re.compile(r"\b[^\W_]+(?:[’'\-][^\W_]+)*\b", re.UNICODE)
PLACEHOLDER_RE = re.compile(
    r"\[(?:VERIFY|CONFIRM|INSERT|CHECK|TODO|TBD|PENDING)"
    r"(?:[ :/_\-][^\]\n]*)?\]"
    # SOURCE/CITATION can also be ordinary Markdown link labels. Apply this
    # exception only to those ambiguous labels, not to explicit review markers.
    r"|\[(?:SOURCE|CITATION)(?:[ :/_\-][^\]\n]*)?\](?!\s*[\(\[])"
    r"|\{\{[^{}\n]+\}\}|\b(?:TODO|TBD)\b",
    re.IGNORECASE,
)
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)


def read_input(path: Path) -> tuple[bytes, str]:
    raw = path.read_bytes()
    return raw, raw.decode("utf-8-sig")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def length_summary(lengths: list[int]) -> dict:
    return {
        "count": len(lengths),
        "minimum": min(lengths) if lengths else None,
        "maximum": max(lengths) if lengths else None,
        "mean": round(statistics.mean(lengths), 2) if lengths else None,
        "median": statistics.median(lengths) if lengths else None,
        "lengths": lengths,
    }


def occurrence(text: str, match: re.Match, value: str) -> dict:
    start = match.start()
    return {
        "text": value,
        "line": text.count("\n", 0, start) + 1,
        "column": start - text.rfind("\n", 0, start),
    }


def clean_doi(value: str) -> str:
    # Prose punctuation is not normally part of a DOI. Retain balanced
    # parentheses inside a DOI, but remove a Markdown/citation closing bracket.
    value = value.rstrip(".,;:")
    while value.endswith(")") and value.count(")") > value.count("("):
        value = value[:-1].rstrip(".,;:")
    return value


def audit_text(text: str, raw: bytes, source: str) -> dict:
    paragraphs = [p.strip() for p in re.split(r"\r?\n(?:[ \t]*\r?\n)+", text) if p.strip()]
    sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?。！？])\s+|(?<=[。！？])", text)
        if s.strip()
    ]
    starts: dict[str, list[int]] = {}
    for index, paragraph in enumerate(paragraphs, 1):
        first_words = words(paragraph)[:3]
        if first_words:
            key = " ".join(first_words).casefold()
            starts.setdefault(key, []).append(index)
    dois = [occurrence(text, match, clean_doi(match.group())) for match in DOI_RE.finditer(text)]
    doi_counts = Counter(item["text"].casefold() for item in dois)
    placeholders = [
        occurrence(text, match, match.group()) for match in PLACEHOLDER_RE.finditer(text)
    ]
    return {
        "schema_version": "1.0",
        "purpose": "Advisory writing diagnostics; not AI detection or an authorship verdict.",
        "source": {"path": source, "sha256": sha256(raw), "bytes": len(raw), "encoding": "UTF-8"},
        "counts": {
            "words": len(words(text)),
            "characters": len(text),
            "paragraphs": len(paragraphs),
            "sentences_heuristic": len(sentences),
        },
        "unresolved_placeholders": placeholders,
        "doi_occurrences": dois,
        "doi_unique_count": len(doi_counts),
        "paragraph_word_lengths": length_summary([len(words(p)) for p in paragraphs]),
        "sentence_word_lengths_heuristic": length_summary([len(words(s)) for s in sentences]),
        "repeated_paragraph_starts": [
            {"opening_words": key, "paragraph_numbers": positions, "count": len(positions)}
            for key, positions in starts.items()
            if len(positions) > 1
        ],
        "limitations": [
            "Counts describe the supplied text, including Markdown headings and references; they do not measure writing quality or authorship.",
            "Word counting uses Unicode letter/number runs with internal apostrophes or hyphens; it is not linguistic segmentation for Chinese or other languages without spaces.",
            "Sentence splitting is approximate; abbreviations, headings and formatting can affect it.",
            "DOI extraction is syntactic only; existence and support for a claim require checking the source. Trailing prose punctuation is trimmed heuristically.",
            "Repeated openings and length patterns are review prompts, not errors or evidence of AI use. There are no target sentence lengths or randomness requirements.",
        ],
        "language_editing_confounds": "Human editing, translation, genre conventions and language background can change these patterns. No detector score or authenticity conclusion can be inferred from this report.",
        "external_detector_test": "Not performed by this program.",
    }


def cell(text: str | None, line_number: int | None, change: str) -> str:
    if text is None:
        return '<td class="line">—</td><td class="text missing"><span class="sr-only">No corresponding line</span></td>'
    escaped = html.escape(text, quote=True)
    if change == "delete":
        escaped = f"<del>{escaped}</del>"
    elif change == "insert":
        escaped = f"<ins>{escaped}</ins>"
    return f'<td class="line">{line_number}</td><td class="text"><pre>{escaped or " "}</pre></td>'


def diff_html(before: str, after: str, before_raw: bytes, after_raw: bytes,
              before_name: str, after_name: str) -> str:
    left, right = before.splitlines(), after.splitlines()
    matcher = difflib.SequenceMatcher(a=left, b=right, autojunk=False)
    rows = []
    added = removed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            removed += i2 - i1
            added += j2 - j1
        for offset in range(max(i2 - i1, j2 - j1)):
            li = i1 + offset if i1 + offset < i2 else None
            ri = j1 + offset if j1 + offset < j2 else None
            label = {"equal": "Unchanged", "replace": "Replaced", "delete": "Removed", "insert": "Added"}[tag]
            rows.append(
                f'<tr class="{tag}"><th scope="row">{label}</th>'
                + cell(left[li] if li is not None else None, li + 1 if li is not None else None,
                       "delete" if tag != "equal" else "equal")
                + cell(right[ri] if ri is not None else None, ri + 1 if ri is not None else None,
                       "insert" if tag != "equal" else "equal")
                + "</tr>"
            )
    if not rows:
        rows.append('<tr><td colspan="5">Both inputs contain no text lines.</td></tr>')
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Writing revision comparison</title>
<style>
body {{margin:0 auto;padding:1.5rem;max-width:110rem;font:1rem/1.5 system-ui,sans-serif;color:#17212b;background:#fff}}
h1 {{line-height:1.2}} .note {{max-width:90ch}} code,pre {{font:0.9rem/1.5 ui-monospace,monospace}}
code {{overflow-wrap:anywhere}} table {{border-collapse:collapse;table-layout:fixed;width:100%}}
caption {{text-align:left;padding:.8rem 0;font-weight:600}} th,td {{border:1px solid #bcc5ce;padding:.5rem;text-align:left;vertical-align:top}}
thead th {{background:#e9eef3}} .status {{width:6rem}} .number {{width:3rem}} .line {{color:#4b5563;text-align:right}}
pre {{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;word-break:normal}} .missing {{background:#f3f4f6}}
del {{background:#ffe6e6;color:#7b1111;text-decoration:line-through}} ins {{background:#e2f3e7;color:#124c2b;text-decoration:underline}}
.equal th {{color:#4b5563}} .sr-only {{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)}}
@media(max-width:650px){{body{{padding:.5rem}}th,td{{padding:.25rem}}.status{{width:4rem}}.number{{width:2rem}}pre{{font-size:.8rem}}}}
@media print{{body{{max-width:none;padding:0}}thead{{display:table-header-group}}tr{{break-inside:avoid}}}}
</style></head><body>
<h1>Writing revision comparison</h1>
<p class="note">Removed text is struck through; added text is underlined. Replaced lines count as both removed and added. This comparison does not detect AI, predict detector scores, or establish authorship.</p>
<p><strong>Changed lines:</strong> {removed} removed; {added} added.</p>
<p class="note">Line endings and the presence of a final newline are not shown as line changes. SHA-256 hashes below cover exact input bytes.</p>
<dl><dt>Before</dt><dd>{html.escape(before_name, quote=True)}<br><code>{sha256(before_raw)}</code></dd>
<dt>After</dt><dd>{html.escape(after_name, quote=True)}<br><code>{sha256(after_raw)}</code></dd></dl>
<table><caption>Full document comparison</caption><colgroup><col class="status"><col class="number"><col><col class="number"><col></colgroup>
<thead><tr><th scope="col">Change</th><th scope="col">Line</th><th scope="col">Before</th><th scope="col">Line</th><th scope="col">After</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table><p>Generated: {timestamp} (UTC).</p></body></html>'''


def write_output(path: Path, text: str, inputs: list[Path]) -> None:
    resolved_output = path.resolve()
    if any(resolved_output == item.resolve() for item in inputs):
        raise ValueError("Output must not overwrite an input file.")
    if path.exists() and any(path.samefile(item) for item in inputs):
        raise ValueError("Output must not overwrite an input file or its hard link.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit", help="Write advisory diagnostics as JSON.")
    audit.add_argument("input", type=Path)
    audit.add_argument("--output", type=Path, required=True)
    diff = sub.add_parser("diff", help="Write a standalone, escaped HTML line comparison.")
    diff.add_argument("before", type=Path)
    diff.add_argument("after", type=Path)
    diff.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            raw, text = read_input(args.input)
            result = audit_text(text, raw, str(args.input.resolve()))
            write_output(args.output, json.dumps(result, ensure_ascii=False, indent=2) + "\n", [args.input])
        else:
            before_raw, before = read_input(args.before)
            after_raw, after = read_input(args.after)
            result = diff_html(before, after, before_raw, after_raw,
                               str(args.before.resolve()), str(args.after.resolve()))
            write_output(args.output, result, [args.before, args.after])
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(args.output.resolve()), "command": args.command}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
