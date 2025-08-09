"""공통 데이터 검증 유틸리티"""
import re
from typing import Optional
from datetime import date, datetime
from utils.error_handlers import ErrorResponses


class Validators:
    """공통 검증 유틸리티"""
    
    @staticmethod
    def validate_phone(phone: Optional[str]) -> Optional[str]:
        """전화번호 검증 및 정제"""
        if not phone:
            return None
        
        # 숫자만 추출
        numbers = re.sub(r'[^0-9]', '', phone)
        
        # 한국 휴대폰 번호 검증
        if len(numbers) == 11 and numbers.startswith('010'):
            return f"{numbers[:3]}-{numbers[3:7]}-{numbers[7:]}"
        elif len(numbers) == 10:
            if numbers.startswith('02'):  # 서울
                return f"{numbers[:2]}-{numbers[2:6]}-{numbers[6:]}"
            elif numbers[:3] in ['031', '032', '033', '041', '042', '043', 
                                '044', '051', '052', '053', '054', '055', 
                                '061', '062', '063', '064']:  # 지역번호
                return f"{numbers[:3]}-{numbers[3:6]}-{numbers[6:]}"
        
        raise ErrorResponses.validation_error(f"올바른 전화번호 형식이 아닙니다: {phone}")
    
    @staticmethod
    def validate_email(email: str) -> str:
        """이메일 검증"""
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            raise ErrorResponses.validation_error(f"올바른 이메일 형식이 아닙니다: {email}")
        return email.lower()
    
    @staticmethod
    def validate_date_range(
        date_from: Optional[date],
        date_to: Optional[date]
    ) -> tuple[Optional[date], Optional[date]]:
        """날짜 범위 검증"""
        if date_from and date_to and date_from > date_to:
            raise ErrorResponses.validation_error("시작일이 종료일보다 늦을 수 없습니다")
        return date_from, date_to
    
    @staticmethod
    def validate_positive_number(
        value: float,
        field_name: str = "값"
    ) -> float:
        """양수 검증"""
        if value <= 0:
            raise ErrorResponses.validation_error(f"{field_name}은(는) 0보다 커야 합니다")
        return value
    
    @staticmethod
    def validate_percentage(
        value: float,
        field_name: str = "비율"
    ) -> float:
        """백분율 검증 (0-100)"""
        if not 0 <= value <= 100:
            raise ErrorResponses.validation_error(f"{field_name}은(는) 0에서 100 사이여야 합니다")
        return value
    
    @staticmethod
    def validate_required_string(
        value: Optional[str],
        field_name: str
    ) -> str:
        """필수 문자열 검증"""
        if not value or not value.strip():
            raise ErrorResponses.validation_error(f"{field_name}은(는) 필수 입력 항목입니다")
        return value.strip()
    
    @staticmethod
    def validate_enum_value(
        value: str,
        allowed_values: list[str],
        field_name: str
    ) -> str:
        """열거형 값 검증"""
        if value not in allowed_values:
            allowed = ", ".join(allowed_values)
            raise ErrorResponses.validation_error(
                f"{field_name}은(는) 다음 중 하나여야 합니다: {allowed}"
            )
        return value
    
    @staticmethod
    def sanitize_string(value: Optional[str]) -> Optional[str]:
        """문자열 정제 (XSS 방지)"""
        if not value:
            return None
        
        # HTML 태그 제거
        value = re.sub(r'<[^>]+>', '', value)
        # 연속 공백 제거
        value = ' '.join(value.split())
        # 앞뒤 공백 제거
        return value.strip() or None