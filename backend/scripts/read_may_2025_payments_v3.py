#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 정확히 읽기 - 날짜 컬럼 수정
"""

import pandas as pd
import os
from datetime import datetime

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

def read_may_2025_payments():
    """2025년 5월 결제 데이터 읽기"""
    
    file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    try:
        # 헤더 행을 1로 지정하여 읽기
        df = pd.read_excel(file_path, sheet_name="2025년 5월", header=1)
        
        print(f"\n현재 컬럼: {list(df.columns)}")
        
        # 실제 데이터만 필터링 (고객명이 있는 행만)
        df_filtered = df[df['고객명'].notna()].copy()
        
        # 합계 행 제외
        df_payments = df_filtered[
            (df_filtered['고객명'] != '합계') &
            (df_filtered['고객명'] != '총합계') &
            (df_filtered['고객명'] != '계')
        ].copy()
        
        print(f"\n실제 결제 건수: {len(df_payments)}건")
        
        # 결제 금액을 숫자로 변환
        df_payments['결제 금액'] = pd.to_numeric(df_payments['결제 금액'], errors='coerce')
        
        # 총 금액 계산
        total_amount = df_payments['결제 금액'].sum()
        print(f"총 결제 금액: {total_amount:,.0f}원")
        
        # 각 결제 건 출력
        print("\n상세 결제 내역:")
        print("-" * 120)
        print(f"{'번호':>3} {'날짜':^12} {'고객명':^10} {'프로그램':^40} {'금액':>12} {'담당자':^8}")
        print("-" * 120)
        
        for idx, (_, row) in enumerate(df_payments.iterrows()):
            try:
                date = pd.to_datetime(row['결제일자']).strftime('%Y-%m-%d')
                customer = str(row['고객명'])[:10]
                program = str(row['결제 프로그램'])[:40].replace('\n', ' ')
                amount = int(row['결제 금액'])
                staff = str(row['결제 담당자'])[:8]
                
                print(f"{idx+1:>3} {date:^12} {customer:^10} {program:^40} {amount:>12,} {staff:^8}")
            except Exception as e:
                print(f"행 {idx+1} 처리 중 오류: {e}")
                print(f"    결제일자: {row['결제일자']}")
        
        print("-" * 120)
        print(f"{'합계':>68} {total_amount:>12,.0f}원")
        
        # 11,933,310원과 비교
        expected_total = 11933310
        print(f"\n예상 총액과 비교: {expected_total:,.0f}원")
        print(f"차이: {total_amount - expected_total:,.0f}원")
        
        # 데이터프레임 정리
        df_payments['payment_date'] = pd.to_datetime(df_payments['결제일자'])
        df_payments['customer_name'] = df_payments['고객명']
        df_payments['payment_amount'] = df_payments['결제 금액']
        df_payments['program'] = df_payments['결제 프로그램']
        df_payments['staff'] = df_payments['결제 담당자']
        df_payments['card_name'] = df_payments['카드 명의자명']
        df_payments['approval_number'] = df_payments['승인번호']
        df_payments['inflow'] = df_payments['유입']
        df_payments['grade'] = df_payments['등급']
        df_payments['purchase'] = df_payments['구매']
        
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