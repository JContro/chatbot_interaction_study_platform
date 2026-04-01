"""
vLLM LLM implementation.

This module provides an LLM backend that uses vLLM for efficient inference
with PagedAttention and tensor parallelism support.

Configuration kwargs (all optional):
    tensor_parallel_size  – number of GPUs for tensor parallelism (default: 1)
    gpu_memory_utilization – fraction of GPU memory to use (default: 0.9)
    max_model_len         – maximum model context length (default: 2048)
    dtype                  – data type: 'float16', 'bfloat16', or 'auto' (default: 'auto')
    enforce_eager         – don't capture CUDA graphs (default: False)
    trust_remote_code      – allow custom model code (default: True)
"""

import gc
import logging
from typing import Any, Dict, Iterator, Optional

from .base import BaseLLM, ConversationHistory, GenerationParams

logger = logging.getLogger(__name__)


class VLLM(BaseLLM):
    """
    LLM backend that uses vLLM for high-throughput inference.

    vLLM provides:
    - PagedAttention for efficient memory management
    - Tensor parallelism for multi-GPU inference
    - Automatic batching of requests
    - CUDA graph optimization
    """

    def __init__(
        self,
        model_name: str,
        tensor_parallel_size: int = 1,
        gpu_memory_utilization: float = 0.9,
        max_model_len: Optional[int] = None,
        dtype: str = "auto",
        enforce_eager: bool = False,
        trust_remote_code: bool = True,
        **kwargs,
    ):
        """
        Initialize the vLLM backend.

        Args:
            model_name: HuggingFace model name or path
            tensor_parallel_size: Number of GPUs for tensor parallelism
            gpu_memory_utilization: Fraction of GPU memory to use (0.0-1.0)
            max_model_len: Maximum context length (None = auto from model)
            dtype: Data type for model weights
            enforce_eager: Disable CUDA graph capture
            trust_remote_code: Allow custom model code from Hub
            **kwargs: Additional configuration (passed to base)
        """
        super().__init__(model_name, **kwargs)
        self.tensor_parallel_size = tensor_parallel_size
        self.gpu_memory_utilization = gpu_memory_utilization
        self.max_model_len = max_model_len
        self.dtype = dtype
        self.enforce_eager = enforce_eager
        self.trust_remote_code = trust_remote_code
        self._llm = None
        self._tokenizer = None

    # ------------------------------------------------------------------
    # BaseLLM interface
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Load the model using vLLM's LLM engine."""
        if self._initialized:
            return

        try:
            from vllm import LLM, SamplingParams
            from transformers import AutoTokenizer

            logger.info("Loading tokenizer for '%s' …", self.model_name)
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=self.trust_remote_code,
            )

            logger.info(
                "Initializing vLLM engine for '%s' "
                "(tensor_parallel_size=%d, gpu_memory_utilization=%.2f) …",
                self.model_name,
                self.tensor_parallel_size,
                self.gpu_memory_utilization,
            )

            self._llm = LLM(
                model=self.model_name,
                tensor_parallel_size=self.tensor_parallel_size,
                gpu_memory_utilization=self.gpu_memory_utilization,
                max_model_len=self.max_model_len,
                dtype=self.dtype,
                enforce_eager=self.enforce_eager,
                trust_remote_code=self.trust_remote_code,
            )

            self._initialized = True
            logger.info("vLLM engine for '%s' ready.", self.model_name)

        except Exception:
            logger.exception("Failed to initialise vLLM model '%s'", self.model_name)
            raise

    def generate(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory] = None,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate a reply to *prompt*, optionally using *conversation_history*
        for multi-turn context.

        When topic_data and assigned_stance are provided, the chatbot will be
        instructed to adopt a specific perspective on the topic.
        """
        if not self._initialized:
            self.initialize()

        from vllm import SamplingParams

        # ---- resolve generation parameters --------------------------------
        gen_param_keys = {
            "temperature", "max_new_tokens", "top_p", "top_k",
            "repetition_penalty", "do_sample",
        }
        gen_kwargs = {k: v for k, v in kwargs.items() if k in gen_param_keys}
        params = GenerationParams(**gen_kwargs)

        # vLLM uses different parameter names
        sampling_params = SamplingParams(
            temperature=params.temperature,
            max_tokens=params.max_new_tokens,
            top_p=params.top_p,
            top_k=params.top_k if params.top_k > 0 else None,
            repetition_penalty=params.repetition_penalty,
        )

        # ---- build system prompt with topic and stance info ---------------
        system_prompt = self._build_system_prompt(topic_data, assigned_stance)

        # ---- build the message list for the model -------------------------
        if conversation_history is not None:
            messages = conversation_history.get_messages()
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

        # ---- format the prompt using chat template -----------------------
        input_text = self._format_prompt(messages)

        # ---- generate -----------------------------------------------------
        outputs = self._llm.generate([input_text], sampling_params)
        response = outputs[0].outputs[0].text.strip()
        return response

    def generate_stream(
        self,
        prompt: str,
        conversation_history: Optional[ConversationHistory] = None,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
        **kwargs,
    ) -> Iterator[str]:
        """
        Generate a streaming reply to *prompt*, yielding tokens as they are generated.
        """
        if not self._initialized:
            self.initialize()

        from vllm import SamplingParams

        # ---- resolve generation parameters --------------------------------
        gen_param_keys = {
            "temperature", "max_new_tokens", "top_p", "top_k",
            "repetition_penalty", "do_sample",
        }
        gen_kwargs = {k: v for k, v in kwargs.items() if k in gen_param_keys}
        params = GenerationParams(**gen_kwargs)

        sampling_params = SamplingParams(
            temperature=params.temperature,
            max_tokens=params.max_new_tokens,
            top_p=params.top_p,
            top_k=params.top_k if params.top_k > 0 else None,
            repetition_penalty=params.repetition_penalty,
        )

        # ---- build system prompt with topic and stance info ---------------
        system_prompt = self._build_system_prompt(topic_data, assigned_stance)

        # ---- build the message list for the model -------------------------
        if conversation_history is not None:
            messages = conversation_history.get_messages()
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages
        else:
            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                messages = [{"role": "system", "content": system_prompt}] + messages

        # ---- format the prompt --------------------------------------------
        input_text = self._format_prompt(messages)

        # ---- streaming generate -------------------------------------------
        # vLLM 0.13.x doesn't have sync=False parameter.
        # For true streaming, we would need AsyncLLMEngine.
        # Here we use the simpler approach of generating and yielding at once.
        outputs = self._llm.generate([input_text], sampling_params)
        response = outputs[0].outputs[0].text.strip()
        yield response

    def _format_prompt(self, messages: list) -> str:
        """
        Format messages into a prompt string using the tokenizer's chat template,
        or fall back to a simple concatenation.
        """
        if self._tokenizer and getattr(self._tokenizer, "chat_template", None):
            return self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            # Fallback: naive role-labelled concatenation
            input_text = ""
            for msg in messages:
                role = msg["role"].capitalize()
                input_text += f"{role}: {msg['content']}\n"
            input_text += "Assistant:"
            return input_text

    def _build_system_prompt(
        self,
        topic_data: Optional[Dict[str, Any]] = None,
        assigned_stance: Optional[str] = None,
    ) -> str:
        """
        Build a system prompt that sets the chatbot's perspective based on
        the topic and assigned stance.
        """
        if not topic_data or not assigned_stance:
            return ""

        stance_info = topic_data.get('stances', {}).get(assigned_stance, {})
        if not stance_info:
            return ""

        # Build a comprehensive system prompt
        system_parts = [
            f"You are having a conversation about: {topic_data.get('specific_question', 'Unknown topic')}",
            f"Topic Area: {topic_data.get('topic_area', 'General')}",
            "",
            f"Your assigned stance is: {assigned_stance.upper()}",
            "",
            "Your perspective positions:",
            f"- PRO (supporting): {stance_info.get('pro', 'Not available')}",
            f"- CON (opposing): {stance_info.get('con', 'Not available')}",
            f"- NEUTRAL (balanced): {stance_info.get('neutral', 'Not available')}",
            "",
            "Instructions:",
            f"- Adopt the {assigned_stance} perspective in your responses",
            "- Be engaging, thoughtful, and true to your assigned stance",
            "- You may reference your pro/con/neutral positions as needed",
            "- Stay in character as a chatbot with this specific viewpoint",
        ]

        return "\n".join(system_parts)

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "vLLM",
            "model_name": self.model_name,
            "tensor_parallel_size": self.tensor_parallel_size,
            "gpu_memory_utilization": self.gpu_memory_utilization,
            "initialized": self._initialized,
        }

    def cleanup(self) -> None:
        """Release GPU memory held by the vLLM engine."""
        if self._llm is not None:
            del self._llm
            self._llm = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        gc.collect()
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass
        super().cleanup()
