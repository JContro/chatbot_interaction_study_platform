import json
import logging
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm, CustomAuthenticationForm, PasswordResetRequestForm, SetPasswordForm
from .models import User, Conversation, ConversationMessage, MessageAnnotation
from .utils import send_verification_email, verify_email, send_password_reset_email
from .topics_data import (
    CONVERSATION_TOPICS, get_topic_areas, get_topics_by_area,
    get_topic_by_id, get_all_stance_types
)

logger = logging.getLogger(__name__)


def home_view(request):
    """
    Landing page with welcome message and login/register links.
    """
    if request.user.is_authenticated:
        return redirect('topic_selection')
    return render(request, 'accounts/home.html')


def login_view(request):
    """
    Handle user login with email authentication.
    """
    if request.user.is_authenticated:
        return redirect('topic_selection')

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
                return redirect('topic_selection')
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
        return redirect('topic_selection')

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
        return redirect('topic_selection')

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
        return redirect('topic_selection')
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm_view(request, token):
    """
    Handle password reset confirmation - show form to set new password.
    """
    if request.user.is_authenticated:
        return redirect('topic_selection')

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
def topic_selection_view(request):
    """
    View for selecting a conversation topic.
    """
    # Check if user's email is verified before allowing access
    if not request.user.is_email_verified:
        messages.warning(
            request, 'Please verify your email address to access the chat.')
        logout(request)
        return redirect('login')

    # Get all unique topic areas
    topic_areas = get_topic_areas()

    # Build a structured dictionary of topic areas with their questions
    topic_areas_with_topics = []
    for area in topic_areas:
        topics = get_topics_by_area(area)
        topic_areas_with_topics.append({
            'name': area,
            'topics': topics
        })

    # Convert to JSON for JavaScript
    import json
    topic_areas_json = json.dumps(topic_areas_with_topics)

    return render(request, 'accounts/topic_selection.html', {
        'topic_areas': topic_areas_with_topics,
        'topic_areas_json': topic_areas_json
    })


@login_required
def chat_view(request, topic_id=None):
    """
    Main chat view - the main application page.
    """
    # Check if user's email is verified before allowing access
    if not request.user.is_email_verified:
        messages.warning(
            request, 'Please verify your email address to access the chat.')
        logout(request)
        return redirect('login')

    # If no topic is selected, redirect to topic selection
    if topic_id is None:
        return redirect('topic_selection')

    # Get the topic data
    topic_data = get_topic_by_id(int(topic_id))
    if topic_data is None:
        return redirect('topic_selection')

    # Randomly assign a stance to the chatbot
    stances = list(topic_data['stances'].keys())
    assigned_stance = random.choice(stances)
    stance_data = topic_data['stances'][assigned_stance]

    # Create a context with all the necessary information
    chat_context = {
        'topic_id': topic_id,
        'topic_area': topic_data['topic_area'],
        'specific_question': topic_data['specific_question'],
        'primary_exile': topic_data['primary_exile'],
        'intensity': topic_data['intensity'],
        'intensity_symbol': topic_data['intensity_symbol'],
        'assigned_stance': assigned_stance,
        'stance_pro': stance_data['pro'],
        'stance_con': stance_data['con'],
        'stance_neutral': stance_data['neutral'],
    }

    return render(request, 'accounts/chat.html', chat_context)


@login_required
def analysis_view(request, topic_id):
    """
    Analysis view - displays the conversation with annotation capabilities.
    Shows chat history on the left and analysis panel on the right.
    """
    # Check if user's email is verified before allowing access
    if not request.user.is_email_verified:
        messages.warning(
            request, 'Please verify your email address to access the analysis.')
        logout(request)
        return redirect('login')

    # Get the topic data
    topic_data = get_topic_by_id(int(topic_id))
    if topic_data is None:
        return redirect('topic_selection')

    # Get or create the conversation
    conversation, _ = Conversation.objects.get_or_create(topic=topic_id)

    # Get all messages for this user's conversation
    chat_messages = ConversationMessage.objects.filter(
        user=request.user,
        conversation=conversation
    ).order_by('created_at')

    # Get existing annotations for this conversation
    annotations = MessageAnnotation.objects.filter(
        user=request.user,
        message__conversation=conversation
    ).select_related('message').order_by('created_at')

    # Build context with all necessary information
    analysis_context = {
        'topic_id': topic_id,
        'topic_area': topic_data['topic_area'],
        'specific_question': topic_data['specific_question'],
        'conversation': conversation,
        'chat_messages': chat_messages,
        'annotations': annotations,
    }

    return render(request, 'accounts/analysis.html', analysis_context)


