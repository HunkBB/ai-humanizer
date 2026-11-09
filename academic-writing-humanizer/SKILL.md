---
name: academic-writing-humanizer
description: Draft, humanize, and edit research proposals, research statements, and supervisor outreach using verified background, actual voice samples, and primary sources. Use for generic or mechanical AI-style prose, Wikipedia Signs of AI writing checks, dense methods, personal voice, citations, or US/Hong Kong/Singapore academic applications. Apply a full contextual style review, preserve factual and methodological meaning, and compare revisions; keep actual detector results separate from editorial judgment.
---

# Academic Writing Humanizer

Produce specific, readable research writing that the author can explain and support. Use modules A–I by default; scale their depth to the task. Preserve meaning, facts, technical precision, and actual authorship contributions. Treat factual correctness and readable prose as separate acceptance conditions: improvement in one does not establish improvement in the other.

## Establish the inputs

1. Identify audience, genre, target programme/professor, language, length, deadline, output format, and source draft. Distinguish informal outreach from a formal application or protocol.
2. Read the supplied CV, sources, and genuine author samples. Use [intake-and-voice.md](references/intake-and-voice.md) and [intake-template.md](assets/intake-template.md) to record facts, provenance, conflicts and voice status. Distinguish CV-reported from independently verified facts.
3. Check exact programme/material requirements when available. Consult [process-and-review.md](references/process-and-review.md). Do not infer a national rule from a department's policy. Unknown policy means unknown.
4. Continue useful work despite nonessential gaps. Ask one bundled set of material questions only when answers would change the proposal. Without authentic prose samples, use restrained academic English and mark voice calibration incomplete. Propose alternatives or mark missing author decisions rather than inventing them.

## Apply all nine modules

| Module | Action | Completion evidence |
|---|---|---|
| A — Voice | Match supported tendencies in actual author samples; adapt to genre. | Sample provenance and observed preferences, or explicit uncalibrated status. |
| B — Background | Reconcile experiences, skills, outcomes and access claims. | Fact ledger with unresolved conflicts excluded or flagged. |
| C — Question | Specify question, mechanism, population and modest contribution. | Answerable question and literature-grounded contribution. |
| D — Methods | Align data, units, measures, design, assumptions and limitations. | Feasibility check and descriptive/causal distinction. |
| E — Fit | Read the scholar's relevant primary work and connect an actual design choice. | Specific connection without invented relationship or availability. |
| F — Language | Rebuild weak paragraphs and sentences using the complete contextual style check. | Specific evidence of clearer flow and fewer gratuitous rhetorical patterns, with protected meaning intact. |
| G — Sources | Verify source identity and support for each central claim. | Claim-to-source ledger with access level and limits. |
| H — Decisions | Preserve real inputs, decisions, revisions and AI roles. | Actual change record, author decisions and appropriate disclosure. |
| I — Review | Review independently where possible and ask research questions. | Evidence-based critique and questions the author must answer. |

## Draft and revise in three passes

### Pass 1: research content

Read [research-checks.md](references/research-checks.md) for B, C, D, E and G.

- For new writing, formulate a focused working question with explicit assumptions, then draft from the ledgers. Label AI-proposed topics as proposed, not as established personal motivations.
- For an existing draft, preserve a copy and distinguish language edits from substantive changes. If a method/scope must change, explain why and mark author review required; never silently replace the author's project.
- Check sources before claiming a literature gap. Never invent citations, data access, sample sizes, effects, collaborations or experiences. A real DOI does not establish support for a claim.
- Prefer a feasible core study over a list of techniques. Provide a usable fallback for unavailable data. Mark proposed research choices pending author confirmation.
- Use supplied evidence when browsing is unavailable and state the verification limit. Never describe retrieval as performed when it was not.

### Pass 2: expression

Read [language-editing.md](references/language-editing.md), [rewrite-examples.md](references/rewrite-examples.md), and [wikipedia-coverage.md](references/wikipedia-coverage.md). The coverage reference includes every substantive heading in the dated Wikipedia source and its Style/Markup pages, with scope-specific actions. It is an editorial resource, not a classifier.

