"""
Redis 캐싱 유틸리티
API 응답 성능 최적화를 위한 캐싱 시스템
"""

import json
import redis
from typing import Any, Optional
from datetime import timedelta
from functools import wraps
import hashlib
import pickle

# Redis 클라이언트 초기화 (개발환경에서는 메모리 캐시 사용)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    # Redis가 없는 경우 간단한 메모리 캐시 사용
    REDIS_AVAILABLE = False
    memory_cache = {}

class CacheService:
    """캐싱 서비스 클래스"""
    
    @staticmethod
    def _generate_key(prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return f"aibio:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        try:
            if REDIS_AVAILABLE:
                data = redis_client.get(key)
                if data:
                    return json.loads(data)
            else:
                return memory_cache.get(key)
        except Exception as e:
            print(f"캐시 조회 실패: {e}")
        return None
    
    @staticmethod
    def set(key: str, value: Any, expire: int = 300) -> bool:
        """캐시에 데이터 저장 (기본 5분)"""
        try:
            if REDIS_AVAILABLE:
                redis_client.setex(key, expire, json.dumps(value, ensure_ascii=False, default=str))
            else:
                memory_cache[key] = value
                # 메모리 캐시는 단순하게 구현 (실제로는 TTL 구현 필요)
            return True
        except Exception as e:
            print(f"캐시 저장 실패: {e}")
        return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """캐시에서 데이터 삭제"""
        try:
            if REDIS_AVAILABLE:
                redis_client.delete(key)
            else:
                memory_cache.pop(key, None)
            return True
        except Exception as e:
            print(f"캐시 삭제 실패: {e}")
        return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """패턴에 맞는 캐시 키들 삭제"""
        try:
            if REDIS_AVAILABLE:
                keys = redis_client.keys(pattern)
                if keys:
                    return redis_client.delete(*keys)
            else:
                keys_to_delete = [k for k in memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del memory_cache[key]
                return len(keys_to_delete)
        except Exception as e:
            print(f"캐시 패턴 삭제 실패: {e}")
        return 0

def cached(expire: int = 300, key_prefix: str = "api"):
    """API 응답 캐싱 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = CacheService._generate_key(key_prefix, func.__name__, *args, **kwargs)
            
            # 캐시에서 조회
            cached_result = CacheService.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 캐시 미스 시 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            CacheService.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator

def cache_invalidate(pattern: str):
    """캐시 무효화 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # 함수 실행 후 관련 캐시 삭제
            CacheService.clear_pattern(f"aibio:*{pattern}*")
            return result
        return wrapper
    return decorator

# 자주 사용되는 캐시 설정들
CACHE_SETTINGS = {
    'dashboard_stats': {'expire': 300, 'key_prefix': 'dashboard'},  # 5분
    'customer_list': {'expire': 600, 'key_prefix': 'customers'},    # 10분
    'service_stats': {'expire': 300, 'key_prefix': 'services'},     # 5분
    'payment_stats': {'expire': 900, 'key_prefix': 'payments'},     # 15분
    'package_stats': {'expire': 1800, 'key_prefix': 'packages'},    # 30분
    'reports': {'expire': 3600, 'key_prefix': 'reports'},           # 1시간
}