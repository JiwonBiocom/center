#!/usr/bin/env python3
"""유입고객 CSV 파일 분석"""

import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_csv_structure():
    """CSV 파일 구조 분석"""
    
    csv_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/유입고객_DB리스트.csv"
    
    # CSV 파일 읽기
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    print("=== CSV 파일 구조 분석 ===")
    print(f"전체 행 수: {len(df)}개")
    print(f"전체 컬럼 수: {len(df.columns)}개")
    
    print("\n[컬럼 목록]")
    for i, col in enumerate(df.columns):
        print(f"{i+1}. {col}")
    
    print("\n[각 컬럼의 데이터 타입과 NULL 값]")
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        null_count = df[col].isna().sum()
        print(f"- {col}: {non_null_count}개 값 있음, {null_count}개 NULL")
    
    print("\n[유입경로 분포]")
    if '유입경로' in df.columns:
        channel_counts = df['유입경로'].value_counts()
        for channel, count in channel_counts.items():
            print(f"  - {channel}: {count}개")
    
    print("\n[DB작성 채널 분포]")
    if 'DB작성 채널' in df.columns:
        db_channel_counts = df['DB작성 채널'].value_counts()
        for channel, count in db_channel_counts.items():
            print(f"  - {channel}: {count}개")
    
    # 날짜 컬럼 분석
    date_columns = ['DB입력일', '전화상담일', '방문상담일', '등록일']
    print("\n[날짜 데이터 분석]")
    for col in date_columns:
        if col in df.columns:
            non_null_dates = df[col].notna().sum()
            print(f"  - {col}: {non_null_dates}개 날짜 있음")
    
    # 매출 데이터 분석
    if '매출' in df.columns:
        revenue_data = df[df['매출'].notna()]
        print(f"\n[매출 데이터]")
        print(f"  - 매출이 있는 고객: {len(revenue_data)}명")
        if len(revenue_data) > 0:
            # 매출 컬럼을 숫자로 변환 시도
            try:
                df['매출_숫자'] = pd.to_numeric(df['매출'], errors='coerce')
                total_revenue = df['매출_숫자'].sum()
                print(f"  - 총 매출액: {total_revenue:,.0f}원")
            except:
                print("  - 매출 데이터 변환 실패")
    
    # 샘플 데이터 몇 개 출력
    print("\n[샘플 데이터 (상위 5개)]")
    sample_cols = ['이름', '유입경로', '연락처', '등록일', '구매상품', '매출']
    available_cols = [col for col in sample_cols if col in df.columns]
    sample_df = df[available_cols].head(5)
    print(sample_df.to_string(index=False))
    
    return df

def create_mapping_plan(df):
    """CSV 컬럼과 DB 모델 매핑 계획"""
    
    print("\n\n=== CSV 컬럼과 MarketingLead 모델 매핑 계획 ===")
    
    mapping = {
        '이름': 'name',
        '연락처': 'phone',
        '나이': 'age',
        '거주지역': 'region',
        '유입경로': 'lead_channel',
        '당근아이디': 'carrot_id',
        '시청 광고': 'ad_watched',
        '가격안내': 'price_informed',
        'A/B 테스트': 'ab_test_group',
        'DB입력일': 'db_entry_date',
        '전화상담일': 'phone_consult_date',
        '방문상담일': 'visit_consult_date',
        '등록일': 'registration_date',
        '구매상품': 'purchased_product',
        '미등록사유': 'no_registration_reason',
        '비고': 'notes',
        '매출': 'revenue'
    }
    
    print("[매핑 관계]")
    for csv_col, db_col in mapping.items():
        if csv_col in df.columns:
            print(f"  ✓ {csv_col} → {db_col}")
        else:
            print(f"  ✗ {csv_col} → {db_col} (CSV에 컬럼 없음)")
    
    # CSV에는 있지만 매핑이 없는 컬럼
    print("\n[매핑되지 않는 CSV 컬럼]")
    unmapped_cols = [col for col in df.columns if col not in mapping.keys()]
    for col in unmapped_cols:
        print(f"  - {col}")
    
    # DB 모델에는 있지만 CSV에 없는 필드
    print("\n[CSV에 없는 DB 필드]")
    db_fields = ['sub_channel', 'campaign', 'lead_date', 'status', 'converted_customer_id']
    for field in db_fields:
        print(f"  - {field} (기본값 또는 자동 설정 필요)")

if __name__ == "__main__":
    df = analyze_csv_structure()
    create_mapping_plan(df)