@login_required
@require_POST
def chat_api_view(request):
    """
    JSON API endpoint: receive a user message + conversation history,
    return the LLM's reply.

    Request body (JSON):
        {
            "message": "<user text>",
            "topic_id": "<topic ID (1-20)>",
            "assigned_stance": "<stance type (e.g., conservative)>",
            "history": [
                {"role": "user",      "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }

    Success response (200):
        {"response": "<assistant text>"}

    Error response (4xx / 500):
        {"error": "<reason>"}

    The view is completely provider-agnostic: it talks only to the
    BaseLLM interface via the registry. Swapping the backend requires
    no changes here.
    """
    # -- parse request body --------------------------------------------------
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    user_message = body.get("message", "").strip()
    if not user_message:
        return JsonResponse({"error": "Message cannot be empty."}, status=400)

    topic_id = body.get("topic_id", "").strip()
    if not topic_id:
        return JsonResponse({"error": "Topic ID is required."}, status=400)

    # Validate topic_id exists
    topic_data = get_topic_by_id(int(topic_id))
    if topic_data is None:
        return JsonResponse({"error": "Invalid topic ID."}, status=400)

    assigned_stance = body.get("assigned_stance", "").strip()
    if not assigned_stance or assigned_stance not in topic_data['stances']:
        return JsonResponse({"error": "Invalid or missing stance."}, status=400)

    raw_history = body.get("history", [])   # list of {role, content} dicts

    # -- call LLM ------------------------------------------------------------
    try:
        from .llm.registry import get_llm
        from .llm.base import ConversationHistory

        # Rebuild server-side ConversationHistory from the client's state.
        history = ConversationHistory()
        for entry in raw_history:
            role = entry.get("role", "user")
            content = entry.get("content", "")
            if role and content:
                history.add_message(role, content)

        # Append the incoming user message so the model sees the full turn.
        history.add_user_message(user_message)

        llm = get_llm()
        response_text = llm.generate(
            prompt=user_message,
            conversation_history=history,
            topic_data=topic_data,
            assigned_stance=assigned_stance,
        )

        # Save messages to database
        conversation, _ = Conversation.objects.get_or_create(topic=topic_id)

        # Save user message
        ConversationMessage.objects.create(
            user=request.user,
            conversation=conversation,
            role='user',
            content=user_message
        )

        # Save assistant response
        ConversationMessage.objects.create(
            user=request.user,
            conversation=conversation,
            role='assistant',
            content=response_text
        )

        return JsonResponse({"response": response_text})

    except Exception:
        logger.exception("LLM generation failed for user '%s'",
                         request.user.email)
        return JsonResponse(
            {"error": "The model encountered an error generating a response."},
            status=500,
        )


@login_required
@require_POST
def transcribe_audio_view(request):
    """
    JSON API endpoint: receive audio data, transcribe it using Whisper,
    return the transcribed text.

    Request body (multipart/form-data):
        - audio: audio file (webm, wav, mp3)

    Success response (200):
        {"transcription": "<transcribed text>"}

    Error response (4xx / 500):
        {"error": "<reason>"}
    """
    # -- check for audio file ---------------------------------------------------
    if 'audio' not in request.FILES:
        logger.warning("No audio file in request.FILES. Keys: %s",
                       list(request.FILES.keys()))
        return JsonResponse({"error": "No audio file provided."}, status=400)

    audio_file = request.FILES['audio']
    logger.info("Received audio file: name=%s, content_type=%s, size=%s",
                audio_file.name, audio_file.content_type, audio_file.size)

    # Validate file type - be more permissive to debug
    # Accept any audio type for now
    if audio_file.size == 0:
        return JsonResponse({"error": "Audio file is empty."}, status=400)

    # -- transcribe audio -------------------------------------------------------
    try:
        import whisper
        import tempfile
        import os

        # Read audio data first to check if it's empty
        audio_data = audio_file.read()
        if len(audio_data) < 1000:  # Less than 1KB is likely empty or too short
            logger.warning("Audio file too small: %s bytes", len(audio_data))
            return JsonResponse({"error": "Audio recording is too short or empty. Please try recording again."}, status=400)

        # Load Whisper base model fresh each time to avoid caching issues
        # This is slower but more reliable
        model = whisper.load_model("base")

        # Save uploaded file to temporary file (Whisper requires a file path)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name

        try:
            # Transcribe the audio
            result = model.transcribe(tmp_path, language='en')
            transcription = result['text'].strip()
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)

        if not transcription:
            return JsonResponse({"transcription": ""})

        return JsonResponse({"transcription": transcription})

    except Exception as e:
        logger.exception("Audio transcription failed for user '%s'",
                         request.user.email)
        # Return more detailed error for debugging
        error_msg = str(e)
        return JsonResponse(
            {"error": f"Failed to transcribe audio: {error_msg}"},
            status=500,
        )


