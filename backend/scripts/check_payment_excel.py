"""
결제 엑셀 파일의 구조를 자세히 확인
"""

import pandas as pd
import os

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"
file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")

# 전체 결제대장 시트를 자세히 확인
print("=== 전체 결제대장 시트 분석 ===")
df = pd.read_excel(file_path, sheet_name="전체 결제대장", header=None)

print(f"전체 행 수: {len(df)}")
print("\n처음 20행 확인:")
for i in range(min(20, len(df))):
    row = df.iloc[i]
    # 비어있지 않은 값만 출력
    non_empty = [(j, val) for j, val in enumerate(row) if pd.notna(val)]
    if non_empty:
        print(f"Row {i}: {non_empty[:5]}...")  # 처음 5개 값만

# 실제 데이터가 있는 행 찾기
print("\n\n데이터가 있는 행 찾기:")
for i in range(len(df)):
    row = df.iloc[i]
    # 숫자로 시작하는 행 찾기 (NO 컬럼)
    if pd.notna(row[0]) and str(row[0]).strip().isdigit():
        print(f"\n첫 번째 데이터 행: {i}")
        print(f"데이터: {list(row.values[:10])}")
        break

# 2025년 1월 시트도 확인
print("\n\n=== 2025년 1월 시트 분석 ===")
df_jan = pd.read_excel(file_path, sheet_name="2025년 1월", header=None)
print(f"전체 행 수: {len(df_jan)}")

print("\n처음 10행:")
for i in range(min(10, len(df_jan))):
    row = df_jan.iloc[i]
    non_empty = [(j, val) for j, val in enumerate(row) if pd.notna(val)]
    if non_empty:
        print(f"Row {i}: {non_empty[:5]}...")