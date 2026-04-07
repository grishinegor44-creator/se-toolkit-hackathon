"""Database-backed caching and history service."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cocktail import CachedCocktail, SearchHistory, Favorite


class CocktailDBService:
    """Handles caching, history, and favorites in PostgreSQL."""

    # ------------------------------------------------------------------ cache

    async def get_cached_cocktail(
        self, db: AsyncSession, cocktail_id: str
    ) -> dict[str, Any] | None:
        result = await db.execute(
            select(CachedCocktail).where(CachedCocktail.cocktail_id == cocktail_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._row_to_dict(row)

    async def upsert_cocktail(
        self, db: AsyncSession, cocktail: dict[str, Any]
    ) -> None:
        result = await db.execute(
            select(CachedCocktail).where(
                CachedCocktail.cocktail_id == cocktail["id"]
            )
        )
        row = result.scalar_one_or_none()
        ingredients_json = json.dumps(cocktail.get("ingredients", []))
        if row:
            row.name = cocktail["name"]
            row.category = cocktail.get("category")
            row.alcoholic = cocktail.get("alcoholic")
            row.glass = cocktail.get("glass")
            row.instructions = cocktail.get("instructions")
            row.thumbnail_url = cocktail.get("thumbnail")
            row.ingredients_json = ingredients_json
        else:
            row = CachedCocktail(
                cocktail_id=cocktail["id"],
                name=cocktail["name"],
                category=cocktail.get("category"),
                alcoholic=cocktail.get("alcoholic"),
                glass=cocktail.get("glass"),
                instructions=cocktail.get("instructions"),
                thumbnail_url=cocktail.get("thumbnail"),
                ingredients_json=ingredients_json,
            )
            db.add(row)
        await db.commit()

    # --------------------------------------------------------------- history

    async def record_search(
        self,
        db: AsyncSession,
        telegram_user_id: int | None,
        query_type: str,
        query_text: str,
        results_count: int,
    ) -> None:
        entry = SearchHistory(
            telegram_user_id=telegram_user_id,
            query_type=query_type,
            query_text=query_text,
            results_count=results_count,
        )
        db.add(entry)
        await db.commit()

    async def get_recent_history(
        self,
        db: AsyncSession,
        limit: int = 20,
        telegram_user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        stmt = select(SearchHistory).order_by(SearchHistory.created_at.desc()).limit(limit)
        if telegram_user_id is not None:
            stmt = stmt.where(SearchHistory.telegram_user_id == telegram_user_id)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [
            {
                "id": r.id,
                "telegram_user_id": r.telegram_user_id,
                "query_type": r.query_type,
                "query_text": r.query_text,
                "results_count": r.results_count,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]

    # -------------------------------------------------------------- favorites

    async def add_favorite(
        self,
        db: AsyncSession,
        telegram_user_id: int,
        cocktail_id: str,
        cocktail_name: str,
    ) -> dict[str, Any]:
        # Avoid duplicates
        result = await db.execute(
            select(Favorite).where(
                Favorite.telegram_user_id == telegram_user_id,
                Favorite.cocktail_id == cocktail_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return {"status": "already_exists", "cocktail_name": cocktail_name}

        fav = Favorite(
            telegram_user_id=telegram_user_id,
            cocktail_id=cocktail_id,
            cocktail_name=cocktail_name,
        )
        db.add(fav)
        await db.commit()
        return {"status": "added", "cocktail_name": cocktail_name}

    async def remove_favorite(
        self,
        db: AsyncSession,
        telegram_user_id: int,
        cocktail_id: str,
    ) -> bool:
        result = await db.execute(
            delete(Favorite).where(
                Favorite.telegram_user_id == telegram_user_id,
                Favorite.cocktail_id == cocktail_id,
            )
        )
        await db.commit()
        return result.rowcount > 0

    async def get_favorites(
        self,
        db: AsyncSession,
        telegram_user_id: int,
    ) -> list[dict[str, Any]]:
        result = await db.execute(
            select(Favorite)
            .where(Favorite.telegram_user_id == telegram_user_id)
            .order_by(Favorite.created_at.desc())
        )
        rows = result.scalars().all()
        return [
            {
                "cocktail_id": r.cocktail_id,
                "cocktail_name": r.cocktail_name,
                "added_at": r.created_at.isoformat(),
            }
            for r in rows
        ]

    # ----------------------------------------------------------------- utils

    @staticmethod
    def _row_to_dict(row: CachedCocktail) -> dict[str, Any]:
        return {
            "id": row.cocktail_id,
            "name": row.name,
            "category": row.category,
            "alcoholic": row.alcoholic,
            "glass": row.glass,
            "instructions": row.instructions,
            "thumbnail": row.thumbnail_url,
            "ingredients": json.loads(row.ingredients_json or "[]"),
        }
