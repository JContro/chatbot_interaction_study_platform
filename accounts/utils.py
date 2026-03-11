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
    verify_url = f"{protocol}://{host}/accounts/verify-email/{verification_token}/"

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
