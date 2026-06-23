"""
Tests for accounts.study_flow — the participant-journey source of truth.

These are flow-logic tests (PRD testing seam 1): given a participant's state,
assert the flow module resolves them to the correct next step. No HTTP /
Django-client spinning-up; pure model + function calls.
"""

from django.test import TestCase

from accounts import study_flow as flow
from accounts.models import User, Conversation, ConversationMessage, StanceRating


def _make_user(email=None, baseline_status='pending',
               is_email_verified=True):
    if email is None:
        email = f'{baseline_status}@y.com'
    user = User.objects.create_user(email=email, password='pw')
    user.is_email_verified = is_email_verified
    user.baseline_status = baseline_status
    user.save()
    return user


class NextStepTests(TestCase):
    def test_pending_user_routes_to_baseline(self):
        user = _make_user(baseline_status='pending')
        self.assertEqual(flow.next_step(user)['name'], 'baseline')

    def test_completed_user_routes_to_topic_selection(self):
        user = _make_user(baseline_status='completed')
        self.assertEqual(flow.next_step(user)['name'], 'topic_selection')

    def test_attention_failed_routes_to_terminal(self):
        user = _make_user(baseline_status='attention_failed')
        self.assertEqual(flow.next_step(user)['name'], 'attention_failed')

    def test_abandoned_is_non_terminal_routes_back_to_baseline(self):
        user = _make_user(baseline_status='abandoned')
        self.assertEqual(flow.next_step(user)['name'], 'baseline')


class IsTerminalTests(TestCase):
    def test_attention_failed_is_terminal(self):
        user = _make_user(baseline_status='attention_failed')
        self.assertTrue(flow.is_terminal(user))

    def test_non_terminal_statuses(self):
        for status in ('pending', 'completed', 'abandoned'):
            user = _make_user(baseline_status=status)
            self.assertFalse(flow.is_terminal(user),
                             f"{status} should not be terminal")
            user.delete()


class PostLoginRedirectTests(TestCase):
    def test_pending_routes_to_baseline_intro(self):
        user = _make_user(baseline_status='pending')
        self.assertEqual(flow.post_login_redirect(user), 'baseline_intro')

    def test_completed_routes_to_topic_selection(self):
        user = _make_user(baseline_status='completed')
        self.assertEqual(flow.post_login_redirect(user), 'topic_selection')

    def test_attention_failed_routes_to_baseline_failed(self):
        user = _make_user(baseline_status='attention_failed')
        self.assertEqual(flow.post_login_redirect(user), 'baseline_failed')


class NextStepForTopicTests(TestCase):
    """Walks a single topic through the full per-topic flow."""

    def setUp(self):
        self.user = _make_user(email='topic@y.com',
                               baseline_status='completed')
        self.topic_id = 1

    def test_initial_step_is_stance_pre(self):
        self.assertEqual(
            flow.next_step_for_topic(self.user, self.topic_id)['name'],
            'stance_pre')

    def test_after_pre_rating_next_is_chat(self):
        StanceRating.objects.create(
            user=self.user, topic_id=self.topic_id,
            topic_area='area', specific_question='q?',
            rating_type='pre', pro_rating=3, con_rating=3, neutral_rating=3)
        self.assertEqual(
            flow.next_step_for_topic(self.user, self.topic_id)['name'],
            'chat')

    def test_after_chat_next_is_stance_post(self):
        StanceRating.objects.create(
            user=self.user, topic_id=self.topic_id,
            topic_area='area', specific_question='q?',
            rating_type='pre', pro_rating=3, con_rating=3, neutral_rating=3)
        conversation = Conversation.objects.create(topic=str(self.topic_id),
                                                   title='t', description='')
        ConversationMessage.objects.create(
            user=self.user, conversation=conversation,
            role='user', content='hello')
        self.assertEqual(
            flow.next_step_for_topic(self.user, self.topic_id)['name'],
            'stance_post')

    def test_after_post_rating_next_is_analysis(self):
        StanceRating.objects.create(
            user=self.user, topic_id=self.topic_id,
            topic_area='area', specific_question='q?',
            rating_type='pre', pro_rating=3, con_rating=3, neutral_rating=3)
        conversation = Conversation.objects.create(topic=str(self.topic_id),
                                                   title='t', description='')
        ConversationMessage.objects.create(
            user=self.user, conversation=conversation,
            role='user', content='hello')
        StanceRating.objects.create(
            user=self.user, topic_id=self.topic_id,
            topic_area='area', specific_question='q?',
            rating_type='post', pro_rating=3, con_rating=3, neutral_rating=3)
        self.assertEqual(
            flow.next_step_for_topic(self.user, self.topic_id)['name'],
            'analysis')

    def test_baseline_incomplete_returns_baseline_step(self):
        self.user.baseline_status = 'pending'
        self.user.save()
        self.assertEqual(
            flow.next_step_for_topic(self.user, self.topic_id)['name'],
            'baseline')


class ResolveUrlTests(TestCase):
    def test_once_step_no_topic(self):
        # topic_selection url exists in the current urls.py; reversing should
        # succeed and return a path string.
        step = {"url_name": "topic_selection"}
        url = flow.resolve_url(step)
        self.assertTrue(url.startswith('/'))

    def test_per_topic_step_with_topic(self):
        step = {"url_name": "chat_topic"}
        url = flow.resolve_url(step, topic_id=5)
        self.assertIn('5', url)

    def test_missing_url_falls_back_to_name(self):
        # baseline_intro is not yet wired in urls.py — resolve_url should fall
        # back to returning the url_name string rather than raising.
        step = {"url_name": "baseline_intro"}
        self.assertEqual(flow.resolve_url(step), 'baseline_intro')
