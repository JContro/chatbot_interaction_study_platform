"""
LLM Registry – thread-safe lazy singleton for the configured LLM backend.

Usage
-----
From any view or service:

    from accounts.llm.registry import get_llm

    llm = get_llm()               # loads & caches on first call
    reply = llm.generate(prompt, history)

Configuration (in Django settings.py)
--------------------------------------
    LLM_CONFIG = {
        # Dotted import path to any BaseLLM subclass.
        # Swap this to change backend without touching application code.
        "provider": "accounts.llm.huggingface.HuggingFaceLLM",

        # Passed as model_name to the provider constructor.
        "model_name": "Qwen/Qwen3.5-35B-A3B",

        # Any additional constructor kwargs for the chosen provider:
        "device": "cpu",
    }

To hot-swap the model (e.g. in tests), call reset_llm() then get_llm() again.
"""

import importlib
import logging
import threading
from typing import Optional

from .base import BaseLLM

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_llm_instance: Optional[BaseLLM] = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _import_class(dotted_path: str) -> type:
    """Resolve a dotted import path like 'a.b.c.ClassName' to the class."""
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_llm() -> BaseLLM:
    """
    Return the globally-shared, lazily-initialised LLM instance.

    Thread-safe: the model is loaded and initialised at most once per process.
    Subsequent calls return the cached instance immediately.
    """
    global _llm_instance

    # Fast path – no lock needed once the instance exists.
    if _llm_instance is not None:
        return _llm_instance

    with _lock:
        # Double-checked locking: re-check after acquiring the lock.
        if _llm_instance is not None:
            return _llm_instance

        from django.conf import settings

        config: dict = getattr(settings, "LLM_CONFIG", {})

        provider_path: str = config.get(
            "provider",
            "accounts.llm.huggingface.HuggingFaceLLM",
        )
        model_name: str = config.get(
            "model_name",
            "en/Qwen3-14QwB",
        )

        # Everything else in LLM_CONFIG is forwarded to the constructor.
        init_kwargs = {
            k: v for k, v in config.items()
            if k not in ("provider", "model_name")
        }

        logger.info(
            "Initialising LLM | provider=%s | model=%s | kwargs=%s",
            provider_path,
            model_name,
            init_kwargs,
        )

        cls = _import_class(provider_path)
        instance: BaseLLM = cls(model_name=model_name, **init_kwargs)
        instance.initialize()

        _llm_instance = instance
        return _llm_instance


def reset_llm() -> None:
    """
    Release the current LLM instance and free its resources.

    Useful in tests or when you want to reload the model with new settings.
    After calling this, the next call to get_llm() will create a fresh instance.
    """
    global _llm_instance
    with _lock:
        if _llm_instance is not None:
            _llm_instance.cleanup()
            _llm_instance = None
            logger.info("LLM instance released.")
