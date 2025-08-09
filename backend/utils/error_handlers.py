"""API 에러 처리 유틸리티"""
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class APIError(HTTPException):
    """커스텀 API 에러 클래스"""
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


# 표준 에러 응답
class ErrorResponses:
    """표준화된 에러 응답 모음"""
    
    @staticmethod
    def not_found(resource: str, identifier: Any) -> APIError:
        return APIError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource}을(를) 찾을 수 없습니다. (ID: {identifier})",
            error_code="RESOURCE_NOT_FOUND"
        )
    
    @staticmethod
    def already_exists(resource: str, field: str, value: Any) -> APIError:
        return APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"이미 존재하는 {resource}입니다. ({field}: {value})",
            error_code="ALREADY_EXISTS"
        )
    
    @staticmethod
    def validation_error(message: str) -> APIError:
        return APIError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
            error_code="VALIDATION_ERROR"
        )
    
    @staticmethod
    def unauthorized(message: str = "인증이 필요합니다") -> APIError:
        return APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            error_code="UNAUTHORIZED"
        )
    
    @staticmethod
    def forbidden(message: str = "권한이 없습니다") -> APIError:
        return APIError(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
            error_code="FORBIDDEN"
        )
    
    @staticmethod
    def database_error(operation: str) -> APIError:
        return APIError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터베이스 {operation} 중 오류가 발생했습니다",
            error_code="DATABASE_ERROR"
        )
    
    @staticmethod
    def business_logic_error(message: str) -> APIError:
        return APIError(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            error_code="BUSINESS_LOGIC_ERROR"
        )


def handle_database_error(func):
    """데이터베이스 에러 처리 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"Database integrity error: {str(e)}")
            if "UNIQUE constraint failed" in str(e):
                raise ErrorResponses.already_exists("데이터", "값", "중복")
            elif "FOREIGN KEY constraint failed" in str(e):
                raise ErrorResponses.validation_error("참조하는 데이터가 존재하지 않습니다")
            else:
                raise ErrorResponses.database_error("처리")
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            raise ErrorResponses.database_error("처리")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise APIError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="예기치 않은 오류가 발생했습니다",
                error_code="INTERNAL_ERROR"
            )
    return wrapper


def handle_api_errors(operation: str):
    """API 에러 처리 데코레이터 (async 지원)"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # HTTPException은 그대로 통과
                raise
            except IntegrityError as e:
                logger.error(f"Database integrity error in {operation}: {str(e)}")
                if "UNIQUE constraint failed" in str(e):
                    raise ErrorResponses.already_exists("데이터", "값", "중복")
                elif "FOREIGN KEY constraint failed" in str(e):
                    raise ErrorResponses.validation_error("참조하는 데이터가 존재하지 않습니다")
                else:
                    raise ErrorResponses.database_error(operation)
            except SQLAlchemyError as e:
                logger.error(f"Database error in {operation}: {str(e)}")
                raise ErrorResponses.database_error(operation)
            except Exception as e:
                logger.error(f"Unexpected error in {operation}: {str(e)}")
                raise APIError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"{operation} 중 오류가 발생했습니다",
                    error_code="INTERNAL_ERROR"
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                # HTTPException은 그대로 통과
                raise
            except IntegrityError as e:
                logger.error(f"Database integrity error in {operation}: {str(e)}")
                if "UNIQUE constraint failed" in str(e):
                    raise ErrorResponses.already_exists("데이터", "값", "중복")
                elif "FOREIGN KEY constraint failed" in str(e):
                    raise ErrorResponses.validation_error("참조하는 데이터가 존재하지 않습니다")
                else:
                    raise ErrorResponses.database_error(operation)
            except SQLAlchemyError as e:
                logger.error(f"Database error in {operation}: {str(e)}")
                raise ErrorResponses.database_error(operation)
            except Exception as e:
                logger.error(f"Unexpected error in {operation}: {str(e)}")
                raise APIError(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"{operation} 중 오류가 발생했습니다",
                    error_code="INTERNAL_ERROR"
                )
        
        # 함수가 코루틴인지 확인
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def format_error_response(error: APIError) -> Dict[str, Any]:
    """에러 응답 포맷팅"""
    return {
        "error": {
            "code": error.error_code,
            "message": error.detail,
            "status": error.status_code
        }
    }