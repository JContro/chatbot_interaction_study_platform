# Study Flow

This document is the prose companion to `accounts/study_flow.py`. Together they
are the primary "I need to change this later" deliverable: the Python module is
the source of truth a participant's request is resolved against at runtime, and
this file explains it for a human maintainer. **If you want to reorder, insert,
or remove a step in the participant journey, read this file, then edit
`STEPS` in `study_flow.py`.**

## The participant journey

A verified, logged-in participant moves through these steps:

```
login → baseline (psych tests) → topic_selection → stance_rating(pre)
      → chat → stance_rating(post) → analysis/review
                              ↑__________________________|
                       (returns to topic_selection after each topic)
```

The `baseline` step is **new**: it is the first thing a freshly-verified
participant does, before topic selection. It is a one-attempt-ever psychology
battery (BFI-2-S then IDAS-R). See the [Baseline battery](#the-baseline-battery)
section below and `docs/prd_baseline_psych_battery.md` for full detail.

### Why a flow module?

Before this module, each view hardcoded its own
`if not request.user.is_email_verified: logout + redirect('login')` block, and
post-login went straight to `topic_selection`. Adding the baseline step the
"old way" would have meant editing every view's redirect and duplicating the
gate. Instead:

- **Step order lives in one declarative list** (`STEPS`). Reordering or
  inserting a step is a one-file edit.
- **Completion predicates live as methods on the models** (e.g.
  `User.has_completed_baseline()`), referenced *by name* from the flow module.
  The flow module stays a thin list; the logic stays testable alongside the
  data it queries.
- **Gating is consolidated.** Views call `flow.gate(request)` instead of
  re-implementing the email-verified + baseline checks.
- **Post-login routing is one call.** `flow.post_login_redirect(user)` decides
  where a freshly-logged-in user goes (baseline, topic selection, or the
  attention-failed terminal page).

## The `STEPS` list

Each step is a dict with a `name` (human label), a `url_name` (the Django URL
name to route to), a `predicate` (the *name* of a `User` method that returns
`True` when the step is complete), and a `shape`:

- `shape: "once"` — a once-ever step. The predicate takes just `(self)` (the
  user). Used for the baseline gate.
- `shape: "per_topic"` — a step repeated for each topic. The predicate takes
  `(self, topic_id)`. Used for the stance/chat steps.

| Step name        | URL name            | Predicate                    | Shape     |
| :--------------- | :------------------ | :--------------------------- | :-------- |
| `baseline`       | `baseline_intro`    | `has_completed_baseline`     | once      |
| `topic_selection`| `topic_selection`   | _none_ (hub, never "done")   | once      |
| `stance_pre`     | `stance_rating`     | `has_completed_stance_pre`   | per_topic |
| `chat`           | `chat_topic`        | `has_completed_chat`         | per_topic |
| `stance_post`    | `stance_rating_post`| `has_completed_stance_post`  | per_topic |
| `analysis`       | `analysis`          | `has_completed_stance_post`  | per_topic |

`topic_selection` has no predicate: it is the hub a participant returns to
between topics, so it is never itself "complete" — once the baseline is done,
`next_step` resolves to it as the fallback.

`analysis` reuses the `has_completed_stance_post` predicate: a topic is
considered "done" once the post-conversation stance rating exists, after which
the analysis/review view is the natural destination.

## Terminal state: `attention_failed`

A separate `TERMINAL_STEP` (`{"name": "attention_failed", "url_name": "baseline_failed"}`)
handles the one terminal state in the flow. If a participant fails a baseline
attention check, `baseline_status` becomes `attention_failed` and:

- `flow.is_terminal(user)` returns `True`.
- `flow.next_step(user)` returns the `attention_failed` step.
- `flow.post_login_redirect(user)` returns `'baseline_failed'`.
- `flow.gate(request)` redirects them to the failed page from any other
  participant view (the failed page itself is exempt, so there is no loop).

There is **no** "completed-but-terminal" ambiguity: `completed` and
`attention_failed` are distinct `baseline_status` values (see
`accounts/models.py`, `BASELINE_STATUS_CHOICES`). The full set is
`pending | completed | attention_failed | abandoned`. `abandoned` is
non-terminal — an abandoned participant is routed back to the baseline to
resume.

## How to add / reorder a step

1. **Add a completion predicate.** Put it on the model that owns the data (a
   `User` method for once-ever steps, or a query against the relevant model for
   per-topic steps). Keep it a thin query wrapper — no flow logic inside. See
   `has_completed_stance_pre` in `models.py` for the pattern.
2. **Add the step to `STEPS`** in `accounts/study_flow.py` in the position you
   want it. Give it a `name`, `url_name`, `predicate` (the method name as a
   string), and `shape`.
3. **Wire the URL** in `accounts/urls.py` with the `url_name` you used.
4. **Add the view.** Start it with the standard gate:
   ```python
   gate = flow.gate(request)
   if gate is not None:
       return gate
   ```
   so the rest of the flow is enforced. On completion, redirect to
   `flow.next_step(...)` / `flow.next_step_for_topic(...)` rather than
   hardcoding the next URL.
5. **Update this table** and any relevant narrative above.

To *reorder*, just move the step dict within `STEPS`. To *remove*, delete the
dict (and consider whether its predicate is still used elsewhere).

## API reference (`accounts/study_flow.py`)

- `STEPS` — the declarative step list (source of truth for order).
- `TERMINAL_STEP` — the attention-failed terminal step.
- `is_terminal(user) -> bool`
- `next_step(user) -> dict` — the next *once-ever* step for a user (baseline
  if incomplete, topic_selection once baseline is done, attention_failed if
  terminal).
- `next_step_for_topic(user, topic_id) -> dict` — the next step *within* a
  topic's flow (assumes baseline done; returns the baseline step if not).
  Returns `analysis` when all per-topic steps for that topic are complete.
- `resolve_url(step, topic_id=None) -> str` — `reverse()` a step's URL.
- `gate(request) -> HttpResponseRedirect | None` — the consolidated gate for
  participant-facing views. Returns a redirect if the user should not be on the
  current page (unverified → login, terminal → baseline_failed, baseline
  incomplete → baseline_intro), else `None`. Self-loop-safe: the baseline views
  are exempt.
- `post_login_redirect(user) -> str` — URL name for a freshly-logged-in user.

## The baseline battery

The baseline step presents two psychology instruments, one item at a time, in
this fixed order:

1. **BFI-2-S** (`bfi_2_s`) — 30 items, 5 domains + 15 facets, some reverse-keyed.
2. **IDAS-R** (`idas_r`) — 40 items, total + 8 subscales, no reverse-keyed items.

### Where the instrument content lives

Instrument definitions — item text, 1–5 scale labels, reverse-keying flags, and
scoring-group mappings — live in **`accounts/instruments_data.py`**, keyed by
slug (`bfi_2_s`, `idas_r`). This is a plain-Python data module (no Django, no
database). **Adding or fixing an instrument is a code edit, not a migration.**
The generic response table (`InstrumentResponse`: `user`, `instrument_slug`,
`item_index`, `value`, with `unique_together = (user, instrument_slug,
item_index)`) means a third instrument could be added later with no schema
change.

Source documents: `docs/psychological_test/big_five.md` (BFI-2-S) and
`docs/psychological_test/idas_r.md` (IDAS-R).

### Scoring

Scores are **computed on demand** from raw responses + the definition module by
`score_instrument(responses, slug)` — they are never stored. A scoring-key fix
therefore applies instantly to all participants with no stale snapshots. A path
to publication-time snapshotting (a management command writing a frozen score
table) is left open but out of scope.

### A scoring caveat to apply at analysis time

The BFI-2-S authors recommend its two-item facet scales only be interpreted in
samples with **approximately 400 or more observations**. The definition module
still computes facets (they are cheap and on demand), but researchers should
apply this caveat in their analysis rather than treating individual facet
scores as reliable. Domain scales are reliable enough for individual use.

### IDAS-R numbering correction

The IDAS-R source doc has a numbering discrepancy: its factor table references
items 43–46, which do not exist in the 40-item appendix. Per the document's own
note, these map back to the appendix numbering as **43→40, 44→32, 45→24, 46→16**.
The corrected subscale item lists are encoded in `instruments_data.py`. Note
that item 40 appears in both Maladaptive Dialogues and Social Dialogues, and
items 40/32/24/16 each appear in Change of Perspective — this overlap is
intentional and transcribed verbatim.

### Attempts, timing, and attention checks

- **One attempt, ever.** Timer fields live on the participant:
  `baseline_started_at` (set when the intro "Start" button is pressed) and
  `baseline_completed_at` (set when the final item save is confirmed). Duration
  = difference. Wall-clock only; no active-vs-idle split. A future "allow
  retake" change would require a migration to a per-attempt table — a conscious
  tradeoff for a clean protocol.
- **Attention checks:** three, at hardcoded fixed positions (not randomized);
  the prompt letter is random per render. Pass (correct letter) advances;
  wrong non-number letter re-asks; a number key fails. The first failure ends
  the run immediately and sets `baseline_status = attention_failed` (only the
  first failure is recorded; there is no per-check log table).
- **Admin re-open:** staff can reset `attention_failed → pending`, clearing the
  failure fields, to give a recruited participant a second chance.
- **Analysis-time exclusion:** exports include `baseline_status` and failure
  fields; whether an `attention_failed` row is excluded is a filter the
  researcher applies in their analysis tool, never auto-decided by the app.

## Testing the flow

Per the project's testing philosophy, the flow is tested as a pure-logic seam
(`accounts/tests/test_study_flow.py`): construct users with various
`baseline_status` and model states and assert what `next_step` /
`next_step_for_topic` / `is_terminal` resolve to — no HTTP, views, or
templates. Scoring is tested in `accounts/tests/test_instruments_scoring.py`,
and the frame-flattening + view contracts in
`accounts/tests/test_baseline_views.py`. The participant-facing JS (keyboard
handling, AJAX save, undo toast, animations, shutdown sequence) is verified
manually during piloting.
