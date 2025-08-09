# Settings API Module
from fastapi import APIRouter
from .profile import router as profile_router
from .users import router as users_router
from .system import router as system_router
from .services import router as services_router
from .notifications import router as notifications_router
from .backup import router as backup_router
from .kakao import router as kakao_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(profile_router, tags=["settings-profile"])
router.include_router(users_router, prefix="/users", tags=["settings-users"])
router.include_router(system_router, prefix="/system", tags=["settings-system"])
router.include_router(services_router, prefix="/service-types", tags=["settings-services"])
router.include_router(notifications_router, prefix="/notifications", tags=["settings-notifications"])
router.include_router(backup_router, prefix="/backup", tags=["settings-backup"])
router.include_router(kakao_router, prefix="/kakao", tags=["settings-kakao"])