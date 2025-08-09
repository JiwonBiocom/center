#!/usr/bin/env python3
"""
키트 고객 데이터 마이그레이션 스크립트
"""

import sys
import os
import csv
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.kit import KitManagement, KitType
from models.customer import Customer
from core.database import SessionLocal

def parse_date(date_str):
    """날짜 문자열을 date 객체로 변환"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        # 2025-02-27 형식
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
    except:
        try:
            # 다른 형식 시도
            return datetime.strptime(date_str.strip(), '%Y/%m/%d').date()
        except:
            print(f"날짜 파싱 실패: {date_str}")
            return None

def ensure_kit_types(db):
    """키트 타입이 없으면 생성"""
    kit_types = [
        {'name': '유기산', 'code': 'ORGANIC_ACID', 'price': 200000},
        {'name': '음식물과민증', 'code': 'FOOD_SENSITIVITY', 'price': 250000},
        {'name': '장내미생물', 'code': 'GUT_MICROBIOME', 'price': 300000},
        {'name': '유전자검사', 'code': 'GENETIC_TEST', 'price': 400000}
    ]
    
    for kt_data in kit_types:
        existing = db.query(KitType).filter_by(code=kt_data['code']).first()
        if not existing:
            new_kit_type = KitType(
                name=kt_data['name'],
                code=kt_data['code'],
                price=kt_data['price'],
                description=f"{kt_data['name']} 검사 키트",
                is_active=True
            )
            db.add(new_kit_type)
            print(f"키트 타입 추가: {kt_data['name']}")
    
    db.commit()

def import_kit_data(csv_file):
    """CSV 파일에서 키트 데이터 가져오기"""
    db = SessionLocal()
    
    try:
        # 키트 타입 확인 및 생성
        ensure_kit_types(db)
        
        # CSV 파일 읽기
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            success_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    customer_name = row.get('고객명', '').strip()
                    kit_type_name = row.get('키트', '').strip()
                    serial_number = row.get('시리얼번호', '').strip()
                    received_date = parse_date(row.get('키트수령일', ''))
                    result_received_date = parse_date(row.get('결과지 수령일', ''))
                    result_delivered_date = parse_date(row.get('결과지 전달일', ''))
                    
                    if not customer_name or not kit_type_name or not serial_number:
                        print(f"필수 정보 누락: {row}")
                        error_count += 1
                        continue
                    
                    # 고객 찾기
                    customer = db.query(Customer).filter_by(name=customer_name).first()
                    if not customer:
                        print(f"고객 찾을 수 없음: {customer_name}")
                        # 새 고객 생성
                        customer = Customer(
                            name=customer_name,
                            phone='010-0000-0000',  # 기본값
                            first_visit_date=datetime.now().date(),
                            customer_type='키트고객',
                            status='active'
                        )
                        db.add(customer)
                        db.flush()
                        print(f"새 고객 생성: {customer_name}")
                    
                    # 키트 타입 찾기
                    kit_type = db.query(KitType).filter_by(name=kit_type_name).first()
                    if not kit_type:
                        print(f"키트 타입 찾을 수 없음: {kit_type_name}")
                        error_count += 1
                        continue
                    
                    # 중복 체크 - 동일한 시리얼 번호가 여러 고객에게 사용될 수 있음
                    existing_kit = db.query(KitManagement).filter_by(
                        serial_number=serial_number,
                        customer_id=customer.customer_id
                    ).first()
                    
                    if existing_kit:
                        print(f"이미 존재하는 키트: {customer_name} - {serial_number}")
                        # 업데이트
                        existing_kit.kit_type = kit_type_name
                        existing_kit.kit_type_id = kit_type.kit_type_id
                        if received_date:
                            existing_kit.received_date = received_date
                        if result_received_date:
                            existing_kit.result_received_date = result_received_date
                        if result_delivered_date:
                            existing_kit.result_delivered_date = result_delivered_date
                        print(f"키트 정보 업데이트: {serial_number}")
                    else:
                        # 시리얼 번호 중복 체크 (다른 고객)
                        other_kit = db.query(KitManagement).filter_by(serial_number=serial_number).first()
                        if other_kit:
                            # 시리얼 번호에 고객명 추가하여 고유하게 만들기
                            unique_serial = f"{serial_number}_{customer_name}"
                            print(f"시리얼 번호 중복, 고유 번호 생성: {unique_serial}")
                            serial_number = unique_serial
                        
                        # 새 키트 추가
                        new_kit = KitManagement(
                            customer_id=customer.customer_id,
                            kit_type=kit_type_name,
                            kit_type_id=kit_type.kit_type_id,
                            serial_number=serial_number,
                            received_date=received_date,
                            result_received_date=result_received_date,
                            result_delivered_date=result_delivered_date
                        )
                        db.add(new_kit)
                        db.flush()  # 즉시 DB에 반영
                        print(f"새 키트 추가: {customer_name} - {kit_type_name} - {serial_number}")
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"행 처리 중 오류: {e}")
                    print(f"문제 행: {row}")
                    error_count += 1
                    continue
            
            db.commit()
            print(f"\n완료: 성공 {success_count}건, 실패 {error_count}건")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

def verify_import(db):
    """가져온 데이터 확인"""
    total_kits = db.query(KitManagement).count()
    print(f"\n총 키트 수: {total_kits}")
    
    # 키트 타입별 통계
    kit_types = db.query(KitType).all()
    for kt in kit_types:
        count = db.query(KitManagement).filter_by(kit_type_id=kt.kit_type_id).count()
        print(f"{kt.name}: {count}개")
    
    # 최근 5개 키트
    recent_kits = db.query(KitManagement).order_by(KitManagement.created_at.desc()).limit(5).all()
    print("\n최근 추가된 키트:")
    for kit in recent_kits:
        print(f"- {kit.customer.name if kit.customer else 'Unknown'}: {kit.kit_type} ({kit.serial_number})")

def main():
    csv_file = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장_키트고객.csv'
    
    if not os.path.exists(csv_file):
        print(f"파일을 찾을 수 없습니다: {csv_file}")
        return
    
    print("키트 고객 데이터 가져오기 시작...")
    import_kit_data(csv_file)
    
    # 결과 확인
    db = SessionLocal()
    verify_import(db)
    db.close()

if __name__ == "__main__":
    main()