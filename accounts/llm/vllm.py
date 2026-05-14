"""
vLLM Server API implementation.

This module provides an LLM backend that communicates with a running vLLM server
via its OpenAI-compatible REST API. No model loading is performed locally,
making it suitable for scenarios where the vLLM server runs on a separate
container/machine with dedicated GPU memory.

vLLM API Reference: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
"""

import logging
import time
from typing import Any, Dict, Iterator, Optional

import requests

from .base import BaseLLM, ConversationHistory, GenerationParams

logger = logging.getLogger(__name__)


class VLLMAPI(BaseLLM):
    """
    LLM backend that delegates to a vLLM server via HTTP API.

    This provider does NOT load any model locally. It communicates with
    a vLLM server that is expected to be already running.

    Configuration kwargs:
        api_base      – Base URL of the vLLM server (default: http://localhost:8090)
        api_key       – API key for authentication (optional, default: None)
        timeout       – Request timeout in seconds (default: 120)
    """

    def __init__(self, model_name: str, api_base: str = "http://localhost:8090", **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_base = api_base.rstrip("/")
        self.api_key = self.config.get("api_key", None)
        self.timeout = self.config.get("timeout", 120)

    # ------------------------------------------------------------------
    # BaseLLM interface
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """
        Verify connectivity with the vLLM server.

        Unlike HuggingFaceLLM, this does NOT load any model locally.
        It only checks that the vLLM server is reachable and has the
        expected model available.

        Retries with exponential backoff to handle the case where the
        vLLM server is still starting up (e.g. loading the model, capturing
        CUDA graphs) when this method is first called.
        """
        if self._initialized:
            return

        max_retries = self.config.get("init_max_retries", 30)
        base_delay = self.config.get("init_base_delay", 2.0)
        max_delay = self.config.get("init_max_delay", 30.0)

        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                # Try to get model info - vLLM provides this via /v1/models
                response = requests.get(
                    f"{self.api_base}/v1/models",
                    timeout=10,
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                )
                response.raise_for_status()
                models = response.json().get("data", [])
                model_ids = [m.get("id") for m in models]

                logger.info(
                    "Connected to vLLM server at '%s'. Available models: %s",
                    self.api_base,
                    model_ids,
                )

                # Optionally verify the configured model is available
                if self.model_name not in model_ids:
                    logger.warning(
                        "Model '%s' not found in vLLM server models: %s. "
                        "Proceeding anyway - the server may still serve it.",
                        self.model_name,
                        model_ids,
                    )

                self._initialized = True
                return

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < max_retries:
                    # Exponential backoff: 2s, 4s, 8s, ... capped at max_delay
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        "vLLM server not ready yet (attempt %d/%d): %s. "
                        "Retrying in %.1fs ...",
                        attempt,
                        max_retries,
                        e,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        "Failed to connect to vLLM server at '%s' after %d attempts: %s",
                        self.api_base,
                        max_retries,
                        e,
                    )

        raise RuntimeError(
            f"Cannot connect to vLLM server at {self.api_base} after {max_retries} "
            f"retries. Please ensure the vLLM server is running."
        ) from last_exception

    def generate(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory] = None,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate a non-streaming reply to *prompt*.

        Accumulates the full response from the streaming API and returns it as a string.
        For streaming, use generate_stream() directly.
        """
        # Collect all chunks from streaming
        chunks = list(self.generate_stream(
            prompt=prompt,
            conversation_history=conversation_history,
            topic_data=topic_data,
            assigned_stance=assigned_stance,
            **kwargs,
        ))
        return "".join(chunks)

    def generate_stream(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory] = None,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
        **kwargs,
    ) -> Iterator[str]:
        """
        Generate a streaming reply via the vLLM chat completion API.

        Yields chunks of the generated response as they arrive from the server.
        Uses the OpenAI-compatible /v1/chat/completions endpoint with stream=True.
        """
        if not self._initialized:
            self.initialize()

        # Build system prompt with topic and stance info
        system_prompt = self._build_system_prompt(topic_data, assigned_stance)

        # Build the message list for the API
        messages = self._build_messages(prompt, conversation_history, system_prompt)

        # Resolve generation parameters
        params = self._resolve_generation_params(**kwargs)

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Prepare request payload for /v1/chat/completions
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            **params,
        }

        logger.debug(
            "vLLM chat completion request | model=%s | payload=%s",
            self.model_name,
            payload,
        )

        try:
            with requests.post(
                f"{self.api_base}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=self.timeout,
                stream=True,
            ) as response:
                response.raise_for_status()

                # Process streaming SSE response
                for line in response.iter_lines():
                    if not line:
                        continue

                    # vLLM sends SSE data lines prefixed with "data: "
                    line_text = line.decode("utf-8")
                    if not line_text.startswith("data: "):
                        continue

                    data_str = line_text[6:].strip()
                    if data_str == "[DONE]":
                        break

                    # Parse the SSE data payload
                    import json as _json

                    try:
                        chunk = _json.loads(data_str)
                    except _json.JSONDecodeError:
                        logger.warning("Failed to parse SSE chunk: %s", data_str)
                        continue

                    # Extract delta content from the chunk
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content

        except requests.exceptions.RequestException as e:
            logger.error("vLLM API request failed: %s", e)
            raise RuntimeError(f"vLLM API request failed: {e}") from e

    def get_model_info(self) -> Dict[str, Any]:
        """Return metadata about the model served by the vLLM server."""
        return {
            "provider": "vllm",
            "model_name": self.model_name,
            "api_base": self.api_base,
            "description": f"vLLM server at {self.api_base} serving {self.model_name}",
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_system_prompt(
        self,
        topic_data: Optional[Dict[str, Any]],
        assigned_stance: Optional[str],
    ) -> Optional[str]:
        """
        Build a system prompt incorporating topic and stance information.

        Returns None if neither topic_data nor assigned_stance is provided.
        """
        if not topic_data and not assigned_stance:
            return None

        parts = []

        if topic_data:
            topic_title = topic_data.get("title", "")
            topic_description = topic_data.get("description", "")
            if topic_title:
                parts.append(f"Topic: {topic_title}")
            if topic_description:
                parts.append(f"Description: {topic_description}")

        if assigned_stance:
            parts.append(
                f"You are taking the perspective of someone with a '{assigned_stance}' stance on this topic."
            )

        return "\n\n".join(parts)

    def _build_messages(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory],
        system_prompt: Optional[str],
    ) -> list:
        """
        Build the messages list for the vLLM chat completion API.

        Constructs a properly ordered list of messages following the
        OpenAI chat format.
        """
        messages = []

        # Add system prompt first if present
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        if conversation_history is not None:
            history_messages = conversation_history.get_messages()
            messages.extend(history_messages)

        # Add the current user prompt
        messages.append({"role": "user", "content": prompt})

        return messages

    def _resolve_generation_params(self, **kwargs) -> Dict[str, Any]:
        """
        Extract and normalize generation parameters for the vLLM API.

        Maps common parameter names to vLLM/OpenAI-compatible names.
        """
        gen_param_keys = {
            "temperature",
            "max_tokens",
            "max_new_tokens",
            "top_p",
            "top_k",
            "repetition_penalty",
            "do_sample",
            "stop",
        }

        params = {}

        for key in gen_param_keys:
            if key in kwargs:
                value = kwargs[key]
                # Map max_new_tokens to max_tokens for API compatibility
                if key == "max_new_tokens":
                    params["max_tokens"] = value
                else:
                    params[key] = value

        # Set defaults if not provided
        if "temperature" not in params and "do_sample" in kwargs:
            # Only set temperature if explicitly asked to sample
            params.setdefault("temperature", 0.7)

        if "max_tokens" not in params and "max_new_tokens" not in kwargs:
            params["max_tokens"] = 2048

        return params
