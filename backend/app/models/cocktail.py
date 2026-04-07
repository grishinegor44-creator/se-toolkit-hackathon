from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class CachedCocktail(Base):
    """Cached cocktail data from TheCocktailDB API."""

    __tablename__ = "cached_cocktails"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cocktail_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    alcoholic: Mapped[str | None] = mapped_column(String(50), nullable=True)
    glass: Mapped[str | None] = mapped_column(String(100), nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingredients_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class SearchHistory(Base):
    """Records of user search queries."""

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    query_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "by_name" | "by_ingredients"
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Favorite(Base):
    """User favorite cocktails."""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    cocktail_id: Mapped[str] = mapped_column(String(50), nullable=False)
    cocktail_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
