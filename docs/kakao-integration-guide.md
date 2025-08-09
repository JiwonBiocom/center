# 카카오톡 예약 알림 연동 가이드

## 1. 개요

AIBIO Center 관리 시스템에서 고객에게 예약 확인 메시지를 카카오톡으로 발송하기 위한 API 연동 가이드입니다.

## 2. 카카오톡 비즈니스 메시지 옵션

### 2.1 카카오톡 채널 (구 플러스친구)
- **특징**: 무료로 시작 가능, 광고성 메시지 발송
- **제한사항**: 친구 추가한 사용자에게만 발송 가능
- **용도**: 마케팅, 프로모션 메시지

### 2.2 카카오 알림톡 ⭐️ (권장)
- **특징**: 정보성 메시지 발송, 높은 도달률
- **장점**: 
  - 친구 추가 없이 발송 가능
  - 24시간 발송 가능
  - 발송 실패 시 SMS 대체 발송 가능
- **비용**: 건당 약 10-20원 (대량 계약 시 할인)
- **용도**: 예약 확인, 변경 알림, 리마인더 등

### 2.3 카카오 친구톡
- **특징**: 광고성 메시지, 이미지/링크 포함 가능
- **제한사항**: 친구 추가 필요, 발송 시간 제한 (08:00-20:30)
- **용도**: 프로모션, 이벤트 안내

## 3. 알림톡 연동 프로세스

### 3.1 사전 준비사항
```
1. 사업자 등록증
2. 카카오톡 채널 개설
3. 발신 프로필 등록
4. 템플릿 검수 및 승인 (1-3일 소요)
```

### 3.2 연동 방식 선택

#### 방식 1: 직접 연동
- **장점**: 수수료 없음, 완전한 제어
- **단점**: 개발 복잡도 높음, 유지보수 필요
- **필요 작업**:
  - 카카오 비즈니스 계정 생성
  - 발신 프로필 등록
  - 템플릿 등록 및 검수
  - API 인증 구현

#### 방식 2: 대행사 API 활용 ⭐️ (권장)
- **장점**: 빠른 구현, 통합 관리, 기술 지원
- **단점**: 건당 수수료 추가 (1-3원)
- **주요 업체**:
  - 알리고 (Aligo)
  - 비즈엠 (BizM)
  - 솔라피 (Solapi)
  - NHN Toast

## 4. 알림톡 템플릿 예시

### 4.1 예약 확인 템플릿
```
[AIBIO Center 예약 확인]

안녕하세요, #{고객명}님
예약이 확인되었습니다.

▶ 예약 정보
- 일시: #{예약일시}
- 서비스: #{서비스명}
- 담당자: #{담당자명}

▶ 센터 위치
#{센터주소}

예약 변경/취소는 #{센터전화번호}로 연락 주세요.

감사합니다.
```

### 4.2 예약 리마인더 템플릿
```
[AIBIO Center 예약 알림]

#{고객명}님, 내일 예약을 잊지 마세요!

▶ 예약 정보
- 일시: #{예약일시}
- 서비스: #{서비스명}

준비물이 필요한 경우 미리 안내드립니다.
문의: #{센터전화번호}
```

### 4.3 예약 변경 알림 템플릿
```
[AIBIO Center 예약 변경]

#{고객명}님의 예약이 변경되었습니다.

▶ 변경된 예약 정보
- 기존: #{기존일시}
- 변경: #{변경일시}
- 서비스: #{서비스명}

문의사항은 #{센터전화번호}로 연락 주세요.
```

## 5. 솔라피(Solapi) API 연동 예시

### 5.1 설치
```bash
pip install solapi
```

### 5.2 Python 구현 예시
```python
from solapi import SolAPI

class KakaoNotificationService:
    def __init__(self, api_key: str, api_secret: str, sender_key: str):
        self.client = SolAPI(api_key, api_secret)
        self.sender_key = sender_key
        self.sender_number = "0212345678"  # 발신번호
    
    def send_reservation_confirmation(
        self, 
        phone: str, 
        customer_name: str,
        reservation_datetime: str,
        service_name: str,
        staff_name: str
    ):
        """예약 확인 알림톡 발송"""
        
        # 템플릿 변수 설정
        variables = {
            "고객명": customer_name,
            "예약일시": reservation_datetime,
            "서비스명": service_name,
            "담당자명": staff_name,
            "센터주소": "서울시 강남구 테헤란로 123",
            "센터전화번호": "02-1234-5678"
        }
        
        # 메시지 발송
        try:
            response = self.client.send_message(
                to=phone,
                from_number=self.sender_number,
                type="ATA",  # 알림톡
                template_code="RESERVATION_CONFIRM_001",  # 승인된 템플릿 코드
                sender_key=self.sender_key,
                variables=variables,
                # 알림톡 실패 시 SMS 대체 발송
                fallback_message=f"{customer_name}님, AIBIO Center 예약이 확인되었습니다. {reservation_datetime}",
                fallback_type="SMS"
            )
            
            return {
                "success": True,
                "message_id": response.get("messageId"),
                "status": response.get("status")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_reminder(self, phone: str, customer_name: str, reservation_datetime: str, service_name: str):
        """예약 리마인더 발송"""
        # 구현 생략...
        pass
```

