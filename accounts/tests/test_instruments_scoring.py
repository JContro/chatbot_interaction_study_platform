"""
Pure-Python tests for accounts.instruments_data.

These tests use ``unittest.TestCase`` (no Django dependency in the module
under test) but are discoverable by Django's test runner via
``python manage.py test accounts.tests.test_instruments_scoring``.
"""

import unittest

from accounts.instruments_data import (
    INSTRUMENTS,
    INSTRUMENT_ORDER,
    get_instrument,
    get_item,
    instrument_item_count,
    score_instrument,
)


class BFI2SDefinitionTests(unittest.TestCase):
    """Sanity checks on the BFI-2-S instrument definition."""

    def test_item_count(self):
        self.assertEqual(instrument_item_count("bfi_2_s"), 30)

    def test_reverse_keyed_set(self):
        expected = {
            1, 3, 7, 8, 10, 14, 17, 19, 20, 21, 24, 26, 27, 28, 30,
        }
        actual = {
            item["index"] for item in get_instrument("bfi_2_s")["items"]
            if item["reverse"]
        }
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 15)

    def test_item_indices_are_1_to_30(self):
        indices = [item["index"] for item in get_instrument("bfi_2_s")["items"]]
        self.assertEqual(indices, list(range(1, 31)))

    def test_get_item(self):
        item = get_item("bfi_2_s", 1)
        self.assertEqual(item["index"], 1)
        self.assertEqual(item["text"], "Tends to be quiet.")
        self.assertTrue(item["reverse"])


class BFI2SScoringTests(unittest.TestCase):
    """Scoring behavior for BFI-2-S, including reverse keying."""

    def test_all_neutral_domain_means_are_three(self):
        responses = {i: 3 for i in range(1, 31)}
        scores = score_instrument(responses, "bfi_2_s")
        for domain in [
            "Extraversion", "Agreeableness", "Conscientiousness",
            "Negative Emotionality", "Open-Mindedness",
        ]:
            self.assertEqual(scores[domain], 3.0, domain)
        self.assertTrue(scores["complete"])

    def test_all_neutral_facet_means_are_three(self):
        responses = {i: 3 for i in range(1, 31)}
        scores = score_instrument(responses, "bfi_2_s")
        for facet in [
            "Sociability", "Assertiveness", "Energy Level", "Compassion",
            "Respectfulness", "Trust", "Organization", "Productiveness",
            "Responsibility", "Anxiety", "Depression", "Emotional Volatility",
            "Aesthetic Sensitivity", "Intellectual Curiosity",
            "Creative Imagination",
        ]:
            self.assertEqual(scores[facet], 3.0, facet)

    def test_reverse_keyed_item_affects_domain_and_facet(self):
        # All items 3 except item 1 = 5. Item 1 is reverse-keyed
        # (Extraversion, Sociability). reverse(5) = 1.
        responses = {i: 3 for i in range(1, 31)}
        responses[1] = 5
        scores = score_instrument(responses, "bfi_2_s")

        # Extraversion = [1R, 6, 11, 16, 21R, 26R].
        # Scored values: reverse(5)=1, 3, 3, 3, reverse(3)=3, reverse(3)=3.
        # Sum = 1+3+3+3+3+3 = 16; mean = 16/6.
        expected_extraversion = (1 + 3 + 3 + 3 + 3 + 3) / 6
        self.assertAlmostEqual(scores["Extraversion"], expected_extraversion)

        # Sociability = [1R, 16]. Scored: reverse(5)=1, 3. Mean = 2.0.
        self.assertAlmostEqual(scores["Sociability"], (1 + 3) / 2)

        # Other domains untouched by item 1, should remain 3.0.
        self.assertAlmostEqual(scores["Agreeableness"], 3.0)

    def test_complete_flag_false_when_missing(self):
        responses = {i: 3 for i in range(1, 31)}
        del responses[30]
        scores = score_instrument(responses, "bfi_2_s")
        self.assertFalse(scores["complete"])
        # Groups missing an item still produce a mean over present items.
        # Open-Mindedness = [5, 10R, 15, 20R, 25, 30R]; missing 30 -> 5 items.
        self.assertAlmostEqual(scores["Open-Mindedness"], 3.0)


class IDASRDefinitionTests(unittest.TestCase):
    """Sanity checks on the IDAS-R instrument definition."""

    def test_item_count(self):
        self.assertEqual(instrument_item_count("idas_r"), 40)

    def test_no_reverse_items(self):
        for item in get_instrument("idas_r")["items"]:
            self.assertFalse(item["reverse"])

    def test_item_indices_are_1_to_40(self):
        indices = [item["index"] for item in get_instrument("idas_r")["items"]]
        self.assertEqual(indices, list(range(1, 41)))


