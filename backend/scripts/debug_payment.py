import pandas as pd
import os

file_path = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"

# 헤더 없이 읽기
df_raw = pd.read_excel(file_path, sheet_name="전체 결제대장", header=None)

print("처음 5행 원본 데이터:")
for i in range(5):
    print(f"Row {i}: {list(df_raw.iloc[i])}")

# 실제 헤더는 1행에 있음
print("\n\n헤더 행 (인덱스 1):", list(df_raw.iloc[1]))

# pandas가 자동으로 헤더를 찾도록
df_all = pd.read_excel(file_path, sheet_name="전체 결제대장", skiprows=2)
print("\n\n컬럼명:", list(df_all.columns))

print(f"\n전체 행수: {len(df_all)}")
print("\n처음 10개 데이터:")
for idx, row in df_all.head(10).iterrows():
    print(f"Row {idx}: {dict(row)}")

# 숫자만 있는 행 필터링
print("\n\n첫 번째 열이 숫자인 행:")
numeric_rows = 0
for idx, row in df_all.iterrows():
    no_val = row.iloc[0]
    if pd.notna(no_val):
        try:
            int(no_val)
            numeric_rows += 1
            if numeric_rows <= 5:
                print(f"Row {idx}: NO={no_val}, 고객명={row.get('고객명')}, 금액={row.get('결제 금액')}")
        except:
            pass

print(f"\n첫 번째 열이 숫자인 행 총 개수: {numeric_rows}")