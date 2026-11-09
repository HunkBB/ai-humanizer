# v2.1 register update: execution and review record

Date: 2026-11-08 (America/New_York). Version: 2.1.0.

## Change

Formal academic documents now use an explicit analytical, precise and restrained register. Outreach emails have separate guidance. Editing preserves effective passages, functional sentence complexity, disciplinary terminology and justified first person. A project preference avoids would/will and modal contractions in newly authored formal body text, without changing conditions, uncertainty or proposed/completed status. Quotes, titles, proper names and nonmodal uses remain protected; explicit task instructions can override the default. Intake and review now distinguish confirmed preferences from authenticated personal voice.

## Execution

Three fresh Codex agent sessions received the skill and raw tasks, without the editing diagnosis or a desired verdict. Another fresh agent assessed task inputs and outputs for fidelity, clarity and register, without editor notes. A separate review checked the instruction files and examples. These are AI-agent evaluations, not professor evaluations, detector measurements or statistical validation.

| Group | Task | Observed outcome |
|---|---|---|
| Existing proposal | Edit a previously generated proposal into formal prose, preserving the design and references | Substantive fidelity, clarity and register passed independent review. All five references remained textually identical. No would/will candidates remained in the revised body. The source contains personal material and is not published here. |
| New genre pair | Draft a formal proposal summary and outreach email from synthetic facts | Both meet the requested lengths, retain pending data access and descriptive limits, and use distinct genres. The proposal keeps the future-date restriction in both continuity numerator and denominator. No modal candidates appeared in either body. |
| Restraint and exceptions | Light-edit suitable academic prose, revise a conditional proposal, and honor an explicit override | Suitable prose remains verbatim, including valid first person, an exact quotation containing Would, and the noun phrase political will. The conditional paragraph preserves dictionary acquisition, missing data access, approval dependence and hypothetical expectation. The override paragraph retains would verbatim. |

Reproducible synthetic prompts, outputs and editor notes are in [new_genres](new_genres/) and [restraint](restraint/). Files are practice artifacts; the email was not sent. Personal proposal drafts and raw private reviews remain outside the public repository.

## Findings and corrections

- Instruction review caught an example that changed an assessment of quarterly stability into a comparison of provider files. The final example retains the original analytical target and proposed status without adding a data source.
- Output review found one subject-verb agreement error in the existing-proposal revision: “unusable physician identifiers precludes”. The final draft uses “preclude”; its reviewed snapshot and the correction are retained in the local project record.
- The reviewer noted mild abstraction in parts of the formalized proposal. This did not impair interpretation or lose design information in this case; it remains a useful focus for future user feedback.

## Checks and limits

- Skill frontmatter validation passed; interface metadata regenerated with the creator helper.
- All 22 existing helper-script unit tests passed. No helper-script behavior was changed.
- Contextual inspection of would/will candidates distinguished lexical restrictions from protected quotations, nonmodal uses and explicit overrides. Counts were not treated as an authorship or quality score.
- Personal voice remains uncalibrated: no authenticated independently written prose sample was supplied.
- These runs used Codex agents. No independent Claude Code execution was performed. Source facts in the proposal test were preserved from supplied material rather than newly verified online.
- Turnitin and other detectors: not tested. No percentage or avoidance claim is inferred from these results.
