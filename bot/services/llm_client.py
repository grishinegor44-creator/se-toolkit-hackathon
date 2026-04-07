"""
Optional LLM integration for natural language understanding.
When LLM_ENABLED=false or credentials are missing, the parse() method
returns None and the bot falls back to deterministic intent detection.
"""

import json
import logging
from typing import Any

from bot.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a cocktail assistant intent parser.
Your job is to classify user messages and extract search parameters.

Always respond with JSON only, no prose. Schema:
{
  "intent": "by_name" | "by_ingredients" | "favorites" | "history" | "help" | "unknown",
  "name": "<cocktail name if intent=by_name, else null>",
  "ingredients": ["<ingredient>", ...] if intent=by_ingredients, else null>
}

Examples:
User: "mojito recipe" → {"intent":"by_name","name":"mojito","ingredients":null}
User: "what can I make with vodka and lime?" → {"intent":"by_ingredients","name":null,"ingredients":["vodka","lime"]}
User: "my favorites" → {"intent":"favorites","name":null,"ingredients":null}
User: "show history" → {"intent":"history","name":null,"ingredients":null}
"""


class LLMClient:
    def __init__(self) -> None:
        self._enabled = (
            settings.llm_enabled
            and bool(settings.llm_api_key)
        )
        if self._enabled:
            try:
                from openai import AsyncOpenAI  # type: ignore
                self._client = AsyncOpenAI(
                    api_key=settings.llm_api_key,
                    base_url=settings.llm_api_base_url,
                )
                logger.info("LLM integration enabled (model=%s)", settings.llm_api_model)
            except ImportError:
                logger.warning("openai package not installed — LLM disabled")
                self._enabled = False
        else:
            logger.info("LLM integration disabled — using deterministic intent detection")

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def parse_intent(self, user_message: str) -> dict[str, Any] | None:
        """
        Parse user intent via LLM.
        Returns a dict with keys: intent, name, ingredients.
        Returns None if LLM is disabled or an error occurs.
        """
        if not self._enabled:
            return None
        try:
            response = await self._client.chat.completions.create(
                model=settings.llm_api_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=150,
                temperature=0.0,
            )
            raw = response.choices[0].message.content or ""
            # Strip markdown code blocks if present
            raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(raw)
        except Exception as e:
            logger.warning("LLM parse_intent failed: %s", e)
            return None
