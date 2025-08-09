"""
표준 API 응답 스키마
"""
from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """
    표준 API 응답 형식
    
    모든 API 응답은 이 형식을 따름
    """
    success: bool
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    페이지네이션이 적용된 응답 형식
    """
    success: bool = True
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    message: Optional[str] = None
    timestamp: datetime = datetime.now()
    
    @classmethod
    def create(
        cls,
        data: List[T],
        total: int,
        page: int,
        page_size: int,
        message: Optional[str] = None
    ) -> "PaginatedResponse[T]":
        """페이지네이션 응답 생성 헬퍼"""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            data=data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            message=message
        )


class ErrorResponse(BaseModel):
    """
    에러 응답 형식
    """
    success: bool = False
    error: Dict[str, Any]
    message: str
    timestamp: datetime = datetime.now()
    request_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        code: str,
        message: str,
        details: Optional[Any] = None,
        request_id: Optional[str] = None
    ) -> "ErrorResponse":
        """에러 응답 생성 헬퍼"""
        error = {
            "code": code,
            "details": details
        }
        return cls(
            error=error,
            message=message,
            request_id=request_id
        )


# 응답 생성 헬퍼 함수
def success_response(
    data: T,
    message: Optional[str] = None
) -> APIResponse[T]:
    """성공 응답 생성"""
    return APIResponse(
        success=True,
        data=data,
        message=message
    )


def error_response(
    code: str,
    message: str,
    details: Optional[Any] = None
) -> ErrorResponse:
    """에러 응답 생성"""
    return ErrorResponse.create(
        code=code,
        message=message,
        details=details
    )


def paginated_response(
    data: List[T],
    total: int,
    page: int = 1,
    page_size: int = 20,
    message: Optional[str] = None
) -> PaginatedResponse[T]:
    """페이지네이션 응답 생성"""
    return PaginatedResponse.create(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        message=message
    )