# Reservations API Module
from fastapi import APIRouter
from .crud import router as crud_router
from .calendar import router as calendar_router
from .slots import router as slots_router
from .notifications import router as notifications_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(crud_router, tags=["reservations-crud"])
router.include_router(calendar_router, prefix="/calendar", tags=["reservations-calendar"])
router.include_router(slots_router, prefix="/slots", tags=["reservations-slots"])
router.include_router(notifications_router, prefix="/notifications", tags=["reservations-notifications"])