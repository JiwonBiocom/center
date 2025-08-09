from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Package(Base):
    __tablename__ = "packages"

    package_id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String(100), nullable=False)
    total_sessions = Column(Integer)
    base_price = Column(Integer)  # 변경: price -> base_price, Numeric -> Integer
    valid_months = Column(Integer)  # 변경: valid_days -> valid_months
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Enhanced service relationships (commented out - model not yet implemented)
    # enhanced_package_usages = relationship("EnhancedPackageUsage", back_populates="package")

class PackagePurchase(Base):
    __tablename__ = "package_purchases"

    purchase_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), index=True)
    package_id = Column(Integer, ForeignKey("packages.package_id"))
    purchase_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    total_sessions = Column(Integer)
    used_sessions = Column(Integer, default=0)
    remaining_sessions = Column(Integer)
    notes = Column(String)  # 서비스별 할당 정보 등을 JSON으로 저장
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", backref="package_purchases")
    package = relationship("Package", backref="purchases")
