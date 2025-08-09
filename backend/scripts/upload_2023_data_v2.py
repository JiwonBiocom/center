#!/usr/bin/env python3
"""2023년 결제 데이터 업로드 스크립트 v2"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import requests
import json
from datetime import datetime

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
        print(f"  - 헤더를 찾을 수 없습니다.")
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

    print(f"\n=== {sheet_name} 파싱 결과 ===")
    print(f"헤더 위치: {header_row}행")
    print(f"데이터 행수: {len(data_df)}행")
    print(f"컬럼: {list(data_df.columns)}")

    return data_df

def extract_payment_data(df, sheet_name):
    """데이터프레임에서 결제 데이터 추출"""
    # 월 추출
    month_str = sheet_name.replace("23년", "").strip()
    month = int(month_str.replace("월", "").strip())

    payments = []

    for _, row in df.iterrows():
        try:
            # 고객명 찾기
            customer_name = None
            for col in ['고객명', '회원명', '성명']:
                if col in df.columns:
                    val = str(row[col]).strip()
                    if val and val != 'nan':
                        customer_name = val
                        break

            if not customer_name:
                continue

            # 금액 찾기
            amount = 0
            for col in ['결제 금액', '결제금액', '금액', '매출액']:
                if col in df.columns:
                    try:
                        amount_str = str(row[col]).replace(',', '').replace('원', '').strip()
                        if amount_str and amount_str != 'nan':
                            amount = int(float(amount_str))
                            break
                    except:
                        continue

            if amount == 0:
                continue

            # 상품명 찾기
            product_name = ""
            for col in ['결제 프로그램', '프로그램', '상품명', '서비스']:
                if col in df.columns:
                    val = str(row[col]).strip()
                    if val and val != 'nan':
                        product_name = val
                        break

            # 결제일자 찾기
            payment_date = f"2023-{month:02d}-01"  # 기본값
            for col in ['결제일자', '결제일', '날짜']:
                if col in df.columns:
                    try:
                        date_val = row[col]
                        if pd.notna(date_val):
                            if isinstance(date_val, datetime):
                                payment_date = date_val.strftime('%Y-%m-%d')
                            elif isinstance(date_val, str) and '2023' in date_val:
                                # 날짜 파싱 시도
                                parsed_date = pd.to_datetime(date_val, errors='coerce')
                                if pd.notna(parsed_date):
                                    payment_date = parsed_date.strftime('%Y-%m-%d')
                            break
                    except:
                        continue

            # 메모 정보 수집
            memo_parts = []

            # 승인번호
            for col in ['승인번호', '승인 번호']:
                if col in df.columns:
                    val = str(row[col]).strip()
                    if val and val != 'nan':
                        memo_parts.append(f"승인번호: {val}")
                        break

            # 담당자
            for col in ['결제 담당자', '담당자']:
                if col in df.columns:
                    val = str(row[col]).strip()
                    if val and val != 'nan':
                        memo_parts.append(f"담당자: {val}")
                        break

            # 기타
            for col in ['기타', '비고', '메모']:
                if col in df.columns:
                    val = str(row[col]).strip()
                    if val and val != 'nan':
                        memo_parts.append(val)
                        break

            payment = {
                "customer_name": customer_name,
                "customer_number": "",  # 23년 데이터에는 회원번호가 없음
                "product_name": product_name,
                "payment_date": payment_date,
                "amount": amount,
                "payment_status": "완료",
                "memo": " / ".join(memo_parts) if memo_parts else ""
            }

            payments.append(payment)

        except Exception as e:
            print(f"  행 처리 중 오류: {e}")
            continue

    return payments

def main():
    """메인 실행 함수"""
    print("=== 2023년 결제 데이터 업로드 v2 ===\n")

    # 엑셀 파일 읽기
    excel_file = pd.ExcelFile(EXCEL_FILE)

    # 23년으로 시작하는 시트 찾기
    sheets_2023 = [sheet for sheet in excel_file.sheet_names if sheet.startswith("23년")]

    print(f"찾은 23년 시트: {len(sheets_2023)}개")
    for sheet in sorted(sheets_2023):
        print(f"  - {sheet}")

    # 전체 데이터 수집
    all_payments = []

    for sheet_name in sorted(sheets_2023):
        print(f"\n{'='*50}")
        print(f"처리 중: {sheet_name}")

        # 데이터 파싱
        df = parse_2023_sheet(excel_file, sheet_name)

        if len(df) == 0:
            print("  - 데이터가 없습니다.")
            continue

        # 결제 데이터 추출
        payments = extract_payment_data(df, sheet_name)

        print(f"\n추출된 결제 건수: {len(payments)}건")

        if payments:
            # 샘플 출력
            print("\n샘플 데이터 (처음 3건):")
            for i, payment in enumerate(payments[:3]):
                print(f"  {i+1}. {payment['customer_name']} - {payment['product_name']} - {payment['amount']:,}원")

            # 금액 합계
            total_amount = sum(p['amount'] for p in payments)
            print(f"\n금액 합계: {total_amount:,}원")

            all_payments.extend(payments)

    print(f"\n{'='*50}")
    print(f"전체 추출 결과: {len(all_payments)}건")

    if not all_payments:
        print("업로드할 데이터가 없습니다.")
        return

    # 월별 요약
    monthly_summary = {}
    for payment in all_payments:
        month = payment['payment_date'][5:7]
        if month not in monthly_summary:
            monthly_summary[month] = {"count": 0, "amount": 0}
        monthly_summary[month]["count"] += 1
        monthly_summary[month]["amount"] += payment['amount']

    print("\n월별 요약:")
    for month in sorted(monthly_summary.keys()):
        summary = monthly_summary[month]
        print(f"  2023년 {int(month)}월: {summary['count']}건, {summary['amount']:,}원")

    # API로 업로드 - 개별 결제 데이터 POST
    print("\n업로드 시작...")
    success_count = 0
    error_count = 0

    for payment in all_payments:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/payments/",
                json=payment
            )

            if response.status_code in [200, 201]:
                success_count += 1
            else:
                error_count += 1
                if error_count <= 3:  # 처음 몇 개 에러만 출력
                    print(f"  에러: {payment['customer_name']} - {response.status_code}")

        except Exception as e:
            error_count += 1
            if error_count <= 3:
                print(f"  예외: {payment['customer_name']} - {e}")

    print(f"\n업로드 완료: 성공 {success_count}건, 실패 {error_count}건")

    # 검증
    print("\n=== 업로드 검증 ===")
    try:
        response = requests.get(
            f"{API_BASE_URL}/payments/",
            params={
                "date_from": "2023-01-01",
                "date_to": "2023-12-31"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"2023년 전체 데이터: {len(data)}건")

            # 월별 확인
            monthly_check = {}
            for payment in data:
                month = payment['payment_date'][5:7]
                if month not in monthly_check:
                    monthly_check[month] = 0
                monthly_check[month] += 1

            print("\n월별 데이터 확인:")
            for month in sorted(monthly_check.keys()):
                print(f"  {int(month)}월: {monthly_check[month]}건")

        else:
            print(f"검증 실패: {response.status_code}")

    except Exception as e:
        print(f"검증 중 오류: {e}")

if __name__ == "__main__":
    main()
