import pandas as pd
import sys
import os
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from models.customer import Customer
from models.package import Package, PackagePurchase
from models.service import ServiceUsage

def extract_package_info_from_excel():
    """엑셀에서 이성윤 고객의 패키지 정보 추출"""

    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025.xlsm'
    xls = pd.ExcelFile(excel_path)

    package_info = {
        '브레인': {'total': 0, 'used': 0, 'remaining': 0},
        '펄스': {'total': 0, 'used': 0, 'remaining': 0},
        '림프': {'total': 0, 'used': 0, 'remaining': 0},
        '레드': {'total': 0, 'used': 0, 'remaining': 0}
    }

    # 최신 월별 시트에서 패키지 정보 찾기
    for sheet_name in ['2025년5월', '2025년4월', '2025년3월']:
        if sheet_name not in xls.sheet_names:
            continue

        try:
            # 헤더 찾기
            df_raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=None, nrows=20)

            header_row = None
            for i in range(20):
                row_values = df_raw.iloc[i].astype(str)
                if '성함' in row_values.values:
                    header_row = i
                    break

            if header_row is None:
                continue

            # 데이터 읽기
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row)

            # 이성윤 고객 찾기
            if '성함' in df.columns:
                lee_data = df[df['성함'] == '이성윤']

                if len(lee_data) > 0:
                    # 가장 최근 데이터 사용
                    latest_row = lee_data.iloc[-1]

                    # 잔여횟수 추출
                    for col in df.columns:
                        if '브레인' in col and '잔여횟수' in col:
                            remaining = latest_row[col]
                            if pd.notna(remaining) and str(remaining).replace('.', '').isdigit():
                                package_info['브레인']['remaining'] = int(float(remaining))
                        elif '펄스' in col and '잔여횟수' in col:
                            remaining = latest_row[col]
                            if pd.notna(remaining) and str(remaining).replace('.', '').isdigit():
                                package_info['펄스']['remaining'] = int(float(remaining))
                        elif '림프' in col and '잔여횟수' in col:
                            remaining = latest_row[col]
                            if pd.notna(remaining) and str(remaining).replace('.', '').isdigit():
                                package_info['림프']['remaining'] = int(float(remaining))
                        elif '레드' in col and '잔여횟수' in col:
                            remaining = latest_row[col]
                            if pd.notna(remaining) and str(remaining).replace('.', '').isdigit():
                                package_info['레드']['remaining'] = int(float(remaining))

                    # 이용횟수/전체횟수 추출
                    for col in df.columns:
                        if '브레인' in col and '이용횟수' in col:
                            usage = latest_row[col]
                            if pd.notna(usage) and '/' in str(usage):
                                used, total = str(usage).split('/')
                                package_info['브레인']['used'] = int(float(used))
                                package_info['브레인']['total'] = int(float(total))
                        elif '펄스' in col and '이용횟수' in col:
                            usage = latest_row[col]
                            if pd.notna(usage) and '/' in str(usage):
                                used, total = str(usage).split('/')
                                package_info['펄스']['used'] = int(float(used))
                                package_info['펄스']['total'] = int(float(total))
                        elif '림프' in col and '이용횟수' in col:
                            usage = latest_row[col]
                            if pd.notna(usage) and '/' in str(usage):
                                used, total = str(usage).split('/')
                                package_info['림프']['used'] = int(float(used))
                                package_info['림프']['total'] = int(float(total))
                        elif '레드' in col and '이용횟수' in col:
                            usage = latest_row[col]
                            if pd.notna(usage) and '/' in str(usage):
                                used, total = str(usage).split('/')
                                package_info['레드']['used'] = int(float(used))
                                package_info['레드']['total'] = int(float(total))

                    # 데이터가 있으면 종료
                    if any(info['total'] > 0 for info in package_info.values()):
                        print(f"{sheet_name}에서 패키지 정보 추출 완료")
                        break

        except Exception as e:
            print(f"{sheet_name} 처리 중 에러: {e}")
            continue

    return package_info

