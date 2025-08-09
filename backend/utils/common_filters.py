"""공통 필터링 유틸리티"""
from typing import Optional, Any
from datetime import date
from sqlalchemy import Select, and_, or_
from sqlalchemy.orm import Query


class CommonFilters:
    """공통 필터링 기능 모음"""
    
    @staticmethod
    def apply_date_filter(
        query: Select,
        model_class: Any,
        date_field: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Select:
        """날짜 범위 필터링 적용"""
        if date_from:
            query = query.where(getattr(model_class, date_field) >= date_from)
        if date_to:
            query = query.where(getattr(model_class, date_field) <= date_to)
        return query
    
    @staticmethod
    def apply_search_filter(
        query: Select,
        model_class: Any,
        search_term: str,
        search_fields: list[str]
    ) -> Select:
        """검색 필터링 적용"""
        if not search_term:
            return query
        
        conditions = []
        for field in search_fields:
            if hasattr(model_class, field):
                conditions.append(getattr(model_class, field).contains(search_term))
        
        if conditions:
            query = query.where(conditions[0] if len(conditions) == 1 else or_(*conditions))
        
        return query
    
    @staticmethod
    def apply_pagination(
        query: Select,
        skip: int = 0,
        limit: int = 20
    ) -> Select:
        """페이지네이션 적용"""
        return query.offset(skip).limit(limit)
    
    @staticmethod
    def apply_status_filter(
        query: Select,
        model_class: Any,
        status_field: str,
        status_value: Optional[str] = None
    ) -> Select:
        """상태 필터링 적용"""
        if status_value:
            query = query.where(getattr(model_class, status_field) == status_value)
        return query
    
    @staticmethod
    def apply_id_filter(
        query: Select,
        model_class: Any,
        id_field: str,
        id_value: Optional[int] = None
    ) -> Select:
        """ID 필터링 적용"""
        if id_value:
            query = query.where(getattr(model_class, id_field) == id_value)
        return query


class QueryParams:
    """공통 쿼리 파라미터"""
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 20,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search: Optional[str] = None,
        status: Optional[str] = None
    ):
        self.skip = skip
        self.limit = limit
        self.date_from = date_from
        self.date_to = date_to
        self.search = search
        self.status = status
    
    def apply_to_query(
        self,
        query: Select,
        model_class: Any,
        date_field: Optional[str] = None,
        search_fields: Optional[list[str]] = None,
        status_field: Optional[str] = None
    ) -> Select:
        """쿼리에 모든 파라미터 적용"""
        # 날짜 필터
        if date_field:
            query = CommonFilters.apply_date_filter(
                query, model_class, date_field, self.date_from, self.date_to
            )
        
        # 검색 필터
        if search_fields and self.search:
            query = CommonFilters.apply_search_filter(
                query, model_class, self.search, search_fields
            )
        
        # 상태 필터
        if status_field and self.status:
            query = CommonFilters.apply_status_filter(
                query, model_class, status_field, self.status
            )
        
        # 페이지네이션
        query = CommonFilters.apply_pagination(query, self.skip, self.limit)
        
        return query