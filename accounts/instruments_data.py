"""
Psychological instrument definitions and scoring for the chatbot study platform.

Instruments are defined here in plain Python (not in the database) so that the
item text, scale labels, reverse-keying rules, and scoring groups live in one
auditable place. Scores are computed on demand by ``score_instrument`` from a
dict of responses; nothing is persisted by this module.

Instruments
-----------
* **BFI-2-S** -- Big Five Inventory-2 Short Form. 30 items on a 1-5 scale.
  Reverse-keyed items are scored as ``6 - raw_value`` before averaging. The
  two-item facet scales have limited reliability: per the BFI-2-S authors, they
  should only be interpreted in samples with approximately 400 or more
  observations. Domain scales are reliable enough for individual use.
* **IDAS-R** -- Internal Dialogical Activity Scale - Revised. 40 items on a
  1-5 scale, no reverse-keyed items. Scored by summing five items per
  subscale plus an overall total.

IDAS-R numbering correction
---------------------------
The IDAS-R factor table in the source document lists items 43-46, which do not
exist in the 40-item appendix listing. Per the document's own note, those
factor-table numbers map back to the appendix numbering as
43->40, 44->32, 45->24, 46->16. The subscale item lists below apply this
correction. Note that item 40 appears in both Maladaptive Dialogues and Social
Dialogues, and items 40/32/24/16 each appear in Change of Perspective -- this
overlap is intentional and is transcribed verbatim from the source.

This module has NO Django imports and is importable without configured
settings.
"""

# BFI-2-S scale labels (1-5).
BFI_2_S_SCALE = {
    1: "Disagree strongly",
    2: "Disagree a little",
    3: "Neutral; no opinion",
    4: "Agree a little",
    5: "Agree strongly",
}

# IDAS-R scale labels (1-5).
IDAS_R_SCALE = {
    1: "Never",
    2: "Seldom",
    3: "Sometimes",
    4: "Often",
    5: "Very Often",
}

# Reverse-keyed BFI-2-S item indices (items marked "R" in the Domain Scales
# scoring key).
BFI_2_S_REVERSE_ITEMS = {
    1, 21, 26,   # Extraversion
    7, 17, 27,   # Agreeableness
    3, 8, 28,    # Conscientiousness
    14, 19, 24,  # Negative Emotionality
    10, 20, 30,  # Open-Mindedness
}

# BFI-2-S domain scoring groups (item number lists from the Domain Scales table).
BFI_2_S_DOMAINS = {
    "Extraversion": [1, 6, 11, 16, 21, 26],
    "Agreeableness": [2, 7, 12, 17, 22, 27],
    "Conscientiousness": [3, 8, 13, 18, 23, 28],
    "Negative Emotionality": [4, 9, 14, 19, 24, 29],
    "Open-Mindedness": [5, 10, 15, 20, 25, 30],
}

# BFI-2-S facet scoring groups (item number lists from the Facet Scales table).
BFI_2_S_FACETS = {
    "Sociability": [1, 16],
    "Assertiveness": [6, 21],
    "Energy Level": [11, 26],
    "Compassion": [2, 17],
    "Respectfulness": [7, 22],
    "Trust": [12, 27],
    "Organization": [3, 18],
    "Productiveness": [8, 23],
    "Responsibility": [13, 28],
    "Anxiety": [4, 19],
    "Depression": [9, 24],
    "Emotional Volatility": [14, 29],
    "Aesthetic Sensitivity": [5, 20],
    "Intellectual Curiosity": [10, 25],
    "Creative Imagination": [15, 30],
}

# IDAS-R subscale scoring groups (corrected numbering applied).
IDAS_R_SUBSCALES = {
    "Identity Dialogues (IdD)": [33, 25, 17, 9, 1],
    "Maladaptive Dialogues (MaD)": [34, 26, 18, 2, 40],
    "Social Dialogues (SoD)": [35, 27, 19, 11, 40],
    "Supportive Dialogues (SuD)": [36, 28, 20, 12, 32],
    "Spontaneous Dialogues (SpD)": [37, 29, 21, 13, 24],
    "Ruminative Dialogues (RuD)": [38, 30, 22, 14, 16],
    "Confronting Dialogues (CoD)": [39, 31, 23, 15, 7],
    "Change of Perspective (ChP)": [40, 32, 24, 16, 8],
}


