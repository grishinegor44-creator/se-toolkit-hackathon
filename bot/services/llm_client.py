"""
Optional LLM integration for natural language understanding.
When LLM_ENABLED=false or credentials are missing, parse_intent() returns
None and the bot falls back to deterministic intent detection.
"""

import json
import logging
from typing import Any

from bot.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a cocktail assistant intent parser.
Classify user messages and extract search parameters.

Always respond with JSON ONLY — no prose, no markdown code fences.

Schema:
{
  "intent": "by_name" | "by_ingredients" | "random" | "favorites" | "history" | "help" | "unknown",
  "name": "<cocktail name if intent=by_name, else null>",
  "ingredients": ["<ingredient>", ...] or null
}

Rules:
- "by_name": user asks about a specific cocktail recipe or wants to know how to make one.
  Extract ONLY the cocktail name — strip noise like "how to do", "recipe for", "how to make", qualifiers like "standard", "classic".
- "by_ingredients": user provides a list of ingredients or asks what can be made FROM them.
  Normalize ingredient names to standard English cocktail terms (e.g. "cola" → "Coca-Cola", "tonic" → "Tonic Water").
- "random": user wants any/random/surprise cocktail.
- "favorites": user asks about their saved cocktails.
- "history": user asks about their search history.

Examples:
"how to do standart cosmopolitan"  → {"intent":"by_name","name":"Cosmopolitan","ingredients":null}
"what can i do with rum and cola"  → {"intent":"by_ingredients","name":null,"ingredients":["rum","Coca-Cola"]}
"Mojito recipe"                    → {"intent":"by_name","name":"Mojito","ingredients":null}
"vodka, lime, mint"                → {"intent":"by_ingredients","name":null,"ingredients":["Vodka","Lime juice","Mint"]}
"surprise me"                      → {"intent":"random","name":null,"ingredients":null}
"random cocktail"                  → {"intent":"random","name":null,"ingredients":null}
"show my favorites"                → {"intent":"favorites","name":null,"ingredients":null}
"""


class LLMClient:
    def __init__(self) -> None:
        self._enabled = settings.llm_enabled and bool(settings.llm_api_key)
        if self._enabled:
            try:
                from openai import AsyncOpenAI  # type: ignore
                self._client = AsyncOpenAI(
                    api_key=settings.llm_api_key,
                    base_url=settings.llm_api_base_url,
                )
                logger.info("LLM enabled: %s via %s", settings.llm_api_model, settings.llm_api_base_url)
            except ImportError:
                logger.warning("openai package not installed — LLM disabled")
                self._enabled = False
        else:
            logger.info("LLM disabled — using deterministic intent detection")

    @property
    def enabled(self) -> bool:
        return self._enabled

    async def parse_intent(self, user_message: str) -> dict[str, Any] | None:
        """
        Parse user intent via LLM.
        Returns dict with keys: intent, name, ingredients.
        Returns None if LLM is disabled or an error occurs (bot falls back to deterministic).
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
                max_tokens=200,
                temperature=0.0,
            )
            raw = response.choices[0].message.content or ""
            return self._extract_json(raw)
        except Exception as e:
            logger.warning("LLM request failed: %s — falling back to deterministic", e)
            return None

    @staticmethod
    def _extract_json(raw: str) -> dict | None:
        """Robustly extract a JSON object from a possibly verbose model response."""
        import re
        raw = raw.strip()
        if not raw:
            return None
        # Strip markdown code fences
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        # Try parsing the whole thing first
        try:
            result = json.loads(raw)
            if isinstance(result, dict) and "intent" in result:
                return result
        except json.JSONDecodeError:
            pass
        # Find the first {...} block (handles verbose model preamble)
        match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                if isinstance(result, dict) and "intent" in result:
                    return result
            except json.JSONDecodeError:
                pass
        logger.warning("LLM returned unparseable content: %r", raw[:120])
        return None
