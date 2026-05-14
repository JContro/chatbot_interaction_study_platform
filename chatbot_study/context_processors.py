"""
Context processors for the chatbot study platform.
"""


def risks_processor(request):
    """
    Context processor to make RISKS available in all templates.
    """
    from django.conf import settings
    return {
        'risks': getattr(settings, 'RISKS', [])
    }