def _bfi_2_s_items():
    """Build the BFI-2-S item list, marking reverse-keyed items."""
    texts = [
        "Tends to be quiet.",
        "Is compassionate, has a soft heart.",
        "Tends to be disorganized.",
        "Worries a lot.",
        "Is fascinated by art, music, or literature.",
        "Is dominant, acts as a leader.",
        "Is sometimes rude to others.",
        "Has difficulty getting started on tasks.",
        "Tends to feel depressed, blue.",
        "Has little interest in abstract ideas.",
        "Is full of energy.",
        "Assumes the best about people.",
        "Is reliable, can always be counted on.",
        "Is emotionally stable, not easily upset.",
        "Is original, comes up with new ideas.",
        "Is outgoing, sociable.",
        "Can be cold and uncaring.",
        "Keeps things neat and tidy.",
        "Is relaxed, handles stress well.",
        "Has few artistic interests.",
        "Prefers to have others take charge.",
        "Is respectful, treats others with respect.",
        "Is persistent, works until the task is finished.",
        "Feels secure, comfortable with self.",
        "Is complex, a deep thinker.",
        "Is less active than other people.",
        "Tends to find fault with others.",
        "Can be somewhat careless.",
        "Is temperamental, gets emotional easily.",
        "Has little creativity.",
    ]
    return [
        {
            "index": i + 1,
            "text": texts[i],
            "reverse": (i + 1) in BFI_2_S_REVERSE_ITEMS,
        }
        for i in range(len(texts))
    ]


def _idas_r_items():
    """Build the IDAS-R item list (no reverse-keyed items)."""
    texts = [
        "I ask myself questions and try to answer them.",
        "My inner dialogues with myself and others hinder me from focusing on what I have to do.",
        "I imagine fictitious scenarios of conversations and events.",
        "When I remember the words that others have spoken to me in the past, I respond to them in my mind.",
        "I play out my internal dilemmas as discussions going on in my thoughts.",
        "In my mind, I discuss past thoughts I've had.",
        "I like to talk with the better side of my personality.",
        "When I don't know something and I cannot ask anybody about it, I try to figure it out in my thoughts.",
        "It is easier for me to make a decision if I first carry out a discussion about it in my thoughts.",
        "Imagining conversations feels strange to me.",
        "Before an important meeting I visualize scenarios of discussions, imagining who will say what.",
        "I \"hear\" the words that were spoken to me in the past as if they are directed to me now.",
        "When I cannot find a definite solution for a conflict, I talk to myself.",
        "I discuss with myself how my failures could have been avoided.",
        "My \"good\" side argues with my \"bad\" side.",
        "When talking to myself, I experience very strong conflicts that prevent me from finding a clear solution.",
        "Thanks to dialogues with myself, I understand myself better.",
        "It is very unpleasant to argue with myself in my thoughts.",
        "In my thoughts, I debate the arguments of someone I am disagreeing with.",
        "I carry on discussions in my mind with the important people in my life.",
        "I talk with myself about those things that are important to me.",
        "Some of the inner dialogues I have with myself and others heighten my sense of misfortune.",
        "My internal conversations make it difficult for me to feel whole.",
        "I discuss my problems with myself as if they are someone else's problems rather than my own.",
        "Through internal discussions, I come to certain truths about my life and myself.",
        "The conversations in my mind upset me.",
        "I continue past conversations with other people in my mind.",
        "When I am alone, I catch myself conversing with someone in my thoughts.",
        "I talk to myself.",
        "I have conversations in my mind which confuse me.",
        "I argue with that part of myself that I do not like.",
        "In my thoughts I take the perspective of someone else.",
        "Thanks to dialogues with myself, I can answer the question, \"Who am I?\"",
        "I would prefer not to carry on internal conversations.",
        "When preparing for a conversation with someone, I practice the conversation in my thoughts.",
        "When I cannot speak with someone in person, I carry on a conversation with him/her in my mind.",
        "I converse with myself.",
        "After failures, I blame myself in my thoughts.",
        "I feel that I am two different people, who argue with each other, each wanting something different.",
        "When I have a difficult choice, I talk the decision over with myself from different points of view.",
    ]
    return [
        {"index": i + 1, "text": texts[i], "reverse": False}
        for i in range(len(texts))
    ]


