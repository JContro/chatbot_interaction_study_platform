import json
import logging
import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm, CustomAuthenticationForm, PasswordResetRequestForm, SetPasswordForm
from .models import User, Conversation, ConversationMessage, MessageAnnotation, StanceRating
from .utils import send_verification_email, verify_email, send_password_reset_email
from .topics_data import (
    CONVERSATION_TOPICS, get_topic_areas, get_topics_by_area,
    get_topic_by_id, get_all_stance_types
)

logger = logging.getLogger(__name__)


def home_view(request):
    """
    Landing page with welcome message and login/register links.
    For authenticated users, shows conversation history.
    """
    if request.user.is_authenticated:
        # Get all conversations this user has participated in
        user_conversation_ids = ConversationMessage.objects.filter(
            user=request.user
        ).values_list('conversation', flat=True).distinct()

        conversations_qs = Conversation.objects.filter(id__in=user_conversation_ids)
        total_count = conversations_qs.count()

        # Build conversation metadata
        conversation_history = []
        for conv in conversations_qs:
            topic_data = get_topic_by_id(int(conv.topic))
            last_message = ConversationMessage.objects.filter(
                user=request.user, conversation=conv
            ).last()
            message_count = ConversationMessage.objects.filter(
                user=request.user, conversation=conv
            ).count()
            conversation_history.append({
                'topic_id': conv.topic,
                'topic_area': topic_data['topic_area'] if topic_data else 'Unknown',
                'specific_question': topic_data['specific_question'] if topic_data else '',
                'completed_at': last_message.created_at if last_message else None,
                'message_count': message_count,
            })

        # Sort by most recent, limit to 5 on home page
        conversation_history.sort(key=lambda c: c['completed_at'] or timezone.datetime.min, reverse=True)
        limited_history = conversation_history[:5]

        return render(request, 'accounts/home.html', {
            'conversation_history': limited_history,
            'total_conversations': total_count,
            'has_more': total_count > 5,
            'is_authenticated': True
        })
    return render(request, 'accounts/home.html', {
        'is_authenticated': False
    })


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

    # Get completed topic IDs for this user (topics with post-conversation stance ratings)
    completed_topic_ids = set(
        StanceRating.objects.filter(
            user=request.user,
            rating_type='post'
        ).values_list('topic_id', flat=True)
    )

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
        'topic_areas_json': topic_areas_json,
        'completed_topic_ids': list(completed_topic_ids)
    })


