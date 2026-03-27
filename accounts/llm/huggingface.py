"""
HuggingFace Transformers LLM implementation.

Supports any causal language model available on HuggingFace Hub that can
be loaded via AutoModelForCausalLM / AutoTokenizer (e.g. SmolLM2-135M-Instruct,
Mistral, LLaMA, Phi, etc.).

This module only imports from .base and from transformers/torch at runtime so
that the rest of the application does not take a hard dependency on those
packages unless this backend is actually configured.
"""

import gc
import logging
from typing import Any, Dict, Optional

from .base import BaseLLM, ConversationHistory, GenerationParams

logger = logging.getLogger(__name__)


class HuggingFaceLLM(BaseLLM):
    """
    LLM backend that delegates to a HuggingFace causal-language model.

    Configuration kwargs (all optional):
        device       – 'cpu', 'cuda', 'mps', or 'auto'  (default: 'cpu')
        torch_dtype  – torch dtype string, e.g. 'float16' or 'float32'.
                       Defaults to float32 on CPU, float16 on GPU.
        cache_dir    – local directory to cache downloaded weights.
    """

    def __init__(self, model_name: str, device: str = "cpu", **kwargs):
        super().__init__(model_name, **kwargs)
        self.device = device
        self._model = None
        self._tokenizer = None

    # ------------------------------------------------------------------
    # BaseLLM interface
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Download (or load from cache) the model and tokenizer."""
        if self._initialized:
            return

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            cache_dir = self.config.get("cache_dir", None)

            logger.info("Loading tokenizer for '%s' …", self.model_name)
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=cache_dir,
            )

            # Resolve dtype
            dtype_str = self.config.get("torch_dtype", None)
            if dtype_str:
                torch_dtype = getattr(torch, dtype_str)
            elif self.device == "cpu":
                torch_dtype = torch.float32
            else:
                torch_dtype = torch.float16

            logger.info(
                "Loading model '%s' on device '%s' (dtype=%s) …",
                self.model_name,
                self.device,
                torch_dtype,
            )

            # When device == 'auto' let accelerate handle placement;
            # otherwise load on CPU first then move.
            if self.device == "auto":
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch_dtype,
                    device_map="auto",
                    cache_dir=cache_dir,
                )
            else:
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch_dtype,
                    cache_dir=cache_dir,
                )
                self._model = self._model.to(self.device)

            self._model.eval()
            self._initialized = True
            logger.info("Model '%s' ready.", self.model_name)

        except Exception:
            logger.exception(
                "Failed to initialise model '%s'", self.model_name)
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

        Generation kwargs (temperature, max_new_tokens, top_p, top_k,
        repetition_penalty, do_sample) can be overridden per-call.
        """
        if not self._initialized:
            self.initialize()

        import torch

        # ---- resolve generation parameters --------------------------------
        gen_param_keys = {
            "temperature", "max_new_tokens", "top_p", "top_k",
            "repetition_penalty", "do_sample",
        }
        gen_kwargs = {k: v for k, v in kwargs.items() if k in gen_param_keys}
        params = GenerationParams(**gen_kwargs)

        # ---- build system prompt with topic and stance info ---------------
        system_prompt = self._build_system_prompt(topic_data, assigned_stance)

        # ---- build the message list for the model -------------------------
        if conversation_history is not None:
            messages = conversation_history.get_messages()
            # Prepend system prompt if we have topic/stance info
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt}] + messages
        else:
            messages = [{"role": "user", "content": prompt}]
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt}] + messages

        # ---- format the prompt --------------------------------------------
        if getattr(self._tokenizer, "chat_template", None):
            # Best path: use the tokenizer's own chat template (handles INST
            # tags, <|im_start|>, etc. automatically for each model family).
            input_text = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            # Fallback: naive role-labelled concatenation.
            input_text = ""
            for msg in messages:
                role = msg["role"].capitalize()
                input_text += f"{role}: {msg['content']}\n"
            input_text += "Assistant:"

        # ---- tokenise & generate ------------------------------------------
        model_device = next(self._model.parameters()).device
        inputs = self._tokenizer(
            input_text, return_tensors="pt").to(model_device)
        prompt_length = inputs["input_ids"].shape[1]

        with torch.no_grad():
            output_ids = self._model.generate(
                **inputs,
                max_new_tokens=params.max_new_tokens,
                temperature=params.temperature,
                top_p=params.top_p,
                top_k=params.top_k,
                repetition_penalty=params.repetition_penalty,
                do_sample=params.do_sample,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        # Decode only the newly generated tokens (strip the echoed prompt).
        new_ids = output_ids[0][prompt_length:]
        response = self._tokenizer.decode(
            new_ids, skip_special_tokens=True).strip()
        return response

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
            "provider": "HuggingFace",
            "model_name": self.model_name,
            "device": self.device,
            "initialized": self._initialized,
        }

    def cleanup(self) -> None:
        """Release GPU / CPU memory held by the model."""
        if self._model is not None:
            del self._model
            self._model = None
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
