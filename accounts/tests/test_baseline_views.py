"""
Tests for the baseline psych battery views and the pure-logic flattening seam.

Two layers:
  * ``BuildBatteryFramesTests`` exercises ``accounts.baseline_battery`` directly
    (PRD testing seam: the deterministic frame flattening). No HTTP.
  * ``BaselineViewTests`` drives the seven baseline endpoints via the Django
    test client, asserting response codes, JSON contracts, and the User /
    InstrumentResponse state transitions the views perform.
"""

import json

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, InstrumentResponse
from accounts.baseline_battery import (
    build_battery_frames,
    ATTENTION_CHECK_AFTER,
    ATTENTION_CHECK_COUNT,
    attention_check_frame_indices,
    total_frame_count,
)
from accounts.instruments_data import INSTRUMENT_ORDER, instrument_item_count


# ---------------------------------------------------------------------------
# Pure-logic: frame flattening.
# ---------------------------------------------------------------------------

class BuildBatteryFramesTests(TestCase):
    """Lock the deterministic flattening of the battery into frames."""

    def test_total_frame_count_is_70_items_plus_3_attention_checks(self):
        frames = build_battery_frames(["a", "b", "c"])
        self.assertEqual(ATTENTION_CHECK_COUNT, 3)
        self.assertEqual(len(frames), 73)
        self.assertEqual(total_frame_count(), 73)
        item_count = sum(1 for f in frames if f["type"] == "item")
        attention_count = sum(1 for f in frames if f["type"] == "attention")
        self.assertEqual(item_count, 70)
        self.assertEqual(attention_count, 3)

    def test_attention_frames_at_fixed_positions_matching_constant(self):
        frames = build_battery_frames(["a", "b", "c"])
        # The authoritative positions come from ATTENTION_CHECK_AFTER; the
        # frames produced must place an attention frame immediately after the
        # named item, in the order the constant declares.
        expected_after = list(ATTENTION_CHECK_AFTER)
        attention_positions = attention_check_frame_indices()
        self.assertEqual(attention_positions, [10, 21, 52])
        # For each attention frame, the preceding frame must be the item named
        # by the matching entry of ATTENTION_CHECK_AFTER (in order).
        for k, pos in enumerate(attention_positions):
            self.assertGreater(pos, 0)
            prev = frames[pos - 1]
            self.assertEqual(prev["type"], "item")
            slug, idx = expected_after[k]
            self.assertEqual(prev["slug"], slug)
            self.assertEqual(prev["item_index"], idx)

    def test_attention_frames_carry_supplied_letters_in_order(self):
        frames = build_battery_frames(["x", "y", "q"])
        letters = [f["target_letter"] for f in frames
                   if f["type"] == "attention"]
        self.assertEqual(letters, ["x", "y", "q"])

    def test_item_frame_shape_has_required_keys(self):
        frames = build_battery_frames(["a", "b", "c"])
        for f in frames:
            if f["type"] == "item":
                self.assertEqual(
                    set(f.keys()),
                    {"type", "slug", "item_index", "text", "scale_labels"})
                self.assertIn(f["slug"], INSTRUMENT_ORDER)
                self.assertIsInstance(f["item_index"], int)
                self.assertIsInstance(f["text"], str)
                self.assertIsInstance(f["scale_labels"], dict)
        for f in frames:
            if f["type"] == "attention":
                self.assertEqual(set(f.keys()), {"type", "target_letter"})

    def test_exact_expected_sequence_locks_flattening(self):
        """Assert the full frame sequence so the flattening order is frozen."""
        frames = build_battery_frames(["a", "b", "c"])

        # BFI-2-S items 1..10 -> frames 0..9
        for i in range(10):
            self.assertEqual(frames[i]["type"], "item")
            self.assertEqual(frames[i]["slug"], "bfi_2_s")
            self.assertEqual(frames[i]["item_index"], i + 1)

        # Frame 10 is the first attention check.
        self.assertEqual(frames[10]["type"], "attention")
        self.assertEqual(frames[10]["target_letter"], "a")

        # BFI-2-S items 11..20 -> frames 11..20
        for i in range(11, 21):
            self.assertEqual(frames[i]["type"], "item")
            self.assertEqual(frames[i]["slug"], "bfi_2_s")
            self.assertEqual(frames[i]["item_index"], i)

        # Frame 21 is the second attention check (right after bfi item 20).
        self.assertEqual(frames[21]["type"], "attention")
        self.assertEqual(frames[21]["target_letter"], "b")

        # BFI-2-S items 21..30 -> frames 22..31
        for i in range(22, 32):
            self.assertEqual(frames[i]["type"], "item")
            self.assertEqual(frames[i]["slug"], "bfi_2_s")
            self.assertEqual(frames[i]["item_index"], i - 1)

        # IDAS-R items 1..20 -> frames 32..51
        for i in range(32, 52):
            self.assertEqual(frames[i]["type"], "item")
            self.assertEqual(frames[i]["slug"], "idas_r")
            self.assertEqual(frames[i]["item_index"], i - 31)

        # Frame 52 is the third attention check (right after idas item 20).
        self.assertEqual(frames[52]["type"], "attention")
        self.assertEqual(frames[52]["target_letter"], "c")

        # IDAS-R items 21..40 -> frames 53..72
        for i in range(53, 73):
            self.assertEqual(frames[i]["type"], "item")
            self.assertEqual(frames[i]["slug"], "idas_r")
            self.assertEqual(frames[i]["item_index"], i - 32)

    def test_wrong_number_of_attention_letters_raises(self):
        with self.assertRaises(ValueError):
            build_battery_frames(["a", "b"])
        with self.assertRaises(ValueError):
            build_battery_frames(["a", "b", "c", "d"])
        with self.assertRaises(ValueError):
            build_battery_frames([])


