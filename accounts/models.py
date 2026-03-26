from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


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
