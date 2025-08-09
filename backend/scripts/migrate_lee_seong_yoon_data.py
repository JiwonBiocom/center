import pandas as pd
import sys
import os
from datetime import datetime, date
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine
from models.customer import Customer
from models.package import Package, PackagePurchase
from models.service import ServiceUsage

def find_service_data_for_customer(customer_name):
    """모든 월별 시트에서 고객의 서비스 이용 데이터 찾기"""
    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025.xlsm'
    xls = pd.ExcelFile(excel_path)

    all_service_data = []

    for sheet_name in xls.sheet_names:
        if '년' in sheet_name and '월' in sheet_name:  # 월별 시트만
            try:
                # 각 시트마다 헤더 위치가 다를 수 있으므로 처음 몇 행을 확인
                df_raw = pd.read_excel(excel_path, sheet_name=sheet_name, header=None, nrows=10)

                # '성함' 컬럼이 있는 행 찾기
                header_row = None
                for i in range(10):
                    row_values = df_raw.iloc[i].astype(str)
                    if '성함' in row_values.values:
                        header_row = i
                        break

                if header_row is None:
                    continue

                # 실제 데이터 읽기
                df = pd.read_excel(excel_path, sheet_name=sheet_name, header=header_row)

                # 고객 데이터 찾기
                if '성함' in df.columns:
                    customer_data = df[df['성함'] == customer_name]
                    if len(customer_data) > 0:
                        print(f"\\n{sheet_name}에서 {customer_name} 고객 데이터 {len(customer_data)}건 발견")

                        for idx, row in customer_data.iterrows():
                            service_info = {
                                'sheet_name': sheet_name,
                                'date': row.get('날짜'),
                                'package_info': row.get('실행 패키지 \\nor 프로모션 '),
                                'session_details': row.get('세션 진행 사항'),
                                'special_notes': row.get('특이사항'),
                                'consultation': row.get('상담내용(Q&A 형태로 작성)'),
                                'main_service': row.get('주 관심 서비스'),
                                'brain_remaining': row.get('브레인\\n잔여횟수'),
                                'pulse_remaining': row.get('펄스\\n잔여횟수'),
                                'lymph_remaining': row.get('림프\\n잔여횟수'),
                                'red_remaining': row.get('레드\\n잔여횟수'),
                                'brain_usage': row.get('브레인\\n(이용횟수/전체횟수)'),
                                'pulse_usage': row.get('펄스\\n(이용횟수/전체횟수)'),
                                'lymph_usage': row.get('림프\\n(이용횟수/전체횟수)'),
                                'red_usage': row.get('레드\\n(이용횟수/전체횟수)')
                            }
                            all_service_data.append(service_info)

            except Exception as e:
                print(f"{sheet_name} 처리 중 에러: {e}")
                continue

    return all_service_data

def migrate_lee_seong_yoon_data():
    """이성윤 고객 데이터 마이그레이션"""

    with Session(engine) as db:
        # 1. 이성윤 고객 찾기
        customer = db.query(Customer).filter(Customer.name == '이성윤').first()
        if not customer:
            print("이성윤 고객을 찾을 수 없습니다.")
            return

        print(f"이성윤 고객 ID: {customer.customer_id}")

        # 2. 모든 월별 시트에서 서비스 데이터 찾기
        service_data_list = find_service_data_for_customer('이성윤')
        print(f"\\n총 {len(service_data_list)}건의 서비스 이용 기록 발견")

        # 3. 패키지 정보 파싱 및 생성
        package_info = {}
        for data in service_data_list:
            if data['package_info'] and pd.notna(data['package_info']):
                package_str = str(data['package_info'])
                # 간단한 패키지 이름 추출 (실제로는 더 복잡한 파싱 필요)
                if '패키지' in package_str or '프로모션' in package_str:
                    package_name = package_str.strip()
                    if package_name not in package_info:
                        package_info[package_name] = {
                            'first_date': data['date'],
                            'sessions': []
                        }
                    package_info[package_name]['sessions'].append(data)

        # 4. 패키지 구매 기록 생성
        for package_name, info in package_info.items():
            # 패키지가 없으면 생성
            package = db.query(Package).filter(Package.package_name == package_name).first()
            if not package:
                package = Package(
                    package_name=package_name,
                    total_sessions=44,  # 기본값 (11*4)
                    base_price=1000000,  # 기본값
                    valid_months=12,
                    is_active=True
                )
                db.add(package)
                db.commit()
                print(f"패키지 생성: {package_name}")

            # 패키지 구매 기록 생성
            purchase_date = info['first_date'] if pd.notna(info['first_date']) else date(2023, 1, 1)
            if isinstance(purchase_date, str):
                try:
                    purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                except:
                    purchase_date = date(2023, 1, 1)

            purchase = PackagePurchase(
                customer_id=customer.customer_id,
                package_id=package.package_id,
                purchase_date=purchase_date,
                expiry_date=date(2025, 12, 31),  # 임시 만료일
                total_sessions=44,
                used_sessions=0,
                remaining_sessions=44,
                price_paid=1000000
            )
            db.add(purchase)
            db.commit()
            print(f"패키지 구매 기록 생성: {package_name}")

        # 5. 서비스 이용 기록 생성
        for data in service_data_list:
            if data['session_details'] and pd.notna(data['session_details']):
                service_date = data['date'] if pd.notna(data['date']) else date(2023, 1, 1)
                if isinstance(service_date, str):
                    try:
                        service_date = datetime.strptime(service_date, '%Y-%m-%d').date()
                    except:
                        service_date = date(2023, 1, 1)

                # 서비스 타입 추측
                session_details = str(data['session_details'])
                service_type_id = 1  # 기본값
                if '브레인' in session_details:
                    service_type_id = 1
                elif '펄스' in session_details:
                    service_type_id = 2
                elif '림프' in session_details:
                    service_type_id = 3
                elif '레드' in session_details:
                    service_type_id = 4

                usage = ServiceUsage(
                    customer_id=customer.customer_id,
                    service_date=service_date,
                    service_type_id=service_type_id,
                    session_details=session_details,
                    created_by='migration'
                )
                db.add(usage)

        db.commit()
        print("\\n서비스 이용 기록 마이그레이션 완료")

        # 6. 결과 확인
        usage_count = db.query(ServiceUsage).filter(
            ServiceUsage.customer_id == customer.customer_id
        ).count()
        print(f"\\n이성윤 고객의 총 서비스 이용 기록: {usage_count}건")

if __name__ == "__main__":
    print("이성윤 고객 데이터 마이그레이션 시작...")
    migrate_lee_seong_yoon_data()
    print("\\n완료!")
