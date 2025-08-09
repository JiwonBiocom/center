#!/usr/bin/env python3
"""
엑셀에서 서비스 이용 내역 추출
"""

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 엑셀 파일 읽기
excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025.xlsm'
df = pd.read_excel(excel_path, sheet_name='2025년5월', engine='openpyxl')

# 컬럼명 정리
df.columns = ['날짜', '성함', '비고', '실행패키지', '세션진행사항', '특이사항', 
              '상담내용', '주관심서비스', '브레인잔여', '펄스잔여', '림프잔여', 
              '레드잔여', 'AI바이크잔여', '매출', '비고2', '쿠폰매출', 
              '상품권', '행사', '프로모션', '비고3']

# 데이터가 있는 행만 필터링
df_valid = df[df['성함'].notna()]
df_valid = df_valid[df_valid['성함'] != '성함']

# 최미라 고객 데이터
choi_data = df_valid[df_valid['성함'] == '최미라']

print('최미라 서비스 이용 내역:')
for idx, row in choi_data.iterrows():
    print(f'\n날짜: {row["날짜"]}')
    print(f'실행패키지: {row["실행패키지"]}')
    print(f'세션진행사항: {row["세션진행사항"]}')

# 전체 5월 이용 현황
print(f'\n2025년 5월 총 이용 건수: {len(df_valid)}')
print(f'고유 고객 수: {df_valid["성함"].nunique()}')

# CSV로 저장
output_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/2025년5월_서비스이용내역.csv'
df_valid.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f'\n데이터를 {output_path}에 저장했습니다.')