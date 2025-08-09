import requests
import json
from typing import Dict, Optional, List, Union
from datetime import datetime
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class AligoSMSService:
    """알리고 SMS 발송 서비스"""
    
    def __init__(self):
        self.base_url = "https://apis.aligo.in"
        self.api_key = settings.ALIGO_API_KEY
        self.user_id = settings.ALIGO_USER_ID
        self.sender = settings.ALIGO_SENDER
        
    def send_sms(
        self,
        receiver: Union[str, List[str]],
        message: str,
        title: Optional[str] = None,
        testmode_yn: str = "N"
    ) -> Dict:
        """
        SMS/LMS 발송
        
        Args:
            receiver: 수신자 전화번호 (단일 또는 리스트)
            message: 메시지 내용
            title: LMS 제목 (90자 이상 시 자동 LMS 발송)
            testmode_yn: 테스트 모드 여부 (Y/N)
            
        Returns:
            발송 결과 딕셔너리
        """
        
        # 수신자 처리 (리스트인 경우 콤마로 구분)
        if isinstance(receiver, list):
            receiver_str = ",".join([r.replace("-", "") for r in receiver])
            receiver_cnt = len(receiver)
        else:
            receiver_str = receiver.replace("-", "")
            receiver_cnt = 1
            
        # 메시지 타입 자동 결정 (90자 기준)
        msg_type = "LMS" if len(message) > 90 else "SMS"
        
        # 요청 데이터
        data = {
            "key": self.api_key,
            "user_id": self.user_id,
            "sender": self.sender.replace("-", ""),
            "receiver": receiver_str,
            "msg": message,
            "msg_type": msg_type,
            "testmode_yn": testmode_yn
        }
        
        # LMS인 경우 제목 추가
        if msg_type == "LMS" and title:
            data["title"] = title
        elif msg_type == "LMS" and not title:
            data["title"] = "[AIBIO 센터]"
            
        try:
            response = requests.post(
                f"{self.base_url}/send/",
                data=data,
                timeout=10
            )
            
            result = response.json()
            
            if result.get("result_code") == "1":
                return {
                    "success": True,
                    "message_id": result.get("msg_id"),
                    "success_cnt": result.get("success_cnt", receiver_cnt),
                    "error_cnt": result.get("error_cnt", 0),
                    "msg_type": result.get("msg_type", msg_type)
                }
            else:
                logger.error(f"알리고 SMS 발송 실패: {result}")
                return {
                    "success": False,
                    "error_code": result.get("result_code"),
                    "error_message": result.get("message", "SMS 발송 실패")
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"알리고 API 요청 오류: {str(e)}")
            return {
                "success": False,
                "error_code": "NETWORK_ERROR",
                "error_message": f"네트워크 오류: {str(e)}"
            }
        except Exception as e:
            logger.error(f"SMS 발송 중 오류: {str(e)}")
            return {
                "success": False,
                "error_code": "UNKNOWN_ERROR",
                "error_message": f"알 수 없는 오류: {str(e)}"
            }
    
    def send_mass(
        self,
        receivers: List[Dict[str, str]],
        testmode_yn: str = "N"
    ) -> Dict:
        """
        대량 SMS 발송 (개별 메시지)
        
        Args:
            receivers: [{"phone": "010-1234-5678", "message": "안녕하세요", "name": "홍길동"}]
            testmode_yn: 테스트 모드 여부
            
        Returns:
            발송 결과
        """
        
        # 수신자 데이터 포맷팅
        rec_data = []
        for idx, rec in enumerate(receivers):
            rec_data.append({
                "r": rec["phone"].replace("-", ""),
                "c": rec["message"],
                "n": rec.get("name", "")
            })
            
        data = {
            "key": self.api_key,
            "user_id": self.user_id,
            "sender": self.sender.replace("-", ""),
            "rec": json.dumps(rec_data),
            "msg_type": "SMS",  # 대량 발송은 기본 SMS
            "testmode_yn": testmode_yn
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/send_mass/",
                data=data,
                timeout=30
            )
            
            result = response.json()
            
            if result.get("result_code") == "1":
                return {
                    "success": True,
                    "message_id": result.get("msg_id"),
                    "success_cnt": result.get("success_cnt", len(receivers)),
                    "error_cnt": result.get("error_cnt", 0)
                }
            else:
                return {
                    "success": False,
                    "error_code": result.get("result_code"),
                    "error_message": result.get("message", "대량 SMS 발송 실패")
                }
                
        except Exception as e:
            logger.error(f"대량 SMS 발송 중 오류: {str(e)}")
            return {
                "success": False,
                "error_code": "UNKNOWN_ERROR",
                "error_message": str(e)
            }
    
    def get_remain_sms(self) -> Dict:
        """SMS 잔여건수 조회"""
        
        data = {
            "key": self.api_key,
            "user_id": self.user_id
        }
        
        try:
            logger.info(f"알리고 잔여건수 조회 시작: user_id={self.user_id}")
            response = requests.post(
                f"{self.base_url}/remain/",
                data=data,
                timeout=10
            )
            
            result = response.json()
            logger.info(f"알리고 잔여건수 조회 응답: {result}")
            
            # 알리고 API 응답 구조 확인
            if isinstance(result, dict):
                # result_code가 문자열 "1"이거나 성공 메시지인 경우
                if result.get("result_code") == "1" or result.get("code") == "0" or "success" in str(result).lower():
                    return {
                        "success": True,
                        "sms_count": int(result.get("SMS_CNT", result.get("sms_cnt", 0))),
                        "lms_count": int(result.get("LMS_CNT", result.get("lms_cnt", 0))),
                        "mms_count": int(result.get("MMS_CNT", result.get("mms_cnt", 0)))
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("message", result.get("msg", "잔여건수 조회 실패"))
                    }
            else:
                # 응답이 딕셔너리가 아닌 경우
                return {
                    "success": False,
                    "error": f"예상치 못한 응답 형식: {type(result)}"
                }
                
        except Exception as e:
            logger.error(f"잔여건수 조회 중 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_sent_list(
        self,
        page: int = 1,
        page_size: int = 30,
        start_date: Optional[str] = None,
        limit_day: int = 7
    ) -> Dict:
        """발송 이력 조회"""
        
        data = {
            "key": self.api_key,
            "user_id": self.user_id,
            "page": page,
            "page_size": page_size,
            "limit_day": limit_day
        }
        
        if start_date:
            data["start_date"] = start_date
            
        try:
            response = requests.post(
                f"{self.base_url}/list/",
                data=data,
                timeout=10
            )
            
            result = response.json()
            
            if result.get("result_code") == "1":
                return {
                    "success": True,
                    "list": result.get("list", []),
                    "total_count": result.get("total_count", 0),
                    "current_page": result.get("currentPage", page)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "발송 이력 조회 실패")
                }
                
        except Exception as e:
            logger.error(f"발송 이력 조회 중 오류: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


class SMSMessageTemplates:
    """SMS 메시지 템플릿"""
    
    @staticmethod
    def reservation_confirmation(
        customer_name: str,
        reservation_date: str,
        reservation_time: str,
        service_name: str,
        staff_name: Optional[str] = None
    ) -> str:
        """예약 확인 메시지"""
        staff_info = f"\n담당: {staff_name}" if staff_name else ""
        return f"""[AIBIO 센터] 예약 확인
{customer_name}님, 예약이 확정되었습니다.

▶ 일시: {reservation_date} {reservation_time}
▶ 서비스: {service_name}{staff_info}

변경/취소: 02-2039-2783"""

    @staticmethod
    def reservation_reminder(
        customer_name: str,
        reservation_date: str,
        reservation_time: str,
        service_name: str
    ) -> str:
        """예약 리마인더 (D-1)"""
        return f"""[AIBIO 센터] 예약 알림
{customer_name}님, 내일 예약이 있습니다.

▶ 일시: {reservation_date} {reservation_time}
▶ 서비스: {service_name}

문의: 02-2039-2783"""

    @staticmethod
    def reservation_cancelled(
        customer_name: str,
        reservation_date: str,
        reservation_time: str,
        service_name: str
    ) -> str:
        """예약 취소 메시지"""
        return f"""[AIBIO 센터] 예약 취소
{customer_name}님의 예약이 취소되었습니다.

▶ 취소된 예약
- 일시: {reservation_date} {reservation_time}
- 서비스: {service_name}

재예약: 02-2039-2783"""

    @staticmethod
    def service_completed(
        customer_name: str,
        service_name: str
    ) -> str:
        """서비스 완료 메시지"""
        return f"""[AIBIO 센터]
{customer_name}님, 오늘 {service_name} 서비스는 만족스러우셨나요?

다음 방문 시 더 나은 서비스로 보답하겠습니다.

예약: 02-2039-2783"""

    @staticmethod
    def birthday_greeting(customer_name: str) -> str:
        """생일 축하 메시지"""
        return f"""[AIBIO 센터] 생일 축하
{customer_name}님, 생일을 진심으로 축하드립니다! 🎂

특별한 날, 건강한 하루 보내세요.
생일 고객 할인 혜택도 준비되어 있습니다.

문의: 02-2039-2783"""

    @staticmethod
    def dormant_customer_reactivation(
        customer_name: str,
        last_visit_date: str
    ) -> str:
        """휴면 고객 재방문 유도"""
        return f"""[AIBIO 센터]
{customer_name}님, 오랜만입니다.
마지막 방문({last_visit_date}) 이후 새로운 서비스가 추가되었습니다.

재방문 고객 할인 혜택을 확인해보세요.

예약: 02-2039-2783"""

    @staticmethod
    def promotion(
        customer_name: str,
        promotion_title: str,
        promotion_content: str
    ) -> str:
        """프로모션 메시지"""
        return f"""[AIBIO 센터] {promotion_title}
{customer_name}님께 특별한 혜택을 알려드립니다.

{promotion_content}

예약: 02-2039-2783"""


# 싱글톤 인스턴스
aligo_service = AligoSMSService()
sms_templates = SMSMessageTemplates()