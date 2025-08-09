#!/usr/bin/env python3
"""
AIBIO 센터 가격표 업데이트 스크립트
2025년 6월 최신 가격표 반영
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.package import Package
from core.database import SessionLocal
import json

def backup_current_packages(db):
    """현재 패키지 데이터를 백업"""
    print("현재 패키지 데이터 백업 중...")
    packages = db.query(Package).all()
    backup_data = []
    
    for pkg in packages:
        backup_data.append({
            'package_id': pkg.package_id,
            'package_name': pkg.package_name,
            'total_sessions': pkg.total_sessions,
            'price': float(pkg.price) if pkg.price else 0,
            'valid_days': pkg.valid_days,
            'description': pkg.description,
            'is_active': pkg.is_active
        })
    
    # 백업 파일 저장
    backup_file = f"packages_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f"백업 완료: {backup_file}")
    return backup_file

def update_packages(db):
    """새로운 가격표에 맞게 패키지 업데이트"""
    
    # 기존 패키지 비활성화
    db.query(Package).update({'is_active': False})
    db.commit()
    
    # 새로운 패키지 데이터
    new_packages = [
        # 개별 세션 패키지 (집중 관리 패키지)
        {
            'package_name': '펄스 10회',
            'total_sessions': 10,
            'price': Decimal('700000'),
            'valid_days': 180,  # 6개월
            'description': '펄스 10회 패키지 (회당 70,000원)',
            'is_active': True
        },
        {
            'package_name': '펄스 20회',
            'total_sessions': 20,
            'price': Decimal('1200000'),
            'valid_days': 365,  # 1년
            'description': '펄스 20회 패키지 (회당 60,000원)',
            'is_active': True
        },
        {
            'package_name': '펄스 30회',
            'total_sessions': 30,
            'price': Decimal('1500000'),
            'valid_days': 365,  # 1년
            'description': '펄스 30회 이상 패키지 (회당 50,000원)',
            'is_active': True
        },
        {
            'package_name': '브레인 10회',
            'total_sessions': 10,
            'price': Decimal('800000'),
            'valid_days': 180,  # 6개월
            'description': '브레인 10회 패키지 (회당 80,000원)',
            'is_active': True
        },
        {
            'package_name': '브레인 20회',
            'total_sessions': 20,
            'price': Decimal('1400000'),
            'valid_days': 365,  # 1년
            'description': '브레인 20회 패키지 (회당 70,000원)',
            'is_active': True
        },
        {
            'package_name': '브레인 30회',
            'total_sessions': 30,
            'price': Decimal('1800000'),
            'valid_days': 365,  # 1년
            'description': '브레인 30회 이상 패키지 (회당 60,000원)',
            'is_active': True
        },
        {
            'package_name': '림프 10회',
            'total_sessions': 10,
            'price': Decimal('700000'),
            'valid_days': 180,  # 6개월
            'description': '림프 10회 패키지 (회당 70,000원)',
            'is_active': True
        },
        {
            'package_name': '림프 20회',
            'total_sessions': 20,
            'price': Decimal('1200000'),
            'valid_days': 365,  # 1년
            'description': '림프 20회 패키지 (회당 60,000원)',
            'is_active': True
        },
        {
            'package_name': '림프 30회',
            'total_sessions': 30,
            'price': Decimal('1500000'),
            'valid_days': 365,  # 1년
            'description': '림프 30회 이상 패키지 (회당 50,000원)',
            'is_active': True
        },
        {
            'package_name': '레드 10회',
            'total_sessions': 10,
            'price': Decimal('500000'),
            'valid_days': 180,  # 6개월
            'description': '레드 10회 패키지 (회당 50,000원)',
            'is_active': True
        },
        {
            'package_name': '레드 20회',
            'total_sessions': 20,
            'price': Decimal('900000'),
            'valid_days': 365,  # 1년
            'description': '레드 20회 패키지 (회당 45,000원)',
            'is_active': True
        },
        {
            'package_name': '레드 30회',
            'total_sessions': 30,
            'price': Decimal('1200000'),
            'valid_days': 365,  # 1년
            'description': '레드 30회 이상 패키지 (회당 40,000원)',
            'is_active': True
        },
        
        # 종합 패키지 (종합 대사 기능 분석 1회 무료 포함)
        {
            'package_name': '대사개선 + 식욕조절',
            'total_sessions': 40,  # 펄스 20 + 브레인 20
            'price': Decimal('2340000'),  # 할인가
            'valid_days': 365,  # 1년
            'description': '펄스 20회 + 브레인 20회 + 종합대사기능분석 1회 무료\n대사 활성화로 체중 감량 촉진, 식욕 조절을 통한 건강한 다이어트 유지\n정가 2,600,000원 → 10% 할인',
            'is_active': True
        },
        {
            'package_name': '대사개선 + 붓기케어',
            'total_sessions': 40,  # 펄스 20 + 림프 20
            'price': Decimal('2160000'),  # 할인가
            'valid_days': 365,  # 1년
            'description': '펄스 20회 + 림프 20회 + 종합대사기능분석 1회 무료\n대사 촉진과 체액 순환 개선으로 붓기 완화, 림프 마사지로 독소 배출\n정가 2,400,000원 → 10% 할인',
            'is_active': True
        },
        {
            'package_name': '대사개선 + 화이트닝',
            'total_sessions': 40,  # 펄스 20 + 레드 20
            'price': Decimal('1890000'),  # 할인가
            'valid_days': 365,  # 1년
            'description': '펄스 20회 + 레드 20회 + 종합대사기능분석 1회 무료\n신진대사 촉진으로 체중 관리, 레드 라이트를 통한 피부톤 개선\n정가 2,100,000원 → 10% 할인',
            'is_active': True
        },
        {
            'package_name': '올케어 40회',
            'total_sessions': 40,  # 각 10회씩
            'price': Decimal('2430000'),  # 할인가
            'valid_days': 180,  # 6개월
            'description': '펄스 10회 + 브레인 10회 + 림프 10회 + 레드 10회 + 종합대사기능분석 1회 무료\n주 3회(6세션): 1.5개월, 주 2회(4세션): 2.5개월 소요\n정가 2,700,000원 → 10% 할인',
            'is_active': True
        },
        {
            'package_name': '올케어 80회',
            'total_sessions': 80,  # 각 20회씩
            'price': Decimal('3990000'),  # 할인가
            'valid_days': 365,  # 1년
            'description': '펄스 20회 + 브레인 20회 + 림프 20회 + 레드 20회 + 종합대사기능분석 1회 무료\n주 3회(6세션): 3.5개월, 주 2회(4세션): 4.5개월 소요\n정가 4,700,000원 → 10% 할인',
            'is_active': True
        },
        {
            'package_name': '올케어 120회',
            'total_sessions': 120,  # 각 30회씩
            'price': Decimal('4980000'),  # 할인가
            'valid_days': 540,  # 1.5년
            'description': '펄스 30회 + 브레인 30회 + 림프 30회 + 레드 30회 + 종합대사기능분석 1회 무료\n주 3회(6세션): 4.5개월, 주 2회(4세션): 8개월 소요\n정가 6,000,000원 → 10% 할인',
            'is_active': True
        }
    ]
    
    # 새로운 패키지 추가
    for pkg_data in new_packages:
        # 이미 존재하는 패키지인지 확인
        existing = db.query(Package).filter_by(package_name=pkg_data['package_name']).first()
        
        if existing:
            # 기존 패키지 업데이트
            existing.total_sessions = pkg_data['total_sessions']
            existing.price = pkg_data['price']
            existing.valid_days = pkg_data['valid_days']
            existing.description = pkg_data['description']
            existing.is_active = pkg_data['is_active']
            print(f"업데이트: {pkg_data['package_name']}")
        else:
            # 새 패키지 생성
            new_package = Package(**pkg_data)
            db.add(new_package)
            print(f"추가: {pkg_data['package_name']}")
    
    db.commit()
    print("\n패키지 업데이트 완료!")

def verify_updates(db):
    """업데이트된 패키지 확인"""
    print("\n=== 활성화된 패키지 목록 ===")
    active_packages = db.query(Package).filter_by(is_active=True).order_by(Package.price).all()
    
    for pkg in active_packages:
        print(f"\n패키지명: {pkg.package_name}")
        print(f"가격: {int(pkg.price):,}원")
        print(f"총 세션수: {pkg.total_sessions}회")
        print(f"유효기간: {pkg.valid_days}일")
        if pkg.description:
            print(f"설명: {pkg.description[:50]}...")

def main():
    db = SessionLocal()
    
    try:
        print("AIBIO 센터 패키지 가격표 업데이트 시작...")
        
        # 1. 현재 데이터 백업
        backup_file = backup_current_packages(db)
        
        # 2. 패키지 업데이트
        response = input("\n패키지를 업데이트하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            update_packages(db)
            
            # 3. 업데이트 확인
            verify_updates(db)
        else:
            print("업데이트 취소됨")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()