import pandas as pd
import sys
import os
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import text
import re
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from models.customer import Customer
from models.package import Package, PackagePurchase
from models.service import ServiceUsage, ServiceType

# 서비스 타입 매핑
SERVICE_TYPE_MAP = {
    "브레인": 1,
    "펄스": 2,
    "림프": 3,
    "레드": 4,
    "상담": 1  # 기본값
}

def extract_service_type_from_details(details):
    """세션 상세 정보에서 서비스 타입 추출"""
    if not details:
        return 1  # 기본값: 상담/브레인

    details_lower = details.lower()

    # 명확한 키워드 우선
    if '하체' in details_lower or 'w/' in details_lower:
        return 3  # 림프
    elif '전신' in details_lower and ('링' in details_lower or '패드' in details_lower):
        return 2  # 펄스
    elif 'h(' in details_lower or '브레인' in details_lower:
        return 1  # 브레인
    elif '주' in details_lower and ('1000' in details_lower or '800' in details_lower):
        return 4  # 레드

    return 1  # 기본값

def migrate_all_customers():
    """전체 고객 데이터 마이그레이션"""

    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025.xlsm'
    xls = pd.ExcelFile(excel_path)

    with Session(engine) as db:
        # 기존 고객 목록 가져오기
        existing_customers = {c.name: c for c in db.query(Customer).all()}
        print(f"기존 고객 수: {len(existing_customers)}명")

        # 통계 초기화
        stats = {
            'new_customers': 0,
            'updated_customers': 0,
            'new_packages': 0,
            'new_services': 0,
            'errors': []
        }

        # 고객별 데이터 수집
        customer_service_data = defaultdict(list)
        customer_package_data = defaultdict(dict)

        # 월별 시트 처리
        monthly_sheets = [sheet for sheet in xls.sheet_names if '년' in sheet and '월' in sheet]

        for sheet_idx, sheet_name in enumerate(monthly_sheets):
            print(f"\n[{sheet_idx+1}/{len(monthly_sheets)}] {sheet_name} 처리 중...")

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

                if '성함' not in df.columns:
                    continue

                # 각 행 처리
                for idx, row in df.iterrows():
                    customer_name = row.get('성함')
                    if pd.isna(customer_name) or customer_name == '성함':
                        continue

                    customer_name = str(customer_name).strip()
                    if not customer_name:
                        continue

                    # 서비스 이용 데이터 수집
                    service_date = row.get('날짜')
                    session_details = row.get('세션 진행 사항', '')
                    package_info = row.get('실행 패키지 \nor 프로모션 ', '')

                    if pd.notna(service_date) and pd.notna(session_details):
                        service_data = {
                            'date': service_date,
                            'details': str(session_details),
                            'package_info': str(package_info) if pd.notna(package_info) else '',
                            'sheet_name': sheet_name
                        }
                        customer_service_data[customer_name].append(service_data)

                    # 패키지 정보 수집 (최신 데이터 우선)
                    if customer_name not in customer_package_data:
                        package_data = {}

                        for service in ['브레인', '펄스', '림프', '레드']:
                            # 잔여횟수
                            for col in df.columns:
                                if service in col and '잔여횟수' in col:
                                    if pd.notna(row[col]):
                                        try:
                                            package_data[f'{service}_remaining'] = int(float(row[col]))
                                        except:
                                            pass

                                # 이용횟수/전체횟수
                                elif service in col and '이용횟수' in col:
                                    usage = row[col]
                                    if pd.notna(usage) and '/' in str(usage):
                                        try:
                                            used, total = str(usage).split('/')
                                            package_data[f'{service}_used'] = int(float(used))
                                            package_data[f'{service}_total'] = int(float(total))
                                        except:
                                            pass

                        if package_data:
                            customer_package_data[customer_name] = package_data

            except Exception as e:
                stats['errors'].append(f"{sheet_name}: {str(e)}")
                print(f"  에러 발생: {e}")

        # 데이터베이스에 저장
        print("\n데이터베이스 저장 시작...")

        # 1. 고객 정보 확인 (전체 고객관리대장에서)
        if '전체 고객관리대장' in xls.sheet_names:
            df_all = pd.read_excel(excel_path, sheet_name='전체 고객관리대장', header=3)

            for idx, row in df_all.iterrows():
                customer_name = row.get('성함')
                if pd.isna(customer_name) or not str(customer_name).strip():
                    continue

                customer_name = str(customer_name).strip()

                # 기존 고객이 없으면 생성
                if customer_name not in existing_customers:
                    customer = Customer(
                        name=customer_name,
                        phone=str(row.get('연락처', '')) if pd.notna(row.get('연락처')) else None,
                        address=str(row.get('거주지역', '')) if pd.notna(row.get('거주지역')) else None,
                        first_visit_date=row.get('첫방문일') if pd.notna(row.get('첫방문일')) else date.today(),
                        notes=str(row.get('비고(메모)', '')) if pd.notna(row.get('비고(메모)')) else None
                    )
                    db.add(customer)
                    stats['new_customers'] += 1
                    existing_customers[customer_name] = customer

            db.commit()
            print(f"  신규 고객 {stats['new_customers']}명 생성")

        # 2. 패키지 생성 및 구매 정보 저장
        print("\n패키지 정보 처리 중...")

        # 기본 패키지 생성
        packages = {}
        for service_name in ['브레인', '펄스', '림프', '레드']:
            package = db.query(Package).filter(Package.package_name.like(f'%{service_name}%')).first()
            if not package:
                package = Package(
                    package_name=f"{service_name} 패키지",
                    total_sessions=24,  # 기본값
                    base_price=960000,
                    valid_months=12,
                    is_active=True,
                    description=f"{service_name} 서비스 패키지"
                )
                db.add(package)
            packages[service_name] = package

        db.commit()

        # 고객별 패키지 구매 정보 저장
        for customer_name, package_data in customer_package_data.items():
            if customer_name not in existing_customers:
                continue

            customer = existing_customers[customer_name]

            # 각 서비스별로 패키지 구매 정보 생성
            for service_name in ['브레인', '펄스', '림프', '레드']:
                total = package_data.get(f'{service_name}_total', 0)
                used = package_data.get(f'{service_name}_used', 0)
                remaining = package_data.get(f'{service_name}_remaining', 0)

                if total > 0 or remaining > 0:
                    # 기존 구매 확인
                    existing_purchase = db.query(PackagePurchase).filter(
                        PackagePurchase.customer_id == customer.customer_id,
                        PackagePurchase.package_id == packages[service_name].package_id
                    ).first()

                    if not existing_purchase:
                        # 새 구매 생성
                        db.execute(text("""
                            INSERT INTO package_purchases
                            (customer_id, package_id, purchase_date, expiry_date,
                             total_sessions, used_sessions, remaining_sessions, price_paid)
                            VALUES (:customer_id, :package_id, :purchase_date, :expiry_date,
                                    :total_sessions, :used_sessions, :remaining_sessions, :price_paid)
                        """), {
                            'customer_id': customer.customer_id,
                            'package_id': packages[service_name].package_id,
                            'purchase_date': date(2024, 1, 1),
                            'expiry_date': date(2025, 12, 31),
                            'total_sessions': total if total > 0 else (used + remaining),
                            'used_sessions': used,
                            'remaining_sessions': remaining,
                            'price_paid': 40000 * (total if total > 0 else (used + remaining))
                        })
                        stats['new_packages'] += 1

        db.commit()
        print(f"  패키지 구매 {stats['new_packages']}건 생성")

        # 3. 서비스 이용 기록 저장
        print("\n서비스 이용 기록 처리 중...")

        batch_size = 100
        service_batch = []

        for customer_name, services in customer_service_data.items():
            if customer_name not in existing_customers:
                continue

            customer = existing_customers[customer_name]

            for service in services:
                try:
                    service_date = service['date']
                    if isinstance(service_date, str):
                        service_date = datetime.strptime(service_date, '%Y-%m-%d').date()
                    elif hasattr(service_date, 'date'):
                        service_date = service_date.date()

                    service_type_id = extract_service_type_from_details(service['details'])

                    service_batch.append({
                        'customer_id': customer.customer_id,
                        'service_date': service_date,
                        'service_type_id': service_type_id,
                        'session_details': service['details'],
                        'created_by': 'migration'
                    })

                    # 배치 처리
                    if len(service_batch) >= batch_size:
                        db.execute(text("""
                            INSERT INTO service_usage
                            (customer_id, service_date, service_type_id, session_details, created_by)
                            VALUES (:customer_id, :service_date, :service_type_id, :session_details, :created_by)
                        """), service_batch)
                        stats['new_services'] += len(service_batch)
                        service_batch = []

                except Exception as e:
                    stats['errors'].append(f"서비스 기록 오류 ({customer_name}): {str(e)}")

        # 남은 배치 처리
        if service_batch:
            db.execute(text("""
                INSERT INTO service_usage
                (customer_id, service_date, service_type_id, session_details, created_by)
                VALUES (:customer_id, :service_date, :service_type_id, :session_details, :created_by)
            """), service_batch)
            stats['new_services'] += len(service_batch)

        db.commit()
        print(f"  서비스 이용 기록 {stats['new_services']}건 생성")

        # 결과 출력
        print("\n=== 마이그레이션 완료 ===")
        print(f"신규 고객: {stats['new_customers']}명")
        print(f"패키지 구매: {stats['new_packages']}건")
        print(f"서비스 이용 기록: {stats['new_services']}건")

        if stats['errors']:
            print(f"\n에러 발생: {len(stats['errors'])}건")
            for error in stats['errors'][:10]:
                print(f"  - {error}")
            if len(stats['errors']) > 10:
                print(f"  ... 외 {len(stats['errors']) - 10}건")

        # 마이그레이션 결과 저장
        report_path = '/Users/vibetj/coding/center/docs/migration_report.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"전체 고객 데이터 마이그레이션 보고서\n")
            f.write(f"실행 일시: {datetime.now()}\n")
            f.write(f"={'='*50}\n\n")
            f.write(f"신규 고객: {stats['new_customers']}명\n")
            f.write(f"패키지 구매: {stats['new_packages']}건\n")
            f.write(f"서비스 이용 기록: {stats['new_services']}건\n")
            f.write(f"에러: {len(stats['errors'])}건\n")

        print(f"\n마이그레이션 보고서: {report_path}")

if __name__ == "__main__":
    print("전체 고객 데이터 마이그레이션 시작...")
    print("이 작업은 시간이 걸릴 수 있습니다...")
    migrate_all_customers()
    print("\n완료!")
