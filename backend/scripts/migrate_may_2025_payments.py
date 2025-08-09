#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 마이그레이션 스크립트
"""

import os
import sys
import pandas as pd
from datetime import datetime, date
from decimal import Decimal

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.customer import Customer
from models.payment import Payment

# 엑셀 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

# 데이터베이스 설정
DATABASE_URL = settings.DATABASE_URL or "postgresql://aibio_user:aibio_password@localhost:5432/aibio_center"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def read_may_2025_data():
    """Excel에서 2025년 5월 데이터 읽기"""
    file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    # 헤더는 2번째 행(index=1)에 있으므로 skiprows=2로 설정하고 names로 컬럼명 지정
    column_names = ['번호', '결제일자', '고객명', '결제 프로그램', '결제 금액', 
                    '카드 명의자명', '승인번호', '결제 담당자', '유입', '등급', 
                    '구매', '세션시작일', '계약만료일', '기타']
    
    df = pd.read_excel(file_path, sheet_name="2025년 5월", skiprows=2, names=column_names)
    
    # 실제 데이터만 필터링 (고객명이 있고 합계가 아닌 행)
    df_payments = df[
        df['고객명'].notna() & 
        (df['고객명'] != '합계') &
        (df['고객명'] != '총합계') &
        (df['고객명'] != '계') &
        (df['고객명'] != '고객명')  # 헤더 행 제외
    ].copy()
    
    # 결제 금액을 숫자로 변환
    df_payments['결제 금액'] = pd.to_numeric(df_payments['결제 금액'], errors='coerce')
    
    # 날짜 변환 (errors='coerce'로 변환 실패 시 NaT 반환)
    df_payments['결제일자'] = pd.to_datetime(df_payments['결제일자'], errors='coerce')
    
    # 유효한 데이터만 필터링 (환불 건도 포함하기 위해 != 0으로 변경)
    df_payments = df_payments[
        df_payments['결제일자'].notna() & 
        (df_payments['결제 금액'] != 0)
    ].copy()
    
    return df_payments

def migrate_may_2025_payments():
    """2025년 5월 결제 데이터 마이그레이션"""
    
    session = SessionLocal()
    
    try:
        # Excel 데이터 읽기
        df_payments = read_may_2025_data()
        print(f"\nExcel에서 {len(df_payments)}건의 결제 데이터를 읽었습니다.")
        print(f"총 금액: {df_payments['결제 금액'].sum():,.0f}원")
        
        # 기존 고객 매핑 로드
        result = session.execute(select(Customer))
        customers = result.scalars().all()
        customer_map = {c.name: c.customer_id for c in customers}
        print(f"\n기존 고객 {len(customers)}명 로드")
        
        # 마이그레이션 시작
        success_count = 0
        error_count = 0
        
        print("\n마이그레이션 시작...")
        print("-" * 80)
        
        for idx, row in df_payments.iterrows():
            try:
                customer_name = row['고객명'].strip()
                payment_date = row['결제일자'].date()
                amount = float(row['결제 금액'])
                
                # 고객 찾기 또는 생성
                customer_id = customer_map.get(customer_name)
                if not customer_id:
                    # 새 고객 생성
                    customer = Customer(
                        name=customer_name,
                        assigned_staff=row['결제 담당자'],
                        grade=row['등급'] if pd.notna(row['등급']) else None,
                        inflow_channel=row['유입'] if pd.notna(row['유입']) else None
                    )
                    session.add(customer)
                    session.flush()
                    customer_id = customer.customer_id
                    customer_map[customer_name] = customer_id
                    print(f"새 고객 생성: {customer_name}")
                
                # 중복 확인
                existing = session.query(Payment).filter(
                    and_(
                        Payment.customer_id == customer_id,
                        Payment.payment_date == payment_date,
                        Payment.amount == amount
                    )
                ).first()
                
                if existing:
                    print(f"중복 결제 건너뛰기: {customer_name} - {payment_date} - {amount:,.0f}원")
                    continue
                
                # 결제 데이터 생성
                payment = Payment(
                    customer_id=customer_id,
                    payment_date=payment_date,
                    amount=amount,
                    payment_method='카드' if row['승인번호'] != '계좌이체' else '계좌이체',
                    card_holder_name=row['카드 명의자명'] if pd.notna(row['카드 명의자명']) else None,
                    approval_number=str(row['승인번호']) if pd.notna(row['승인번호']) else None,
                    payment_staff=row['결제 담당자'] if pd.notna(row['결제 담당자']) else None,
                    purchase_type=row['등급'] if pd.notna(row['등급']) else None,
                    purchase_order=None  # 구매 차수는 별도로 계산 필요
                )
                
                session.add(payment)
                success_count += 1
                
                # 10건마다 커밋
                if success_count % 10 == 0:
                    session.commit()
                    print(f"{success_count}건 처리 완료...")
                
            except Exception as e:
                error_count += 1
                print(f"오류 발생 (행 {idx}): {e}")
                print(f"  고객명: {row['고객명']}, 날짜: {row['결제일자']}, 금액: {row['결제 금액']}")
        
        # 최종 커밋
        session.commit()
        
        print("-" * 80)
        print(f"\n마이그레이션 완료!")
        print(f"성공: {success_count}건")
        print(f"오류: {error_count}건")
        
        # 최종 확인
        may_payments = session.query(Payment).filter(
            and_(
                Payment.payment_date >= date(2025, 5, 1),
                Payment.payment_date < date(2025, 6, 1)
            )
        ).all()
        
        total_amount = sum(float(p.amount) for p in may_payments)
        print(f"\n데이터베이스 2025년 5월 결제 현황:")
        print(f"총 {len(may_payments)}건, {total_amount:,.0f}원")
        
        expected_total = 11933310
        if total_amount == expected_total:
            print("✅ 마이그레이션 성공! 총액이 일치합니다.")
        else:
            print(f"⚠️ 총액 불일치: 차이 {total_amount - expected_total:,.0f}원")
        
    except Exception as e:
        print(f"마이그레이션 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("2025년 5월 결제 데이터 마이그레이션을 시작합니다.")
    migrate_may_2025_payments()