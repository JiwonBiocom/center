"""
Excel 파일의 상세 구조 확인
"""
import pandas as pd
import openpyxl

EXCEL_PATH = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

def check_excel_structure():
    """Excel 파일의 구조를 상세히 확인"""
    
    # openpyxl로 직접 읽기
    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    
    sheet_names = ["2025년 1월", "2025년 2월", "2025년 3월", "2025년 4월"]
    
    for sheet_name in sheet_names:
        if sheet_name not in wb.sheetnames:
            print(f"{sheet_name} 시트가 없습니다.")
            continue
            
        sheet = wb[sheet_name]
        print(f"\n{'='*60}")
        print(f"{sheet_name} 시트 분석")
        print(f"{'='*60}")
        
        # 첫 10행의 데이터 확인
        print("\n첫 10행 데이터:")
        for row_num in range(1, 11):
            row_data = []
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                cell = sheet[f'{col}{row_num}']
                value = cell.value
                if value is not None:
                    row_data.append(f"{col}: {value}")
            if row_data:
                print(f"Row {row_num}: {' | '.join(row_data)}")
        
        # pandas로도 읽어보기
        print("\n\nPandas로 읽은 데이터 (header=2):")
        try:
            df = pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, header=2)
            print(f"컬럼: {list(df.columns)}")
            print(f"데이터 행 수: {len(df)}")
            
            # 처음 5행 출력
            if len(df) > 0:
                print("\n처음 5행:")
                print(df.head())
        except Exception as e:
            print(f"Pandas 읽기 오류: {e}")

if __name__ == "__main__":
    check_excel_structure()