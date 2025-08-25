import sys
import os
# Add backend directory to Python path for Railway deployment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import time
from datetime import datetime
from core.logging_config import setup_logging, get_logger

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE", "logs/app.log"),
    json_format=os.getenv("LOG_FORMAT", "").lower() == "json"
)

logger = get_logger(__name__)

# 배포 버전 정보
# Railway가 주입하는 실제 환경변수들
COMMIT_SHA = os.getenv("RAILWAY_GIT_COMMIT_SHA",
                      os.getenv("RAILWAY_GIT_COMMIT_SHA_SHORT",
                      os.getenv("GIT_SHA", "unknown")))
DEPLOY_TIME = os.getenv("RAILWAY_DEPLOYMENT_ID",
                       os.getenv("RAILWAY_REPLICA_ID", "local"))
BUILD_TIME = datetime.now().strftime("%Y-%m-%d %H:%M KST")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AIBIO Center Management System...")

    # Initialize database tables
    try:
        from core.database import engine, Base
        from models.user import User
        from models.customer import Customer
        from models.service import ServiceUsage, ServiceType
        from models.payment import Payment
        from models.package import Package, PackagePurchase
        from models.lead_management import LeadConsultationHistory, ReregistrationCampaign, CampaignTarget
        from models.notification import Notification, NotificationSettings
        from models.reservation import Reservation
        from models.kit import KitType, KitManagement
        from models.customer_extended import CustomerPreference, CustomerAnalytics, MarketingLead, KitReceipt
        from models.staff_schedule import StaffSchedule
        from models.inbody import InBodyRecord
        from models.system import SystemSettings, CompanyInfo, NotificationPreferences
        from models.audit import AuditLog
        from models.questionnaire import QuestionnaireTemplate, Question, QuestionnaireResponse, Answer, QuestionnaireAnalysis

        logger.info("Creating database tables if they don't exist...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")

        # Create admin user if doesn't exist
        from sqlalchemy.orm import Session
        from core.auth import get_password_hash
        with Session(engine) as db:
            admin = db.query(User).filter(User.email == "admin@aibio.kr").first()
            if not admin:
                admin_user = User(
                    email="admin@aibio.kr",
                    password_hash=get_password_hash("admin123"),
                    name="관리자",
                    role="admin",
                    is_active=True
                )
                db.add(admin_user)
                db.commit()
                logger.info("Admin user created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

    # 회원 등급 스케줄러 시작
    from services.membership_scheduler import start_membership_scheduler
    await start_membership_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down...")

    # 회원 등급 스케줄러 중지
    from services.membership_scheduler import stop_membership_scheduler
    stop_membership_scheduler()

app = FastAPI(
    title="AIBIO Center Management API",
    description="백엔드 API for AIBIO 센터 관리 시스템",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,  # 슬래시 리다이렉트 비활성화
    openapi_tags=[
        {"name": "auth", "description": "인증 관련 API"},
        {"name": "customers", "description": "고객 관리 API"},
        {"name": "services", "description": "서비스 이용 관리 API"},
        {"name": "payments", "description": "결제 관리 API"},
        {"name": "packages", "description": "패키지 관리 API"},
        {"name": "leads", "description": "리드 관리 API"},
        {"name": "reports", "description": "리포트 API"},
        {"name": "notifications", "description": "알림 관리 API"},
        {"name": "settings", "description": "설정 관리 API"},
        {"name": "reservations", "description": "예약 관리 API"},
        {"name": "membership", "description": "회원 등급 관리 API"},
        {"name": "sms", "description": "SMS 발송 API"},
        {"name": "staff-schedule", "description": "직원 일정 관리 API"},
        {"name": "inbody", "description": "인바디 측정 관리 API"},
        {"name": "kits", "description": "키트 관리 API"},
        {"name": "customer-leads", "description": "유입고객 관리 API"},
        {"name": "customers-extended", "description": "확장 고객 정보 API"},
        {"name": "dashboard", "description": "대시보드 API"},
        {"name": "documents", "description": "문서 관리 API"},
        {"name": "questionnaire", "description": "문진 관리 API"},
        {"name": "master", "description": "마스터 권한 API"}
    ]
)

# Configure CORS
default_origins = [
    "http://localhost:3000",
    "http://localhost:4173",  # Vite preview server
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "https://center-frontend.vercel.app",
    "https://frontend-ten-lake-33.vercel.app",
    "https://center-frontend-laso23x2z-taejunjeons-projects.vercel.app",
    "https://center-frontend-4ywbex7qw-taejunjeons-projects.vercel.app",
    "https://center-ten.vercel.app"  # TJ님의 Vercel 도메인
]

# Get additional origins from environment variable
env_origins = os.getenv("CORS_ORIGINS", "").strip()
if env_origins:
    origins = default_origins + env_origins.split(",")
else:
    origins = default_origins

# For development, you can use ["*"] to allow all origins
# origins = ["*"]  # Uncomment for development only!

# TrailingSlashMiddleware 추가 (CORS 미들웨어보다 먼저 등록)
from middleware.trailing_slash import TrailingSlashMiddleware
app.add_middleware(TrailingSlashMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CORS 및 보안 헤더 미들웨어
@app.middleware("http")
async def add_cors_and_security_headers(request: Request, call_next):
    origin = request.headers.get("origin")

    try:
        response = await call_next(request)
        # 배포 버전 정보를 헤더에 추가
        response.headers["x-commit-sha"] = COMMIT_SHA
        response.headers["x-deploy-id"] = DEPLOY_TIME
    except Exception as e:
        # 에러 발생 시에도 CORS 헤더 추가
        from fastapi.responses import JSONResponse
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )
        logger.error(f"Request failed: {e}")

    # CORS 헤더 강제 추가
    if origin and origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    # Content Security Policy - HTTP를 HTTPS로 자동 업그레이드
    response.headers["Content-Security-Policy"] = "upgrade-insecure-requests"

    # HTTPS 강제
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # 추가 보안 헤더
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Generate request ID
    request_id = f"{time.time()}-{request.client.host if request.client else 'unknown'}"

    # Log request
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "ip_address": request.client.host if request.client else None
        }
    )

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} - {response.status_code}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": process_time
        }
    )

    # Add custom headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    return response

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AIBIO Center Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "commit_sha": COMMIT_SHA[:7] if COMMIT_SHA != "unknown" else "unknown",  # 짧은 SHA만 표시
        "deploy_id": DEPLOY_TIME,
        "build_time": BUILD_TIME
    }

