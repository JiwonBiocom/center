#!/usr/bin/env python3
"""
Excel과 DB 데이터를 비교하여 누락된 필드 분석
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

def analyze_missing_data():
    """누락된 데이터 필드 분석"""

    # Excel 데이터 로드
    excel_path = 'docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx'
    df_all = pd.read_excel(excel_path, sheet_name='전체 결제대장', skiprows=2)

    # DB 연결
    load_dotenv('backend/.env')
    engine = create_engine(os.getenv('DATABASE_URL'))
    Session = sessionmaker(bind=engine)
    session = Session()

    print("🔍 누락된 데이터 필드 분석 보고서")
    print("=" * 60)

    # 1. 카드 명의자명 분석
    print("\n1. 카드 명의자명 (card_holder_name)")
    card_holders = df_all['카드 명의자명'].notna().sum()
    print(f"   Excel: {card_holders}건 데이터 존재")
    print(f"   DB: transaction_id 필드는 있지만 데이터 없음")
    print(f"   📌 복구 가능: 카드 명의자명 → transaction_id 또는 별도 필드")

    # 2. 승인번호 분석
    print("\n2. 승인번호 (approval_number)")
    approval_nums = df_all['승인번호'].notna().sum()
    print(f"   Excel: {approval_nums}건 데이터 존재")
    print(f"   DB: transaction_id 필드는 있지만 데이터 없음")
    print(f"   📌 복구 가능: 승인번호 → transaction_id")

    # 3. 결제 프로그램 분석
    print("\n3. 결제 프로그램 (purchase_type)")
    programs = df_all['결제 프로그램'].value_counts()
    print(f"   Excel: {len(programs)}종류의 프로그램")
    print("   상위 5개:")
    for prog, count in programs.head().items():
        print(f"     - {prog}: {count}건")

    # DB에서 reference_type 확인
    result = session.execute(text("""
        SELECT DISTINCT reference_type
        FROM payments
        WHERE reference_type IS NOT NULL
    """))
    db_types = [row[0] for row in result]
    print(f"   DB: reference_type에 {len(db_types)}종류 저장됨")
    print(f"   📌 복구 가능: 결제 프로그램 → reference_type")

    # 4. 기타 필드 분석
    print("\n4. 기타 (notes)")
    notes_count = df_all['기타'].notna().sum()
    print(f"   Excel: {notes_count}건의 메모 존재")
    print("   예시:")
    for note in df_all[df_all['기타'].notna()]['기타'].head(3):
        print(f"     - {note}")
    print(f"   DB: notes 필드는 있지만 데이터 없음")
    print(f"   📌 복구 가능: 기타 → notes")

    # 5. 등급 분석
    print("\n5. 등급 정보")
    grades = df_all['등급'].value_counts()
    print(f"   Excel: {len(grades)}종류의 등급")
    for grade, count in grades.items():
        print(f"     - {grade}: {count}건")
    print(f"   DB: 별도 필드 없음")
    print(f"   📌 검토 필요: 고객 테이블의 membership_level과 연관성 확인")

    # 6. 세션 시작일/계약 만료일
    print("\n6. 세션 시작일/계약 만료일")
    session_start = df_all['세션시작일'].notna().sum()
    contract_end = df_all['계약만료일'].notna().sum()
    print(f"   Excel: 세션시작일 {session_start}건, 계약만료일 {contract_end}건")
    print(f"   DB: 별도 필드 없음")
    print(f"   📌 검토 필요: package_purchases 테이블과 연관 가능")

    # 7. 복구 우선순위 제안
    print("\n📊 복구 우선순위 제안:")
    print("1. 🔴 승인번호 (307건) - 결제 추적에 중요")
    print("2. 🟠 카드 명의자명 (310건) - 결제 확인용")
    print("3. 🟡 결제 프로그램 (310건) - 이미 purchase_type에 일부 저장됨")
    print("4. 🟢 기타 메모 (67건) - 특이사항 기록")
    print("5. ⚪ 등급 정보 (114건) - 별도 분석 필요")

    session.close()

    return {
        'card_holder': card_holders,
        'approval_number': approval_nums,
        'notes': notes_count,
        'grades': len(grades)
    }

if __name__ == "__main__":
    analyze_missing_data()
