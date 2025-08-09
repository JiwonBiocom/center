"""
AIBIO Center 서비스 가격 업데이트 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.service import ServiceType as ServiceTypeModel

def update_service_prices():
    """서비스 타입별 가격 정보 업데이트"""
    db = SessionLocal()
    
    # 가격표 기반 서비스 정보
    services = [
        {
            "service_name": "브레인",
            "description": "뇌파 측정 및 분석, 맞춤형 뉴로피드백 트레이닝",
            "default_duration": 60,
            "default_price": 150000,
            "category": "케어"
        },
        {
            "service_name": "펄스",
            "description": "전신 펄스 자극 치료, 혈액순환 개선",
            "default_duration": 45,
            "default_price": 120000,
            "category": "케어"
        },
        {
            "service_name": "레드",
            "description": "적외선 광선 치료, 세포 재생 촉진",
            "default_duration": 30,
            "default_price": 100000,
            "category": "케어"
        },
        {
            "service_name": "림프",
            "description": "림프 순환 마사지, 독소 배출 촉진",
            "default_duration": 90,
            "default_price": 180000,
            "category": "케어"
        },
        {
            "service_name": "AI바이크&레드엔바이브",
            "description": "AI 기반 운동 프로그램 + 적외선 치료",
            "default_duration": 40,
            "default_price": 80000,
            "category": "운동"
        },
        {
            "service_name": "상담",
            "description": "건강 상태 종합 분석 및 케어 플랜 수립",
            "default_duration": 60,
            "default_price": 200000,  # 초기 상담 기준
            "category": "상담"
        },
        {
            "service_name": "정기상담",
            "description": "진행 상황 모니터링 및 플랜 조정",
            "default_duration": 30,
            "default_price": 100000,
            "category": "상담"
        }
    ]
    
    try:
        # 기존 서비스 타입 확인
        existing_count = db.query(ServiceTypeModel).count()
        print(f"기존 서비스 타입 수: {existing_count}개")
        
        # 서비스 정보 업데이트 또는 추가
        updated_count = 0
        added_count = 0
        
        for svc_data in services:
            # 기존 서비스 확인
            existing = db.query(ServiceTypeModel).filter(
                ServiceTypeModel.service_name == svc_data["service_name"]
            ).first()
            
            if existing:
                # 업데이트
                existing.description = svc_data["description"]
                existing.default_duration = svc_data["default_duration"]
                existing.default_price = svc_data["default_price"]
                existing.category = svc_data["category"]
                existing.is_active = True
                updated_count += 1
                print(f"업데이트: {svc_data['service_name']} - {svc_data['default_price']:,}원")
            else:
                # 새로 추가
                new_service = ServiceTypeModel(
                    service_name=svc_data["service_name"],
                    description=svc_data["description"],
                    default_duration=svc_data["default_duration"],
                    default_price=svc_data["default_price"],
                    category=svc_data["category"],
                    is_active=True
                )
                db.add(new_service)
                added_count += 1
                print(f"추가됨: {svc_data['service_name']} - {svc_data['default_price']:,}원")
        
        db.commit()
        print(f"\n✅ {added_count}개 추가, {updated_count}개 업데이트 완료")
        
        # 전체 서비스 목록 출력
        print("\n💆 전체 서비스 목록:")
        all_services = db.query(ServiceTypeModel).filter(
            ServiceTypeModel.is_active == True
        ).order_by(ServiceTypeModel.category).all()
        
        current_category = None
        for svc in all_services:
            if svc.category != current_category:
                current_category = svc.category
                print(f"\n[{current_category}]")
            print(f"- {svc.service_name}: {svc.default_price:,}원 ({svc.default_duration}분)")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 AIBIO Center 서비스 가격 업데이트")
    print("=" * 50)
    update_service_prices()