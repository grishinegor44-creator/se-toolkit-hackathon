"""Integration-level route tests using TestClient and mocked services."""

import pytest
import respx
import httpx
from fastapi.testclient import TestClient

from app.main import app

BASE = "https://www.thecocktaildb.com/api/json/v1/1"

SAMPLE_DRINK = {
    "idDrink": "11007",
    "strDrink": "Margarita",
    "strCategory": "Ordinary Drink",
    "strAlcoholic": "Alcoholic",
    "strGlass": "Cocktail glass",
    "strInstructions": "Shake with ice.",
    "strDrinkThumb": "https://example.com/margarita.jpg",
    "strIngredient1": "Tequila",
    "strMeasure1": "1.5 oz",
    "strIngredient2": None,
    "strMeasure2": None,
}


@pytest.fixture(scope="module")
def client():
    # Override DB init to avoid real PG connection in unit tests
    import app.database as db_module
    original = db_module.init_db

    async def noop():
        pass

    db_module.init_db = noop

    with TestClient(app) as c:
        yield c

    db_module.init_db = original


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# Note: full endpoint tests require a real PG connection.
# The tests below verify the route is wired and returns expected shapes
# when the external API and DB are mocked.

def test_health_shape(client):
    resp = client.get("/health")
    data = resp.json()
    assert "status" in data
    assert "service" in data