# Include routers
from api.v1 import customers, customer_packages, dashboard, services, payments, packages, reports, auth, notifications, settings
from api.v1.reservations import router as reservations_router
from api.v1 import kits, customers_extended, customer_leads, membership, sms_v2 as sms, staff_schedule, inbody, docs, questionnaire
from api.v1 import admin_temp  # 임시 관리자 엔드포인트
from api.v1 import system_info  # 시스템 정보
from api.v1 import public_info  # 공개 정보
from api.v1 import master  # 마스터 권한 API
from api.v1 import admin_init  # 관리자 초기화 API
from api.v1 import customers_import_service  # 고객 서비스 이력 가져오기
from api.v1 import unreflected_customers  # 미반영 고객 관리
from api.v1 import customer_preferences  # 고객 선호도 관리
from api.v1 import counseling  # 상담 내역 관리
# Temporarily disabled enhanced services until relationships are fixed
# from api.v1 import enhanced_services, equipment, test_enhanced

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(customer_packages.router, prefix="/api/v1/customers", tags=["customer-packages"])
app.include_router(customers_import_service.router, prefix="/api/v1/customers", tags=["customers-import"])
app.include_router(customer_preferences.router, prefix="/api/v1", tags=["customer-preferences"])
app.include_router(services.router, prefix="/api/v1/services", tags=["services"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(packages.router, prefix="/api/v1/packages", tags=["packages"])
# leads.py removed - using customer_leads instead
app.include_router(customer_leads.router, tags=["customer-leads"])  # 새로운 유입고객 관리 API
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(kits.router, prefix="/api/v1/kits", tags=["kits"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(reservations_router, prefix="/api/v1/reservations", tags=["reservations"])
app.include_router(membership.router, prefix="/api/v1", tags=["membership"])
app.include_router(sms.router, prefix="/api/v1/sms", tags=["sms"])
app.include_router(staff_schedule.router, prefix="/api/v1/staff-schedule", tags=["staff-schedule"])
app.include_router(inbody.router, prefix="/api/v1", tags=["inbody"])
# Temporarily disabled enhanced services until relationships are fixed
# app.include_router(enhanced_services.router, prefix="/api/v1/enhanced", tags=["enhanced-services"])
# app.include_router(equipment.router, prefix="/api/v1/equipment", tags=["equipment"])
# app.include_router(test_enhanced.router, prefix="/api/v1/test-enhanced", tags=["test-enhanced"])
# Extended customer routes
app.include_router(customers_extended.router, prefix="/api/v1", tags=["customers-extended"])
# Documents (admin only)
app.include_router(docs.router, prefix="/api/v1", tags=["documents"])
# Questionnaire
app.include_router(questionnaire.router, prefix="/api/v1", tags=["questionnaire"])
# 임시 관리자 엔드포인트
app.include_router(admin_temp.router, prefix="/api/v1/admin", tags=["admin-temp"])
# 시스템 정보
app.include_router(system_info.router, prefix="/api/v1/system", tags=["system"])
# 공개 정보 (인증 불필요)
app.include_router(public_info.router, prefix="/api/v1/public", tags=["public"])
# 마스터 권한 API
app.include_router(master.router, prefix="/api/v1/master", tags=["master"])
# 관리자 초기화 API (임시)
app.include_router(admin_init.router, prefix="/api/v1/init", tags=["admin-init"])
# 미반영 고객 관리
app.include_router(unreflected_customers.router, prefix="/api/v1/unreflected-customers", tags=["unreflected-customers"])
# 상담 내역 관리
app.include_router(counseling.router, prefix="/api/v1/customers", tags=["counseling"])

if __name__ == "__main__":
    # Railway나 다른 플랫폼에서 PORT 환경변수 사용
    port = int(os.getenv("PORT", 8000))
    # 프로덕션에서는 reload=False
    is_dev = os.getenv("PYTHON_ENV", "development") == "development"

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=is_dev
    )
