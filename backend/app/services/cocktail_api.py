"""Client for TheCocktailDB public API (free tier, no key needed)."""

import asyncio
import json
import time
import httpx
from typing import Any

from app.settings import settings

# Common user-supplied aliases → canonical TheCocktailDB ingredient names
_INGREDIENT_ALIASES: dict[str, str] = {
    "cola":        "Coca-Cola",
    "coke":        "Coca-Cola",
    "coca cola":   "Coca-Cola",
    "tonic":       "Tonic Water",
    "lime":        "Lime juice",
    "lemon":       "Lemon juice",
    "oj":          "Orange juice",
    "orange":      "Orange juice",
    "cranberry":   "Cranberry juice",
    "pineapple":   "Pineapple juice",
    "grapefruit":  "Grapefruit juice",
    "milk":        "Cream",
    "simple syrup":"Sugar syrup",
    "soda":        "Club soda",
    "club soda":   "Club soda",
    "whiskey":     "Blended whiskey",
    "whisky":      "Blended whiskey",
    "bourbon":     "Bourbon",
    "scotch":      "Scotch",
    "rum":         "Light rum",
}


class CocktailAPIService:
    """Thin async wrapper around TheCocktailDB v1 API."""

    def __init__(self) -> None:
        self.base_url = settings.cocktaildb_base_url
        self._client: httpx.AsyncClient | None = None
        self._last_request_time: float = 0
        self._min_request_interval = settings.cocktaildb_rate_limit_ms / 1000.0  # Convert ms to seconds

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def _throttle_request(self) -> None:
        """Ensure we don't exceed rate limits by adding delays between requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.monotonic()

    async def _make_request_with_retry(
        self, url: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        """Make HTTP request with exponential backoff on 429 errors."""
        max_retries = 3
        base_delay = 2.0

        for attempt in range(max_retries + 1):
            await self._throttle_request()
            client = await self._get_client()
            resp = await client.get(url, params=params)

            if resp.status_code != 429:
                resp.raise_for_status()
                return resp

            # Rate limited - wait with exponential backoff
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
            else:
                resp.raise_for_status()  # Raise on final attempt

        # Should never reach here, but just in case
        resp.raise_for_status()
        return resp

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def search_by_name(self, name: str) -> list[dict[str, Any]]:
        """Search cocktails by name. Returns list of cocktail dicts."""
        resp = await self._make_request_with_retry(
            f"{self.base_url}/search.php", params={"s": name}
        )
        data = resp.json()
        drinks = data.get("drinks")
        return drinks if isinstance(drinks, list) else []

    async def resolve_ingredient_name(self, ingredient: str) -> str:
        """
        Resolve a user-supplied ingredient string to its canonical
        TheCocktailDB name.
        1. Check built-in alias table (fast, no network call).
        2. Fall back to TheCocktailDB ingredient search endpoint.
        3. Return original string if nothing found.
        """
        lower = ingredient.strip().lower()
        if lower in _INGREDIENT_ALIASES:
            return _INGREDIENT_ALIASES[lower]
        resp = await self._make_request_with_retry(
            f"{self.base_url}/search.php", params={"i": ingredient}
        )
        data = resp.json()
        ingredients = data.get("ingredients")
        if isinstance(ingredients, list) and ingredients:
            return ingredients[0].get("strIngredient", ingredient)
        return ingredient

    async def search_by_ingredient(self, ingredient: str) -> list[dict[str, Any]]:
        """Filter cocktails by a canonical ingredient name via filter.php.
        NOTE: caller is responsible for resolving the ingredient name first
        (via resolve_ingredient_name). This method is a pure filter call.
        Returns slim dicts with at least {idDrink}.
        """
        resp = await self._make_request_with_retry(
            f"{self.base_url}/filter.php", params={"i": ingredient}
        )
        data = resp.json()
        # TheCocktailDB returns {"drinks": "None"} (string!) when nothing found
        drinks = data.get("drinks")
        return drinks if isinstance(drinks, list) else []

    async def lookup_by_id(self, cocktail_id: str) -> dict[str, Any] | None:
        """Fetch full cocktail details by its TheCocktailDB ID."""
        resp = await self._make_request_with_retry(
            f"{self.base_url}/lookup.php", params={"i": cocktail_id}
        )
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

    async def get_random(self) -> dict[str, Any] | None:
        """Fetch a completely random cocktail from TheCocktailDB."""
        resp = await self._make_request_with_retry(f"{self.base_url}/random.php")
        data = resp.json()
        drinks = data.get("drinks")
        if isinstance(drinks, list) and drinks:
            return self.to_normalized(drinks[0])
        return None

    async def find_by_multiple_ingredients(
        self, ingredients: list[str]
    ) -> list[dict[str, Any]]:
        """
        Find cocktails matching the provided ingredients.
        Strategy:
          1. Resolve each ingredient to its canonical TheCocktailDB name.
          2. Try strict AND-intersection of all ingredients.
          3. If no strict match, fall back to partial match:
             score each cocktail by how many ingredients it contains,
             return top results sorted by score (descending).
        """
        if not ingredients:
            return []

        # Resolve canonical names first
        canonical: list[str] = []
        for ing in ingredients:
            canonical.append(await self.resolve_ingredient_name(ing.strip()))

        # Fetch candidate ID sets per ingredient
        id_sets: list[set[str]] = []
        for ing in canonical:
            drinks = await self.search_by_ingredient(ing)
            id_sets.append({d["idDrink"] for d in drinks} if drinks else set())

        # Strict intersection
        if id_sets:
            common_ids = id_sets[0].copy()
            for s in id_sets[1:]:
                common_ids &= s
        else:
            common_ids = set()

        MAX_RESULTS = 25

        candidate_ids: list[str]
        if common_ids:
            candidate_ids = list(common_ids)[:MAX_RESULTS]
        else:
            # Partial match: score each cocktail by ingredient hit count
            score: dict[str, int] = {}
            for id_set in id_sets:
                for cid in id_set:
                    score[cid] = score.get(cid, 0) + 1
            if not score:
                return []
            candidate_ids = sorted(score, key=lambda k: score[k], reverse=True)[:MAX_RESULTS]

        # Fetch full cocktail details IN PARALLEL
        raw = await asyncio.gather(
            *[self.lookup_by_id(cid) for cid in candidate_ids],
            return_exceptions=False,
        )
        return [self.to_normalized(drink) for drink in raw if drink is not None]
