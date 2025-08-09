from fastapi import APIRouter
from .crud import router as crud_router
from .stats import router as stats_router
from .receipt import router as receipt_router

router = APIRouter()

# Include all sub-routers
router.include_router(crud_router, tags=["payments-crud"])
router.include_router(stats_router, prefix="/stats", tags=["payments-stats"])
router.include_router(receipt_router, tags=["payments-receipt"])