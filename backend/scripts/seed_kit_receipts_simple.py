#!/usr/bin/env python3
"""
검사키트 수령 데이터를 간단하게 시드하는 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime
from core.database import engine
from models.customer_extended import KitReceipt
from models.customer import Customer
from sqlalchemy.orm import Session
from sqlalchemy import text
import re

def clean_phone_number(phone):
    """전화번호 정리"""
    if pd.isna(phone) or not phone:
        return None
    
    phone = str(phone).strip()
    phone = re.sub(r'[^\d]', '', phone)
    
    if len(phone) in [10, 11]:
        if len(phone) == 10:
            return f"010-{phone[3:7]}-{phone[7:]}"
        else:
            return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    
    return None

def parse_date(date_value):
    """엑셀 날짜 값을 파싱"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, pd.Timestamp):
        return date_value.date()
    
    if isinstance(date_value, str):
        try:
            return pd.to_datetime(date_value).date()
        except:
            return None
    
    return None

def get_or_create_customer(session, name, phone=None):
    """고객 찾기 또는 생성"""
    # 전화번호로 먼저 찾기
    if phone:
        customer = session.query(Customer).filter(Customer.phone == phone).first()
        if customer:
            return customer.customer_id
    
    # 이름으로 찾기
    customer = session.query(Customer).filter(Customer.name == name).first()
    if customer:
        return customer.customer_id
    
    # 새로 생성
    new_customer = Customer(name=name, phone=phone)
    session.add(new_customer)
    session.flush()  # ID 즉시 생성
    return new_customer.customer_id

def main():
    print("🚀 검사키트 수령 데이터 시드 시작...")
    
    # Excel 파일 읽기
    excel_path = "../backend/seed/kit_receipts.xlsx"
    df = pd.read_excel(excel_path)
    print(f"📊 총 {len(df)}개 행 발견")
    
    with Session(engine) as session:
        # 기존 데이터 삭제
        print("\n🧹 기존 데이터 정리 중...")
        session.execute(text("DELETE FROM kit_receipts"))
        session.commit()
        
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # 필수 필드 확인
                name = row.get('고객명', row.get('name'))
                if pd.isna(name) or not name:
                    continue
                
                # 전화번호 정리
                phone = clean_phone_number(row.get('연락처', row.get('phone')))
                
                # 고객 ID 찾기 또는 생성
                customer_id = get_or_create_customer(session, name, phone)
                
                # 키트 시리얼 번호
                serial = row.get('시리얼', row.get('kit_serial'))
                if serial:
                    serial = str(serial).strip()
                
                # 새 키트 수령 정보 생성
                kit_receipt = KitReceipt(
                    customer_id=customer_id,
                    name=str(name).strip(),
                    phone=phone,
                    kit_type=row.get('키트종류', row.get('kit_type', '장내미생물')),
                    kit_serial=serial,
                    received_date=parse_date(row.get('키트수령일', row.get('received_date'))),
                    result_date=parse_date(row.get('결과지수령일', row.get('result_date'))),
                    delivered_date=parse_date(row.get('결과지전달일', row.get('delivered_date'))),
                    status=row.get('상태', row.get('status', 'received')),
                    notes=row.get('비고', row.get('notes')) if pd.notna(row.get('비고', row.get('notes'))) else None
                )
                
                session.add(kit_receipt)
                success_count += 1
                
                # 진행 상황 표시
                if success_count % 10 == 0:
                    print(f"  처리 중... {success_count}개 완료")
                    session.commit()
                
            except Exception as e:
                error_count += 1
                print(f"❌ 행 {idx+2} 오류: {str(e)}")
                session.rollback()
                continue
        
        # 최종 커밋
        session.commit()
        
        # 결과 확인
        total_count = session.execute(text("SELECT COUNT(*) FROM kit_receipts")).scalar()
        
        print(f"\n✅ 검사키트 수령 데이터 시드 완료!")
        print(f"   - 성공: {success_count}개")
        print(f"   - 실패: {error_count}개")
        print(f"   - 전체 레코드: {total_count}개")
        
        # 샘플 데이터 확인
        samples = session.execute(text("""
            SELECT name, phone, kit_type, kit_serial, received_date 
            FROM kit_receipts 
            ORDER BY kit_receipt_id DESC 
            LIMIT 5
        """)).fetchall()
        
        if samples:
            print(f"\n📋 최근 추가된 데이터 샘플:")
            for sample in samples:
                print(f"   - {sample[0]}, {sample[1]}, {sample[2]}, {sample[3]}, {sample[4]}")

if __name__ == "__main__":
    main()