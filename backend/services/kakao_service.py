import requests
import json
import hashlib
import time
from typing import Dict, Optional, List
from datetime import datetime
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class KakaoAlimtalkService:
    """카카오 알림톡 직접 연동 서비스"""
    
    def __init__(self):
        # 카카오 비즈니스 API 설정
        self.base_url = "https://kapi.kakao.com"
        self.biz_url = "https://bizmessage-api.kakao.com"
        
        # 인증 정보 (환경변수에서 가져옴)
        self.rest_api_key = settings.KAKAO_REST_API_KEY
        self.admin_key = settings.KAKAO_ADMIN_KEY
        self.sender_key = settings.KAKAO_SENDER_KEY
        self.sender_number = settings.BUSINESS_PHONE  # 발신번호
        
    def _get_headers(self, use_admin_key: bool = False) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        if use_admin_key:
            return {
                "Authorization": f"KakaoAK {self.admin_key}",
                "Content-Type": "application/json"
            }
        else:
            return {
                "Authorization": f"KakaoAK {self.rest_api_key}",
                "Content-Type": "application/json"
            }
    
    def send_alimtalk(
        self,
        phone_number: str,
        template_code: str,
        template_args: Dict[str, str],
        reserved_time: Optional[str] = None,
        fallback_message: Optional[str] = None
    ) -> Dict:
        """
        알림톡 발송
        
        Args:
            phone_number: 수신자 전화번호 (010-1234-5678 형식)
            template_code: 승인된 템플릿 코드
            template_args: 템플릿 변수 딕셔너리
            reserved_time: 예약 발송 시간 (YYYYMMDDHHMISS)
            fallback_message: 알림톡 실패 시 SMS 대체 발송 메시지
            
        Returns:
            발송 결과 딕셔너리
        """
        
        # 전화번호 형식 정규화 (하이픈 제거)
        phone_number = phone_number.replace("-", "")
        
        # 요청 데이터 구성
        data = {
            "sender_key": self.sender_key,
            "receiver_no": phone_number,
            "template_code": template_code,
            "template_args": template_args,
            "sender_no": self.sender_number
        }
        
        # 예약 발송 설정
        if reserved_time:
            data["reserved_time"] = reserved_time
            
        # SMS 대체 발송 설정
        if fallback_message:
            data["fallback_type"] = "SMS"
            data["fallback_msg"] = fallback_message
        
        try:
            # API 요청
            response = requests.post(
                f"{self.biz_url}/v2/sender/alimtalk",
                headers=self._get_headers(use_admin_key=True),
                json=data,
                timeout=10
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message_id": response_data.get("msgid"),
                    "status": "sent",
                    "sent_at": datetime.now()
                }
            else:
                logger.error(f"카카오 알림톡 발송 실패: {response_data}")
                return {
                    "success": False,
                    "error_code": response_data.get("code"),
                    "error_message": response_data.get("msg", "알림톡 발송 실패"),
                    "status": "failed"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"카카오 API 요청 오류: {str(e)}")
            return {
                "success": False,
                "error_code": "NETWORK_ERROR",
                "error_message": f"네트워크 오류: {str(e)}",
                "status": "failed"
            }
        except Exception as e:
            logger.error(f"알림톡 발송 중 오류: {str(e)}")
            return {
                "success": False,
                "error_code": "UNKNOWN_ERROR",
                "error_message": f"알 수 없는 오류: {str(e)}",
                "status": "failed"
            }
    
    def get_template_list(self) -> List[Dict]:
        """승인된 템플릿 목록 조회"""
        try:
            response = requests.get(
                f"{self.biz_url}/v2/sender/alimtalk/template/list",
                headers=self._get_headers(use_admin_key=True),
                params={
                    "sender_key": self.sender_key,
                    "status": "APR"  # 승인된 템플릿만
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("templates", [])
            else:
                logger.error(f"템플릿 목록 조회 실패: {response.json()}")
                return []
                
        except Exception as e:
            logger.error(f"템플릿 목록 조회 중 오류: {str(e)}")
            return []
    
    def get_message_result(self, message_id: str) -> Dict:
        """발송 결과 조회"""
        try:
            response = requests.get(
                f"{self.biz_url}/v2/sender/alimtalk/result",
                headers=self._get_headers(use_admin_key=True),
                params={
                    "msgid": message_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": result.get("status"),
                    "delivered_at": result.get("delivered_time"),
                    "read_at": result.get("read_time"),
                    "result_code": result.get("result_code"),
                    "result_message": result.get("result_msg")
                }
            else:
                return {
                    "status": "unknown",
                    "error": response.json()
                }
                
        except Exception as e:
            logger.error(f"발송 결과 조회 중 오류: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

class KakaoMessageBuilder:
    """카카오톡 메시지 템플릿 빌더"""
    
    @staticmethod
    def build_reservation_confirmation(
        customer_name: str,
        reservation_datetime: str,
        service_name: str,
        staff_name: str,
        center_address: str = "서울시 강남구 테헤란로 123",
        center_phone: str = "02-1234-5678"
    ) -> Dict[str, str]:
        """예약 확인 메시지 변수 생성"""
        return {
            "고객명": customer_name,
            "예약일시": reservation_datetime,
            "서비스명": service_name,
            "담당자명": staff_name,
            "센터주소": center_address,
            "센터전화번호": center_phone
        }
    
    @staticmethod
    def build_reminder(
        customer_name: str,
        reservation_datetime: str,
        service_name: str,
        center_phone: str = "02-1234-5678"
    ) -> Dict[str, str]:
        """예약 리마인더 메시지 변수 생성"""
        return {
            "고객명": customer_name,
            "예약일시": reservation_datetime,
            "서비스명": service_name,
            "센터전화번호": center_phone
        }
    
    @staticmethod
    def build_cancellation(
        customer_name: str,
        reservation_datetime: str,
        service_name: str,
        cancel_reason: str,
        center_phone: str = "02-1234-5678"
    ) -> Dict[str, str]:
        """예약 취소 메시지 변수 생성"""
        return {
            "고객명": customer_name,
            "예약일시": reservation_datetime,
            "서비스명": service_name,
            "취소사유": cancel_reason,
            "센터전화번호": center_phone
        }
    
    @staticmethod
    def build_change_notification(
        customer_name: str,
        old_datetime: str,
        new_datetime: str,
        service_name: str,
        center_phone: str = "02-1234-5678"
    ) -> Dict[str, str]:
        """예약 변경 메시지 변수 생성"""
        return {
            "고객명": customer_name,
            "기존일시": old_datetime,
            "변경일시": new_datetime,
            "서비스명": service_name,
            "센터전화번호": center_phone
        }

# 싱글톤 인스턴스
kakao_service = KakaoAlimtalkService()
message_builder = KakaoMessageBuilder()