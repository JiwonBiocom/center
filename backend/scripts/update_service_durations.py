"""
서비스별 소요시간 업데이트 스크립트
- 브레인피드백: 45분
- 펄스: 30분
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.service import ServiceType

def update_service_durations():
    """서비스별 소요시간 업데이트"""
    db = SessionLocal()

    try:
        # 브레인피드백 서비스 업데이트 (45분)
        brain_feedback = db.query(ServiceType).filter(
            ServiceType.service_name == "브레인피드백"
        ).first()

        if brain_feedback:
            print(f"브레인피드백 소요시간 변경: {brain_feedback.default_duration}분 → 45분")
            brain_feedback.default_duration = 45
        else:
            print("❌ 브레인피드백 서비스를 찾을 수 없습니다.")

        # 펄스 서비스 업데이트 (30분)
        pulse = db.query(ServiceType).filter(
            ServiceType.service_name == "펄스"
        ).first()

        if pulse:
            print(f"펄스 소요시간 변경: {pulse.default_duration}분 → 30분")
            pulse.default_duration = 30
        else:
            print("❌ 펄스 서비스를 찾을 수 없습니다.")

        db.commit()
        print("\n✅ 서비스 소요시간 업데이트 완료")

        # 전체 서비스 목록 확인
        print("\n📋 전체 서비스 소요시간:")
        all_services = db.query(ServiceType).order_by(ServiceType.service_name).all()
        for svc in all_services:
            print(f"- {svc.service_name}: {svc.default_duration}분")

    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 AIBIO Center 서비스 소요시간 업데이트")
    print("=" * 50)
    update_service_durations()
