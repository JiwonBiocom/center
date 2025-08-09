"""API 응답 포맷터"""
from typing import Any, Dict, List, Optional, TypeVar, Generic
from pydantic import BaseModel
from datetime import datetime

T = TypeVar('T')


class PaginationInfo(BaseModel):
    """페이지네이션 정보"""
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class APIResponse(BaseModel, Generic[T]):
    """표준 API 응답 형식"""
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginatedResponse(APIResponse[List[T]], Generic[T]):
    """페이지네이션된 응답 형식"""
    pagination: PaginationInfo


class ResponseFormatter:
    """응답 포맷터"""
    
    @staticmethod
    def success(data: Any = None, message: str = None) -> APIResponse:
        """성공 응답 생성"""
        return APIResponse(
            success=True,
            data=data,
            message=message
        )
    
    @staticmethod
    def paginated(
        items: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = None
    ) -> PaginatedResponse:
        """페이지네이션된 응답 생성"""
        total_pages = (total + page_size - 1) // page_size
        
        pagination = PaginationInfo(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
        return PaginatedResponse(
            success=True,
            data=items,
            message=message,
            pagination=pagination
        )
    
    @staticmethod
    def created(data: Any, message: str = "생성되었습니다") -> APIResponse:
        """생성 응답"""
        return APIResponse(
            success=True,
            data=data,
            message=message
        )
    
    @staticmethod
    def updated(data: Any, message: str = "수정되었습니다") -> APIResponse:
        """수정 응답"""
        return APIResponse(
            success=True,
            data=data,
            message=message
        )
    
    @staticmethod
    def deleted(message: str = "삭제되었습니다") -> APIResponse:
        """삭제 응답"""
        return APIResponse(
            success=True,
            data=None,
            message=message
        )
    
    @staticmethod
    def file_response(
        file_name: str,
        file_size: int,
        message: str = "파일이 생성되었습니다"
    ) -> APIResponse:
        """파일 응답"""
        return APIResponse(
            success=True,
            data={
                "file_name": file_name,
                "file_size": file_size
            },
            message=message
        )


def paginate_query(query, page: int, page_size: int) -> Dict[str, Any]:
    """SQLAlchemy 쿼리에 페이지네이션 적용"""
    # 전체 개수
    total = query.count()
    
    # 페이지네이션 적용
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # 총 페이지 수
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }