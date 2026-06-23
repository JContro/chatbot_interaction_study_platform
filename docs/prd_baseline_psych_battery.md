# PRD: Baseline Psychology-Test Battery

Status: Ready for agent
Triage label: `ready-for-agent`

## Problem Statement

As a researcher re-running this chatbot-interaction study, I need every participant to complete two psychology instruments (BFI-2-S and IDAS-R) as a **baseline** before they enter any conversation, so that I can later correlate their personality / internal-dialogue profile with how they interact with the chatbot. Right now the platform jumps straight from login to topic selection — there is no baseline capture at all, no way to link a participant's traits to their chat behavior, and no way for me (the researcher) to inspect, score, or export that data. I am rewriting the study and need this baseline step added in a way I can change later (reorder steps, swap instruments, fix scoring keys) without editing a dozen views — and I need documentation of the study flow so it's editable as prose.

## Solution

Insert a **baseline battery** as the new first step after login. A freshly-logged-in, email-verified participant lands on a baseline intro page; pressing "Start" begins a timed, one-item-at-a-time survey that presents the 30 BFI-2-S items followed by the 40 IDAS-R items, answered via keyboard keys 1–5 with fast animated transitions. Each keypress is saved to the server instantly, so the survey is refresh-safe and resumable. The battery is **one attempt, ever**. Embedded at fixed positions are attention checks ("Press the letter X"); pressing a number on an attention check fails it, and the first failure shuts the battery down. Completion (or attention failure) is recorded as a status on the participant, which gates access to the rest of the study. Researchers get a Django-admin raw view plus a custom scored summary view with two CSV exports (flat scores, long raw responses). The entire participant journey is governed by a single declarative flow module so the step order can be changed in one file, documented alongside.

## User Stories

### Participant — entry & flow
1. As a participant, after registering and verifying my email, I want my first post-login screen to be the baseline survey intro (not topic selection), so that I complete the psychology tests before anything else.
2. As a participant, I want a "Start" button on the intro page that begins the survey, so that the timing of my attempt is captured from the moment I actually begin.
3. As a participant, once I complete the baseline battery, I want to be taken automatically to topic selection, so that I can proceed into the study without manual navigation.
4. As a participant who returns after already completing the baseline, I want to skip straight to topic selection on login, so that I'm never asked to re-take a completed baseline.
5. As a participant who abandoned the baseline mid-way, I want to resume exactly where I left off on next login, so that I don't lose my prior answers or have to restart.
6. As a participant, I want every keypress saved instantly, so that a refresh or connection drop never loses my progress.
7. As a participant, I want a single clear error/terminal page if I fail an attention check, so that I understand why I can't continue.

### Participant — survey UX
8. As a participant, I want to see one survey item at a time, so that I can focus on each statement without being overwhelmed by 70 items at once.
9. As a participant, I want to answer each item by pressing a number key 1–5 on my keyboard, so that I can move through the battery quickly without mouse interaction.
10. As a participant, I want a fast animated transition between items after I answer, so that the survey feels fluid and keeps me in flow.
11. As a participant, I want the 5-point scale labels visible for each item, so that I know what each number means.
12. As a participant, I want a 10-second "Undo" option after each answer, so that I can correct a fat-fingered key before the next item locks in.
13. As a participant, I do not want to navigate back to previous items, so that my first impressions are captured cleanly (forward-only).
14. As a participant, I want to know my progress through the battery, so that I have a sense of how much remains.

### Participant — attention checks
15. As a participant, I want an attention check to appear as a clear instruction "Press the letter X", so that I can comply if I'm paying attention.
16. As a participant, if I press the correct target letter on an attention check, I want to advance immediately, so that compliant behavior is uninterrupted.
17. As a participant, if I press a wrong (non-target, non-number) letter on an attention check, I want the item to simply re-ask, so that a slipped finger doesn't unfairly fail me.
18. As a participant, if I press a number on an attention check, I want to see the next real item briefly before the survey shuts down, so that the failure sequence is non-jarring.
19. As a participant who failed an attention check, I want a clear "you're not paying attention" shutdown message, so that I understand the session has ended.

### Researcher — administration
20. As a researcher, I want each participant's baseline status (pending / completed / attention_failed / abandoned) visible, so that I know who has done what.
21. As a researcher, I want to see each participant's baseline duration (start to completion), so that I can flag implausibly fast attempts.
22. As a researcher, I want to reset a participant's attention_failed status back to pending, so that I can give a recruited participant a second chance after a genuine slip.
23. As a researcher, I want to inspect a participant's raw per-item responses, so that I can audit their data.
24. As a researcher, I want to see a failed participant's failed attention-check item and the keystroke they pressed, so that I can verify the failure was legitimate.

