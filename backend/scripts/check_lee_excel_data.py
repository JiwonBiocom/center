import pandas as pd

# CSV 파일 경로
csv_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/csv_export/2025년5월.csv'

# CSV 읽기
df = pd.read_csv(csv_path)

# 컬럼명 확인
print("CSV 컬럼명:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

print("\n" + "="*50 + "\n")

# 이성윤 고객 데이터 찾기
lee_mask = df['Unnamed: 1'] == '이성윤'
lee_data = df[lee_mask]

print(f"이성윤 고객 데이터 {len(lee_data)}건 발견")

# 각 행의 데이터 확인
for idx, row in lee_data.iterrows():
    print(f"\n행 {idx}:")
    print(f"  날짜: {row.iloc[0]}")
    print(f"  성함: {row.iloc[1]}")
    print(f"  패키지 정보: {row.iloc[3]}")
    print(f"  브레인 잔여: {row.iloc[8]}")
    print(f"  펄스 잔여: {row.iloc[9]}")
    print(f"  림프 잔여: {row.iloc[10]}")
    print(f"  레드 잔여: {row.iloc[11]}")
    print(f"  브레인 사용: {row.iloc[12]}")
    print(f"  펄스 사용: {row.iloc[14]}")
    print(f"  림프 사용: {row.iloc[16]}")
    print(f"  레드 사용: {row.iloc[18]}")
