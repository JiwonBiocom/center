from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(20), unique=True, index=True)  # 결제번호 (예: PAY-2025-000001)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), index=True)
    payment_date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(20))  # card, transfer, cash
    payment_type = Column(String(20))  # package, single, additional, refund
    payment_status = Column(String(20))  # completed, pending, cancelled
    payment_staff = Column(String(50))  # 결제 담당 직원
    transaction_id = Column(String(100))  # 거래 ID (승인번호)
    card_holder_name = Column(String(100))  # 카드 명의자명
    reference_id = Column(Integer)  # 참조 ID (패키지 구매 ID 등)
    reference_type = Column(String(50))  # 참조 타입 (결제 프로그램)
    notes = Column(String(500))  # 메모
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", backref="payments")