@login_required
@require_POST
def annotation_api_view(request):
    """
    JSON API endpoint for managing message annotations.

    POST body (JSON):
        {
            "message_id": "<message ID>",
            "start_index": <character start offset>,
            "end_index": <character end offset>,
            "selected_text": "<text being annotated>",
            "classification": "<good|bad|null>",
            "comment": "<optional comment text>"
        }

    Success response (200):
        {"id": <annotation_id>, "messageId": "...", ...}

    Error response (4xx / 500):
        {"error": "<reason>"}
    """
    try:
        import json
        data = json.loads(request.body)

        message_id = data.get('message_id')
        start_index = data.get('start_index')
        end_index = data.get('end_index')
        selected_text = data.get('selected_text')
        classification = data.get('classification')
        comment = data.get('comment', '')

        if not all([message_id, start_index is not None, end_index is not None, selected_text]):
            return JsonResponse(
                {"error": "Missing required fields: message_id, start_index, end_index, selected_text"},
                status=400,
            )

        # Get the message (temporary ID format: temp-timestamp)
        from .models import ConversationMessage

        if str(message_id).startswith('temp-'):
            # This is a temporary message that hasn't been saved yet
            # For now, return an error - in the future we might want to save messages first
            return JsonResponse(
                {"error": "Message must be saved before annotation. Please refresh and try again."},
                status=400,
            )

        try:
            message = ConversationMessage.objects.get(id=message_id)
        except ConversationMessage.DoesNotExist:
            return JsonResponse(
                {"error": "Message not found"},
                status=404,
            )

        # Check if annotation already exists for this message at these positions
        existing = MessageAnnotation.objects.filter(
            message=message,
            user=request.user,
            start_index=start_index,
            end_index=end_index
        ).first()

        if existing:
            # Update existing annotation
            if classification is None and not comment:
                # Delete if no classification or comment
                existing.delete()
                return JsonResponse({"deleted": True, "id": existing.id})
            else:
                existing.classification = classification
                existing.comment = comment
                existing.save()
                return JsonResponse({
                    "id": existing.id,
                    "messageId": message.id,
                    "startIndex": existing.start_index,
                    "endIndex": existing.end_index,
                    "text": existing.selected_text,
                    "classification": existing.classification,
                    "comment": existing.comment,
                })
        else:
            # Create new annotation
            if classification is None and not comment:
                # Nothing to save
                return JsonResponse(
                    {"error": "Must provide classification or comment to save annotation"},
                    status=400,
                )

            annotation = MessageAnnotation.objects.create(
                message=message,
                user=request.user,
                start_index=start_index,
                end_index=end_index,
                selected_text=selected_text,
                classification=classification,
                comment=comment,
            )

            return JsonResponse({
                "id": annotation.id,
                "messageId": message.id,
                "startIndex": annotation.start_index,
                "endIndex": annotation.end_index,
                "text": annotation.selected_text,
                "classification": annotation.classification,
                "comment": annotation.comment,
            })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON in request body"},
            status=400,
        )
    except Exception as e:
        logger.exception("Error in annotation_api_view")
        return JsonResponse(
            {"error": f"Failed to process annotation: {str(e)}"},
            status=500,
        )


@login_required
def admin_conversations_view(request):
    """
    Admin view to see all conversations across all users.
    Only staff users can access this view.
    """
    if not request.user.is_staff:
        messages.error(
            request, 'You do not have permission to access this page.')
        return redirect('topic_selection')

    # Get all users who have conversations
    users_with_conversations = User.objects.filter(
        messages__isnull=False
    ).distinct().prefetch_related('messages')

    # Get conversation stats
    conversation_data = []
    for user in users_with_conversations:
        messages = user.messages.all()
        topics = {}
        for msg in messages:
            topic_key = msg.conversation.topic
            if topic_key not in topics:
                topics[topic_key] = {
                    'topic': msg.conversation,
                    'messages': [],
                    'message_count': 0
                }
            topics[topic_key]['messages'].append(msg)
            topics[topic_key]['message_count'] += 1

        conversation_data.append({
            'user': user,
            'topics': topics,
            'total_messages': messages.count()
        })

    return render(request, 'accounts/admin_conversations.html', {
        'conversation_data': conversation_data,
    })


@login_required
def admin_conversation_detail_view(request, user_id, topic):
    """
    Admin view to see a specific user's conversation for a specific topic.
    Only staff users can access this view.
    """
    if not request.user.is_staff:
        messages.error(
            request, 'You do not have permission to access this page.')
        return redirect('topic_selection')

    user = get_object_or_404(User, id=user_id)
    conversation = get_object_or_404(Conversation, topic=topic)

    messages = ConversationMessage.objects.filter(
        user=user,
        conversation=conversation
    ).order_by('created_at')

    return render(request, 'accounts/admin_conversation_detail.html', {
        'user': user,
        'conversation': conversation,
        'messages': messages,
    })
