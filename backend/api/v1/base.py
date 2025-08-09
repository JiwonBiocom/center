"""
CRUD 베이스 클래스
모든 모델에 대한 공통 CRUD 작업을 제공
"""
from typing import Type, TypeVar, Generic, List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from sqlalchemy.sql import Select
from fastapi import HTTPException
from pydantic import BaseModel

from utils.error_handlers import ErrorResponses

# 타입 변수 정의
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD 객체의 기본 클래스
    
    **사용 예시**:
    ```python
    from models.customer import Customer
    from schemas.customer import CustomerCreate, CustomerUpdate
    
    customer_crud = CRUDBase[Customer, CustomerCreate, CustomerUpdate](Customer)
    ```
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        CRUD 객체 생성
        
        Args:
            model: SQLAlchemy 모델 클래스
        """
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        ID로 단일 객체 조회
        
        Args:
            db: 데이터베이스 세션
            id: 객체 ID
            
        Returns:
            모델 인스턴스 또는 None
        """
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_field(
        self, 
        db: Session, 
        field_name: str, 
        value: Any
    ) -> Optional[ModelType]:
        """
        특정 필드 값으로 단일 객체 조회
        
        Args:
            db: 데이터베이스 세션
            field_name: 필드명
            value: 필드 값
            
        Returns:
            모델 인스턴스 또는 None
        """
        field = getattr(self.model, field_name)
        return db.query(self.model).filter(field == value).first()
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[List[Any]] = None,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """
        여러 객체 조회 (페이지네이션 지원)
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 레코드 수
            limit: 반환할 최대 레코드 수
            filters: SQLAlchemy 필터 조건 리스트
            order_by: 정렬 조건
            
        Returns:
            모델 인스턴스 리스트
        """
        query = db.query(self.model)
        
        if filters:
            for filter_condition in filters:
                query = query.filter(filter_condition)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        return query.offset(skip).limit(limit).all()
    
    def count(
        self, 
        db: Session,
        *,
        filters: Optional[List[Any]] = None
    ) -> int:
        """
        조건에 맞는 레코드 수 계산
        
        Args:
            db: 데이터베이스 세션
            filters: SQLAlchemy 필터 조건 리스트
            
        Returns:
            레코드 수
        """
        query = db.query(func.count()).select_from(self.model)
        
        if filters:
            for filter_condition in filters:
                query = query.filter(filter_condition)
        
        return query.scalar()
    
    def create(
        self, 
        db: Session, 
        *, 
        obj_in: CreateSchemaType
    ) -> ModelType:
        """
        새 객체 생성
        
        Args:
            db: 데이터베이스 세션
            obj_in: 생성할 객체 데이터
            
        Returns:
            생성된 모델 인스턴스
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        객체 업데이트
        
        Args:
            db: 데이터베이스 세션
            db_obj: 업데이트할 객체
            obj_in: 업데이트 데이터
            
        Returns:
            업데이트된 모델 인스턴스
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> ModelType:
        """
        객체 삭제
        
        Args:
            db: 데이터베이스 세션
            id: 삭제할 객체 ID
            
        Returns:
            삭제된 모델 인스턴스
            
        Raises:
            HTTPException: 객체를 찾을 수 없는 경우
        """
        obj = db.query(self.model).get(id)
        if not obj:
            raise ErrorResponses.not_found(self.model.__name__, id)
        
        db.delete(obj)
        db.commit()
        return obj
    
    def exists(
        self,
        db: Session,
        *,
        id: Optional[int] = None,
        filters: Optional[List[Any]] = None
    ) -> bool:
        """
        객체 존재 여부 확인
        
        Args:
            db: 데이터베이스 세션
            id: 객체 ID
            filters: SQLAlchemy 필터 조건 리스트
            
        Returns:
            존재 여부
        """
        query = db.query(self.model.id)
        
        if id is not None:
            query = query.filter(self.model.id == id)
        
        if filters:
            for filter_condition in filters:
                query = query.filter(filter_condition)
        
        return query.first() is not None
    
    def get_or_404(self, db: Session, id: int) -> ModelType:
        """
        ID로 객체 조회, 없으면 404 에러
        
        Args:
            db: 데이터베이스 세션
            id: 객체 ID
            
        Returns:
            모델 인스턴스
            
        Raises:
            HTTPException: 객체를 찾을 수 없는 경우
        """
        obj = self.get(db, id=id)
        if not obj:
            raise ErrorResponses.not_found(self.model.__name__, id)
        return obj