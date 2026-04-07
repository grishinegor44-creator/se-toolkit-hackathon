"""Unit tests for CocktailAPIService — all HTTP calls are mocked with respx."""

import pytest
import respx
import httpx

from app.services.cocktail_api import CocktailAPIService

BASE = "https://www.thecocktaildb.com/api/json/v1/1"

SAMPLE_DRINK = {
    "idDrink": "11007",
    "strDrink": "Margarita",
    "strCategory": "Ordinary Drink",
    "strAlcoholic": "Alcoholic",
    "strGlass": "Cocktail glass",
    "strInstructions": "Rub the rim of the glass with the lime slice.",
    "strDrinkThumb": "https://example.com/margarita.jpg",
    "strIngredient1": "Tequila",
    "strMeasure1": "1 1/2 oz",
    "strIngredient2": "Triple sec",
    "strMeasure2": "1/2 oz",
    "strIngredient3": "Lime juice",
    "strMeasure3": "1 oz",
    "strIngredient4": None,
    "strMeasure4": None,
}


@pytest.fixture
def service() -> CocktailAPIService:
    return CocktailAPIService()


class TestSearchByName:
    @respx.mock
    async def test_returns_list(self, service: CocktailAPIService) -> None:
        respx.get(f"{BASE}/search.php").mock(
            return_value=httpx.Response(200, json={"drinks": [SAMPLE_DRINK]})
        )
        result = await service.search_by_name("Margarita")
        assert len(result) == 1
        assert result[0]["strDrink"] == "Margarita"

    @respx.mock
    async def test_empty_result(self, service: CocktailAPIService) -> None:
        respx.get(f"{BASE}/search.php").mock(
            return_value=httpx.Response(200, json={"drinks": None})
        )
        result = await service.search_by_name("XYZUnknown999")
        assert result == []


class TestExtractIngredients:
    def test_extracts_ingredients(self) -> None:
        result = CocktailAPIService.extract_ingredients(SAMPLE_DRINK)
        assert len(result) == 3
        assert result[0] == {"ingredient": "Tequila", "measure": "1 1/2 oz"}
        assert result[2] == {"ingredient": "Lime juice", "measure": "1 oz"}

    def test_skips_empty(self) -> None:
        drink = {"strIngredient1": "Vodka", "strMeasure1": "", "strIngredient2": None}
        result = CocktailAPIService.extract_ingredients(drink)
        assert len(result) == 1
        assert result[0]["ingredient"] == "Vodka"


class TestToNormalized:
    def test_normalized_structure(self) -> None:
        result = CocktailAPIService.to_normalized(SAMPLE_DRINK)
        assert result["id"] == "11007"
        assert result["name"] == "Margarita"
        assert result["alcoholic"] == "Alcoholic"
        assert len(result["ingredients"]) == 3


class TestResolveIngredientName:
    @respx.mock
    async def test_resolves_partial_name(self, service: CocktailAPIService) -> None:
        respx.get(f"{BASE}/search.php", params={"i": "tonic"}).mock(
            return_value=httpx.Response(
                200,
                json={"ingredients": [{"strIngredient": "Tonic Water"}]},
            )
        )
        result = await service.resolve_ingredient_name("tonic")
        assert result == "Tonic Water"

    @respx.mock
    async def test_fallback_on_no_match(self, service: CocktailAPIService) -> None:
        respx.get(f"{BASE}/search.php", params={"i": "zzznope"}).mock(
            return_value=httpx.Response(200, json={"ingredients": None})
        )
        result = await service.resolve_ingredient_name("zzznope")
        assert result == "zzznope"


