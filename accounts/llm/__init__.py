"""
LLM package for the chatbot study platform.

Exports the abstract base classes so the rest of the application only
depends on these contracts - never on a specific provider or model.
"""

from .base import BaseLLM, Message, ConversationHistory, GenerationParams

__all__ = ["BaseLLM", "Message", "ConversationHistory", "GenerationParams"]
