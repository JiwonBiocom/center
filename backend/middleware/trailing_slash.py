"""
TrailingSlashMiddleware for AIBIO Center Management System

이 미들웨어는 POST/PUT/PATCH 요청에 대해 trailing slash를 자동으로 처리합니다.
- POST/PUT/PATCH 요청에서 trailing slash가 있으면 제거
- GET/DELETE 요청은 캐시 키 일관성을 위해 처리하지 않음
- WebSocket, 파일 업로드 등 특수 경로는 예외 처리

Author: Hephaestus (헤파이스토스)
Date: 2025-06-25
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class TrailingSlashMiddleware(BaseHTTPMiddleware):
    """
    POST/PUT/PATCH 요청의 trailing slash를 정규화하는 미들웨어
    """

    # 미들웨어 처리에서 제외할 경로 패턴
    EXCLUDED_PATHS = {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/ws",  # WebSocket 경로
        "/upload",  # 파일 업로드 경로
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        요청을 가로채서 trailing slash를 처리

        Args:
            request: 들어온 HTTP 요청
            call_next: 다음 미들웨어나 엔드포인트로 전달하는 함수

        Returns:
            Response: HTTP 응답
        """
        # 경로 가져오기
        path = request.scope.get("path", "")
        method = request.method

        # 예외 경로는 그대로 통과
        if self._is_excluded_path(path):
            return await call_next(request)

        # POST/PUT/PATCH 메서드만 처리
        if method in {"POST", "PUT", "PATCH"}:
            # trailing slash가 있고 루트 경로가 아닌 경우
            if path.endswith("/") and path != "/":
                # scope 복사 후 수정 (원본 수정 방지)
                new_scope = request.scope.copy()
                new_scope["path"] = path.rstrip("/")

                # 로깅 (개발 환경에서만)
                logger.debug(f"Trailing slash removed: {path} -> {new_scope['path']}")

                # 새로운 Request 객체 생성
                request._scope = new_scope

        # 요청을 다음 미들웨어/엔드포인트로 전달
        response = await call_next(request)
        return response

    def _is_excluded_path(self, path: str) -> bool:
        """
        경로가 예외 처리 대상인지 확인

        Args:
            path: 검사할 경로

        Returns:
            bool: 예외 경로면 True, 아니면 False
        """
        # 정확히 일치하는 경로
        if path in self.EXCLUDED_PATHS:
            return True

        # 특정 경로로 시작하는 경우
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded + "/"):
                return True

        # 정적 파일 경로
        if path.startswith("/static/") or path.startswith("/media/"):
            return True

        return False
