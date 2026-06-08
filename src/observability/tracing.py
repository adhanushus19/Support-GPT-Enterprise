import os
import logging
from src.config import settings

logger = logging.getLogger("supportgpt.observability.tracing")

def init_tracing() -> None:
    """Initialize OpenTelemetry and LangChain LangSmith tracing settings."""
    # LangSmith config
    if settings.LANGCHAIN_TRACING_V2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if settings.LANGCHAIN_API_KEY:
            os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        logger.info("LangSmith tracing enabled and environment variables configured.")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        logger.info("LangSmith tracing is disabled.")

    # OpenTelemetry config (simulated hook or basic setup)
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        provider = TracerProvider()
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry TracerProvider initialized with Console Exporter.")
    except Exception as e:
        logger.warning(f"Could not initialize OpenTelemetry exporter: {e}")