@login_required
def stance_rating_view(request, topic_id=None, rating_type='pre'):
    """
    Survey view - collects Likert scale ratings for each stance.
    Can be pre-conversation (before chat) or post-conversation (after chat).
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

    # Determine if this is pre or post conversation rating
    is_post = rating_type == 'post'
    
    # For pre-conversation: check if user already submitted ratings for this topic and type
    # For post-conversation: check if there's an existing post rating (for page refreshes)
    # but don't pre-fill with pre-conversation values
    existing_rating = StanceRating.objects.filter(
        user=request.user, topic_id=topic_id, rating_type=rating_type).first()

    if request.method == 'POST':
        # Save the ratings
        pro_rating = int(request.POST.get('pro_rating', 3))
        con_rating = int(request.POST.get('con_rating', 3))
        neutral_rating = int(request.POST.get('neutral_rating', 3))

        # Update or create the rating
        if existing_rating:
            existing_rating.pro_rating = pro_rating
            existing_rating.con_rating = con_rating
            existing_rating.neutral_rating = neutral_rating
            existing_rating.save()
        else:
            StanceRating.objects.create(
                user=request.user,
                topic_id=topic_id,
                topic_area=topic_data['topic_area'],
                specific_question=topic_data['specific_question'],
                rating_type=rating_type,
                pro_rating=pro_rating,
                con_rating=con_rating,
                neutral_rating=neutral_rating
            )

        if is_post:
            # After post-conversation rating, go to topic selection (homepage)
            messages.success(request, 'Thank you for completing the conversation!')
            return redirect('topic_selection')
        else:
            # After pre-conversation rating, go to chat
            return redirect('chat_topic', topic_id=topic_id)

    # Build context with topic data and stance positions
    chat_context = {
        'topic_id': topic_id,
        'topic_area': topic_data['topic_area'],
        'specific_question': topic_data['specific_question'],
        'stance_pro': topic_data['stances']['pro'],
        'stance_con': topic_data['stances']['con'],
        'stance_neutral': topic_data['stances']['neutral'],
        'existing_rating': existing_rating,
        'is_post': is_post,
    }

    return render(request, 'accounts/stance_rating.html', chat_context)


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

    # Get user's pre-conversation stance ratings (if any)
    stance_rating = StanceRating.objects.filter(
        user=request.user, topic_id=topic_id, rating_type='pre').first()

    # Compute the user's preferred stance (the one with the highest rating)
    preferred_stance = None
    stance_ratings_dict = {}
    if stance_rating:
        ratings = {
            'pro': stance_rating.pro_rating,
            'con': stance_rating.con_rating,
            'neutral': stance_rating.neutral_rating,
        }
        stance_ratings_dict = ratings
        # Find the stance with the max rating (ties broken by order: pro, con, neutral)
        max_rating = max(ratings.values())
        for stance in ['pro', 'con', 'neutral']:
            if ratings[stance] == max_rating:
                preferred_stance = stance
                break

    # Create a context with all the necessary information
    chat_context = {
        'topic_id': topic_id,
        'topic_area': topic_data['topic_area'],
        'specific_question': topic_data['specific_question'],
        'assigned_stance': assigned_stance,
        'assigned_stance_text': stance_data,
        'stance_pro': topic_data['stances']['pro'],
        'stance_con': topic_data['stances']['con'],
        'stance_neutral': topic_data['stances']['neutral'],
        'stance_rating_pro': stance_ratings_dict.get('pro'),
        'stance_rating_con': stance_ratings_dict.get('con'),
        'stance_rating_neutral': stance_ratings_dict.get('neutral'),
        'preferred_stance': preferred_stance,
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
    user_stance_ratings = body.get("user_stance_ratings")

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
            user_stance_ratings=user_stance_ratings,
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
def chat_api_stream_view(request):
    """
    Streaming JSON API endpoint: receive a user message + conversation history,
    stream the LLM's reply using Server-Sent Events.

    Request body (JSON) - same as chat_api_view:
        {
            "message": "<user text>",
            "topic_id": "<topic ID (1-20)>",
            "assigned_stance": "<stance type (e.g., conservative)>",
            "history": [
                {"role": "user",      "content": "..."},
                {"role": "assistant", "content": "..."}
            ]
        }

    Response: Server-Sent Events stream where each event is:
        data: {"token": "<token text>"}
        data: {"done": true, "response": "<full response>"}

    Error response (4xx / 500):
        data: {"error": "<reason>"}
    """
    # -- parse request body --------------------------------------------------
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return StreamingHttpResponse(
            iter([json.dumps({"error": "Invalid JSON body."})]),
            status=400,
            content_type="application/json"
        )

    user_message = body.get("message", "").strip()
    if not user_message:
        return StreamingHttpResponse(
            iter([json.dumps({"error": "Message cannot be empty."})]),
            status=400,
            content_type="application/json"
        )

    topic_id = body.get("topic_id", "").strip()
    if not topic_id:
        return StreamingHttpResponse(
            iter([json.dumps({"error": "Topic ID is required."})]),
            status=400,
            content_type="application/json"
        )

    # Validate topic_id exists
    topic_data = get_topic_by_id(int(topic_id))
    if topic_data is None:
        return StreamingHttpResponse(
            iter([json.dumps({"error": "Invalid topic ID."})]),
            status=400,
            content_type="application/json"
        )

    assigned_stance = body.get("assigned_stance", "").strip()
    if not assigned_stance or assigned_stance not in topic_data['stances']:
        return StreamingHttpResponse(
            iter([json.dumps({"error": "Invalid or missing stance."})]),
            status=400,
            content_type="application/json"
        )

    raw_history = body.get("history", [])
    user_stance_ratings = body.get("user_stance_ratings")

    # -- generator function for streaming ------------------------------------
    def generate():
        try:
            from .llm.registry import get_llm
            from .llm.base import ConversationHistory

            # Rebuild server-side ConversationHistory
            history = ConversationHistory()
            for entry in raw_history:
                role = entry.get("role", "user")
                content = entry.get("content", "")
                if role and content:
                    history.add_message(role, content)

            history.add_user_message(user_message)

            llm = get_llm()
            full_response = ""

            # Save messages to database
            conversation, _ = Conversation.objects.get_or_create(topic=topic_id)

            # Save user message
            ConversationMessage.objects.create(
                user=request.user,
                conversation=conversation,
                role='user',
                content=user_message
            )

            # Stream tokens as they come
            for token in llm.generate_stream(
                prompt=user_message,
                conversation_history=history,
                topic_data=topic_data,
                assigned_stance=assigned_stance,
                user_stance_ratings=user_stance_ratings,
            ):
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"

            # Save assistant response
            ConversationMessage.objects.create(
                user=request.user,
                conversation=conversation,
                role='assistant',
                content=full_response
            )

            # Send completion event
            yield f"data: {json.dumps({'done': True, 'response': full_response})}\n\n"

        except Exception:
            logger.exception("LLM streaming failed for user '%s'",
                             request.user.email)
            yield json.dumps({"error": "The model encountered an error generating a response."})

    response = StreamingHttpResponse(
        generate(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


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
def review_view(request, topic_id=None):
    """
    Review view - shows all user conversations in a sidebar
    and a selected conversation in split-screen (conversation on left, annotations on right).
    """
    # Check if user's email is verified
    if not request.user.is_email_verified:
        messages.warning(
            request, 'Please verify your email address to access this page.')
        logout(request)
        return redirect('login')

    # Get all conversations for this user
    user_conversation_ids = ConversationMessage.objects.filter(
        user=request.user
    ).values_list('conversation', flat=True).distinct()

    conversations_list = Conversation.objects.filter(id__in=user_conversation_ids)

    # Build conversation metadata for sidebar
    conversation_meta = []
    for conv in conversations_list:
        topic_data = get_topic_by_id(int(conv.topic))
        message_count = ConversationMessage.objects.filter(
            user=request.user, conversation=conv
        ).count()
        last_message = ConversationMessage.objects.filter(
            user=request.user, conversation=conv
        ).last()
        conversation_meta.append({
            'topic_id': conv.topic,
            'topic_area': topic_data['topic_area'] if topic_data else 'Unknown',
            'specific_question': topic_data['specific_question'] if topic_data else '',
            'message_count': message_count,
            'last_message_at': last_message.created_at if last_message else None,
        })

    # Sort by most recent first
    conversation_meta.sort(key=lambda c: c['last_message_at'] or timezone.datetime.min, reverse=True)

    # If a specific conversation is selected, load its data
    chat_messages = None
    annotations = None
    selected_topic_data = None

    if topic_id is not None:
        topic_data = get_topic_by_id(int(topic_id))
        if topic_data:
            conversation = Conversation.objects.filter(topic=topic_id).first()
            if conversation:
                chat_messages = ConversationMessage.objects.filter(
                    user=request.user,
                    conversation=conversation
                ).order_by('created_at')

                annotations = MessageAnnotation.objects.filter(
                    message__conversation=conversation
                ).select_related('message', 'user').order_by('created_at')

                selected_topic_data = topic_data

    return render(request, 'accounts/review.html', {
        'conversations_list': conversation_meta,
        'selected_topic_id': topic_id,
        'selected_topic': selected_topic_data,
        'chat_messages': chat_messages,
        'annotations': annotations,
    })


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


@login_required
def admin_analysis_view(request, user_id, topic):
    """
    Admin view for analyzing a specific user's conversation with annotation capabilities.
    Annotations created here are assigned to the admin user doing the analysis.
    Only staff users can access this view.
    """
    if not request.user.is_staff:
        messages.error(
            request, 'You do not have permission to access this page.')
        return redirect('topic_selection')

    user = get_object_or_404(User, id=user_id)
    conversation = get_object_or_404(Conversation, topic=topic)

    # Get topic data for display
    topic_data = get_topic_by_id(topic)
    if topic_data is None:
        topic_data = {'topic_area': 'Unknown Topic', 'specific_question': ''}

    # Get all messages for this user's conversation
    chat_messages = ConversationMessage.objects.filter(
        user=user,
        conversation=conversation
    ).order_by('created_at')

    # Get existing annotations for this conversation (by any admin)
    annotations = MessageAnnotation.objects.filter(
        message__conversation=conversation
    ).select_related('message', 'user').order_by('created_at')

    return render(request, 'accounts/analysis.html', {
        'topic_id': topic,
        'topic_area': topic_data['topic_area'],
        'specific_question': topic_data.get('specific_question', ''),
        'conversation': conversation,
        'chat_messages': chat_messages,
        'annotations': annotations,
        'is_admin_view': True,
        'admin_target_user': user,
    })


@login_required
@require_POST
def llm_suggest_analysis_view(request, user_id, topic):
    """
    JSON API endpoint for admin LLM suggest analysis.
    Uses OpenRouter to generate an analysis of the conversation.

    Request body (JSON):
        None required

    Success response (200):
        {"suggestion": "<analysis text>"}

    Error response (4xx / 500):
        {"error": "<reason>"}
    """
    # Check if user is staff
    if not request.user.is_staff:
        return JsonResponse(
            {"error": "Only admin users can access this feature."},
            status=403,
        )

    user = get_object_or_404(User, id=user_id)
    conversation = get_object_or_404(Conversation, topic=topic)

    # Get topic data for context
    topic_data = get_topic_by_id(topic)
    if topic_data is None:
        topic_data = {'topic_area': 'Unknown Topic', 'specific_question': ''}

    # Get all messages for this user's conversation
    chat_messages = ConversationMessage.objects.filter(
        user=user,
        conversation=conversation
    ).order_by('created_at')

    # Build conversation text for the LLM
    conversation_text = ""
    for msg in chat_messages:
        role = "User" if msg.role == 'user' else "Assistant"
        conversation_text += f"{role}: {msg.content}\n\n"

    # Build the analysis prompt
    analysis_prompt = f"""You are analyzing a conversation from a research study about human-AI interaction.