class TestFindByMultipleIngredients:
    @respx.mock
    async def test_intersection(self, service: CocktailAPIService) -> None:
        # "vodka" not in alias table → resolve via API → "Vodka"
        # "lime" IS in alias table → "Lime juice" (no API call needed)
        respx.get(f"{BASE}/search.php", params={"i": "vodka"}).mock(
            return_value=httpx.Response(200, json={"ingredients": [{"strIngredient": "Vodka"}]})
        )
        respx.get(f"{BASE}/filter.php", params={"i": "Vodka"}).mock(
            return_value=httpx.Response(
                200, json={"drinks": [{"idDrink": "11003"}, {"idDrink": "11007"}]}
            )
        )
        respx.get(f"{BASE}/filter.php", params={"i": "Lime juice"}).mock(
            return_value=httpx.Response(
                200, json={"drinks": [{"idDrink": "11007"}, {"idDrink": "99999"}]}
            )
        )
        respx.get(f"{BASE}/lookup.php", params={"i": "11007"}).mock(
            return_value=httpx.Response(200, json={"drinks": [SAMPLE_DRINK]})
        )
        result = await service.find_by_multiple_ingredients(["vodka", "lime"])
        assert len(result) == 1
        assert result[0]["name"] == "Margarita"

    @respx.mock
    async def test_no_common_partial_match(self, service: CocktailAPIService) -> None:
        """When no strict intersection, partial match returns results scored by hits.
        'milk' is in the alias table -> 'Cream', no API resolve call needed.
        """
        # 'vodka' not in alias table -> API resolve
        respx.get(f"{BASE}/search.php", params={"i": "vodka"}).mock(
            return_value=httpx.Response(200, json={"ingredients": [{"strIngredient": "Vodka"}]})
        )
        respx.get(f"{BASE}/filter.php", params={"i": "Vodka"}).mock(
            return_value=httpx.Response(200, json={"drinks": [{"idDrink": "111"}]})
        )
        # 'milk' -> alias 'Cream', no search.php call
        respx.get(f"{BASE}/filter.php", params={"i": "Cream"}).mock(
            return_value=httpx.Response(200, json={"drinks": [{"idDrink": "222"}]})
        )
        respx.get(f"{BASE}/lookup.php", params={"i": "111"}).mock(
            return_value=httpx.Response(200, json={"drinks": [SAMPLE_DRINK]})
        )
        respx.get(f"{BASE}/lookup.php", params={"i": "222"}).mock(
            return_value=httpx.Response(200, json={"drinks": [{**SAMPLE_DRINK, "idDrink": "222", "strDrink": "Milky Way"}]})
        )
        result = await service.find_by_multiple_ingredients(["vodka", "milk"])
        # Partial match should return results (both score 1)
        assert len(result) == 2

    @respx.mock
    async def test_alias_cola(self, service: CocktailAPIService) -> None:
        """'cola' is resolved via alias to 'Coca-Cola' without API call."""
        # No search.php call expected for "cola" (alias table)
        respx.get(f"{BASE}/filter.php", params={"i": "Coca-Cola"}).mock(
            return_value=httpx.Response(200, json={"drinks": [{"idDrink": "11118"}]})
        )
        respx.get(f"{BASE}/filter.php", params={"i": "Light rum"}).mock(
            return_value=httpx.Response(200, json={"drinks": [{"idDrink": "11118"}, {"idDrink": "99"}]})
        )
        respx.get(f"{BASE}/lookup.php", params={"i": "11118"}).mock(
            return_value=httpx.Response(200, json={"drinks": [SAMPLE_DRINK]})
        )
        result = await service.find_by_multiple_ingredients(["rum", "cola"])
        assert len(result) == 1  # strict intersection = {11118}

    @respx.mock
    async def test_none_string_response(self, service: CocktailAPIService) -> None:
        """TheCocktailDB returns string 'None' for unknown ingredients."""
        respx.get(f"{BASE}/search.php", params={"i": "xyzunknown"}).mock(
            return_value=httpx.Response(200, json={"ingredients": None})
        )
        respx.get(f"{BASE}/filter.php", params={"i": "xyzunknown"}).mock(
            return_value=httpx.Response(200, json={"drinks": "None"})
        )
        result = await service.find_by_multiple_ingredients(["xyzunknown"])
        assert result == []

    async def test_empty_input(self, service: CocktailAPIService) -> None:
        result = await service.find_by_multiple_ingredients([])
        assert result == []
