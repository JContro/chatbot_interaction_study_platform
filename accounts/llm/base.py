"""
Abstract base class for LLM (Large Language Model) providers.

This module defines the interface that all LLM implementations must follow,
making the chat functionality model-agnostic and provider-agnostic.
"""

from abc import ABC, abstractmethod
from typing import Iterator, List, Dict, Any, Optional


class Message:
    """
    Represents a single message in the conversation history.
    """

    def __init__(self, role: str, content: str):
        """
        Initialize a message.

        Args:
            role: The role of the message sender ('user', 'assistant', or 'system')
            content: The content of the message
        """
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """Convert message to dictionary format."""
        return {"role": self.role, "content": self.content}


class ConversationHistory:
    """
    Manages the conversation history for a chat session.
    """

    def __init__(self, system_prompt: Optional[str] = None):
        """
        Initialize conversation history.

        Args:
            system_prompt: Optional system prompt to prepend to the conversation
        """
        self.messages: List[Message] = []
        if system_prompt:
            self.messages.append(Message("system", system_prompt))

    def add_user_message(self, content: str) -> None:
        """Add a user message to the history."""
        self.messages.append(Message("user", content))

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the history."""
        self.messages.append(Message("assistant", content))

    def add_message(self, role: str, content: str) -> None:
        """Add a message with the specified role."""
        self.messages.append(Message(role, content))

    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages as a list of dictionaries."""
        return [msg.to_dict() for msg in self.messages]

    def clear(self) -> None:
        """Clear all messages except system prompt."""
        system_msg = None
        if self.messages and self.messages[0].role == "system":
            system_msg = self.messages[0]
        self.messages = [system_msg] if system_msg else []


class BaseLLM(ABC):
    """
    Abstract base class for LLM implementations.

    All LLM providers must inherit from this class and implement
    the generate method.
    """

    def __init__(self, model_name: str, **kwargs):
        """
        Initialize the LLM.

        Args:
            model_name: The name or path of the model to use
            **kwargs: Additional provider-specific configuration
        """
        self.model_name = model_name
        self.config = kwargs
        self._initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the model and any required resources.

        This method should be called before generate() is used.
        """
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory] = None,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response to the given prompt.

        Args:
            prompt: The user's input prompt
            conversation_history: Optional conversation history for context
            topic_data: Optional topic data dictionary containing topic info
            assigned_stance: Optional stance type (e.g., 'conservative')
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)

        Returns:
            The generated response as a string
        """
        pass

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory] = None,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
        **kwargs
    ) -> Iterator[str]:
        """
        Generate a streaming response to the given prompt.

        Args:
            prompt: The user's input prompt
            conversation_history: Optional conversation history for context
            topic_data: Optional topic data dictionary containing topic info
            assigned_stance: Optional stance type (e.g., 'conservative')
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)

        Yields:
            Chunks of the generated response as strings
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.

        Returns:
            Dictionary containing model metadata
        """
        pass

    def is_initialized(self) -> bool:
        """Check if the model is initialized."""
        return self._initialized

    def cleanup(self) -> None:
        """
        Clean up any resources used by the model.

        Override this method if the implementation uses resources
        that need explicit cleanup (e.g., GPU memory).
        """
        self._initialized = False


class GenerationParams:
    """
    Parameters for text generation.

    This class provides a standardized way to pass generation parameters
    that can be used across different LLM providers.
    """

    def __init__(
        self,
        temperature: float = 0.7,
        max_new_tokens: int = 2048,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 1.0,
        do_sample: bool = True,
        **kwargs
    ):
        """
        Initialize generation parameters.

        Args:
            temperature: Controls randomness (0.0 = deterministic, 1.0 = very random)
            max_new_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling parameter
            repetition_penalty: Penalty for repeating tokens
            do_sample: Whether to use sampling
            **kwargs: Additional provider-specific parameters
        """
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.repetition_penalty = repetition_penalty
        self.do_sample = do_sample
        self.extra = kwargs

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "temperature": self.temperature,
            "max_new_tokens": self.max_new_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
            "do_sample": self.do_sample,
        }
        result.update(self.extra)
        return result
