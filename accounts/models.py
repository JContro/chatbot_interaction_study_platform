from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid
import json


class IFSPart(models.Model):
    """
    Model representing an IFS (Internal Family Systems) part in the taxonomy.
    Used for classifying conversation content based on IFS therapeutic concepts.
    """
    CATEGORY_CHOICES = [
        ('protector', 'Protector'),
        ('exile', 'Exile'),
        ('healthy_capacity', 'Healthy Capacity'),
        ('relational_session', 'Relational/Session Process'),
        ('case_example', 'Case Example'),
    ]

    SUBCATEGORY_CHOICES = [
        ('manager', 'Manager'),
        ('manager_inner_critic', 'Manager - Inner Critic'),
        ('firefighter', 'Firefighter'),
        ('exile', 'Exile'),
        ('healthy_capacity', 'Healthy Capacity'),
        ('relational_session', 'Relational/Session Process'),
        ('case_example', 'Case Example'),
    ]

    # Core identification
    part_id = models.CharField(
        max_length=100, unique=True,
        help_text="Unique identifier for the part (e.g., 'perfectionist', 'frightened_child')")
    name = models.CharField(max_length=200)

    # Categorization
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=30, choices=SUBCATEGORY_CHOICES, blank=True, null=True)

    # Core description and intent
    description = models.TextField()
    positive_intent = models.TextField(blank=True, null=True)

    # JSON fields for list data
    common_behaviors = models.JSONField(default=list, blank=True)
    often_polarized_with = models.JSONField(default=list, blank=True)
    sources = models.JSONField(default=list, blank=True)

    # Exile-specific fields
    burden = models.TextField(blank=True, null=True)
    typical_origins = models.TextField(blank=True, null=True)
    common_expressions = models.TextField(blank=True, null=True)
    exile_protected = models.TextField(blank=True, null=True)

    # Healthy capacity fields
    qualities = models.JSONField(default=list, blank=True)
    healthy_version_of = models.CharField(max_length=200, blank=True, null=True)
    transforms = models.CharField(max_length=200, blank=True, null=True)

    # Relational/session parts
    role_in_sessions = models.TextField(blank=True, null=True)

    # Case example parts
    client = models.CharField(max_length=200, blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'subcategory', 'name']
        verbose_name = 'IFS Part'
        verbose_name_plural = 'IFS Parts'

    def __str__(self):
        return f"{self.name} ({self.part_id})"


class IFSMeta(models.Model):
    """
    Model for storing IFS taxonomy metadata (descriptions and notes about the Self).
    """
    key = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    note_on_self = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'IFS Meta'
        verbose_name_plural = 'IFS Meta'

    def __str__(self):
        return f"IFS Meta: {self.key}"


