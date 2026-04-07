from .cocktails import router as cocktails_router
from .history import router as history_router
from .favorites import router as favorites_router

__all__ = ["cocktails_router", "history_router", "favorites_router"]
