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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
