from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database import get_db
from app.services.cocktail_db import CocktailDBService

router = APIRouter(prefix="/history", tags=["history"])
_db_svc = CocktailDBService()


@router.get("")
async def get_history(
    limit: int = Query(20, ge=1, le=100),
    user_id: int | None = Query(None, description="Filter by Telegram user ID"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return recent search history."""
    return await _db_svc.get_recent_history(db, limit=limit, telegram_user_id=user_id)
