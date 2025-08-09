#!/usr/bin/env python3
"""2023년 데이터를 엑셀 파일로 만들어서 업로드 API로 전송"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import requests
from datetime import datetime
import io

# 엑셀 파일 경로
EXCEL_FILE = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"
API_BASE_URL = "http://localhost:8001/api/v1"

def parse_2023_sheet(excel_file, sheet_name):
    """23년 시트의 특별한 형식을 파싱"""
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # 헤더 행 찾기 - "고객명" 또는 "결제일자"가 포함된 행
    header_row = None
    for i in range(min(10, len(df))):
        row_values = df.iloc[i].astype(str).values
        if any('고객명' in val for val in row_values) or any('결제일자' in val for val in row_values):
            header_row = i
            break

    if header_row is None:
        return pd.DataFrame()

    # 헤더로 사용할 컬럼명 추출
    headers = df.iloc[header_row].astype(str).values

    # 데이터 부분만 추출 (헤더 다음 행부터)
    data_df = df.iloc[header_row + 1:].copy()

    # 컬럼명 설정
    data_df.columns = headers

    # NaN이나 빈 행 제거
    data_df = data_df.dropna(how='all')

    # 숫자 인덱스 컬럼 제거 (첫 번째 컬럼이 보통 순번)
    if data_df.columns[0].isdigit() or data_df.columns[0] == 'nan':
        data_df = data_df.iloc[:, 1:]

    return data_df

def main():
    """메인 실행 함수"""
    print("=== 2023년 결제 데이터 엑셀 업로드 ===\n")

    # 엑셀 파일 읽기
    excel_file = pd.ExcelFile(EXCEL_FILE)

    # 23년으로 시작하는 시트 찾기
    sheets_2023 = [sheet for sheet in excel_file.sheet_names if sheet.startswith("23년")]

    print(f"찾은 23년 시트: {len(sheets_2023)}개")

    # 모든 23년 데이터를 하나의 데이터프레임으로 합치기
    all_data = []

    for sheet_name in sorted(sheets_2023):
        print(f"  - {sheet_name} 처리 중...")
        df = parse_2023_sheet(excel_file, sheet_name)

        if len(df) > 0:
            # 컬럼명 정규화
            df_normalized = pd.DataFrame()

            # 회원번호 (빈 값으로)
            df_normalized['회원번호'] = ''

            # 고객명
            for col in ['고객명', '회원명', '성명']:
                if col in df.columns:
                    df_normalized['회원명'] = df[col]
                    break

            # 상품명
            for col in ['결제 프로그램', '프로그램', '상품명', '서비스']:
                if col in df.columns:
                    df_normalized['상품명'] = df[col]
                    break

            # 결제일자
            for col in ['결제일자', '결제일', '날짜']:
                if col in df.columns:
                    df_normalized['결제일자'] = df[col]
                    break

            # 금액
            for col in ['결제 금액', '결제금액', '금액', '매출액']:
                if col in df.columns:
                    df_normalized['결제금액'] = df[col]
                    break

            # 결제상태
            df_normalized['결제상태'] = '완료'

            # 비고 (여러 정보 합치기)
            memo_parts = []

            # 승인번호
            for col in ['승인번호', '승인 번호']:
                if col in df.columns:
                    df_normalized['승인번호'] = df[col]
                    break
            else:
                df_normalized['승인번호'] = ''

            # 담당자
            for col in ['결제 담당자', '담당자']:
                if col in df.columns:
                    df_normalized['담당자'] = df[col]
                    break
            else:
                df_normalized['담당자'] = ''

            # 기타/비고
            for col in ['기타', '비고', '메모']:
                if col in df.columns:
                    df_normalized['비고'] = df[col]
                    break
            else:
                df_normalized['비고'] = ''

            all_data.append(df_normalized)

    # 모든 데이터 합치기
    combined_df = pd.concat(all_data, ignore_index=True)

    # 빈 값 처리
    combined_df = combined_df.fillna('')

    print(f"\n전체 데이터: {len(combined_df)}건")

    # 데이터 샘플 출력
    print("\n데이터 샘플 (처음 5행):")
    print(combined_df.head())

    # 엑셀 파일로 저장
    output_file = "2023년_결제데이터.xlsx"
    combined_df.to_excel(output_file, index=False, sheet_name='2023년')
    print(f"\n엑셀 파일 생성: {output_file}")

    # API로 업로드
    print("\nAPI로 업로드 중...")

    with open(output_file, 'rb') as f:
        files = {'file': ('2023년_결제데이터.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}

        response = requests.post(
            f"{API_BASE_URL}/payments/import/excel",
            files=files
        )

        if response.status_code == 200:
            result = response.json()
            print(f"업로드 성공!")
            print(f"전체 응답: {result}")
            print(f"  - 처리된 행: {result.get('total_rows', 0)}")
            print(f"  - 성공: {result.get('success_count', 0)}")
            print(f"  - 중복: {result.get('duplicate_count', 0)}")
            print(f"  - 오류: {result.get('error_count', 0)}")

            # 오류가 있으면 샘플 출력
            if result.get('errors'):
                print("\n오류 샘플 (처음 5개):")
                for i, error in enumerate(result['errors'][:5]):
                    print(f"  {i+1}. {error}")
        else:
            print(f"업로드 실패: {response.status_code}")
            print(response.text)

    # 임시 파일 유지 (디버깅용)
    print(f"\n엑셀 파일 유지: {output_file} (수동으로 확인 가능)")

if __name__ == "__main__":
    main()