Topic Area: {topic_data.get('topic_area', 'Unknown')}
Specific Question: {topic_data.get('specific_question', 'Unknown')}

Please analyze this conversation and provide insights on:
1. The quality and nature of the user's engagement
2. Any notable patterns in the conversation
3. Potential issues or concerns (e.g., manipulation, inappropriate content, concerning user behavior)
4. Overall assessment of the interaction

CONVERSATION:
{conversation_text}

Provide a thoughtful, objective analysis focusing on research-relevant observations."""

    # Call OpenRouter API
    try:
        from django.conf import settings
        import requests

        api_key = getattr(settings, 'OPENROUTER_API_KEY', '')
        model = getattr(settings, 'OPENROUTER_MODEL',
                        'anthropic/claude-sonnet-4-5')

        logger.info(
            f"LLM Suggest Analysis: user_id={user_id}, topic={topic}, model={model}")

        if not api_key:
            logger.error(
                "LLM Suggest Analysis: OPENROUTER_API_KEY is not configured")
            return JsonResponse(
                {"error": "OpenRouter API key is not configured. Please set OPENROUTER_API_KEY in environment."},
                status=500,
            )

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        logger.info(
            f"LLM Suggest Analysis: Making API call to OpenRouter with model {model}")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        logger.info(
            f"LLM Suggest Analysis: Response status={response.status_code}")

        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            suggestion = result["choices"][0]["message"]["content"]
            return JsonResponse({"suggestion": suggestion})
        else:
            return JsonResponse(
                {"error": "Unexpected API response format."},
                status=500,
            )

    except requests.exceptions.RequestException as e:
        logger.exception("OpenRouter API request failed")
        return JsonResponse(
            {"error": f"API request failed: {str(e)}"},
            status=500,
        )
    except Exception as e:
        logger.exception("Error in llm_suggest_analysis_view")
        return JsonResponse(
            {"error": f"Failed to generate analysis: {str(e)}"},
            status=500,
        )
