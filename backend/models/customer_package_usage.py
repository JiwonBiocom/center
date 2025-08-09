from sqlalchemy import Column, Integer, ForeignKey, Date, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from core.database import Base


class CustomerPackageUsage(Base):
    """고객별 패키지 서비스 타입별 이용 현황"""
    __tablename__ = "customer_package_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    package_purchase_id = Column(Integer, ForeignKey("package_purchases.purchase_id"), nullable=False)
    service_type = Column(String(50), nullable=False)  # 브레인, 펄스, 림프, 레드
    total_sessions = Column(Integer, nullable=False, default=0)
    used_sessions = Column(Integer, nullable=False, default=0)
    remaining_sessions = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="package_usages")
    package_purchase = relationship("PackagePurchase", back_populates="service_usages")