### 5.3 FastAPI 엔드포인트 예시
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/reservations/{reservation_id}/send-confirmation")
async def send_reservation_confirmation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """예약 확인 카카오톡 발송"""
    
    # 예약 정보 조회
    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id
    ).first()
    
    if not reservation:
        raise HTTPException(status_code=404, detail="예약을 찾을 수 없습니다")
    
    # 카카오톡 발송
    result = kakao_service.send_reservation_confirmation(
        phone=reservation.customer.phone,
        customer_name=reservation.customer.name,
        reservation_datetime=reservation.datetime.strftime("%Y년 %m월 %d일 %H:%M"),
        service_name=reservation.service.name,
        staff_name=reservation.staff.name
    )
    
    # 발송 이력 저장
    notification_log = NotificationLog(
        type="kakao_alimtalk",
        reservation_id=reservation_id,
        customer_id=reservation.customer_id,
        template_code="RESERVATION_CONFIRM_001",
        status="success" if result["success"] else "failed",
        message_id=result.get("message_id"),
        sent_at=datetime.now(),
        error_message=result.get("error")
    )
    db.add(notification_log)
    db.commit()
    
    return result

@router.post("/reservations/send-reminders")
async def send_tomorrow_reminders(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """내일 예약 리마인더 일괄 발송"""
    
    # 내일 예약 조회
    tomorrow = datetime.now().date() + timedelta(days=1)
    reservations = db.query(Reservation).filter(
        func.date(Reservation.datetime) == tomorrow,
        Reservation.status == "confirmed",
        Reservation.reminder_sent == False
    ).all()
    
    results = []
    for reservation in reservations:
        # 각 예약에 대해 리마인더 발송
        # ... 구현
        pass
    
    return {"sent_count": len(results), "results": results}
```

## 6. 비용 예상

### 6.1 월간 예상 비용 (1,000건 기준)
```
- 알림톡 발송비: 15원 × 1,000건 = 15,000원
- 대행사 수수료: 2원 × 1,000건 = 2,000원
- SMS 대체발송: 20원 × 50건 (5% 실패) = 1,000원
- 총 비용: 약 18,000원/월
```

### 6.2 연간 계약 시 할인율
- 월 1만건 이상: 20-30% 할인
- 월 10만건 이상: 40-50% 할인

## 7. 구현 로드맵

### Phase 1: 기본 구현 (2주)
- [ ] 대행사 선정 및 계약
- [ ] 카카오톡 채널 개설
- [ ] 발신 프로필 등록
- [ ] 기본 템플릿 3종 등록
- [ ] API 연동 개발
- [ ] 테스트 환경 구축

### Phase 2: 고도화 (2주)
- [ ] 예약 시스템과 통합
- [ ] 자동 발송 스케줄러 구현
- [ ] 발송 이력 관리
- [ ] 실패 처리 및 재발송
- [ ] 통계 및 리포트

### Phase 3: 확장 (선택사항)
- [ ] 마케팅 메시지 발송 (친구톡)
- [ ] 고객 맞춤형 메시지
- [ ] A/B 테스트
- [ ] ROI 분석

## 8. 주의사항

1. **개인정보보호**
   - 고객 동의 필수
   - 수신거부 처리 구현
   - 발송 이력 보관 (최소 1년)

2. **템플릿 가이드라인**
   - 광고성 문구 금지
   - 변수명 정확히 사용
   - 검수 기준 준수

3. **발송 제한**
   - 동일 번호 일일 발송 제한
   - 야간 발송 시 주의
   - 스팸 방지 정책 준수

## 9. 참고 자료

- [카카오 비즈니스 공식 가이드](https://business.kakao.com/info/bizmessage/)
- [솔라피 API 문서](https://docs.solapi.com/)
- [알리고 API 문서](https://smartsms.aligo.in/admin/api/spec.html)
- [정보통신망법 광고 전송 가이드](https://spam.kisa.or.kr/)

## 10. 결론

카카오톡 알림톡은 예약 관리 시스템에 매우 효과적인 알림 수단입니다. 
초기 구축 비용은 있지만, 높은 도달률과 고객 만족도를 고려하면 투자 가치가 충분합니다.

대행사 API를 활용하면 2-3주 내에 구현 가능하며, 
월 18,000원 정도의 비용으로 1,000건의 알림을 발송할 수 있습니다.