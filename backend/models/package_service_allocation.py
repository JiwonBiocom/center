from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.database import Base

class PackageServiceAllocation(Base):
    """패키지별 서비스 타입별 할당량"""
    __tablename__ = "package_service_allocations"

    allocation_id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("package_purchases.purchase_id"))
    service_type_id = Column(Integer, ForeignKey("service_types.service_type_id"))
    total_sessions = Column(Integer, nullable=False, default=0)
    used_sessions = Column(Integer, nullable=False, default=0)

    # 유니크 제약: 한 구매에 대해 서비스 타입별로 하나씩만
    __table_args__ = (
        UniqueConstraint('purchase_id', 'service_type_id', name='uq_purchase_service'),
    )

    # Relationships
    purchase = relationship("PackagePurchase", backref="service_allocations")
    service_type = relationship("ServiceType")
