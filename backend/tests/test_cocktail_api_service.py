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


class TestFindByMultipleIngredients:
    @respx.mock
    async def test_intersection(self, service: CocktailAPIService) -> None:
        # Two ingredients, one common cocktail ID
        respx.get(f"{BASE}/filter.php", params={"i": "vodka"}).mock(
            return_value=httpx.Response(
                200,
                json={"drinks": [{"idDrink": "11003"}, {"idDrink": "11007"}]},
            )
        )
        respx.get(f"{BASE}/filter.php", params={"i": "lime"}).mock(
            return_value=httpx.Response(
                200,
                json={"drinks": [{"idDrink": "11007"}, {"idDrink": "99999"}]},
            )
        )
        respx.get(f"{BASE}/lookup.php", params={"i": "11007"}).mock(
            return_value=httpx.Response(200, json={"drinks": [SAMPLE_DRINK]})
        )
        result = await service.find_by_multiple_ingredients(["vodka", "lime"])
        assert len(result) == 1
        assert result[0]["name"] == "Margarita"

    @respx.mock
    async def test_no_common(self, service: CocktailAPIService) -> None:
        respx.get(f"{BASE}/filter.php", params={"i": "vodka"}).mock(
            return_value=httpx.Response(200, json={"drinks": [{"idDrink": "111"}]})
        )
        respx.get(f"{BASE}/filter.php", params={"i": "milk"}).mock(
            return_value=httpx.Response(200, json={"drinks": [{"idDrink": "222"}]})
        )
        result = await service.find_by_multiple_ingredients(["vodka", "milk"])
        assert result == []

    async def test_empty_input(self, service: CocktailAPIService) -> None:
        result = await service.find_by_multiple_ingredients([])
        assert result == []
