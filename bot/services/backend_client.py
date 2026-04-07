"""HTTP client that talks to the FastAPI backend."""

import httpx
from typing import Any

from bot.config import settings


class BackendClient:
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=settings.backend_url, timeout=15.0
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def search_by_name(
        self, name: str, user_id: int | None = None
    ) -> list[dict[str, Any]]:
        client = await self._get()
        params: dict[str, Any] = {"name": name}
        if user_id:
            params["user_id"] = user_id
        resp = await client.get("/cocktails/by-name", params=params)
        resp.raise_for_status()
        return resp.json()

    async def search_by_ingredients(
        self, ingredients: list[str], user_id: int | None = None
    ) -> list[dict[str, Any]]:
        client = await self._get()
        params: dict[str, Any] = {"ingredients": ",".join(ingredients)}
        if user_id:
            params["user_id"] = user_id
        resp = await client.get("/cocktails/by-ingredients", params=params)
        resp.raise_for_status()
        return resp.json()

    async def get_history(
        self, user_id: int | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        client = await self._get()
        params: dict[str, Any] = {"limit": limit}
        if user_id:
            params["user_id"] = user_id
        resp = await client.get("/history", params=params)
        resp.raise_for_status()
        return resp.json()

    async def add_favorite(
        self, user_id: int, cocktail_id: str, cocktail_name: str
    ) -> dict[str, Any]:
        client = await self._get()
        resp = await client.post(
            "/favorites",
            json={
                "telegram_user_id": user_id,
                "cocktail_id": cocktail_id,
                "cocktail_name": cocktail_name,
            },
        )
        resp.raise_for_status()
        return resp.json()

    async def get_favorites(self, user_id: int) -> list[dict[str, Any]]:
        client = await self._get()
        resp = await client.get("/favorites", params={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()

    async def health(self) -> bool:
        try:
            client = await self._get()
            resp = await client.get("/health", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False
