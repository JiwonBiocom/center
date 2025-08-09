"""
API 응답 래퍼 유틸리티
기존 엔드포인트를 표준 응답 형식으로 변환
"""
from typing import Any, Callable, TypeVar, Union, List
from functools import wraps
from fastapi import Response
from fastapi.responses import JSONResponse
import inspect

from schemas.response import APIResponse, PaginatedResponse, success_response, paginated_response

T = TypeVar('T')


def wrap_response(func: Callable) -> Callable:
    """
    API 엔드포인트의 응답을 표준 형식으로 래핑
    
    사용 예:
    ```python
    @router.get("/")
    @wrap_response
    def get_items():
        return items  # 자동으로 APIResponse로 래핑됨
    ```
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return format_response(result)
        except Exception as e:
            # 에러는 기존 에러 핸들러가 처리하도록 그대로 raise
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return format_response(result)
        except Exception as e:
            # 에러는 기존 에러 핸들러가 처리하도록 그대로 raise
            raise
    
    # 함수가 코루틴인지 확인
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def format_response(result: Any) -> Union[APIResponse, JSONResponse]:
    """
    결과를 표준 응답 형식으로 변환
    """
    # 이미 Response 객체인 경우 그대로 반환
    if isinstance(result, Response):
        return result
    
    # 이미 APIResponse인 경우 그대로 반환
    if isinstance(result, (APIResponse, PaginatedResponse)):
        return result
    
    # 딕셔너리이고 특정 키가 있는 경우 (기존 응답 형식)
    if isinstance(result, dict):
        # 페이지네이션 응답 감지
        if all(key in result for key in ['items', 'total', 'page', 'page_size']):
            return paginated_response(
                data=result['items'],
                total=result['total'],
                page=result['page'],
                page_size=result['page_size']
            )
        
        # 메시지 응답 감지
        if 'message' in result and len(result) == 1:
            return success_response(data=None, message=result['message'])
        
        # 에러 응답 감지 (이미 처리된 경우)
        if 'error' in result:
            return result
    
    # 리스트인 경우
    if isinstance(result, list):
        return success_response(data=result)
    
    # 기타 모든 경우
    return success_response(data=result)


def wrap_paginated_response(
    page_param: str = 'page',
    page_size_param: str = 'page_size'
) -> Callable:
    """
    페이지네이션이 적용된 엔드포인트용 래퍼
    
    사용 예:
    ```python
    @router.get("/")
    @wrap_paginated_response()
    def get_items(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
        total = get_total_count(db)
        items = get_items_paginated(db, page, page_size)
        return items, total  # 튜플로 반환하면 자동으로 PaginatedResponse로 변환
    ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # 페이지 파라미터 추출 및 변환
                if page_param == 'skip':
                    # skip/limit 방식인 경우 page 계산
                    skip = kwargs.get('skip', 0)
                    limit = kwargs.get('limit', 20)
                    page = (skip // limit) + 1
                    page_size = limit
                else:
                    # 일반적인 page/page_size 방식
                    page = kwargs.get(page_param, 1)
                    page_size = kwargs.get(page_size_param, 20)
                
                result = await func(*args, **kwargs)
                
                # 튜플로 (items, total) 반환하는 경우
                if isinstance(result, tuple) and len(result) == 2:
                    items, total = result
                    return paginated_response(
                        data=items,
                        total=total,
                        page=page,
                        page_size=page_size
                    )
                
                return format_response(result)
            except Exception as e:
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                # 페이지 파라미터 추출 및 변환
                if page_param == 'skip':
                    # skip/limit 방식인 경우 page 계산
                    skip = kwargs.get('skip', 0)
                    limit = kwargs.get('limit', 20)
                    page = (skip // limit) + 1
                    page_size = limit
                else:
                    # 일반적인 page/page_size 방식
                    page = kwargs.get(page_param, 1)
                    page_size = kwargs.get(page_size_param, 20)
                
                result = func(*args, **kwargs)
                
                # 튜플로 (items, total) 반환하는 경우
                if isinstance(result, tuple) and len(result) == 2:
                    items, total = result
                    return paginated_response(
                        data=items,
                        total=total,
                        page=page,
                        page_size=page_size
                    )
                
                return format_response(result)
            except Exception as e:
                raise
        
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator