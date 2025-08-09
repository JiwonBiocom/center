"""
Customer CRUD 작업
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from api.v1.base import CRUDBase
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate
from utils.error_handlers import ErrorResponses


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    """Customer 전용 CRUD 클래스"""
    
    def get_by_phone(self, db: Session, *, phone: str) -> Optional[Customer]:
        """전화번호로 고객 조회"""
        return self.get_by_field(db, "phone", phone)
    
    def search(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        region: Optional[str] = None,
        referral_source: Optional[str] = None,
        membership_level: Optional[str] = None,
        customer_status: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        revenue_min: Optional[int] = None,
        revenue_max: Optional[int] = None,
        visits_min: Optional[int] = None,
        visits_max: Optional[int] = None
    ) -> List[Customer]:
        """고급 검색 기능"""
        filters = []
        
        # 기본 검색 (이름, 전화번호, 이메일)
        if search:
            search_conditions = [
                Customer.name.contains(search),
                Customer.phone.contains(search),
                and_(Customer.email.is_not(None), Customer.email.contains(search))
            ]
            filters.append(or_(*search_conditions))
        
        # 지역 필터
        if region:
            filters.append(Customer.region.contains(region))
        
        # 유입경로 필터
        if referral_source:
            filters.append(Customer.referral_source == referral_source)
        
        # 멤버십 레벨 필터
        if membership_level:
            filters.append(Customer.membership_level == membership_level)
        
        # 고객 상태 필터
        if customer_status:
            filters.append(Customer.customer_status == customer_status)
        
        # 나이 범위 필터
        if age_min is not None or age_max is not None:
            current_year = datetime.now().year
            if age_min is not None:
                max_birth_year = current_year - age_min
                filters.append(Customer.birth_year <= max_birth_year)
            if age_max is not None:
                min_birth_year = current_year - age_max
                filters.append(Customer.birth_year >= min_birth_year)
        
        # 매출 범위 필터 (만원 단위)
        if revenue_min is not None:
            filters.append(Customer.total_revenue >= revenue_min * 10000)
        if revenue_max is not None:
            filters.append(Customer.total_revenue <= revenue_max * 10000)
        
        # 방문 횟수 범위 필터
        if visits_min is not None:
            filters.append(Customer.total_visits >= visits_min)
        if visits_max is not None:
            filters.append(Customer.total_visits <= visits_max)
        
        return self.get_multi(
            db,
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=Customer.customer_id.desc()
        )
    
    def create_with_duplicate_check(
        self,
        db: Session,
        *,
        obj_in: CustomerCreate
    ) -> Customer:
        """중복 체크 후 고객 생성"""
        # 전화번호 중복 체크
        if obj_in.phone:
            existing = self.get_by_phone(db, phone=obj_in.phone)
            if existing:
                raise ErrorResponses.already_exists("고객", "전화번호", obj_in.phone)
        
        return self.create(db, obj_in=obj_in)
    
    def update_with_duplicate_check(
        self,
        db: Session,
        *,
        db_obj: Customer,
        obj_in: CustomerUpdate
    ) -> Customer:
        """중복 체크 후 고객 정보 수정"""
        # 전화번호 변경 시 중복 체크
        if obj_in.phone and obj_in.phone != db_obj.phone:
            filters = [
                Customer.phone == obj_in.phone,
                Customer.customer_id != db_obj.customer_id
            ]
            if self.exists(db, filters=filters):
                raise ErrorResponses.already_exists("고객", "전화번호", obj_in.phone)
        
        return self.update(db, db_obj=db_obj, obj_in=obj_in)


# 싱글톤 인스턴스
customer = CRUDCustomer(Customer)