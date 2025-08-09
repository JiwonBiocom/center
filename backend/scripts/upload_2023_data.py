#!/usr/bin/env python3
"""2023년 결제 데이터 업로드 스크립트"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import requests
import json
from datetime import datetime
from decimal import Decimal

# 엑셀 파일 경로
EXCEL_FILE = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/★2025년 AIBIO 결제현황.xlsx"
API_BASE_URL = "http://localhost:8001"

def find_2023_sheets():
    """엑셀 파일에서 23년으로 시작하는 시트 찾기"""
    print(f"\n엑셀 파일 확인: {EXCEL_FILE}")

    # 엑셀 파일 읽기
    excel_file = pd.ExcelFile(EXCEL_FILE)

    # 모든 시트 이름 출력
    print("\n전체 시트 목록:")
    for sheet in excel_file.sheet_names:
        print(f"  - {sheet}")

    # 23년으로 시작하는 시트 찾기
    sheets_2023 = [sheet for sheet in excel_file.sheet_names if sheet.startswith("23년")]

    print(f"\n'23년'으로 시작하는 시트 ({len(sheets_2023)}개):")
    for sheet in sheets_2023:
        print(f"  - {sheet}")

    return excel_file, sheets_2023

def analyze_sheet_data(excel_file, sheet_name):
    """시트 데이터 분석"""
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # 처음 몇 개 행의 헤더 가능성 확인
    skip_rows = 0
    for i in range(min(10, len(df))):
        if any(col in str(df.iloc[i].values) for col in ['회원명', '회원번호', '상품명']):
            skip_rows = i + 1
            break

    # 데이터 다시 읽기
    if skip_rows > 0:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, skiprows=skip_rows)

    print(f"\n=== {sheet_name} 분석 ===")
    print(f"데이터 건수: {len(df)}행")
    print(f"컬럼: {list(df.columns)}")

    # 금액 관련 컬럼 찾기
    amount_columns = []
    for col in df.columns:
        if any(keyword in str(col) for keyword in ['금액', '결제', '매출', '가격']):
            amount_columns.append(col)

    if amount_columns:
        print(f"금액 컬럼: {amount_columns}")
        for col in amount_columns:
            try:
                # 숫자 변환 시도
                amounts = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.replace('원', ''), errors='coerce')
                total = amounts.sum()
                if total > 0:
                    print(f"  - {col} 합계: {total:,.0f}원")
            except:
                pass

    # 데이터 샘플 출력
    print("\n데이터 샘플 (처음 3행):")
    print(df.head(3).to_string())

    return df

def upload_sheet_data(sheet_name, df):
    """시트 데이터를 API로 업로드"""
    # 월 추출 (예: "23년 4월" -> 4)
    month_str = sheet_name.replace("23년", "").strip()
    month = int(month_str.replace("월", "").strip())

    # 데이터 준비
    data_to_upload = []

    for _, row in df.iterrows():
        try:
            # 회원명이 없으면 건너뛰기
            customer_name = str(row.get('회원명', '')).strip()
            if not customer_name or customer_name == 'nan':
                continue

            # 금액 찾기
            amount = 0
            for col in df.columns:
                if any(keyword in str(col) for keyword in ['결제금액', '금액', '매출액']):
                    try:
                        amount_str = str(row[col]).replace(',', '').replace('원', '').strip()
                        if amount_str and amount_str != 'nan':
                            amount = int(float(amount_str))
                            break
                    except:
                        continue

            if amount <= 0:
                continue

            # 데이터 구성
            payment_data = {
                "customer_name": customer_name,
                "customer_number": str(row.get('회원번호', '')).strip() if pd.notna(row.get('회원번호')) else "",
                "product_name": str(row.get('상품명', '')).strip() if pd.notna(row.get('상품명')) else "",
                "payment_date": f"2023-{month:02d}-01",  # 월 첫째날로 설정
                "amount": amount,
                "payment_status": str(row.get('결제상태', '완료')).strip() if pd.notna(row.get('결제상태')) else "완료",
                "memo": str(row.get('비고', '')).strip() if pd.notna(row.get('비고')) else ""
            }

            data_to_upload.append(payment_data)

        except Exception as e:
            print(f"행 처리 중 오류: {e}")
            continue

    print(f"\n{sheet_name} 업로드 준비: {len(data_to_upload)}건")

    if not data_to_upload:
        print("업로드할 데이터가 없습니다.")
        return 0

    # API 호출
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/payments/upload",
            json={"payments": data_to_upload}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"업로드 성공: {result['created']}건 생성, {result['updated']}건 업데이트")
            return result['created'] + result['updated']
        else:
            print(f"업로드 실패: {response.status_code}")
            print(response.text)
            return 0

    except Exception as e:
        print(f"API 호출 중 오류: {e}")
        return 0

def verify_upload():
    """업로드된 데이터 검증"""
    print("\n=== 2023년 데이터 검증 ===")

    try:
        # 2023년 데이터 조회
        response = requests.get(
            f"{API_BASE_URL}/api/payments",
            params={
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        )

        if response.status_code == 200:
            data = response.json()

            # 월별 집계
            monthly_summary = {}
            total_amount = 0

            for payment in data:
                date = datetime.fromisoformat(payment['payment_date'])
                month_key = f"{date.year}년 {date.month}월"

                if month_key not in monthly_summary:
                    monthly_summary[month_key] = {"count": 0, "amount": 0}

                monthly_summary[month_key]["count"] += 1
                monthly_summary[month_key]["amount"] += payment['amount']
                total_amount += payment['amount']

            print(f"\n2023년 전체: {len(data)}건, {total_amount:,}원")

            print("\n월별 현황:")
            for month in sorted(monthly_summary.keys()):
                summary = monthly_summary[month]
                print(f"  {month}: {summary['count']}건, {summary['amount']:,}원")

        else:
            print(f"데이터 조회 실패: {response.status_code}")

    except Exception as e:
        print(f"검증 중 오류: {e}")

def main():
    """메인 실행 함수"""
    print("=== 2023년 결제 데이터 업로드 시작 ===")

    # 1. 시트 찾기
    excel_file, sheets_2023 = find_2023_sheets()

    if not sheets_2023:
        print("\n'23년'으로 시작하는 시트를 찾을 수 없습니다.")
        return

    # 2. 각 시트 분석 및 업로드
    total_uploaded = 0

    for sheet_name in sorted(sheets_2023):
        # 데이터 분석
        df = analyze_sheet_data(excel_file, sheet_name)

        # 데이터가 있으면 업로드
        if len(df) > 0:
            uploaded = upload_sheet_data(sheet_name, df)
            total_uploaded += uploaded

        print("-" * 50)

    print(f"\n전체 업로드 완료: 총 {total_uploaded}건")

    # 3. 업로드 검증
    verify_upload()

if __name__ == "__main__":
    main()