def create_package_purchases():
    """이성윤 고객의 패키지 구매 정보 생성"""

    with Session(engine) as db:
        # 이성윤 고객 찾기
        customer = db.query(Customer).filter(Customer.name == '이성윤').first()
        if not customer:
            print("이성윤 고객을 찾을 수 없습니다.")
            return

        print(f"이성윤 고객 ID: {customer.customer_id}")

        # 엑셀에서 패키지 정보 추출
        package_info = extract_package_info_from_excel()

        print("\n추출된 패키지 정보:")
        for service_type, info in package_info.items():
            if info['total'] > 0:
                print(f"  {service_type}: 전체 {info['total']}회, 사용 {info['used']}회, 잔여 {info['remaining']}회")

        # 통합 패키지 생성 (이성윤 고객은 통합 패키지를 사용하는 것으로 보임)
        package_name = "AI-BIO 통합 케어 패키지"
        package = db.query(Package).filter(Package.package_name == package_name).first()

        if not package:
            # 전체 세션 수 계산
            total_sessions = sum(info['total'] for info in package_info.values())

            package = Package(
                package_name=package_name,
                total_sessions=total_sessions if total_sessions > 0 else 44,
                base_price=2000000,  # 임시 가격
                valid_months=12,
                is_active=True,
                description="브레인, 펄스, 림프, 레드 통합 패키지"
            )
            db.add(package)
            db.commit()
            print(f"\n패키지 생성: {package_name}")

        # 기존 패키지 구매 확인
        existing_purchase = db.query(PackagePurchase).filter(
            PackagePurchase.customer_id == customer.customer_id,
            PackagePurchase.package_id == package.package_id
        ).first()

        if existing_purchase:
            print("기존 패키지 구매 정보가 있습니다. 업데이트합니다.")
            # 사용 횟수 업데이트
            total_used = sum(info['used'] for info in package_info.values())
            total_remaining = sum(info['remaining'] for info in package_info.values())
            total_sessions = sum(info['total'] for info in package_info.values())

            existing_purchase.total_sessions = total_sessions if total_sessions > 0 else existing_purchase.total_sessions
            existing_purchase.used_sessions = total_used
            existing_purchase.remaining_sessions = total_remaining
        else:
            # 새 패키지 구매 생성
            total_used = sum(info['used'] for info in package_info.values())
            total_remaining = sum(info['remaining'] for info in package_info.values())
            total_sessions = sum(info['total'] for info in package_info.values())

            # 직접 SQL로 삽입 (price_paid 필드 문제 해결)
            db.execute(text("""
                INSERT INTO package_purchases
                (customer_id, package_id, purchase_date, expiry_date, total_sessions, used_sessions, remaining_sessions, price_paid)
                VALUES (:customer_id, :package_id, :purchase_date, :expiry_date, :total_sessions, :used_sessions, :remaining_sessions, :price_paid)
            """), {
                'customer_id': customer.customer_id,
                'package_id': package.package_id,
                'purchase_date': date(2023, 1, 1),
                'expiry_date': date(2025, 12, 31),
                'total_sessions': total_sessions if total_sessions > 0 else 44,
                'used_sessions': total_used,
                'remaining_sessions': total_remaining,
                'price_paid': 2000000  # 임시 가격
            })
            print("\n패키지 구매 정보 생성 완료")

        db.commit()

        # 서비스별 사용 정보 업데이트
        # 기존 서비스 사용 기록에 서비스 타입 업데이트
        service_usage_list = db.query(ServiceUsage).filter(
            ServiceUsage.customer_id == customer.customer_id
        ).all()

        print(f"\n서비스 이용 기록 {len(service_usage_list)}건에 서비스 타입 업데이트 중...")

        for usage in service_usage_list:
            if usage.session_details:
                details = usage.session_details.lower()
                if '하체' in details or 'w/' in details:
                    usage.service_type_id = 3  # 림프
                elif '전신' in details and ('링' in details or '패드' in details):
                    usage.service_type_id = 2  # 펄스
                elif 'h(' in details or '브레인' in details:
                    usage.service_type_id = 1  # 브레인
                elif '주' in details and '1000' in details:
                    usage.service_type_id = 4  # 레드

        db.commit()
        print("서비스 타입 업데이트 완료")

if __name__ == "__main__":
    print("이성윤 고객 패키지 정보 마이그레이션 시작...")
    create_package_purchases()
    print("\n완료!")
