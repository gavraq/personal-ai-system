"""
API routers for the application
"""
from .auth import router as auth_router
from .users import router as users_router
from .deals import router as deals_router
from .integrations import router as integrations_router
from .files import router as files_router
from .activity import router as activity_router

__all__ = ["auth_router", "users_router", "deals_router", "integrations_router", "files_router", "activity_router"]
