"""
Utility functions for email verification.
"""
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


def generate_email_verification_token():
    """Generate a new email verification token."""
    return uuid.uuid4()


def send_verification_email(user, request=None):
    """
    Send an email verification link to the user.

    Args:
        user: The user to send the verification email to
        request: Optional HTTP request for building absolute URLs

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from django.urls import reverse

    # Build verification URL
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
    else:
        protocol = 'http'
        host = 'localhost:8000'

    verification_token = user.email_verification_token
    verify_url = f"{protocol}://{host}/verify-email/{verification_token}/"

    subject = 'Verify your email address - Chatbot Study Platform'
    message = f"""
Welcome to the Chatbot Study Platform!

Thank you for registering. Please verify your email address by clicking the link below:

{verify_url}

If you didn't create an account, please ignore this email.

Best regards,
The Chatbot Study Platform Team
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def verify_email(user):
    """
    Mark a user's email as verified.

    Args:
        user: The user whose email should be verified

    Returns:
        bool: True if verification was successful
    """
    user.is_email_verified = True
    user.email_verified_at = timezone.now()
    user.save(update_fields=['is_email_verified', 'email_verified_at'])
    return True


def send_password_reset_email(user, request=None):
    """
    Send a password reset email to the user.

    Args:
        user: The user to send the password reset email to
        request: Optional HTTP request for building absolute URLs

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    from django.urls import reverse

    # Generate a new password reset token
    user.password_reset_token = uuid.uuid4()
    user.password_reset_sent_at = timezone.now()
    user.save(update_fields=['password_reset_token', 'password_reset_sent_at'])

    # Build password reset URL
    if request:
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
    else:
        protocol = 'http'
        host = 'localhost:8000'

    reset_token = user.password_reset_token
    reset_url = f"{protocol}://{host}/password-reset/{reset_token}/"

    subject = 'Reset your password - Chatbot Study Platform'
    message = f"""
Hello,

We received a request to reset your password. Click the link below to create a new password:

{reset_url}

If you didn't request a password reset, please ignore this email. Your password will remain unchanged.

This link will expire in 24 hours.

Best regards,
The Chatbot Study Platform Team
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False
