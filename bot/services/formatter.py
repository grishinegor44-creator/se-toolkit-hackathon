"""Message formatting helpers for Telegram HTML output."""

from typing import Any


def format_cocktail_short(cocktail: dict[str, Any], index: int | None = None) -> str:
    """One-line summary of a cocktail."""
    prefix = f"{index}. " if index is not None else "• "
    alc = cocktail.get("alcoholic", "")
    cat = cocktail.get("category", "")
    tag = f" [{cat}]" if cat else ""
    alc_tag = f" ({alc})" if alc else ""
    return f"{prefix}<b>{cocktail['name']}</b>{tag}{alc_tag}"


def format_cocktail_full(cocktail: dict[str, Any]) -> str:
    """Full cocktail details formatted for Telegram HTML."""
    lines = []
    lines.append(f"🍹 <b>{cocktail['name']}</b>")

    if cocktail.get("category"):
        lines.append(f"📂 Category: {cocktail['category']}")
    if cocktail.get("alcoholic"):
        lines.append(f"🍸 Type: {cocktail['alcoholic']}")
    if cocktail.get("glass"):
        lines.append(f"🥃 Glass: {cocktail['glass']}")

    ingredients = cocktail.get("ingredients", [])
    if ingredients:
        lines.append("\n<b>Ingredients:</b>")
        for item in ingredients:
            measure = item.get("measure", "")
            ing = item.get("ingredient", "")
            if measure:
                lines.append(f"  • {measure} {ing}")
            else:
                lines.append(f"  • {ing}")

    instructions = cocktail.get("instructions", "")
    if instructions:
        lines.append(f"\n<b>Instructions:</b>\n{instructions[:800]}")
        if len(instructions) > 800:
            lines.append("…(truncated)")

    return "\n".join(lines)


def format_search_results_by_name(
    cocktails: list[dict[str, Any]], query: str
) -> str:
    if not cocktails:
        return (
            f'❌ No cocktails found matching "<b>{query}</b>".\n'
            "Try a different name or use /ingredients to search by what you have."
        )
    if len(cocktails) == 1:
        return format_cocktail_full(cocktails[0])
    # Exact match — show full recipe immediately
    exact = next(
        (c for c in cocktails if c["name"].lower() == query.lower()), None
    )
    if exact:
        return format_cocktail_full(exact)
    # Multiple results, no exact match — show list
    lines = [f'Found {len(cocktails)} cocktails matching "<b>{query}</b>":\n']
    for i, c in enumerate(cocktails[:25], 1):
        lines.append(format_cocktail_short(c, i))
    lines.append("\nSend the exact cocktail name to get the full recipe.")
    return "\n".join(lines)


def format_search_results_by_ingredients(
    cocktails: list[dict[str, Any]], ingredients: list[str]
) -> str:
    ing_str = ", ".join(ingredients)
    if not cocktails:
        return (
            f"❌ No cocktails found containing all of: <b>{ing_str}</b>.\n\n"
            "Tips:\n"
            "• Try fewer ingredients at once\n"
            "• Check spelling (e.g. <code>rum</code>, <code>vodka</code>, <code>lime juice</code>)\n"
            "• Some combos simply have no cocktail in the database"
        )
    lines = [f"🔍 Cocktails you can make with <b>{ing_str}</b>:\n"]
    for i, c in enumerate(cocktails[:10], 1):
        lines.append(format_cocktail_short(c, i))
    lines.append(
        "\nSend the cocktail name to get its full recipe."
    )
    return "\n".join(lines)


def format_history(history: list[dict[str, Any]]) -> str:
    if not history:
        return "📋 Your search history is empty."
    lines = ["📋 <b>Recent searches:</b>\n"]
    for item in history[:10]:
        qt = "🔤" if item["query_type"] == "by_name" else "🧪"
        lines.append(f'{qt} <code>{item["query_text"]}</code> → {item["results_count"]} results')
    return "\n".join(lines)


def format_favorites(favorites: list[dict[str, Any]]) -> str:
    if not favorites:
        return "⭐ You have no favorite cocktails yet.\nUse /favorite <name> to add one."
    lines = ["⭐ <b>Your favorites:</b>\n"]
    for fav in favorites:
        lines.append(f"  • <b>{fav['cocktail_name']}</b>")
    return "\n".join(lines)
