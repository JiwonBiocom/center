#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 정확히 읽고 총액 확인하는 스크립트
"""

import pandas as pd
import os
from datetime import datetime
from decimal import Decimal

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

def read_may_2025_payments():
    """2025년 5월 결제 데이터 읽기"""
    
    file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    try:
        # Excel 파일 읽기 - 헤더는 2번째 행(index=1)에 있음
        df = pd.read_excel(file_path, sheet_name="2025년 5월", header=1)
        
        print(f"\n{'='*50}")
        print("2025년 5월 결제 데이터")
        print('='*50)
        
        # 실제 데이터만 필터링 (결제일자가 있는 행만)
        df_filtered = df[df['결제일자'].notna()].copy()
        
        # 마지막 행이 합계일 수 있으므로 확인
        last_rows = df_filtered.tail(5)
        print("\n마지막 5행 확인:")
        print(last_rows[['고객명', '결제 금액']])
        
        # 합계 행 제거 (고객명이 '합계' 또는 NaN인 경우)
        df_payments = df_filtered[
            (df_filtered['고객명'].notna()) & 
            (df_filtered['고객명'] != '합계') &
            (df_filtered['고객명'] != '총합계')
        ].copy()
        
        print(f"\n실제 결제 건수: {len(df_payments)}건")
        
        # 결제 금액을 숫자로 변환
        df_payments['결제 금액'] = pd.to_numeric(df_payments['결제 금액'], errors='coerce')
        
        # 총 금액 계산
        total_amount = df_payments['결제 금액'].sum()
        print(f"총 결제 금액: {total_amount:,.0f}원")
        
        # 각 결제 건 출력
        print("\n상세 결제 내역:")
        print("-" * 100)
        print(f"{'번호':>3} {'날짜':^12} {'고객명':^10} {'프로그램':^30} {'금액':>10} {'담당자':^8}")
        print("-" * 100)
        
        for idx, row in df_payments.iterrows():
            date = pd.to_datetime(row['결제일자']).strftime('%Y-%m-%d')
            customer = str(row['고객명'])[:10]
            program = str(row['결제 프로그램'])[:30].replace('\n', ' ')
            amount = int(row['결제 금액'])
            staff = str(row['결제 담당자'])[:8]
            
            print(f"{idx:>3} {date:^12} {customer:^10} {program:^30} {amount:>10,} {staff:^8}")
        
        print("-" * 100)
        print(f"{'합계':>56} {total_amount:>10,.0f}원")
        
        # 11,933,310원과 비교
        expected_total = 11933310
        print(f"\n예상 총액과 비교: {expected_total:,.0f}원")
        print(f"차이: {total_amount - expected_total:,.0f}원")
        
        return df_payments
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    read_may_2025_payments()