"""Rate Limiting 유틸리티"""
from typing import Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import time
from fastapi import Request, HTTPException, status
from functools import wraps
import asyncio


class RateLimiter:
    """간단한 메모리 기반 Rate Limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self._cleanup_task = None
    
    def __call__(
        self,
        max_requests: int = 60,
        window_seconds: int = 60,
        identifier: Optional[Callable[[Request], str]] = None
    ):
        """Rate limiting 데코레이터
        
        Args:
            max_requests: 윈도우 내 최대 요청 수
            window_seconds: 시간 윈도우 (초)
            identifier: 클라이언트 식별 함수 (기본값: IP 주소)
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(request: Request, *args, **kwargs):
                # 클라이언트 식별
                if identifier:
                    client_id = identifier(request)
                else:
                    client_id = request.client.host if request.client else "unknown"
                
                # 현재 시간
                now = time.time()
                window_start = now - window_seconds
                
                # 오래된 요청 제거
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if req_time > window_start
                ]
                
                # 요청 수 확인
                if len(self.requests[client_id]) >= max_requests:
                    retry_after = int(self.requests[client_id][0] + window_seconds - now)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"요청 한도 초과. {retry_after}초 후에 다시 시도해주세요.",
                        headers={"Retry-After": str(retry_after)}
                    )
                
                # 요청 기록
                self.requests[client_id].append(now)
                
                # 원래 함수 실행
                return await func(request, *args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(request: Request, *args, **kwargs):
                # 클라이언트 식별
                if identifier:
                    client_id = identifier(request)
                else:
                    client_id = request.client.host if request.client else "unknown"
                
                # 현재 시간
                now = time.time()
                window_start = now - window_seconds
                
                # 오래된 요청 제거
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if req_time > window_start
                ]
                
                # 요청 수 확인
                if len(self.requests[client_id]) >= max_requests:
                    retry_after = int(self.requests[client_id][0] + window_seconds - now)
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"요청 한도 초과. {retry_after}초 후에 다시 시도해주세요.",
                        headers={"Retry-After": str(retry_after)}
                    )
                
                # 요청 기록
                self.requests[client_id].append(now)
                
                # 원래 함수 실행
                return func(request, *args, **kwargs)
            
            # 비동기/동기 함수 구분
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    async def cleanup_old_requests(self, window_seconds: int = 60):
        """오래된 요청 기록 정리"""
        while True:
            await asyncio.sleep(window_seconds)
            now = time.time()
            window_start = now - window_seconds
            
            # 모든 클라이언트의 오래된 요청 제거
            for client_id in list(self.requests.keys()):
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if req_time > window_start
                ]
                # 빈 리스트는 제거
                if not self.requests[client_id]:
                    del self.requests[client_id]


# 전역 rate limiter 인스턴스
rate_limiter = RateLimiter()


# 사전 정의된 rate limiter들
strict_limiter = rate_limiter(max_requests=10, window_seconds=60)  # 분당 10회
standard_limiter = rate_limiter(max_requests=60, window_seconds=60)  # 분당 60회
relaxed_limiter = rate_limiter(max_requests=300, window_seconds=60)  # 분당 300회