### Researcher — scoring & export
25. As a researcher, I want BFI-2-S responses scored into the 5 domains and 15 facets, so that I can use personality variables in analysis.
26. As a researcher, I want IDAS-R responses scored into the total and 8 subscales, so that I can use internal-dialogue variables in analysis.
27. As a researcher, I want a flat CSV export (one row per participant, all scores as columns) so that I can load it directly into SPSS/R/Excel.
28. As a researcher, I want a long CSV export (one row per item-response) so that I can independently re-score or audit raw data.
29. As a researcher, I want baseline_status included in exports, so that I can decide at analysis time whether to exclude attention_failed participants (rather than having the app decide for me).
30. As a researcher, I want the baseline duration and timer fields in exports, so that I can do quality-control filtering.
31. As a researcher, I want computed scores derived live from the raw responses, so that a scoring-key fix applies instantly to all participants with no stale snapshots.

### Researcher / developer — changeability
32. As the developer, I want the participant step order defined in a single declarative flow module, so that reordering or inserting a step is a one-file edit.
33. As the developer, I want completion predicates to live as methods on the models, so that the flow module stays a thin list and the logic stays testable with the data.
34. As the developer, I want instrument definitions (items, reverse-keying, scoring groups) in a data module keyed by slug, so that adding or fixing an instrument is a code edit, not a migration.
35. As the developer, I want documentation of the study flow as a markdown file, so that I (or a future maintainer) can understand and change the step order without reading code.
36. As the developer, I want the existing scattered `is_email_verified` gate checks consolidated into the flow module, so that gate logic lives in one place rather than duplicated across views.
37. As the developer, I want a generic response-storage table, so that a third instrument could be added later with no schema migration.

## Implementation Decisions

### Entry model & gating
- The baseline battery is the new first step **after** register + email-verify + login. It replaces the current login→`topic_selection` redirect.
- A single status field on the participant (`baseline_status`) is the source of truth for the gate, with four states: `pending | completed | attention_failed | abandoned`. A boolean is insufficient because the terminal `attention_failed` state must be distinguishable from never-finished.
- Existing per-view `if not request.user.is_email_verified: logout + redirect('login')` blocks are consolidated into the flow module's gate mechanism (see Flow module).

### Attempts & timing
- **One attempt, ever.** Timer fields live on the participant: `baseline_started_at` (set when the intro "Start" button is pressed) and `baseline_completed_at` (set when the final item save is confirmed). Duration = difference. Wall-clock only; no active-vs-idle split.
- A future "allow retake" change would require a migration to a per-attempt table — accepted as a conscious tradeoff for a clean protocol.

### Storage schema
- A single generic response table: `InstrumentResponse(user, instrument_slug, item_index, value)` with `unique_together = (user, instrument_slug, item_index)`. One row per answered item.
- Instrument definitions (item text, 1–5 scale, reverse-keyed item flags, scoring group mappings) live in a Python data module keyed by `instrument_slug`. Adding or editing an instrument is a code edit, not a migration.
- Two instruments ship initially: `bfi_2_s` (30 items, reverse-keyed items per the BFI-2-S key, 5 domains + 15 facets) and `idas_r` (40 items, total + 8 subscales). Note: the IDAS-R source doc has a numbering discrepancy between its factor table and appendix (factor-table items 43–46 correspond to appendix items 40, 32, 24, 16) — the definition module must encode the corrected mapping.

### Scoring
- Scores are **computed on demand** from raw responses + the definition module, not stored. A `score_instrument(user, slug)` utility returns the domain/facet/subscale/total scores. Single source of truth; a scoring-key fix applies instantly to all participants.
- A path to publication-time snapshotting (a management command writing a frozen score table) is left open but out of scope now.

### Survey UX
- Order: BFI-2-S first, then IDAS-R.
- One item per screen, answered via keyboard 1–5, with a fast animated transition between items. Scale labels visible per item.
- **Per-item save:** every keypress persists to the server via AJAX (optimistic animation, durable background save). Resume position = highest saved `item_index` + 1 for the instrument, with an in-progress refinement during the undo window.
- **Forward-only:** no back-navigation. A 10-second "Undo" toast after each keypress deletes the current item's response row and re-asks the same item. After 10s the answer is final and the next item appears.

### Attention checks
- **Count:** 3.
- **Position:** hardcoded fixed positions in the battery (not randomized). Prompt letter is random per-render, but position is fixed.
- **Prompt:** "Press the letter X" with a single random letter.
- **Pass:** correct target letter → advance immediately. Attention checks are exempt from the 10-second undo.
- **Wrong non-target letter:** neutral — stay on the item, re-ask (no advance, no fail).
- **Fail:** any number key 1–5 → save the failure (failed item index + keystroke) → render the next real item → 3-second grace window → shutdown screen + set `baseline_status = attention_failed`.
- **Strict (C1): the first failure ends the run immediately.** Remaining checks never run. Only the first failure is recorded; no per-check log table.
- Shutdown message is generic ("Unfortunately it looks like you're not paying attention…") with no hint of which check or how many.

### Recovery & exclusion
- **Admin re-open (option B):** a staff action can reset `attention_failed` → `pending`, clearing the failure fields, allowing the participant to retry.
- **Analysis-time exclusion (option C):** exports include `baseline_status` and failure fields; whether an `attention_failed` row is excluded is a filter applied by the researcher in their analysis tool, never auto-decided by the app.

