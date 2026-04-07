from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database import get_db
from app.services.cocktail_db import CocktailDBService

router = APIRouter(prefix="/favorites", tags=["favorites"])
_db_svc = CocktailDBService()


class FavoriteRequest(BaseModel):
    telegram_user_id: int
    cocktail_id: str
    cocktail_name: str


@router.post("")
async def add_favorite(
    req: FavoriteRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Add a cocktail to user favorites."""
    return await _db_svc.add_favorite(
        db, req.telegram_user_id, req.cocktail_id, req.cocktail_name
    )


@router.get("")
async def get_favorites(
    user_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Get all favorites for a user."""
    return await _db_svc.get_favorites(db, user_id)


@router.delete("/{cocktail_id}")
async def remove_favorite(
    cocktail_id: str,
    user_id: int = Query(..., description="Telegram user ID"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Remove a cocktail from favorites."""
    removed = await _db_svc.remove_favorite(db, user_id, cocktail_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"status": "removed", "cocktail_id": cocktail_id}
