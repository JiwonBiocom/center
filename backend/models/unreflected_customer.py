"""
미반영 고객 모델
원본 엑셀에 없는 고객 데이터를 별도로 관리
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from sqlalchemy.sql import func
from core.database import Base

class UnreflectedCustomer(Base):
    """미반영 고객 테이블"""
    __tablename__ = "unreflected_customers"

    id = Column(Integer, primary_key=True, index=True)

    # 기존 customer_id (이동 전 ID 보관)
    original_customer_id = Column(Integer, nullable=True)

    # 고객 정보
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    first_visit_date = Column(Date, nullable=True)
    region = Column(String(100), nullable=True)
    referral_source = Column(String(100), nullable=True)
    health_concerns = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    assigned_staff = Column(String(50), nullable=True)

    # 추가 정보
    birth_year = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(20), nullable=True)
    occupation = Column(String(100), nullable=True)

    # 데이터 출처 정보
    data_source = Column(String(200), nullable=True)  # 어느 파일/import에서 왔는지
    import_date = Column(DateTime, server_default=func.now())  # 언제 import 되었는지
    import_notes = Column(Text, nullable=True)  # import 관련 메모

    # 관리 정보
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # 상태 (pending: 대기중, rejected: 거부됨, moved_back: 다시 이동됨)
    status = Column(String(20), default="pending")
