"""
Deterministic intent detection — used when LLM is disabled.
Classifies free-text messages without any external calls.
"""

import re
from dataclasses import dataclass
from typing import Literal

IntentType = Literal["by_name", "by_ingredients", "favorites", "history", "help", "unknown"]

# Keywords that suggest an ingredient-based query
_INGREDIENT_KEYWORDS = re.compile(
    r"\b(make|mix|with|using|have|ingredients?|из|готовить|ингредиент)\b",
    re.IGNORECASE,
)

# Keywords that suggest a name-based query
_NAME_KEYWORDS = re.compile(
    r"\b(recipe|рецепт|how to make|как приготовить|what is|что такое|details?)\b",
    re.IGNORECASE,
)

# Common cocktail ingredients to detect ingredient-style messages
_COMMON_INGREDIENTS = {
    "vodka", "gin", "rum", "tequila", "whiskey", "whisky", "brandy", "beer",
    "wine", "champagne", "lime", "lemon", "juice", "soda", "water", "mint",
    "sugar", "salt", "ice", "cream", "milk", "triple sec", "vermouth",
    "bitters", "syrup", "ginger", "orange", "grenadine", "kahlua", "baileys",
}


@dataclass
class ParsedIntent:
    intent: IntentType
    name: str | None = None
    ingredients: list[str] | None = None


def detect_intent(text: str) -> ParsedIntent:
    """
    Deterministic heuristic intent detection.

    Rules (in priority order):
    1. Check for history/favorites keywords.
    2. Check if the message looks like an ingredient list (comma-separated
       or contains ingredient keywords).
    3. Otherwise assume it's a cocktail name search.
    """
    lower = text.strip().lower()

    # History / favorites shortcuts
    if any(k in lower for k in ("history", "история", "/history")):
        return ParsedIntent(intent="history")
    if any(k in lower for k in ("favorite", "избранное", "fav", "/favorites")):
        return ParsedIntent(intent="favorites")

    # Comma-separated → almost certainly ingredients
    if "," in text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if len(parts) >= 2:
            return ParsedIntent(intent="by_ingredients", ingredients=parts)

    # Check for ingredient keywords (but only if no name keyword matched)
    if _INGREDIENT_KEYWORDS.search(text) and not _NAME_KEYWORDS.search(text):
        # Try to strip keyword noise and extract ingredient list
        cleaned = _INGREDIENT_KEYWORDS.sub("", text).strip()
        # Remove common stop words
        cleaned = re.sub(r"\b(i|can|what|do|me|a|the|and|or)\b", "", cleaned, flags=re.I)
        parts = [p.strip() for p in re.split(r"[,\s]+", cleaned) if p.strip() and len(p) > 2]
        if parts:
            return ParsedIntent(intent="by_ingredients", ingredients=parts)

    # Check if any word is a known ingredient (only when no name keyword present)
    if not _NAME_KEYWORDS.search(text):
        words = re.findall(r"\b\w+\b", lower)
        matched_ingredients = [w for w in words if w in _COMMON_INGREDIENTS]
        if matched_ingredients:
            return ParsedIntent(intent="by_ingredients", ingredients=matched_ingredients)

    # Name-based keyword or recipe request — check BEFORE ingredient fallback
    if _NAME_KEYWORDS.search(text):
        # Extract name after stripping keyword noise
        cleaned = _NAME_KEYWORDS.sub("", text).strip()
        # Remove filler words
        cleaned = re.sub(r"\b(a|an|the|for|me|i|want|please)\b", "", cleaned, flags=re.I).strip()
        name = cleaned if cleaned else text.strip()
        return ParsedIntent(intent="by_name", name=name)

    # Default: treat entire message as a cocktail name
    return ParsedIntent(intent="by_name", name=text.strip())
