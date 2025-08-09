# Reports API Module
from fastapi import APIRouter
from .summary import router as summary_router
from .revenue import router as revenue_router
from .customer import router as customer_router
from .service import router as service_router
from .staff import router as staff_router
from .export import router as export_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(summary_router, tags=["reports-summary"])
router.include_router(revenue_router, prefix="/revenue", tags=["reports-revenue"])
router.include_router(customer_router, prefix="/customers", tags=["reports-customers"])
router.include_router(service_router, prefix="/services", tags=["reports-services"]) 
router.include_router(staff_router, prefix="/staff", tags=["reports-staff"])
router.include_router(export_router, prefix="/export", tags=["reports-export"])