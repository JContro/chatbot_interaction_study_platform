from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomAuthenticationForm, PasswordResetRequestForm, SetPasswordForm
from .models import User
from .utils import send_verification_email, verify_email, send_password_reset_email


def home_view(request):
    """
    Landing page with welcome message and login/register links.
    """
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'accounts/home.html')


def login_view(request):
    """
    Handle user login with email authentication.
    """
    if request.user.is_authenticated:
        return redirect('chat')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Check if email is verified
                if not user.is_email_verified:
                    messages.error(
                        request, 'Please verify your email address before logging in. Check your inbox for the verification link.')
                    return render(request, 'accounts/login.html', {'form': form})
                login(request, user)
                messages.success(request, f'Welcome back!')
                return redirect('chat')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """
    Handle user registration with email verification.
    """
    if request.user.is_authenticated:
        return redirect('chat')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # User is not verified yet - don't log in
            user.is_active = True  # Keep user active but email not verified
            user.save()

            # Send verification email
            send_verification_email(user, request)

            messages.success(
                request, 'Account created! Please check your email to verify your account before logging in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def verify_email_view(request, token):
    """
    Handle email verification with token.
    """
    user = get_object_or_404(User, email_verification_token=token)

    if user.is_email_verified:
        messages.info(
            request, 'Your email is already verified. You can log in.')
        return redirect('login')

    # Verify the email
    user.is_email_verified = True
    user.email_verified_at = timezone.now()
    user.save(update_fields=['is_email_verified', 'email_verified_at'])

    messages.success(
        request, 'Your email has been verified! You can now log in.')
    return redirect('login')


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


def password_reset_request_view(request):
    """
    Handle password reset request - show form to enter email.
    """
    if request.user.is_authenticated:
        return redirect('chat')

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                send_password_reset_email(user, request)
                messages.success(
                    request, 'If an account with that email exists, we have sent password reset instructions.')
            except User.DoesNotExist:
                # Don't reveal whether email exists or not
                messages.success(
                    request, 'If an account with that email exists, we have sent password reset instructions.')
            return redirect('password_reset_done')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'accounts/password_reset_request.html', {'form': form})


def password_reset_done_view(request):
    """
    Show confirmation that password reset email was sent.
    """
    if request.user.is_authenticated:
        return redirect('chat')
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm_view(request, token):
    """
    Handle password reset confirmation - show form to set new password.
    """
    if request.user.is_authenticated:
        return redirect('chat')

    user = get_object_or_404(User, password_reset_token=token)

    # Check if token is expired (24 hours)
    if user.password_reset_sent_at:
        expiry_time = user.password_reset_sent_at + \
            timezone.timedelta(hours=24)
        if timezone.now() > expiry_time:
            messages.error(
                request, 'This password reset link has expired. Please request a new one.')
            return redirect('password_reset_request')

    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password1')
            user.set_password(new_password)
            # Clear the reset token
            user.password_reset_token = None
            user.password_reset_sent_at = None
            user.save()

            messages.success(
                request, 'Your password has been reset successfully. You can now log in.')
            return redirect('login')
    else:
        form = SetPasswordForm()

    return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'token': token})


@login_required
def chat_view(request):
    """
    Main chat view - the main application page.
    """
    # Check if user's email is verified before allowing access
    if not request.user.is_email_verified:
        messages.warning(
            request, 'Please verify your email address to access the chat.')
        logout(request)
        return redirect('login')

    return render(request, 'accounts/chat.html')
