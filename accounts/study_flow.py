"""
accounts.study_flow — source of truth for the participant journey.

This module is the single declarative description of participant step order.
To change the flow (add, remove, reorder a step), edit this one file.

Flow:
    login -> baseline -> topic_selection -> stance_rating(pre) -> chat
          -> stance_rating(post) -> analysis/review

with ``attention_failed`` as a terminal state (its own page, no progression).

Completion predicates live as methods on the models (see accounts.models.User):
  * once-ever shape: ``predicate(self)`` -> bool
  * per-topic shape:  ``predicate(self, topic_id)`` -> bool

Each step below references the predicate method by name. ``topic_selection`` has
a ``None`` predicate: it is the hub a participant returns to between topics and
is never itself "complete". The ``analysis`` step reuses the ``stance_post``
predicate — a topic is considered "done" once the post-rating exists.

The URL names ``baseline_intro`` and ``baseline_failed`` are referenced here so
the upcoming survey-views branch can wire its views to the exact same names;
``reverse`` is only called at runtime once those URLs exist.
"""

from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout


# Declarative ordered list of participant steps.
STEPS = [
    {"name": "baseline",        "url_name": "baseline_intro",   "predicate": "has_completed_baseline",  "shape": "once"},
    {"name": "topic_selection", "url_name": "topic_selection",  "predicate": None,                       "shape": "once"},
    {"name": "stance_pre",      "url_name": "stance_rating",    "predicate": "has_completed_stance_pre", "shape": "per_topic"},
    {"name": "chat",            "url_name": "chat_topic",       "predicate": "has_completed_chat",       "shape": "per_topic"},
    {"name": "stance_post",     "url_name": "stance_rating_post", "predicate": "has_completed_stance_post", "shape": "per_topic"},
    {"name": "analysis",        "url_name": "analysis",         "predicate": "has_completed_stance_post", "shape": "per_topic"},
]

# Terminal step for participants who fail an attention check during baseline.
TERMINAL_STEP = {"name": "attention_failed", "url_name": "baseline_failed"}

# URL names that are safe landing pages for the baseline-not-complete and
# terminal branches of the gate (used to avoid redirect loops).
_BASELINE_SAFE_URL_NAMES = {"baseline_intro", "baseline_survey"}


def is_terminal(user):
    """True if the user is in the attention_failed terminal state."""
    return user.baseline_status == "attention_failed"


def next_step(user):
    """
    Resolve the next ONCE-ever step for a user.

    Returns the step dict (an entry of STEPS, or TERMINAL_STEP).
    * terminal            -> TERMINAL_STEP (baseline_failed)
    * baseline incomplete -> the baseline step
    * baseline complete   -> the topic_selection step (the hub)
    """
    if is_terminal(user):
        return TERMINAL_STEP

    for step in STEPS:
        if step["shape"] != "once":
            continue
        predicate_name = step["predicate"]
        if predicate_name is None:
            # topic_selection: the fallback hub once baseline is done.
            return step
        predicate = getattr(user, predicate_name)
        if not predicate():
            return step
    # Should not happen (topic_selection is the fallback), but be safe.
    return STEPS[1]


def next_step_for_topic(user, topic_id):
    """
    Resolve the next step WITHIN a single topic's flow.

    Assumes baseline is already complete; if it is not, returns the baseline
    step so the caller can route the user back to the start of the journey.

    Iterates the per_topic steps in order and returns the first whose predicate
    returns False. If all per-topic steps are complete, returns the ``analysis``
    step (the final review page for a completed topic).
    """
    if not user.has_completed_baseline():
        return STEPS[0]  # baseline

    per_topic_steps = [s for s in STEPS if s["shape"] == "per_topic"]
    for step in per_topic_steps:
        predicate = getattr(user, step["predicate"])
        if not predicate(topic_id):
            return step
    # All per-topic steps complete -> analysis is the terminal view for a topic.
    return per_topic_steps[-1]  # analysis


def resolve_url(step, topic_id=None):
    """
    Reverse a step's url_name into a URL path.

    For per-topic steps that require a topic_id kwarg (stance_rating,
    chat_topic, analysis, stance_rating_post), pass ``topic_id``.

    Falls back to returning the url_name string if reverse fails — but the
    names above are expected to resolve at runtime.
    """
    url_name = step["url_name"]
    needs_topic = url_name in {"stance_rating", "stance_rating_post",
                               "chat_topic", "analysis"}
    try:
        if needs_topic and topic_id is not None:
            return reverse(url_name, kwargs={"topic_id": topic_id})
        return reverse(url_name)
    except Exception:
        return url_name


def gate(request):
    """
    Consolidated gate for participant-facing views.

    Returns an HttpResponseRedirect if the user should NOT be on the current
    page, else None. Callers do ``gate = flow.gate(request); if gate is not
    None: return gate``.

    Ordering:
      1. not email-verified          -> logout + login
      2. terminal (attention_failed) -> baseline_failed (unless already there)
      3. baseline incomplete         -> baseline_intro (unless on a baseline
                                         survey page)
      4. otherwise                    -> None (allowed)
    """
    user = request.user

    if not user.is_email_verified:
        logout(request)
        return redirect("login")

    current_url_name = ""
    if request.resolver_match is not None:
        current_url_name = request.resolver_match.url_name or ""

    if is_terminal(user):
        if current_url_name != "baseline_failed":
            return redirect("baseline_failed")
        return None

    if not user.has_completed_baseline():
        if current_url_name not in _BASELINE_SAFE_URL_NAMES:
            return redirect("baseline_intro")
        return None

    return None


def post_login_redirect(user):
    """
    Return the url_name a freshly-logged-in user should be sent to.

    * terminal            -> 'baseline_failed'
    * baseline incomplete -> 'baseline_intro'
    * baseline complete   -> 'topic_selection'

    The view is responsible for calling ``redirect(...)`` with this name.
    """
    if is_terminal(user):
        return "baseline_failed"
    if not user.has_completed_baseline():
        return "baseline_intro"
    return "topic_selection"
