import logging

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.services.backend_client import BackendClient
from bot.services.formatter import (
    format_cocktail_full,
    format_search_results_by_name,
    format_search_results_by_ingredients,
    format_history,
    format_favorites,
)

logger = logging.getLogger(__name__)
router = Router()
_backend = BackendClient()

HELP_TEXT = """🍹 <b>CocktailBot — your cocktail companion</b>

<b>Commands:</b>
/start — welcome message
/help  — this help text
/name &lt;cocktail&gt; — search by cocktail name
/ingredients &lt;list&gt; — search by comma-separated ingredients
/random — get a random cocktail
/history — your recent searches
/favorites — your saved favorites
/favorite &lt;cocktail name&gt; — add to favorites

<b>Or just send plain text!</b>
• A cocktail name → full recipe
• A list of ingredients (e.g. vodka, lime, mint) → matching cocktails
• "surprise me" or "random" → random cocktail
• "how to make a Mojito" → recipe
• "what can I do with rum and cola" → ingredient search

<b>Examples:</b>
• <code>Margarita</code>
• <code>how to do cosmopolitan</code>
• <code>vodka, lime, mint</code>
• <code>what can I do with rum and cola</code>
• <code>/random</code>
"""


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    name = message.from_user.first_name if message.from_user else "there"
    await message.answer(
        f"👋 Hey, <b>{name}</b>! Welcome to CocktailBot.\n\n"
        "Tell me a cocktail name or list your ingredients and I'll help you out.\n"
        "Type /help to see all commands.",
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")


@router.message(Command("name"))
async def cmd_name(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer("Usage: /name <cocktail name>\nExample: /name Mojito", parse_mode="HTML")
        return
    cocktail_name = args[1].strip()
    await _handle_by_name(message, cocktail_name)


@router.message(Command("ingredients"))
async def cmd_ingredients(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer(
            "Usage: /ingredients &lt;ingredient1&gt;, &lt;ingredient2&gt;, ...\n"
            "Example: /ingredients vodka, lime",
            parse_mode="HTML",
        )
        return
    raw = args[1].strip()
    ingredients = [i.strip() for i in raw.split(",") if i.strip()]
    await _handle_by_ingredients(message, ingredients)


@router.message(Command("history"))
async def cmd_history(message: Message) -> None:
    try:
        user_id = message.from_user.id if message.from_user else None
        history = await _backend.get_history(user_id=user_id, limit=10)
        await message.answer(format_history(history), parse_mode="HTML")
    except Exception as e:
        logger.error("Error fetching history: %s", e)
        await message.answer("⚠️ Could not fetch history. Try again later.")


@router.message(Command("favorites"))
async def cmd_favorites(message: Message) -> None:
    if not message.from_user:
        await message.answer("⚠️ Cannot identify your account.")
        return
    try:
        favs = await _backend.get_favorites(message.from_user.id)
        await message.answer(format_favorites(favs), parse_mode="HTML")
    except Exception as e:
        logger.error("Error fetching favorites: %s", e)
        await message.answer("⚠️ Could not fetch favorites. Try again later.")


@router.message(Command("favorite"))
async def cmd_add_favorite(message: Message) -> None:
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer("Usage: /favorite <cocktail name>\nExample: /favorite Mojito", parse_mode="HTML")
        return
    if not message.from_user:
        await message.answer("⚠️ Cannot identify your account.")
        return

    cocktail_name = args[1].strip()
    try:
        # Look up the cocktail to get its ID
        results = await _backend.search_by_name(cocktail_name, user_id=message.from_user.id)
        if not results:
            await message.answer(f'❌ No cocktail found matching "<b>{cocktail_name}</b>".', parse_mode="HTML")
            return
        cocktail = results[0]
        result = await _backend.add_favorite(
            message.from_user.id, cocktail["id"], cocktail["name"]
        )
        if result.get("status") == "already_exists":
            await message.answer(f'⭐ <b>{cocktail["name"]}</b> is already in your favorites.', parse_mode="HTML")
        else:
            await message.answer(f'⭐ Added <b>{cocktail["name"]}</b> to your favorites!', parse_mode="HTML")
    except Exception as e:
        logger.error("Error adding favorite: %s", e)
        await message.answer("⚠️ Could not add favorite. Try again later.")


# --------------------------------------------------------------------------
# Shared helpers (also used by the text message handler)
# --------------------------------------------------------------------------

async def _handle_by_name(message: Message, name: str) -> None:
    user_id = message.from_user.id if message.from_user else None
    try:
        await message.answer("🔍 Searching…")
        results = await _backend.search_by_name(name, user_id=user_id)
        text = format_search_results_by_name(results, name)
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error("Error searching by name '%s': %s", name, e)
        await message.answer("⚠️ Backend error. Make sure the backend is running.")


async def _handle_by_ingredients(message: Message, ingredients: list[str]) -> None:
    user_id = message.from_user.id if message.from_user else None
    try:
        await message.answer("🔍 Searching…")
        results = await _backend.search_by_ingredients(ingredients, user_id=user_id)
        text = format_search_results_by_ingredients(results, ingredients)
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error("Error searching by ingredients %s: %s", ingredients, e)
        await message.answer("⚠️ Backend error. Make sure the backend is running.")


async def _handle_random(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else None
    try:
        await message.answer("🎲 Getting a random cocktail…")
        cocktail = await _backend.get_random(user_id=user_id)
        if not cocktail:
            await message.answer("⚠️ Could not fetch a random cocktail. Try again.")
            return
        from bot.services.formatter import format_cocktail_full
        text = "🎲 <b>Random cocktail for you!</b>\n\n" + format_cocktail_full(cocktail)
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error("Error fetching random cocktail: %s", e)
        await message.answer("⚠️ Backend error. Make sure the backend is running.")
