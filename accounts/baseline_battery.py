"""
accounts.baseline_battery — flatten the baseline psych battery into frames.

The participant-facing survey walks a single ordered list of "frames":

  * **item frames** -- one real instrument item (BFI-2-S then IDAS-R), with its
    text, 1-5 scale labels, slug, and 1-based item index.
  * **attention frames** -- a "Press the letter X" attention check inserted at
    a hardcoded fixed position in the battery.

This module is pure logic (no Django imports) so it is unit-testable in
isolation, mirroring the ``instruments_data`` seam. The random target *letter*
is supplied by the caller (the view, at render time); the *positions* are fixed
here so the battery structure is deterministic.

Attention-check positions are a PRD-locked decision: "hardcoded fixed
positions in the battery (not randomized)". Three checks, inserted after
BFI-2-S item 10, after BFI-2-S item 20, and after IDAS-R item 20.
"""

from .instruments_data import INSTRUMENT_ORDER, get_instrument


# Fixed attention-check insertion points (PRD: hardcoded fixed positions).
# Each entry is (instrument_slug, item_index_after_which_to_insert).
# Order matters: it is the order in which target letters are consumed.
ATTENTION_CHECK_AFTER = [
    ("bfi_2_s", 10),
    ("bfi_2_s", 20),
    ("idas_r", 20),
]

ATTENTION_CHECK_COUNT = len(ATTENTION_CHECK_AFTER)


def build_battery_frames(attention_letters):
    """Return the flattened, ordered list of frames the client walks.

    ``attention_letters`` is a list of single-character strings, one per
    attention check (length must equal ``ATTENTION_CHECK_COUNT``). The letters
    are randomized per render by the caller; the positions are fixed.

    Frame shapes:
      * item:      {"type": "item", "slug", "item_index", "text", "scale_labels"}
      * attention: {"type": "attention", "target_letter"}

    ``scale_labels`` is the instrument's int->label dict (json.dumps coerces
    the int keys to strings on the way to the template).
    """
    if len(attention_letters) != ATTENTION_CHECK_COUNT:
        raise ValueError(
            "expected {} attention letters, got {}".format(
                ATTENTION_CHECK_COUNT, len(attention_letters)))

    # Per-slug ordered list of item indices after which to insert a check.
    insert_after = {}
    for slug, idx in ATTENTION_CHECK_AFTER:
        insert_after.setdefault(slug, []).append(idx)

    frames = []
    letter_iter = iter(attention_letters)
    for slug in INSTRUMENT_ORDER:
        instrument = get_instrument(slug)
        scale_labels = instrument["scale_labels"]
        for item in instrument["items"]:
            frames.append({
                "type": "item",
                "slug": slug,
                "item_index": item["index"],
                "text": item["text"],
                "scale_labels": scale_labels,
            })
            insert_list = insert_after.get(slug, [])
            if item["index"] in insert_list:
                frames.append({
                    "type": "attention",
                    "target_letter": next(letter_iter),
                })
    return frames


def attention_check_frame_indices():
    """Return the 0-based indices of attention-check frames in the flattened
    list (using placeholder letters). Pure/deterministic; for tests."""
    frames = build_battery_frames(["X"] * ATTENTION_CHECK_COUNT)
    return [i for i, f in enumerate(frames) if f["type"] == "attention"]


def total_frame_count():
    """Return the total number of frames (70 items + 3 attention checks = 73)."""
    return len(build_battery_frames(["X"] * ATTENTION_CHECK_COUNT))
