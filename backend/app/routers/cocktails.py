from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database import get_db
from app.services.cocktail_api import CocktailAPIService
from app.services.cocktail_db import CocktailDBService

router = APIRouter(prefix="/cocktails", tags=["cocktails"])

_api_svc = CocktailAPIService()
_db_svc = CocktailDBService()


@router.get("/by-name")
async def get_cocktail_by_name(
    name: str = Query(..., description="Cocktail name to search for"),
    user_id: int | None = Query(None, description="Telegram user ID for history"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Search cocktails by name. Returns up to 10 matches."""
    if not name.strip():
        raise HTTPException(status_code=400, detail="name must not be empty")

    raw_drinks = await _api_svc.search_by_name(name.strip())
    if not raw_drinks:
        await _db_svc.record_search(db, user_id, "by_name", name, 0)
        return []

    results = [_api_svc.to_normalized(d) for d in raw_drinks[:10]]

    # Cache each cocktail in the database
    for cocktail in results:
        await _db_svc.upsert_cocktail(db, cocktail)

    await _db_svc.record_search(db, user_id, "by_name", name, len(results))
    return results


@router.get("/by-ingredients")
async def get_cocktails_by_ingredients(
    ingredients: str = Query(
        ..., description="Comma-separated list of ingredients, e.g. vodka,lime"
    ),
    user_id: int | None = Query(None, description="Telegram user ID for history"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Find cocktails containing ALL listed ingredients."""
    if not ingredients.strip():
        raise HTTPException(status_code=400, detail="ingredients must not be empty")

    ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]
    if not ingredient_list:
        raise HTTPException(status_code=400, detail="provide at least one ingredient")

    results = await _api_svc.find_by_multiple_ingredients(ingredient_list)

    # Cache results
    for cocktail in results:
        await _db_svc.upsert_cocktail(db, cocktail)

    await _db_svc.record_search(
        db, user_id, "by_ingredients", ",".join(ingredient_list), len(results)
    )
    return results
