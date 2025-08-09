#!/usr/bin/env python3
"""
2025년 5월 결제 데이터 상세 확인 스크립트
"""

import pandas as pd
import os
from datetime import datetime
from decimal import Decimal

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

def check_may_2025_payments():
    """2025년 5월 결제 데이터 확인"""
    
    file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    try:
        # Excel 파일 읽기
        xl = pd.ExcelFile(file_path)
        
        # "2025년 5월" 시트 읽기
        sheet_name = "2025년 5월"
        df = pd.read_excel(xl, sheet_name=sheet_name)
        
        print(f"\n{'='*50}")
        print(f"시트: {sheet_name}")
        print(f"전체 행 수: {len(df)}")
        print(f"컬럼: {list(df.columns)}")
        print('='*50)
        
        # 데이터 샘플 확인
        print("\n처음 10행 데이터:")
        print(df.head(10))
        
        # 실제 데이터가 시작되는 행 찾기
        # 보통 Excel에서 헤더가 여러 행에 걸쳐 있을 수 있음
        for i in range(10):
            row = df.iloc[i]
            print(f"\n행 {i}: {list(row.values)}")
            
        # 헤더를 수동으로 확인하여 데이터 시작점 찾기
        # 일반적으로 결제 데이터는 날짜, 고객명, 금액 등이 포함됨
        print("\n" + "="*50)
        print("데이터 구조 분석")
        print("="*50)
        
        # 각 컬럼의 첫 10개 고유값 확인
        for col in df.columns[:10]:  # 처음 10개 컬럼만
            unique_values = df[col].dropna().unique()[:5]
            print(f"\n{col}: {unique_values}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_may_2025_payments()