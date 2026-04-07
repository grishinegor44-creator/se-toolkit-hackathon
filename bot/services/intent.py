"""
Deterministic intent detection — used when LLM is disabled or fails.
Handles free-text messages without any external calls.
"""

import re
from dataclasses import dataclass
from typing import Literal

IntentType = Literal["by_name", "by_ingredients", "random", "favorites", "history", "help", "unknown"]

# ── Noise prefix patterns ─────────────────────────────────────────────────────
# Strips phrases like "how to do", "recipe for", "how to make a", etc.
_NOISE_PREFIX = re.compile(
    r"""(?ix)^
    (?:
        (?:how\s+(?:do\s+i\s+|to\s+)(?:make|do|prepare|mix|create|drink|get)\s+) |
        (?:give\s+me\s+(?:a\s+|the\s+)?(?:recipe\s+(?:for\s+)?)?)          |
        (?:recipe\s+(?:for\s+|of\s+)?)                                       |
        (?:what\s+is\s+(?:a\s+|an\s+|the\s+)?)                              |
        (?:tell\s+me\s+(?:about\s+)?(?:a\s+|an\s+)?)                        |
        (?:show\s+me\s+(?:a\s+|the\s+)?)                                     |
        (?:i\s+want\s+(?:to\s+(?:make\s+|drink\s+))?(?:a\s+|an\s+)?)       |
        (?:make\s+(?:me\s+)?(?:a\s+|an\s+)?)                                |
        (?:can\s+you\s+(?:make\s+)?(?:a\s+|an\s+)?)
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Strips vague qualifiers before the cocktail name
_QUALIFIER = re.compile(
    r"\b(standard|standart|classic|traditional|perfect|simple|basic|regular|original|proper|good|nice)\s+",
    re.IGNORECASE,
)

# Detects "with/using/have/got <ingredients>" patterns
_WITH_PATTERN = re.compile(
    r"\b(?:with|using|have|got|i\s+have|do\s+with|make\s+with)\b\s*(.+?)(?:[?!.]|$)",
    re.IGNORECASE,
)

# Split-word separators inside ingredient lists
_ING_SPLIT = re.compile(r"\band\b|\bor\b|,", re.IGNORECASE)

# Random / surprise keywords
_RANDOM_WORDS = frozenset({
    "random", "surprise", "any", "whatever", "anything",
    "случайный", "случайно", "любой", "удиви",
})

# Well-known cocktail ingredient words for fallback detection
_COMMON_INGREDIENTS = frozenset({
    "vodka", "gin", "rum", "tequila", "whiskey", "whisky", "brandy", "beer",
    "wine", "champagne", "lime", "lemon", "juice", "soda", "water", "mint",
    "sugar", "salt", "ice", "cream", "milk", "triple sec", "vermouth",
    "bitters", "syrup", "ginger", "orange", "grenadine", "kahlua", "baileys",
    "cola", "coke", "tonic", "absinthe", "bourbon", "scotch", "prosecco",
    "amaretto", "campari", "curacao", "schnapps", "mezcal", "sake",
})

_STOP_WORDS = frozenset({"a", "an", "the", "some", "any", "do", "make", "me", "i", "my"})


@dataclass
class ParsedIntent:
    intent: IntentType
    name: str | None = None
    ingredients: list[str] | None = None


def detect_intent(text: str) -> ParsedIntent:
    """
    Detect user intent from free-text input.

    Priority order:
    1. History / favorites shortcuts
    2. Random cocktail keywords
    3. Comma-separated list → ingredients
    4. "with/using/have X and Y" pattern → ingredients
    5. Noise-prefix stripping → clean cocktail name
    6. Known ingredient word fallback → ingredients
    7. Default: treat whole text as cocktail name
    """
    text = text.strip()
    lower = text.lower()

    # 1. History / favorites
    if any(k in lower for k in ("history", "история")):
        return ParsedIntent(intent="history")
    if any(k in lower for k in ("favorite", "избранное", "fav")):
        return ParsedIntent(intent="favorites")

    # 2. Random cocktail
    words = set(re.findall(r"\b\w+\b", lower))
    if words & _RANDOM_WORDS:
        return ParsedIntent(intent="random")

    # 3. Comma-separated → ingredients
    if "," in text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if len(parts) >= 2:
            return ParsedIntent(intent="by_ingredients", ingredients=parts)

    # 4. "with/using/have X and Y" → ingredients
    m = _WITH_PATTERN.search(text)
    if m:
        after = m.group(1).strip()
        parts = [
            p.strip()
            for p in _ING_SPLIT.split(after)
            if p.strip() and len(p.strip()) > 1 and p.strip().lower() not in _STOP_WORDS
        ]
        if parts:
            return ParsedIntent(intent="by_ingredients", ingredients=parts)

    # 5. Strip noise prefix → clean cocktail name
    cleaned = _NOISE_PREFIX.sub("", text).strip()
    cleaned = re.sub(r"^(?:a|an|the)\s+", "", cleaned, flags=re.I).strip()
    cleaned = _QUALIFIER.sub("", cleaned).strip()
    if cleaned and cleaned.lower() != lower and len(cleaned) > 1:
        return ParsedIntent(intent="by_name", name=cleaned)

    # 6. Known ingredient word fallback
    matched = [w for w in words if w in _COMMON_INGREDIENTS]
    if matched:
        return ParsedIntent(intent="by_ingredients", ingredients=matched)

    # 7. Default: treat whole text as cocktail name
    return ParsedIntent(intent="by_name", name=text)
