"""
API routers for the application
"""
from .auth import router as auth_router
from .users import router as users_router
from .deals import router as deals_router

__all__ = ["auth_router", "users_router", "deals_router"]