class IDASRScoringTests(unittest.TestCase):
    """Scoring behavior for IDAS-R, including the numbering correction."""

    def test_all_twos_total_and_subscales(self):
        responses = {i: 2 for i in range(1, 41)}
        scores = score_instrument(responses, "idas_r")
        self.assertEqual(scores["total"], 80)
        for subscale in [
            "Identity Dialogues (IdD)", "Maladaptive Dialogues (MaD)",
            "Social Dialogues (SoD)", "Supportive Dialogues (SuD)",
            "Spontaneous Dialogues (SpD)", "Ruminative Dialogues (RuD)",
            "Confronting Dialogues (CoD)", "Change of Perspective (ChP)",
        ]:
            self.assertEqual(scores[subscale], 10, subscale)
        self.assertTrue(scores["complete"])

    def test_corrected_numbering_item_40_in_mad_and_sod(self):
        # Item 40 -> MaD and SoD (corrected from factor-table item 43).
        responses = {i: 1 for i in range(1, 41)}
        responses[40] = 5  # delta +4
        scores = score_instrument(responses, "idas_r")
        self.assertEqual(scores["Maladaptive Dialogues (MaD)"], 9)
        self.assertEqual(scores["Social Dialogues (SoD)"], 9)
        # Subscales that do NOT contain 40 stay at baseline 5.
        self.assertEqual(scores["Supportive Dialogues (SuD)"], 5)
        self.assertEqual(scores["Spontaneous Dialogues (SpD)"], 5)
        self.assertEqual(scores["Ruminative Dialogues (RuD)"], 5)
        self.assertEqual(scores["Identity Dialogues (IdD)"], 5)
        self.assertEqual(scores["Confronting Dialogues (CoD)"], 5)
        # ChP contains 40 too, so it rises to 9.
        self.assertEqual(scores["Change of Perspective (ChP)"], 9)

    def test_corrected_numbering_item_32_in_sud_and_chp(self):
        # Item 32 -> SuD and ChP (corrected from factor-table item 44).
        responses = {i: 1 for i in range(1, 41)}
        responses[32] = 5
        scores = score_instrument(responses, "idas_r")
        self.assertEqual(scores["Supportive Dialogues (SuD)"], 9)
        self.assertEqual(scores["Change of Perspective (ChP)"], 9)
        # Subscales without 32 stay at baseline.
        self.assertEqual(scores["Maladaptive Dialogues (MaD)"], 5)
        self.assertEqual(scores["Spontaneous Dialogues (SpD)"], 5)

    def test_corrected_numbering_item_24_in_spd_and_chp(self):
        # Item 24 -> SpD and ChP (corrected from factor-table item 45).
        responses = {i: 1 for i in range(1, 41)}
        responses[24] = 5
        scores = score_instrument(responses, "idas_r")
        self.assertEqual(scores["Spontaneous Dialogues (SpD)"], 9)
        self.assertEqual(scores["Change of Perspective (ChP)"], 9)
        self.assertEqual(scores["Ruminative Dialogues (RuD)"], 5)
        self.assertEqual(scores["Supportive Dialogues (SuD)"], 5)

    def test_corrected_numbering_item_16_in_rud_and_chp(self):
        # Item 16 -> RuD and ChP (corrected from factor-table item 46).
        responses = {i: 1 for i in range(1, 41)}
        responses[16] = 5
        scores = score_instrument(responses, "idas_r")
        self.assertEqual(scores["Ruminative Dialogues (RuD)"], 9)
        self.assertEqual(scores["Change of Perspective (ChP)"], 9)
        self.assertEqual(scores["Spontaneous Dialogues (SpD)"], 5)
        self.assertEqual(scores["Maladaptive Dialogues (MaD)"], 5)

    def test_all_four_corrected_items_set_to_five(self):
        # Locking the full correction: 40, 32, 24, 16 = 5, rest = 1.
        responses = {i: 1 for i in range(1, 41)}
        for idx in (40, 32, 24, 16):
            responses[idx] = 5
        scores = score_instrument(responses, "idas_r")
        # Each subscale containing exactly one corrected item -> 9.
        self.assertEqual(scores["Maladaptive Dialogues (MaD)"], 9)
        self.assertEqual(scores["Social Dialogues (SoD)"], 9)
        self.assertEqual(scores["Supportive Dialogues (SuD)"], 9)
        self.assertEqual(scores["Spontaneous Dialogues (SpD)"], 9)
        self.assertEqual(scores["Ruminative Dialogues (RuD)"], 9)
        # ChP contains all four corrected items -> 5+5+5+5+1 = 21.
        self.assertEqual(scores["Change of Perspective (ChP)"], 21)
        # Subscales with no corrected item stay at baseline 5.
        self.assertEqual(scores["Identity Dialogues (IdD)"], 5)
        self.assertEqual(scores["Confronting Dialogues (CoD)"], 5)
        # total = 36 ones + 4 fives = 36 + 20 = 56.
        self.assertEqual(scores["total"], 56)

    def test_complete_flag_false_when_missing(self):
        responses = {i: 2 for i in range(1, 41)}
        del responses[40]
        scores = score_instrument(responses, "idas_r")
        self.assertFalse(scores["complete"])


class InstrumentRegistryTests(unittest.TestCase):
    """Registry-level sanity checks."""

    def test_instrument_order(self):
        self.assertEqual(INSTRUMENT_ORDER, ["bfi_2_s", "idas_r"])

    def test_instruments_keys_match_order(self):
        self.assertEqual(set(INSTRUMENTS), set(INSTRUMENT_ORDER))

    def test_get_instrument_missing_raises(self):
        with self.assertRaises(KeyError):
            get_instrument("does_not_exist")

    def test_get_item_missing_raises(self):
        with self.assertRaises(KeyError):
            get_item("bfi_2_s", 999)

    def test_scale_labels_present(self):
        for slug in INSTRUMENT_ORDER:
            labels = get_instrument(slug)["scale_labels"]
            self.assertEqual(set(labels), {1, 2, 3, 4, 5}, slug)


if __name__ == "__main__":
    unittest.main()
