import csv
import io
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, InstrumentResponse
from accounts.admin import reset_baseline_attention_failed


class AdminBaselineExportsTestCase(TestCase):
    """Tests for baseline battery admin views and exports."""

    def setUp(self):
        """Create staff user and test participants."""
        self.client = Client()

        # Create staff user
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            is_staff=True,
            is_email_verified=True,
        )

        # Create regular participant
        self.participant = User.objects.create_user(
            email='participant@example.com',
            password='partpass123',
            is_email_verified=True,
        )

        # Create completed participant with full responses
        self.completed_participant = User.objects.create_user(
            email='completed@example.com',
            password='completedpass123',
            is_email_verified=True,
            baseline_status='completed',
        )

    def test_admin_baseline_view_get_200(self):
        """Test that the admin baseline view returns 200 for staff users."""
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin_baseline'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/admin_baseline.html')

    def test_admin_baseline_view_non_staff_redirect(self):
        """Test that non-staff users are redirected."""
        self.client.force_login(self.participant)
        response = self.client.get(reverse('admin_baseline'), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('topic_selection'))

    def test_export_scores_view_200(self):
        """Test export scores view returns 200 and valid CSV."""
        # Create full BFI-2-S responses (all 30 items with value 3)
        for i in range(1, 31):
            InstrumentResponse.objects.create(
                user=self.completed_participant,
                instrument_slug='bfi_2_s',
                item_index=i,
                value=3,
            )

        # Create full IDAS-R responses (all 40 items with value 2)
        for i in range(1, 41):
            InstrumentResponse.objects.create(
                user=self.completed_participant,
                instrument_slug='idas_r',
                item_index=i,
                value=2,
            )

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin_baseline_export_scores'))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('baseline_scores.csv', response['Content-Disposition'])

        # Parse CSV
        csv_content = response.content.decode('utf-8')

        # Check header contains expected score columns
        self.assertIn('bfi_2_s__Extraversion', csv_content)
        self.assertIn('idas_r__total', csv_content)
        self.assertIn('bfi_2_s__complete', csv_content)
        self.assertIn('idas_r__complete', csv_content)

        # Parse rows
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        # Find completed participant row
        participant_row = None
        for row in rows:
            if row['user_email'] == self.completed_participant.email:
                participant_row = row
                break

        self.assertIsNotNone(participant_row)

    def test_export_scores_csv_content(self):
        """Test that export scores CSV contains correct computed values."""
        # Create full BFI-2-S responses (all 30 items with value 3)
        for i in range(1, 31):
            InstrumentResponse.objects.create(
                user=self.completed_participant,
                instrument_slug='bfi_2_s',
                item_index=i,
                value=3,
            )

        # Create full IDAS-R responses (all 40 items with value 2)
        for i in range(1, 41):
            InstrumentResponse.objects.create(
                user=self.completed_participant,
                instrument_slug='idas_r',
                item_index=i,
                value=2,
            )

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin_baseline_export_scores'))

        csv_content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        # Find completed participant row
        participant_row = None
        for row in rows:
            if row['user_email'] == self.completed_participant.email:
                participant_row = row
                break

        self.assertIsNotNone(participant_row)

        # BFI-2-S all value 3 -> mean 3.0 (no reverse items in this check, all same)
        # Since all items are 3, all domains and facets should be 3.0
        self.assertEqual(participant_row['bfi_2_s__Extraversion'], '3.0')

        # IDAS-R all value 2 -> sum per subscale = 10 (5 items * 2), total = 80 (40 items * 2)
        self.assertEqual(participant_row['idas_r__total'], '80')

    def test_export_responses_view_200(self):
        """Test export responses view returns 200 and valid CSV."""
        # Create full responses
        for i in range(1, 31):
            InstrumentResponse.objects.create(
                user=self.completed_participant,
                instrument_slug='bfi_2_s',
                item_index=i,
                value=3,
            )

        for i in range(1, 41):
            InstrumentResponse.objects.create(
                user=self.completed_participant,
                instrument_slug='idas_r',
                item_index=i,
                value=2,
            )

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin_baseline_export_responses'))

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('baseline_responses.csv', response['Content-Disposition'])

        # Parse CSV
        csv_content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        # Should have 70 data rows (30 BFI + 40 IDAS)
        self.assertEqual(len(rows), 70)

        # Check header
        reader = csv.DictReader(io.StringIO(csv_content))
        fieldnames = reader.fieldnames
        self.assertIn('user_email', fieldnames)
        self.assertIn('baseline_status', fieldnames)
        self.assertIn('instrument_slug', fieldnames)
        self.assertIn('item_index', fieldnames)
        self.assertIn('value', fieldnames)

    def test_export_responses_includes_baseline_status(self):
        """Test that export responses includes baseline_status column."""
        InstrumentResponse.objects.create(
            user=self.completed_participant,
            instrument_slug='bfi_2_s',
            item_index=1,
            value=3,
        )

        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('admin_baseline_export_responses'))

        csv_content = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_content))
        rows = list(reader)

        self.assertTrue(len(rows) > 0)
        first_row = rows[0]
        self.assertIn('baseline_status', first_row)
        self.assertEqual(first_row['baseline_status'], 'completed')

    def test_admin_action_reset_baseline_attention_failed(self):
        """Test the admin action to reset attention_failed status."""
        # Create a user with attention_failed status
        failed_user = User.objects.create_user(
            email='failed@example.com',
            password='failedpass123',
            is_email_verified=True,
            baseline_status='attention_failed',
            baseline_failed_item_index=15,
            baseline_failed_keystroke='X',
        )

        # Call action
        queryset = User.objects.filter(id=failed_user.id)
        reset_baseline_attention_failed(None, None, queryset)

        # Verify user status changed
        failed_user.refresh_from_db()
        self.assertEqual(failed_user.baseline_status, 'pending')
        self.assertIsNone(failed_user.baseline_failed_item_index)
        self.assertEqual(failed_user.baseline_failed_keystroke, '')

    def test_admin_action_only_resets_attention_failed(self):
        """Test that the admin action only resets attention_failed, not other statuses."""
        # Create users with different statuses
        completed_user = User.objects.create_user(
            email='completed2@example.com',
            password='pass123',
            is_email_verified=True,
            baseline_status='completed',
        )
        pending_user = User.objects.create_user(
            email='pending@example.com',
            password='pass123',
            is_email_verified=True,
            baseline_status='pending',
        )
        failed_user = User.objects.create_user(
            email='failed2@example.com',
            password='pass123',
            is_email_verified=True,
            baseline_status='attention_failed',
            baseline_failed_item_index=15,
        )

        # Call action on all three
        queryset = User.objects.filter(id__in=[completed_user.id, pending_user.id, failed_user.id])
        reset_baseline_attention_failed(None, None, queryset)

        # Verify only failed_user changed
        completed_user.refresh_from_db()
        pending_user.refresh_from_db()
        failed_user.refresh_from_db()

        self.assertEqual(completed_user.baseline_status, 'completed')
        self.assertEqual(pending_user.baseline_status, 'pending')
        self.assertEqual(failed_user.baseline_status, 'pending')
        self.assertIsNone(failed_user.baseline_failed_item_index)

    def test_export_responses_non_staff_redirect(self):
        """Test that non-staff users cannot export responses."""
        self.client.force_login(self.participant)
        response = self.client.get(reverse('admin_baseline_export_responses'), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('topic_selection'))

    def test_export_scores_non_staff_redirect(self):
        """Test that non-staff users cannot export scores."""
        self.client.force_login(self.participant)
        response = self.client.get(reverse('admin_baseline_export_scores'), follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('topic_selection'))