# ---------------------------------------------------------------------------
# HTTP / view contract.
# ---------------------------------------------------------------------------

class BaseBaselineViewTests(TestCase):
    """Shared setup: a verified, logged-in participant."""

    def setUp(self):
        self.user = User.objects.create_user(email='t@t.com', password='pw')
        self.user.is_email_verified = True
        self.user.save()
        self.client = Client()
        self.client.force_login(self.user)

    def _post_json(self, url_name, payload):
        url = reverse(url_name)
        return self.client.post(url, data=json.dumps(payload),
                                 content_type='application/json')


class BaselineSaveViewTests(BaseBaselineViewTests):

    def test_save_creates_row(self):
        resp = self._post_json('baseline_save',
                                {"slug": "bfi_2_s", "item_index": 1, "value": 3})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["ok"])
        rows = InstrumentResponse.objects.filter(
            user=self.user, instrument_slug="bfi_2_s", item_index=1)
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.first().value, 3)

    def test_save_updates_existing_row(self):
        self._post_json('baseline_save',
                        {"slug": "bfi_2_s", "item_index": 1, "value": 3})
        self._post_json('baseline_save',
                        {"slug": "bfi_2_s", "item_index": 1, "value": 4})
        rows = InstrumentResponse.objects.filter(
            user=self.user, instrument_slug="bfi_2_s", item_index=1)
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.first().value, 4)

    def test_save_last_item_completes_battery(self):
        # The battery is "complete" once the final instrument's final item is
        # saved. Save all 40 IDAS-R items; the last save (item 40) must flip the
        # user to completed and return a redirect.
        last_count = instrument_item_count("idas_r")
        self.assertEqual(last_count, 40)
        last_response = None
        for item_index in range(1, last_count + 1):
            last_response = self._post_json(
                'baseline_save',
                {"slug": "idas_r", "item_index": item_index, "value": 3})
        self.assertEqual(last_response.status_code, 200)
        body = last_response.json()
        self.assertTrue(body["battery_complete"])
        self.assertIn("redirect", body)
        self.user.refresh_from_db()
        self.assertEqual(self.user.baseline_status, 'completed')
        self.assertIsNotNone(self.user.baseline_completed_at)

    def test_save_validation_value_out_of_range(self):
        resp = self._post_json('baseline_save',
                                {"slug": "bfi_2_s", "item_index": 1, "value": 6})
        self.assertEqual(resp.status_code, 400)

    def test_save_validation_unknown_slug(self):
        resp = self._post_json('baseline_save',
                                {"slug": "nope", "item_index": 1, "value": 3})
        self.assertEqual(resp.status_code, 400)

    def test_save_validation_missing_fields(self):
        resp = self._post_json('baseline_save', {"slug": "bfi_2_s"})
        self.assertEqual(resp.status_code, 400)
        resp = self._post_json('baseline_save',
                                {"item_index": 1, "value": 3})
        self.assertEqual(resp.status_code, 400)

    def test_save_invalid_json_returns_400(self):
        url = reverse('baseline_save')
        resp = self.client.post(url, data='not-json',
                                 content_type='application/json')
        self.assertEqual(resp.status_code, 400)