INSTRUMENTS = {
    "bfi_2_s": {
        "slug": "bfi_2_s",
        "name": "Big Five Inventory-2 Short Form (BFI-2-S)",
        "instruction": (
            "Here are a number of characteristics that may or may not apply to "
            "you. For each statement, indicate the extent to which you agree or "
            "disagree that it describes you."
        ),
        "scale_labels": BFI_2_S_SCALE,
        "items": _bfi_2_s_items(),
        "scoring": {
            "domains": BFI_2_S_DOMAINS,
            "facets": BFI_2_S_FACETS,
        },
    },
    "idas_r": {
        "slug": "idas_r",
        "name": "Internal Dialogical Activity Scale - Revised (IDAS-R)",
        "instruction": (
            "The following statements relate to your thinking about yourself "
            "and others. Read each of them carefully and select the number "
            "that best describes your way of thinking. Please take your time "
            "and think carefully about each item."
        ),
        "scale_labels": IDAS_R_SCALE,
        "items": _idas_r_items(),
        "scoring": {
            "subscales": IDAS_R_SUBSCALES,
            "total": True,
        },
    },
}

# Battery presentation order.
INSTRUMENT_ORDER = ["bfi_2_s", "idas_r"]


def get_instrument(slug):
    """Return the instrument dict for ``slug``.

    Raises ``KeyError`` with a clear message if the slug is unknown.
    """
    if slug not in INSTRUMENTS:
        raise KeyError("Unknown instrument slug: {!r}".format(slug))
    return INSTRUMENTS[slug]


def get_item(slug, item_index):
    """Return the item dict for a 1-based ``item_index`` within an instrument.

    Raises ``KeyError`` if the instrument or item index is unknown.
    """
    instrument = get_instrument(slug)
    for item in instrument["items"]:
        if item["index"] == item_index:
            return item
    raise KeyError(
        "Item index {} not found in instrument {!r}".format(item_index, slug)
    )


def instrument_item_count(slug):
    """Return the number of items in the instrument for ``slug``."""
    return len(get_instrument(slug)["items"])


def _scored_value(item, raw_value):
    """Apply reverse-keying if needed: reverse items are scored as 6 - raw."""
    if item["reverse"]:
        return 6 - raw_value
    return raw_value


def score_instrument(responses, slug):
    """Compute scores for an instrument from a dict of responses.

    ``responses`` maps 1-based item index (int) -> value (int 1..5).

    Returns a dict of computed scores:

    * For ``bfi_2_s``: each domain name -> mean of its items (reverse items
      scored as ``6 - value`` before averaging); each facet name -> mean of
      its 2 items (reverse applied). Includes ``"complete": bool``.
    * For ``idas_r``: each subscale name -> sum of its 5 items; ``"total"`` ->
      sum of all 40 items; ``"complete": bool``.

    Missing items: if a scoring group is missing one or more of its items,
    BFI-2-S means are computed over the present items only (IDAS-R sums reflect
    only present items) and the top-level ``"complete"`` flag is set to
    ``False``. The function never raises on a missing item. ``"complete"`` is
    ``True`` only when every item in the instrument has a response.
    """
    instrument = get_instrument(slug)
    items_by_index = {item["index"]: item for item in instrument["items"]}
    all_indices = set(items_by_index)

    complete = all(idx in responses for idx in all_indices)
    result = {"complete": complete}

    if slug == "bfi_2_s":
        scoring = instrument["scoring"]
        for group_name, group_map in (
            ("domains", scoring["domains"]),
            ("facets", scoring["facets"]),
        ):
            for name, indices in group_map.items():
                values = [
                    _scored_value(items_by_index[idx], responses[idx])
                    for idx in indices
                    if idx in responses
                ]
                if values:
                    result[name] = sum(values) / len(values)
                else:
                    result[name] = None
    elif slug == "idas_r":
        scoring = instrument["scoring"]
        for name, indices in scoring["subscales"].items():
            result[name] = sum(
                responses[idx] for idx in indices if idx in responses
            )
        if scoring.get("total"):
            result["total"] = sum(
                responses[idx] for idx in all_indices if idx in responses
            )
    else:
        raise ValueError("No scoring rule defined for instrument {!r}".format(slug))

    return result