class Conversation(models.Model):
    """
    Model representing a conversation topic for the chatbot study.
    """
    TOPIC_CHOICES = [
        ('A', 'Sample A'),
        ('B', 'Sample B'),
        ('C', 'Sample C'),
        ('D', 'Sample D'),
    ]

    topic = models.CharField(max_length=1, choices=TOPIC_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['topic']

    def __str__(self):
        return self.title


class ConversationMessage(models.Model):
    """
    Model representing a single message in a conversation.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='messages')
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class MessageAnnotation(models.Model):
    """
    Model representing an annotation/analysis on a portion of a message.
    Allows sentence-level classification and comments.
    """
    CLASSIFICATION_CHOICES = [
        ('good', 'Good'),
        ('bad', 'Bad'),
    ]

    message = models.ForeignKey(
        ConversationMessage, on_delete=models.CASCADE, related_name='annotations')
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='message_annotations')

    # Sentence-level targeting
    start_index = models.IntegerField(
        help_text="Character offset where the annotation starts")
    end_index = models.IntegerField(
        help_text="Character offset where the annotation ends")
    selected_text = models.TextField(
        help_text="The actual text being annotated")

    # Classification and comment
    classification = models.CharField(
        max_length=20, choices=CLASSIFICATION_CHOICES, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Annotation on '{self.selected_text[:30]}...' by {self.user.email}"


class StanceRating(models.Model):
    """
    Model for storing user's stance ratings on a Likert scale.
    Can be pre-conversation (before chat) or post-conversation (after chat).
    Saved to analyze if people's opinions changed after the conversation.
    """
    RATING_TYPE_CHOICES = [
        ('pre', 'Pre-conversation'),
        ('post', 'Post-conversation'),
    ]

    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='stance_ratings')
    topic_id = models.IntegerField(
        help_text="ID of the conversation topic (1-20)")
    topic_area = models.CharField(max_length=200)
    specific_question = models.TextField()
    
    # Rating type: pre or post conversation
    rating_type = models.CharField(
        max_length=10, choices=RATING_TYPE_CHOICES, default='pre',
        help_text="Whether this rating was before or after the conversation")
    
    # Likert scale ratings (1-5) for each stance
    pro_rating = models.IntegerField(
        choices=[(1, '1 - Strongly Disagree'), (2, '2 - Disagree'), (3, '3 - Neutral'), (4, '4 - Agree'), (5, '5 - Strongly Agree')],
        help_text="Rating for the 'pro' stance")
    con_rating = models.IntegerField(
        choices=[(1, '1 - Strongly Disagree'), (2, '2 - Disagree'), (3, '3 - Neutral'), (4, '4 - Agree'), (5, '5 - Strongly Agree')],
        help_text="Rating for the 'con' stance")
    neutral_rating = models.IntegerField(
        choices=[(1, '1 - Strongly Disagree'), (2, '2 - Disagree'), (3, '3 - Neutral'), (4, '4 - Agree'), (5, '5 - Strongly Agree')],
        help_text="Rating for the 'neutral' stance")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'topic_id', 'rating_type']

    def __str__(self):
        return f"Stance ratings by {self.user.email} on '{self.specific_question[:50]}...'"


class InstrumentResponse(models.Model):
    """
    A single 1-5 response to one item of a psychological instrument (BFI-2-S,
    IDAS-R, or a future third instrument). Generic by design: instrument is
    identified by a slug whose definition lives in accounts.instruments_data,
    so adding an instrument requires no schema migration.
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='instrument_responses')
    instrument_slug = models.CharField(max_length=50)
    item_index = models.IntegerField(help_text="1-based index of the item within the instrument")
    value = models.IntegerField(help_text="The 1-5 response value")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'instrument_slug', 'item_index')
        ordering = ['instrument_slug', 'item_index']
        indexes = [
            models.Index(fields=['user', 'instrument_slug']),
        ]

    def __str__(self):
        return f"{self.user.email} / {self.instrument_slug} item {self.item_index} = {self.value}"


class UserManager(BaseUserManager):
    """Custom manager for User model that uses email instead of username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model that uses email for authentication instead of username.
    """
    email = models.EmailField(unique=True)
    username = None

    # Use custom manager
    objects = UserManager()

    # Email verification fields
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(
        default=uuid.uuid4, editable=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Password reset fields
    password_reset_token = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, blank=True)
    password_reset_sent_at = models.DateTimeField(null=True, blank=True)

    # Baseline psych battery fields
    BASELINE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('attention_failed', 'Attention Failed'),
        ('abandoned', 'Abandoned'),
    ]
    baseline_status = models.CharField(
        max_length=20, default='pending', choices=BASELINE_STATUS_CHOICES)
    baseline_started_at = models.DateTimeField(null=True, blank=True)
    baseline_completed_at = models.DateTimeField(null=True, blank=True)
    baseline_failed_item_index = models.IntegerField(
        null=True, blank=True,
        help_text="The instrument item index (global battery position) at which the attention check was failed.")
    baseline_failed_keystroke = models.CharField(
        max_length=20, blank=True, default='',
        help_text="The key the participant pressed to fail the attention check.")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_completed_baseline(self):
        """True if the baseline psych battery is complete (gate for the rest of the study)."""
        return self.baseline_status == 'completed'

    def baseline_is_terminal(self):
        """True if the participant is in a terminal (non-completable) baseline state."""
        return self.baseline_status == 'attention_failed'
