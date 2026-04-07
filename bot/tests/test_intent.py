"""Unit tests for deterministic intent detection."""

import pytest
from bot.services.intent import detect_intent, ParsedIntent


class TestByNameDetection:
    def test_plain_cocktail_name(self) -> None:
        assert detect_intent("Margarita").intent == "by_name"
        assert detect_intent("Margarita").name == "Margarita"

    def test_how_to_make(self) -> None:
        result = detect_intent("how to make a Mojito")
        assert result.intent == "by_name"
        assert "Mojito" in result.name

    def test_how_to_do(self) -> None:
        result = detect_intent("how to do cosmopolitan")
        assert result.intent == "by_name"
        assert result.name.lower() == "cosmopolitan"

    def test_how_to_do_with_qualifier(self) -> None:
        result = detect_intent("how to do standart cosmopolitan")
        assert result.intent == "by_name"
        assert result.name.lower() == "cosmopolitan"

    def test_recipe_keyword(self) -> None:
        result = detect_intent("recipe for Mojito")
        assert result.intent == "by_name"
        assert "Mojito" in result.name

    def test_what_is(self) -> None:
        result = detect_intent("what is a Cosmopolitan")
        assert result.intent == "by_name"

    def test_classic_qualifier_stripped(self) -> None:
        result = detect_intent("classic negroni")
        # "classic" is a qualifier, remainder "negroni" → by_name
        assert result.intent == "by_name"
        assert "negroni" in result.name.lower()


class TestByIngredientsDetection:
    def test_comma_separated(self) -> None:
        result = detect_intent("vodka, lime, mint")
        assert result.intent == "by_ingredients"
        assert "vodka" in result.ingredients

    def test_with_pattern(self) -> None:
        result = detect_intent("what can i do with rum and cola")
        assert result.intent == "by_ingredients"
        assert any("rum" in i.lower() for i in result.ingredients)
        assert any("cola" in i.lower() for i in result.ingredients)

    def test_with_pattern_simple(self) -> None:
        result = detect_intent("make something with gin and tonic")
        assert result.intent == "by_ingredients"

    def test_have_pattern(self) -> None:
        result = detect_intent("I have vodka and lime")
        assert result.intent == "by_ingredients"

    def test_known_ingredient_single(self) -> None:
        result = detect_intent("tequila")
        assert result.intent == "by_ingredients"
        assert "tequila" in result.ingredients


class TestRandomDetection:
    def test_random_word(self) -> None:
        assert detect_intent("random").intent == "random"

    def test_surprise_me(self) -> None:
        assert detect_intent("surprise me").intent == "random"

    def test_random_cocktail(self) -> None:
        assert detect_intent("random cocktail").intent == "random"

    def test_whatever(self) -> None:
        assert detect_intent("whatever").intent == "random"


class TestHistoryAndFavorites:
    def test_history(self) -> None:
        assert detect_intent("history").intent == "history"

    def test_favorites(self) -> None:
        assert detect_intent("my favorites").intent == "favorites"


class TestEdgeCases:
    def test_unknown_word(self) -> None:
        result = detect_intent("Xyzabc123")
        assert result.intent == "by_name"
        assert result.name == "Xyzabc123"

    def test_empty_string(self) -> None:
        result = detect_intent("")
        assert result is not None
