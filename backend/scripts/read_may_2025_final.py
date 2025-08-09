#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 최종 읽기 스크립트
"""

import pandas as pd
import os
from datetime import datetime

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

def read_may_2025_payments():
    """2025년 5월 결제 데이터 읽기"""
    
    file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    try:
        # 먼저 전체 시트를 읽어서 구조 파악
        df_raw = pd.read_excel(file_path, sheet_name="2025년 5월", header=None)
        
        print("처음 5행:")
        print(df_raw.head())
        
        # 실제 헤더는 1번 행(0-indexed)에 있음
        df = pd.read_excel(file_path, sheet_name="2025년 5월", skiprows=1)
        
        print(f"\n컬럼: {list(df.columns)}")
        
        # 컬럼명 정리 (Unnamed 컬럼들을 실제 컬럼명으로 매핑)
        column_mapping = {
            df.columns[0]: '번호',
            df.columns[1]: '결제일자',
            df.columns[2]: '고객명',
            df.columns[3]: '결제 프로그램',
            df.columns[4]: '결제 금액',
            df.columns[5]: '카드 명의자명',
            df.columns[6]: '승인번호',
            df.columns[7]: '결제 담당자',
            df.columns[8]: '유입',
            df.columns[9]: '등급',
            df.columns[10]: '구매',
        }
        
        df = df.rename(columns=column_mapping)
        
        # 실제 데이터만 필터링 (고객명이 있고 합계가 아닌 행)
        df_payments = df[
            df['고객명'].notna() & 
            (df['고객명'] != '합계') &
            (df['고객명'] != '총합계') &
            (df['고객명'] != '계')
        ].copy()
        
        print(f"\n실제 결제 건수: {len(df_payments)}건")
        
        # 결제 금액을 숫자로 변환
        df_payments['결제 금액'] = pd.to_numeric(df_payments['결제 금액'], errors='coerce')
        
        # 총 금액 계산
        total_amount = df_payments['결제 금액'].sum()
        print(f"총 결제 금액: {total_amount:,.0f}원")
        
        # 각 결제 건 출력
        print("\n상세 결제 내역:")
        print("-" * 130)
        print(f"{'번호':>3} {'날짜':^12} {'고객명':^10} {'프로그램':^45} {'금액':>12} {'담당자':^8} {'등급':^8}")
        print("-" * 130)
        
        payments_list = []
        
        for idx, (_, row) in enumerate(df_payments.iterrows()):
            try:
                date = pd.to_datetime(row['결제일자'])
                date_str = date.strftime('%Y-%m-%d')
                customer = str(row['고객명'])[:10]
                program = str(row['결제 프로그램'])[:45].replace('\n', ' ')
                amount = int(row['결제 금액'])
                staff = str(row['결제 담당자'])[:8]
                grade = str(row['등급'])[:8] if pd.notna(row['등급']) else ''
                
                print(f"{idx+1:>3} {date_str:^12} {customer:^10} {program:^45} {amount:>12,} {staff:^8} {grade:^8}")
                
                # 마이그레이션용 데이터 준비
                payments_list.append({
                    'payment_date': date,
                    'customer_name': row['고객명'],
                    'payment_amount': amount,
                    'program': row['결제 프로그램'],
                    'staff': row['결제 담당자'],
                    'card_name': row['카드 명의자명'],
                    'approval_number': str(row['승인번호']),
                    'inflow': row['유입'],
                    'grade': row['등급'],
                    'purchase': row['구매']
                })
                
            except Exception as e:
                print(f"행 {idx+1} 처리 중 오류: {e}")
        
        print("-" * 130)
        print(f"{'합계':>73} {total_amount:>12,.0f}원")
        
        # 11,933,310원과 비교
        expected_total = 11933310
        print(f"\n예상 총액과 비교: {expected_total:,.0f}원")
        if total_amount == expected_total:
            print("✅ 총액이 일치합니다!")
        else:
            print(f"❌ 차이: {total_amount - expected_total:,.0f}원")
        
        return pd.DataFrame(payments_list)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    df = read_may_2025_payments()
    if df is not None:
        # CSV로 저장하여 확인
        output_file = "may_2025_payments_final.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n결과를 {output_file}에 저장했습니다.")