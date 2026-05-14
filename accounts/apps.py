import logging
import os
import sys
import threading

from django.apps import AppConfig

logger = logging.getLogger(__name__)


def _preload_llm() -> None:
    """
    Pre-warm the LLM so the first HTTP request is not penalised by model
    loading time.  Runs in a daemon thread so the server can start serving
    immediately while the model loads in the background.
    """
    import time
    _t0 = time.time()
    try:
        logger.info("LLM pre-load: starting …")
        from accounts.llm.registry import get_llm
        get_llm()
        logger.info("LLM pre-load: complete in %.1f s.", time.time() - _t0)
    except Exception:
        logger.exception(
            "LLM pre-load failed after %.1f s – model will be loaded on the first request instead.",
            time.time() - _t0,
        )


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self) -> None:
        """
        Called by Django once the application registry is fully populated.

        Pre-loads the LLM in a daemon thread so that:
          - The web server is not blocked during startup (no 10-min wait).
          - The first HTTP request does not pay the full model-load penalty.
          - If the model hasn't finished loading by the first request,
            get_llm() will block until it does.

        Guard rails:
          - Skip for management commands that don't serve HTTP (migrate, etc.)
          - On Django's dev server, skip the outer file-watcher process
            (RUN_MAIN is unset there) to avoid loading the model twice.
        """
        _NON_SERVER_COMMANDS = {
            "migrate", "makemigrations", "collectstatic", "shell",
            "createsuperuser", "check", "test", "dbshell",
            "showmigrations", "sqlmigrate", "dumpdata", "loaddata",
        }

        if len(sys.argv) > 1 and sys.argv[1] in _NON_SERVER_COMMANDS:
            logger.debug(
                "Skipping LLM pre-load for management command '%s'.", sys.argv[1]
            )
            return

        # During `manage.py runserver`, Django's autoreloader spawns a child
        # process with RUN_MAIN=true.  Skip the outer watcher process.
        if "runserver" in sys.argv and os.environ.get("RUN_MAIN") != "true":
            return

        # Load LLM in the background so the server starts immediately
        thread = threading.Thread(target=_preload_llm, daemon=True)
        thread.start()
