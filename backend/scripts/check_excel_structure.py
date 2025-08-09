"""
엑셀 파일 구조 확인 스크립트
"""

import pandas as pd
import os

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

def check_file_structure():
    """엑셀 파일들의 시트와 컬럼 구조 확인"""
    
    files = {
        "고객관리대장": "고객관리대장2025.xlsm",
        "결제현황": "★2025년 AIBIO 결제현황.xlsx",
        "리드DB": "유입 고객 DB 리스트.xlsx"
    }
    
    for name, filename in files.items():
        file_path = os.path.join(EXCEL_DIR, filename)
        print(f"\n{'='*50}")
        print(f"{name}: {filename}")
        print('='*50)
        
        try:
            xl = pd.ExcelFile(file_path)
            print(f"\n시트 목록: {len(xl.sheet_names)}개")
            
            # 주요 시트만 확인
            for i, sheet_name in enumerate(xl.sheet_names[:5]):  # 처음 5개만
                print(f"\n[{i+1}] {sheet_name}")
                
                df = pd.read_excel(xl, sheet_name=sheet_name, nrows=5)
                if not df.empty:
                    print(f"  컬럼: {list(df.columns)}")
                    print(f"  행 수: {len(pd.read_excel(xl, sheet_name=sheet_name))}")
                
            if len(xl.sheet_names) > 5:
                print(f"\n... 그 외 {len(xl.sheet_names) - 5}개 시트")
                
        except Exception as e:
            print(f"오류: {e}")

if __name__ == "__main__":
    check_file_structure()