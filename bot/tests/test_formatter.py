"""Unit tests for message formatter functions."""

import pytest
from bot.services.formatter import (
    format_cocktail_short,
    format_cocktail_full,
    format_search_results_by_name,
    format_search_results_by_ingredients,
    format_history,
    format_favorites,
)

SAMPLE_COCKTAIL = {
    "id": "11007",
    "name": "Margarita",
    "category": "Ordinary Drink",
    "alcoholic": "Alcoholic",
    "glass": "Cocktail glass",
    "instructions": "Shake with ice and serve.",
    "thumbnail": "https://example.com/margarita.jpg",
    "ingredients": [
        {"ingredient": "Tequila", "measure": "1.5 oz"},
        {"ingredient": "Lime juice", "measure": "1 oz"},
    ],
}


def test_format_cocktail_short_no_index() -> None:
    result = format_cocktail_short(SAMPLE_COCKTAIL)
    assert "Margarita" in result
    assert "•" in result


def test_format_cocktail_short_with_index() -> None:
    result = format_cocktail_short(SAMPLE_COCKTAIL, index=3)
    assert "3." in result
    assert "Margarita" in result


def test_format_cocktail_full_contains_name() -> None:
    result = format_cocktail_full(SAMPLE_COCKTAIL)
    assert "Margarita" in result


def test_format_cocktail_full_contains_ingredients() -> None:
    result = format_cocktail_full(SAMPLE_COCKTAIL)
    assert "Tequila" in result
    assert "Lime juice" in result


def test_format_cocktail_full_contains_instructions() -> None:
    result = format_cocktail_full(SAMPLE_COCKTAIL)
    assert "Shake with ice" in result


def test_format_search_results_by_name_empty() -> None:
    result = format_search_results_by_name([], "XYZ")
    assert "No cocktails found" in result


def test_format_search_results_by_name_single() -> None:
    result = format_search_results_by_name([SAMPLE_COCKTAIL], "Margarita")
    assert "Margarita" in result
    # Single result → full detail
    assert "Tequila" in result


def test_format_search_results_by_name_multiple() -> None:
    cocktails = [SAMPLE_COCKTAIL, {**SAMPLE_COCKTAIL, "name": "Mojito", "id": "11000"}]
    result = format_search_results_by_name(cocktails, "M")
    assert "Found 2" in result


def test_format_search_results_by_ingredients_empty() -> None:
    result = format_search_results_by_ingredients([], ["vodka", "lime"])
    assert "No cocktails found" in result


def test_format_search_results_by_ingredients_found() -> None:
    result = format_search_results_by_ingredients([SAMPLE_COCKTAIL], ["tequila", "lime"])
    assert "Margarita" in result


def test_format_history_empty() -> None:
    result = format_history([])
    assert "empty" in result.lower()


def test_format_history_items() -> None:
    history = [
        {"query_type": "by_name", "query_text": "Mojito", "results_count": 1},
        {"query_type": "by_ingredients", "query_text": "vodka,lime", "results_count": 3},
    ]
    result = format_history(history)
    assert "Mojito" in result
    assert "vodka,lime" in result


def test_format_favorites_empty() -> None:
    result = format_favorites([])
    assert "no favorite" in result.lower()


def test_format_favorites_items() -> None:
    favs = [{"cocktail_name": "Margarita", "cocktail_id": "11007", "added_at": "2026-01-01"}]
    result = format_favorites(favs)
    assert "Margarita" in result
