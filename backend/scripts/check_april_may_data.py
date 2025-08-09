"""
4월과 5월 결제 데이터 확인
"""

import pandas as pd
import os
from datetime import datetime

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"
file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")

print("=== Excel 파일의 모든 시트 이름 확인 ===")
# 모든 시트 이름 확인
xl_file = pd.ExcelFile(file_path)
sheet_names = xl_file.sheet_names
print(f"전체 시트: {sheet_names}")

# 전체 결제대장에서 4월과 5월 데이터 찾기
print("\n=== 전체 결제대장에서 4월과 5월 데이터 확인 ===")
df = pd.read_excel(file_path, sheet_name="전체 결제대장", header=2)

# 결제일자 컬럼 확인
if '결제일자' in df.columns:
    # 날짜 형식으로 변환
    df['결제일자'] = pd.to_datetime(df['결제일자'], errors='coerce')
    
    # 2024년과 2025년 4월, 5월 데이터 필터링
    april_2024 = df[(df['결제일자'].dt.year == 2024) & (df['결제일자'].dt.month == 4)]
    may_2024 = df[(df['결제일자'].dt.year == 2024) & (df['결제일자'].dt.month == 5)]
    april_2025 = df[(df['결제일자'].dt.year == 2025) & (df['결제일자'].dt.month == 4)]
    may_2025 = df[(df['결제일자'].dt.year == 2025) & (df['결제일자'].dt.month == 5)]
    
    print(f"\n2024년 4월 데이터 수: {len(april_2024)}")
    if len(april_2024) > 0:
        print("2024년 4월 샘플 데이터:")
        for idx, row in april_2024.head(5).iterrows():
            print(f"  - {row['결제일자'].strftime('%Y-%m-%d')}: {row['고객명']} - {row['결제 프로그램']} - {row['결제 금액']:,}원")
    
    print(f"\n2024년 5월 데이터 수: {len(may_2024)}")
    if len(may_2024) > 0:
        print("2024년 5월 샘플 데이터:")
        for idx, row in may_2024.head(5).iterrows():
            print(f"  - {row['결제일자'].strftime('%Y-%m-%d')}: {row['고객명']} - {row['결제 프로그램']} - {row['결제 금액']:,}원")
    
    print(f"\n2025년 4월 데이터 수: {len(april_2025)}")
    if len(april_2025) > 0:
        print("2025년 4월 샘플 데이터:")
        for idx, row in april_2025.head(5).iterrows():
            print(f"  - {row['결제일자'].strftime('%Y-%m-%d')}: {row['고객명']} - {row['결제 프로그램']} - {row['결제 금액']:,}원")
    
    print(f"\n2025년 5월 데이터 수: {len(may_2025)}")
    if len(may_2025) > 0:
        print("2025년 5월 샘플 데이터:")
        for idx, row in may_2025.head(5).iterrows():
            print(f"  - {row['결제일자'].strftime('%Y-%m-%d')}: {row['고객명']} - {row['결제 프로그램']} - {row['결제 금액']:,}원")

# 전체 데이터의 날짜 범위 확인
print("\n=== 전체 데이터의 날짜 범위 ===")
valid_dates = df[df['결제일자'].notna()]['결제일자']
print(f"최초 날짜: {valid_dates.min()}")
print(f"최종 날짜: {valid_dates.max()}")

# 월별 데이터 수 집계
print("\n=== 월별 데이터 수 ===")
monthly_counts = df[df['결제일자'].notna()].groupby([df['결제일자'].dt.year, df['결제일자'].dt.month]).size()
for (year, month), count in monthly_counts.items():
    print(f"{year}년 {month}월: {count}건")