### Admin & export surfaces (staged)
- **Stage A — Django admin:** register `InstrumentResponse` and the participant's timer/status fields in the built-in admin for raw inspection and quick CSV. Minimal effort.
- **Stage B — custom staff view:** a `study-admin/baseline/` page (mirroring the existing `study-admin/conversations/` pattern) showing per-participant baseline duration + computed scores, with two export buttons:
  - `baseline_scores.csv` — flat/wide, one row per participant, all computed scores as columns.
  - `baseline_responses.csv` — long, one row per item-response (a dump of `InstrumentResponse`).
- Both exports include `baseline_status`, duration, and failure fields.

### Flow module
- A single Python module (`study_flow.py`) is the source of truth for participant step order. It is a declarative list of steps; each step has a name, a URL name, and a reference to a completion-predicate method.
- **Completion predicates live as methods on the models** (e.g. `User.has_completed_baseline()`), referenced by name from the flow module. Two predicate shapes: once-ever (takes `user`) and per-topic (takes `user, topic_id`) for the stance/chat steps.
- Views consult `flow.next_step(user, ...)` / `flow.gate(...)` instead of hardcoding redirects.
- The new post-login flow: `login → baseline gate (psych tests) → topic_selection → stance_rating(pre) → chat → stance_rating(post) → analysis/review`. The `attention_failed` terminal state has its own page.
- Paired documentation file `docs/study_flow.md` describes step order, each step's completion predicate, terminal states, and how to add/reorder a step.

## Testing Decisions

**What makes a good test here:** tests assert external behavior of pure-logic modules (given a participant's state, what step do they resolve to? given a set of responses, what scores result?), not implementation details like view internals, template structure, or JS animation. No HTTP/Django-client spinning-up where a pure function call suffices.

**Prior art:** the repo currently has no meaningful test suite, so seams are new. The chosen seams follow the project's existing style of pure-Python data modules (e.g. `topics_data.py`) and model methods.

**Seams (confirmed with user):**

1. **Flow-module seam (primary, highest).** Construct participant instances with various `baseline_status` and model states; assert `flow.next_step(...)` resolves to the correct next step. One seam covers the entire participant journey (login → baseline → topic → stance → chat → stance → analysis) and the `attention_failed` terminal state, without views/templates/HTTP. This is the ideal single seam.

2. **Scoring seam (second).** Test `score_instrument(user, slug)` against hand-computed BFI-2-S and IDAS-R fixtures — including at least one reverse-keyed BFI item and the IDAS-R corrected numbering mapping — to lock the scoring logic. Pure function, no HTTP; verifies the most error-prone data logic.

3. **Attention-check transition seam (third, optional).** A focused test that, given a fixed attention-check position and a simulated number-keypress, yields the `attention_failed` terminal state and records the failure fields. Folds into seam 1 if the flow module owns the failure transition; otherwise a small standalone.

**Out of test scope (manual):** the participant-facing JS — keyboard handling, per-item AJAX save, the 10-second undo toast, the animated transitions, and the 3-second post-failure shutdown sequence — are not unit-tested; they require a browser/E2E layer this repo does not have. They are verified manually during piloting.

## Out of Scope

- **Participant authentication changes:** register / email-verification / login / password-reset flows are reused as-is; no changes to the existing auth model.
- **The chat, stance-rating, analysis, and review features themselves:** only their position in the flow changes (via the flow module); their internals are untouched.
- **A retake/multiple-attempt mechanism:** one attempt ever; the migration to a per-attempt table is deferred (conscious tradeoff).
- **Stored/computed-score snapshots:** scores are computed on demand; a publication-time frozen-score table is deferred.
- **Browser/E2E tests** for the JS survey UX (keyboard, AJAX save, animation, undo toast, shutdown sequence) — manual piloting only.
- **A third instrument:** the generic schema supports it, but adding one is not part of this PRD.
- **Active-vs-idle time split** for the timer; wall-clock duration only.
- **Participant-side revision / back-navigation:** forward-only by design.
- **Randomized attention-check positions:** fixed positions only (per the user's hardcoding decision); letter prompt remains random.
- **Per-check attention logging:** strict first-failure (C1) means only the first failure is recorded; no per-check log table.
- **Publishing to an external issue tracker:** no tracker is configured for this repo; this PRD lives as a markdown file in `docs/`.

## Further Notes

- The two instrument source documents live at `docs/psychological_test/big_five.md` (BFI-2-S) and `docs/psychological_test/idas_r.md` (IDAS-R). The definition module must transcribe their items, reverse-keying flags, and scoring-group mappings faithfully; the IDAS-R numbering discrepancy (factor-table items 43–46 = appendix items 40, 32, 24, 16) must be resolved correctly in code.
- The BFI-2-S recommends its two-item facet scales only be used in samples of ~400+ observations; the definition module should still compute facets (they're cheap, on-demand) but researchers should apply that caveat in analysis.
- The flow module + `docs/study_flow.md` are the primary "I need to change this later" deliverables. They should be the first thing a future maintainer reads.
- All design decisions in this PRD were captured in a `/grilling` design session and are mirrored in the project's memory file for baseline psych battery design.
