"""Unit tests for deterministic intent detection."""

import pytest
from bot.services.intent import detect_intent, ParsedIntent


class TestByNameDetection:
    def test_plain_cocktail_name(self) -> None:
        result = detect_intent("Margarita")
        assert result.intent == "by_name"
        assert result.name == "Margarita"

    def test_recipe_keyword(self) -> None:
        result = detect_intent("recipe for Mojito")
        assert result.intent == "by_name"

    def test_what_is_keyword(self) -> None:
        result = detect_intent("what is a Cosmopolitan")
        assert result.intent == "by_name"

    def test_how_to_make(self) -> None:
        result = detect_intent("how to make an Old Fashioned")
        assert result.intent == "by_name"


class TestByIngredientsDetection:
    def test_comma_separated(self) -> None:
        result = detect_intent("vodka, lime, mint")
        assert result.intent == "by_ingredients"
        assert "vodka" in result.ingredients
        assert "lime" in result.ingredients
        assert "mint" in result.ingredients

    def test_make_with_keyword(self) -> None:
        result = detect_intent("what can I make with vodka and lime")
        assert result.intent == "by_ingredients"

    def test_have_ingredients(self) -> None:
        result = detect_intent("I have vodka and lime")
        assert result.intent == "by_ingredients"

    def test_known_ingredient_word(self) -> None:
        result = detect_intent("tequila")
        assert result.intent == "by_ingredients"
        assert "tequila" in result.ingredients


class TestHistoryAndFavorites:
    def test_history_keyword(self) -> None:
        result = detect_intent("history")
        assert result.intent == "history"

    def test_favorites_keyword(self) -> None:
        result = detect_intent("my favorites")
        assert result.intent == "favorites"

    def test_fav_keyword(self) -> None:
        result = detect_intent("fav")
        assert result.intent == "favorites"


class TestEdgeCases:
    def test_empty_string(self) -> None:
        result = detect_intent("")
        # Should not crash; intent should be by_name with empty name
        assert result is not None

    def test_single_unknown_word(self) -> None:
        result = detect_intent("Xyzabc")
        assert result.intent == "by_name"
        assert result.name == "Xyzabc"
