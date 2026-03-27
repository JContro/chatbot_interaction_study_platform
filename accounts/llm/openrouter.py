"""
OpenRouter LLM provider for admin LLM suggest analysis feature.

Uses the OpenRouter API to call Claude Sonnet models for generating
conversation analysis suggestions.
"""

import json
import logging
from typing import Dict, Any, Optional

import requests

from .base import BaseLLM, ConversationHistory

logger = logging.getLogger(__name__)


class OpenRouterLLM(BaseLLM):
    """
    OpenRouter LLM provider that wraps the OpenRouter API.

    OpenRouter provides unified access to multiple LLM providers including
    Anthropic's Claude models.
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, model_name: str, api_key: str = "", **kwargs):
        """
        Initialize the OpenRouter LLM.

        Args:
            model_name: The model identifier (e.g., 'anthropic/claude-sonnet-4-5')
            api_key: OpenRouter API key
            **kwargs: Additional configuration options
        """
        super().__init__(model_name, **kwargs)
        self.api_key = api_key
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 2048)
        self._initialized = True

    def initialize(self) -> None:
        """Initialize the LLM (no-op for API-based providers)."""
        self._initialized = True

    def generate(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory] = None,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response using the OpenRouter API.

        Args:
            prompt: The user's input prompt
            conversation_history: Optional conversation history for context
            topic_data: Optional topic data dictionary
            assigned_stance: Optional stance type
            **kwargs: Additional generation parameters

        Returns:
            The generated response as a string
        """
        if not self.api_key:
            raise ValueError("OpenRouter API key is not configured")

        # Build messages list
        messages = []

        # Add conversation context if provided
        if conversation_history:
            for msg in conversation_history.get_messages():
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add the current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })

        # Prepare request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }

        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": kwargs.get("referer", ""),
            "X-Title": kwargs.get("app_name", "Chatbot Study Platform"),
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()

            # Extract the generated text
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected API response format: {result}")

        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request failed: {e}")
            raise ValueError(f"OpenRouter API request failed: {str(e)}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Dictionary containing model metadata
        """
        return {
            "provider": "openrouter",
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
