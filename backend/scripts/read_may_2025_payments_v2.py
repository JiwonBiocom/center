#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 정확히 읽기 - 헤더 위치 확인 후
"""

import pandas as pd
import os
from datetime import datetime

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

def read_may_2025_payments():
    """2025년 5월 결제 데이터 읽기"""
    
    file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    try:
        # 먼저 전체 데이터를 읽어서 구조 확인
        df_raw = pd.read_excel(file_path, sheet_name="2025년 5월", header=None)
        
        # 헤더가 있는 행 찾기 (보통 '결제일자'라는 텍스트가 있는 행)
        header_row = None
        for i in range(10):
            row_values = df_raw.iloc[i].values
            if '결제일자' in str(row_values):
                header_row = i
                break
        
        print(f"헤더 행 위치: {header_row}")
        
        # 헤더를 기준으로 다시 읽기
        df = pd.read_excel(file_path, sheet_name="2025년 5월", header=header_row)
        
        # 컬럼명 정리
        columns_map = {
            'Unnamed: 1': '결제일자',
            'Unnamed: 2': '고객명', 
            'Unnamed: 3': '결제 프로그램',
            'Unnamed: 4': '결제 금액',
            'Unnamed: 5': '카드 명의자명',
            'Unnamed: 6': '승인번호',
            'Unnamed: 7': '결제 담당자',
            'Unnamed: 8': '유입',
            'Unnamed: 9': '등급',
            'Unnamed: 10': '구매',
            'Unnamed: 11': '세션시작일',
            'Unnamed: 12': '계약만료일',
            'Unnamed: 13': '기타'
        }
        
        # 실제 컬럼명 확인하고 매핑
        print(f"\n현재 컬럼: {list(df.columns)}")
        
        # 결제일자 컬럼 찾기
        date_col = None
        for col in df.columns:
            if '결제일자' in str(col) or (pd.to_datetime(df[col], errors='coerce').notna().sum() > 10):
                date_col = col
                break
        
        print(f"결제일자 컬럼: {date_col}")
        
        # 실제 데이터만 필터링
        df_filtered = df[df[date_col].notna()].copy()
        
        # 고객명 컬럼 찾기
        customer_col = None
        amount_col = None
        program_col = None
        staff_col = None
        
        for col in df.columns:
            if '고객명' in str(col):
                customer_col = col
            elif '결제 금액' in str(col) or '금액' in str(col):
                amount_col = col
            elif '프로그램' in str(col):
                program_col = col
            elif '담당자' in str(col):
                staff_col = col
        
        print(f"고객명 컬럼: {customer_col}")
        print(f"금액 컬럼: {amount_col}")
        
        # 결제 데이터만 추출 (합계 행 제외)
        df_payments = df_filtered[
            (df_filtered[customer_col].notna()) & 
            (df_filtered[customer_col] != '합계') &
            (df_filtered[customer_col] != '총합계') &
            (df_filtered[customer_col] != '계')
        ].copy()
        
        print(f"\n실제 결제 건수: {len(df_payments)}건")
        
        # 결제 금액을 숫자로 변환
        df_payments[amount_col] = pd.to_numeric(df_payments[amount_col], errors='coerce')
        
        # 총 금액 계산
        total_amount = df_payments[amount_col].sum()
        print(f"총 결제 금액: {total_amount:,.0f}원")
        
        # 각 결제 건 출력
        print("\n상세 결제 내역:")
        print("-" * 120)
        print(f"{'번호':>3} {'날짜':^12} {'고객명':^10} {'프로그램':^40} {'금액':>12} {'담당자':^8}")
        print("-" * 120)
        
        for idx, row in df_payments.iterrows():
            try:
                date = pd.to_datetime(row[date_col]).strftime('%Y-%m-%d')
                customer = str(row[customer_col])[:10]
                program = str(row[program_col])[:40].replace('\n', ' ')
                amount = int(row[amount_col])
                staff = str(row[staff_col])[:8] if staff_col else 'N/A'
                
                print(f"{idx:>3} {date:^12} {customer:^10} {program:^40} {amount:>12,} {staff:^8}")
            except Exception as e:
                print(f"행 {idx} 처리 중 오류: {e}")
        
        print("-" * 120)
        print(f"{'합계':>68} {total_amount:>12,.0f}원")
        
        # 11,933,310원과 비교
        expected_total = 11933310
        print(f"\n예상 총액과 비교: {expected_total:,.0f}원")
        print(f"차이: {total_amount - expected_total:,.0f}원")
        
        # 데이터프레임 저장 (마이그레이션용)
        df_payments['payment_date'] = pd.to_datetime(df_payments[date_col])
        df_payments['customer_name'] = df_payments[customer_col]
        df_payments['payment_amount'] = df_payments[amount_col]
        df_payments['program'] = df_payments[program_col]
        df_payments['staff'] = df_payments[staff_col] if staff_col else None
        
        return df_payments
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    df = read_may_2025_payments()
    if df is not None:
        # CSV로 저장하여 확인
        output_file = "may_2025_payments.csv"
        df[['payment_date', 'customer_name', 'program', 'payment_amount', 'staff']].to_csv(
            output_file, index=False, encoding='utf-8-sig'
        )
        print(f"\n결과를 {output_file}에 저장했습니다.")