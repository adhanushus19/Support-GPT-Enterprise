import time
import logging
from typing import Dict, Any

from src.llm.provider import llm_provider
from src.observability.metrics import AGENT_EXECUTION_DURATION_SECONDS

logger = logging.getLogger("supportgpt.agents.resolver")

class ResolutionAgent:
    """
    Synthesizes historical context, customer problem description, and retrieved 
    KB citations to write a professional customer support message.
    """
    async def resolve(self, state: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"Resolver Node started for ticket_id: {state.get('ticket_id')}")

        if "Security threat" in "".join(state.get("errors", [])):
            return state

        subject = state.get("subject", "")
        description = state.get("description", "")
        citations = state.get("context_citations", [])

        # Build context prompt
        context_blocks = []
        for citation in citations:
            context_blocks.append(f"Source: {citation.source}\nContent: {citation.text}")
        combined_context = "\n\n".join(context_blocks) if context_blocks else "No relevant articles found in KB."

        try:
            # Generate the text from LLM provider
            response_text, in_tok, out_tok = await llm_provider.generate_resolution(
                subject=subject,
                description=description,
                context=combined_context
            )

            # Update metrics
            state["tokens_input"] = state.get("tokens_input", 0) + in_tok
            state["tokens_output"] = state.get("tokens_output", 0) + out_tok

            duration = time.time() - start_time
            AGENT_EXECUTION_DURATION_SECONDS.labels(agent_name="resolution_agent").observe(duration)

            return {
                **state,
                "suggested_response": response_text
            }

        except Exception as e:
            logger.error(f"Error formulating resolution in resolver: {e}")
            return {
                **state,
                "errors": state.get("errors", []) + [f"Resolver agent error: {str(e)}"],
                "suggested_response": "I apologize, but I encountered an error while writing a resolution. Please escalate to a support manager."
            }

resolution_agent = ResolutionAgent()
