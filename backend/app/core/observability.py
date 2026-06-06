"""
Observability module — Langfuse v4 integration.

Langfuse v4 uses OpenTelemetry under the hood. The Langfuse singleton is
initialised lazily from environment variables. When credentials are absent
(e.g. local dev / CI) the module still works — the client auto-disables and
all trace calls become no-ops.
"""

import logging

from langfuse import Langfuse

from app.core.config import settings

logger = logging.getLogger(__name__)

_langfuse_client: Langfuse | None = None


def get_langfuse() -> Langfuse:
    """Return a shared (lazily-initialised) Langfuse v4 client."""
    global _langfuse_client  # noqa: PLW0603

    if _langfuse_client is None:
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            _langfuse_client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
            )
            logger.info("Langfuse observability enabled — host: %s", settings.langfuse_host)
        else:
            # Credentials not provided — Langfuse v4 auto-disables when keys are missing
            _langfuse_client = Langfuse(
                public_key="disabled",
                secret_key="disabled",
                tracing_enabled=False,
            )
            logger.warning(
                "Langfuse credentials not configured. "
                "Set LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY to enable observability."
            )

    return _langfuse_client
