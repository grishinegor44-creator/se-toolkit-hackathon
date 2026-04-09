import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import cocktails_router, history_router, favorites_router, users_router
from app.settings import settings

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initialising database tables…")
    await init_db()
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="CocktailBot API",
    description="Backend for the Cocktail Telegram Bot — search cocktails by name or ingredients.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(cocktails_router)
app.include_router(history_router)
app.include_router(favorites_router)
app.include_router(users_router)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "cocktailbot-api"}