class BaselineFailViewTests(BaseBaselineViewTests):

    def test_fail_marks_terminal_state(self):
        resp = self._post_json('baseline_fail',
                                {"item_index": 11, "keystroke": "3"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["ok"])
        self.assertIn("redirect", body)
        self.user.refresh_from_db()
        self.assertEqual(self.user.baseline_status, 'attention_failed')
        self.assertEqual(self.user.baseline_failed_item_index, 11)
        self.assertEqual(self.user.baseline_failed_keystroke, "3")

    def test_fail_is_idempotent_no_500_on_repeat(self):
        self._post_json('baseline_fail', {"item_index": 11, "keystroke": "3"})
        resp = self._post_json('baseline_fail',
                                {"item_index": 22, "keystroke": "5"})
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        # The first failure is the one recorded; the second is a no-op state-wise
        # (the view returns early for terminal users).
        self.assertEqual(self.user.baseline_status, 'attention_failed')


class BaselineUndoViewTests(BaseBaselineViewTests):

    def test_undo_deletes_response_row(self):
        self._post_json('baseline_save',
                        {"slug": "bfi_2_s", "item_index": 1, "value": 3})
        self.assertEqual(
            InstrumentResponse.objects.filter(
                user=self.user, instrument_slug="bfi_2_s", item_index=1).count(),
            1)
        resp = self._post_json('baseline_undo',
                                {"slug": "bfi_2_s", "item_index": 1})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["ok"])
        self.assertEqual(
            InstrumentResponse.objects.filter(
                user=self.user, instrument_slug="bfi_2_s", item_index=1).count(),
            0)


class BaselineSurveyGetStatesTests(BaseBaselineViewTests):

    def test_pending_and_started_returns_200(self):
        self.user.baseline_started_at = timezone.now()
        self.user.save(update_fields=["baseline_started_at"])
        resp = self.client.get(reverse('baseline_survey'))
        self.assertEqual(resp.status_code, 200)
        # Context carries the data the template needs.
        self.assertContains(resp, 'data-frames=')
        self.assertContains(resp, 'data-resume-index=')
        self.assertContains(resp, 'data-save-url=')

    def test_completed_redirects_to_topic_selection(self):
        self.user.baseline_status = 'completed'
        self.user.baseline_completed_at = timezone.now()
        self.user.save(update_fields=["baseline_status",
                                       "baseline_completed_at"])
        resp = self.client.get(reverse('baseline_survey'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], reverse('topic_selection'))

    def test_pending_and_not_started_redirects_to_intro(self):
        # Pending + no baseline_started_at -> view redirects to baseline_intro.
        resp = self.client.get(reverse('baseline_survey'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], reverse('baseline_intro'))


class BaselinePageAndStartTests(BaseBaselineViewTests):

    def test_baseline_intro_get_returns_200(self):
        resp = self.client.get(reverse('baseline_intro'))
        self.assertEqual(resp.status_code, 200)

    def test_baseline_failed_get_returns_200_for_terminal_user(self):
        self.user.baseline_status = 'attention_failed'
        self.user.save(update_fields=["baseline_status"])
        resp = self.client.get(reverse('baseline_failed'))
        self.assertEqual(resp.status_code, 200)

    def test_baseline_start_post_sets_started_at(self):
        self.assertIsNone(self.user.baseline_started_at)
        resp = self._post_json('baseline_start', {})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["redirect"], reverse('baseline_survey'))
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.baseline_started_at)

    def test_baseline_start_idempotent_does_not_reset_started_at(self):
        self._post_json('baseline_start', {})
        self.user.refresh_from_db()
        first = self.user.baseline_started_at
        self.assertIsNotNone(first)
        # A second start should not overwrite the original timestamp.
        self._post_json('baseline_start', {})
        self.user.refresh_from_db()
        self.assertEqual(self.user.baseline_started_at, first)
