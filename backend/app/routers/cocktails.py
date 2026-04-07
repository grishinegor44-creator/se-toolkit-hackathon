import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.database import get_db
from app.services.cocktail_api import CocktailAPIService
from app.services.cocktail_db import CocktailDBService


def _name_variations(name: str) -> list[str]:
    """
    Generate alternative spellings for a cocktail name when the exact search
    returns no results. Handles common patterns:
      B52   → B-52   (letter + digit without hyphen)
      B-52  → B52    (with hyphen → without)
      7&7   → 7 and 7, Seven and Seven
    """
    variants: list[str] = []
    # letter immediately followed by digit → insert hyphen: B52 → B-52
    with_hyphen = re.sub(r'([A-Za-z])(\d)', r'\1-\2', name)
    if with_hyphen != name:
        variants.append(with_hyphen)
    # has hyphen → remove it: B-52 → B52
    without_hyphen = name.replace('-', '')
    if without_hyphen != name:
        variants.append(without_hyphen)
    # letter + digit with space: B 52
    with_space = re.sub(r'([A-Za-z])(\d)', r'\1 \2', name)
    if with_space != name and with_space not in variants:
        variants.append(with_space)
    return variants

router = APIRouter(prefix="/cocktails", tags=["cocktails"])

_api_svc = CocktailAPIService()
_db_svc = CocktailDBService()


@router.get("/random")
async def get_random_cocktail(
    user_id: int | None = Query(None, description="Telegram user ID for history"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Return a completely random cocktail."""
    cocktail = await _api_svc.get_random()
    if not cocktail:
        raise HTTPException(status_code=503, detail="Could not fetch a random cocktail")
    await _db_svc.upsert_cocktail(db, cocktail)
    await _db_svc.record_search(db, user_id, "random", "[random]", 1)
    return cocktail


@router.get("/by-name")
async def get_cocktail_by_name(
    name: str = Query(..., description="Cocktail name to search for"),
    user_id: int | None = Query(None, description="Telegram user ID for history"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """Search cocktails by name. Returns up to 10 matches.
    If the exact name yields no results, automatically retries with
    common spelling variations (e.g. B52 → B-52).
    """
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="name must not be empty")

    raw_drinks = await _api_svc.search_by_name(name)

    # Retry with variations when nothing found (B52 → B-52, etc.)
    if not raw_drinks:
        for variant in _name_variations(name):
            raw_drinks = await _api_svc.search_by_name(variant)
            if raw_drinks:
                break

    if not raw_drinks:
        await _db_svc.record_search(db, user_id, "by_name", name, 0)
        return []

    results = [_api_svc.to_normalized(d) for d in raw_drinks[:10]]
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
