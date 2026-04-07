"""
Free-text message handler.
Uses LLM for intent detection when enabled, falls back to deterministic
heuristics otherwise.
"""

import logging

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message

from bot.services.intent import detect_intent
from bot.services.llm_client import LLMClient
from bot.handlers.commands import _handle_by_name, _handle_by_ingredients

logger = logging.getLogger(__name__)
router = Router()

_llm = LLMClient()


@router.message(StateFilter(None))
async def handle_text(message: Message) -> None:
    text = (message.text or "").strip()
    if not text or text.startswith("/"):
        return  # Let command router handle slash commands

    # 1. Try LLM intent detection
    parsed = None
    if _llm.enabled:
        raw = await _llm.parse_intent(text)
        if raw:
            intent = raw.get("intent", "unknown")
            parsed_name = raw.get("name")
            parsed_ings = raw.get("ingredients")
            if intent == "by_name" and parsed_name:
                await _handle_by_name(message, parsed_name)
                return
            if intent == "by_ingredients" and parsed_ings:
                await _handle_by_ingredients(message, parsed_ings)
                return
            if intent == "random":
                await _handle_random(message)
                return
            if intent == "history":
                from bot.handlers.commands import cmd_history
                await cmd_history(message)
                return
            if intent == "favorites":
                from bot.handlers.commands import cmd_favorites
                await cmd_favorites(message)
                return
            if intent == "help":
                from bot.handlers.commands import cmd_help
                await cmd_help(message)
                return

    # 2. Deterministic fallback
    p = detect_intent(text)
    if p.intent == "by_name" and p.name:
        await _handle_by_name(message, p.name)
    elif p.intent == "by_ingredients" and p.ingredients:
        await _handle_by_ingredients(message, p.ingredients)
    elif p.intent == "random":
        await _handle_random(message)
    elif p.intent == "history":
        from bot.handlers.commands import cmd_history
        await cmd_history(message)
    elif p.intent == "favorites":
        from bot.handlers.commands import cmd_favorites
        await cmd_favorites(message)
    else:
        # Unknown — prompt user
        await message.answer(
            "🤔 I'm not sure what you mean.\n\n"
            "Try:\n"
            "• A cocktail name: <code>Margarita</code>\n"
            "• Ingredients: <code>vodka, lime, mint</code>\n"
            "• Or type /help for all commands.",
            parse_mode="HTML",
        )