1. Freeze a **meaning ledger**: facts, numbers, actors, work/access status, technical definitions, inferential strength, citations, and research decisions. Preserve these or explicitly record a substantive change.
2. For each applicable coverage row record `revise`, `keep with reason`, or `not present`; use `not applicable` for context-specific rows. Treat parent rows as routing checks. Consolidate repeated findings. Read historical/ineffective-indicator rows as safeguards, not deletion instructions. For a full audit, retain the disposition ledger as a sidecar; present only meaningful changes to the user.
3. Use a **paragraph rewrite** when humanizing or when the user reports formulaic prose. Start with its necessary propositions and write a new paragraph around a concrete question, observation, decision, or consequence. Do not settle for synonym swaps. Use a light edit only when requested or when a paragraph already works.
4. Run distinct passes for argument flow, inflated/vague claims, syntax/wording, assistant residue/format, and citation hygiene. Separate submission prose from editorial notes; keep research limitations that affect interpretation in the text. Explain a measure before stacking labels and exceptions. Do not make every paragraph a protocol checklist.
5. Read the whole draft for repeated openings, uniform paragraph scaffolds, needless summaries, stilted attribution and density. Preserve technical repetition, valid contrasts, uncertainty and author-supported idiosyncrasies. Do not add errors, invented experiences, forced short sentences, random vocabulary or punctuation rules.
6. Compare against the meaning ledger. Review fidelity and reader experience separately with [style-review.md](references/style-review.md). A content improvement cannot compensate for a readability regression. If either fails, revise the affected passages and review them again. Stop when remaining edits are cosmetic; report unresolved issues.

### Pass 3: verification and review

Read [process-and-review.md](references/process-and-review.md) for H and I; use [review-template.md](assets/review-template.md).

1. Check changed numbers, facts, causal statements and attributions against the ledgers.
2. Explain material changes as before → after → reason, and identify additions requiring author confirmation.
3. If available, give an independent agent the draft, requirements, facts and sources without the intended verdict or editing rationale. Assess fidelity and readability separately using [style-review.md](references/style-review.md). Preserve raw reviews and disagreements. Otherwise label it self-review. For A/B comparisons, randomize neutral labels and use comparable scope/length; disclose any content moved to an annex.
4. Produce 5–8 questions on contribution, data, identification, measurement, feasibility and motivation. Do not claim generated answers prove the user's understanding; understanding is untested until the author responds.
5. Apply justified corrections and state remaining issues. One case does not validate country-wide, cross-platform or detector performance.

## Use local helpers when useful

Run with Python 3, resolving scripts relative to this directory:

```bash
python3 scripts/review_text.py audit draft.md --output audit.json
python3 scripts/review_text.py diff before.md after.md --output changes.html
python3 scripts/style_audit.py draft.md --output style-audit.json
```

No third-party dependencies, network, API key or detector account is required. The helpers report mechanical candidates and a visual diff. `style_audit.py` is a limited local preflight, not the complete semantic Wikipedia review. Its triggers are editorial prompts, not validated classification thresholds; do not minimize their count as an objective. Manually inspect findings and preserve legitimate uses. The scripts do not verify references, assess research validity, infer authenticity or detect AI. Never convert counts into an AI percentage. Preserve input files. Do not send unpublished writing to third parties without authorization.

## Report detector status accurately

Read [evidence-and-detectors.md](references/evidence-and-detectors.md) for dated evidence.

- Separate writing-quality review from detector measurement.
- Without an actual run, report: “Turnitin: not tested; corresponding percentage cannot be estimated.” Never substitute another vendor's score, a subjective percentage or language-model judgment.
- With a genuine report, record product, date, submitted version/hash, literal result, meaning and limits. Do not label it the author's actual AI contribution or guarantee acceptance.
- Never promise undetectability or fabricate draft histories, reports, backdated notes or minimized AI-use statements.

## Deliver

Return revised text, concise changes and material author decisions. For full proposals also provide source ledger, A–I review, style dispositions, detector status and discussion questions. Show representative before/after passages and explain the reader-facing improvement, plus meaningful cases deliberately retained. Separate review notes from submission prose. Mark unresolved substantive decisions as a working draft, not ready to submit. Keep personal facts/samples in the user's project, outside this reusable skill.

Scale the visible editing record to the task. For a short passage, use a few concise bullets and material unresolved issues; do not attach the full-proposal review apparatus unless requested. Keep detailed audit records separate when useful.
