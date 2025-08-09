#!/usr/bin/env python3
"""
엑셀 파일의 각 시트의 컬럼명을 확인하는 스크립트
"""
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 엑셀 파일 경로
EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

def check_columns():
    """각 시트의 컬럼명 확인"""
    print(f"📊 엑셀 파일 분석: {EXCEL_PATH}\n")

    try:
        # 모든 시트 이름 가져오기
        xls = pd.ExcelFile(EXCEL_PATH)
        # 월별 시트만 확인 (2025년 2월 시트를 샘플로)
        sample_sheets = ['2025년 2월', '2024년 1월', '1월']

        for sheet_name in sample_sheets:
            if sheet_name not in xls.sheet_names:
                continue

            print(f"\n=== {sheet_name} 시트 ===")

            # 시트를 여러 방식으로 읽기
            print("\n1) 헤더 없이 읽기 (처음 5행):")
            df_no_header = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=None, nrows=5)
            print(df_no_header.to_string())

            print("\n2) 헤더를 2번째 행으로 읽기:")
            df_header_1 = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=1)
            print(f"  컬럼명: {list(df_header_1.columns[:5])}")
            print(f"  첫 번째 데이터:")
            if len(df_header_1) > 0:
                print(f"    {df_header_1.iloc[0].to_dict()}")

            print("\n3) 헤더를 3번째 행으로 읽기:")
            df_header_2 = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=2)
            print(f"  컬럼명: {list(df_header_2.columns[:5])}")
            print(f"  첫 번째 데이터:")
            if len(df_header_2) > 0:
                print(f"    {df_header_2.iloc[0].to_dict()}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_columns()
