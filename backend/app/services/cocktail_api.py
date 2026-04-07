"""Client for TheCocktailDB public API (free tier, no key needed)."""

import json
import httpx
from typing import Any

from app.settings import settings


class CocktailAPIService:
    """Thin async wrapper around TheCocktailDB v1 API."""

    def __init__(self) -> None:
        self.base_url = settings.cocktaildb_base_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def search_by_name(self, name: str) -> list[dict[str, Any]]:
        """Search cocktails by name. Returns list of cocktail dicts."""
        client = await self._get_client()
        resp = await client.get(f"{self.base_url}/search.php", params={"s": name})
        resp.raise_for_status()
        data = resp.json()
        drinks = data.get("drinks")
        return drinks if isinstance(drinks, list) else []

    async def search_by_ingredient(self, ingredient: str) -> list[dict[str, Any]]:
        """Search cocktails that contain a given ingredient. Returns slim dicts."""
        client = await self._get_client()
        resp = await client.get(f"{self.base_url}/filter.php", params={"i": ingredient})
        resp.raise_for_status()
        data = resp.json()
        # TheCocktailDB returns {"drinks": "None"} (string!) when nothing found
        drinks = data.get("drinks")
        return drinks if isinstance(drinks, list) else []

    async def lookup_by_id(self, cocktail_id: str) -> dict[str, Any] | None:
        """Fetch full cocktail details by its TheCocktailDB ID."""
        client = await self._get_client()
        resp = await client.get(f"{self.base_url}/lookup.php", params={"i": cocktail_id})
        resp.raise_for_status()
        data = resp.json()
        drinks = data.get("drinks") or []
        return drinks[0] if drinks else None

    @staticmethod
    def extract_ingredients(drink: dict[str, Any]) -> list[dict[str, str]]:
        """Extract ingredient + measure pairs from a full cocktail dict."""
        result = []
        for i in range(1, 16):
            ingredient = drink.get(f"strIngredient{i}", "")
            measure = drink.get(f"strMeasure{i}", "")
            if ingredient and ingredient.strip():
                result.append({
                    "ingredient": ingredient.strip(),
                    "measure": (measure or "").strip(),
                })
        return result

    @staticmethod
    def to_normalized(drink: dict[str, Any]) -> dict[str, Any]:
        """Normalize a raw API dict to a clean internal structure."""
        from app.services.cocktail_api import CocktailAPIService
        ingredients = CocktailAPIService.extract_ingredients(drink)
        return {
            "id": drink.get("idDrink", ""),
            "name": drink.get("strDrink", ""),
            "category": drink.get("strCategory", ""),
            "alcoholic": drink.get("strAlcoholic", ""),
            "glass": drink.get("strGlass", ""),
            "instructions": drink.get("strInstructions", ""),
            "thumbnail": drink.get("strDrinkThumb", ""),
            "ingredients": ingredients,
        }

    async def find_by_multiple_ingredients(
        self, ingredients: list[str]
    ) -> list[dict[str, Any]]:
        """
        Find cocktails matching ALL provided ingredients.
        Strategy: get candidate IDs for each ingredient, intersect sets,
        then fetch full details for up to 10 matched cocktails.
        """
        if not ingredients:
            return []

        # Fetch candidates per ingredient
        sets: list[set[str]] = []
        for ing in ingredients:
            drinks = await self.search_by_ingredient(ing.strip())
            if not drinks:
                return []  # no match at all
            ids = {d["idDrink"] for d in drinks}
            sets.append(ids)

        # Intersect
        common_ids = sets[0]
        for s in sets[1:]:
            common_ids = common_ids & s

        if not common_ids:
            return []  # No cocktail contains all the given ingredients simultaneously

        # Fetch full details (limit to 10 to avoid flooding)
        results = []
        for cid in list(common_ids)[:10]:
            full = await self.lookup_by_id(cid)
            if full:
                results.append(self.to_normalized(full))

        return results
