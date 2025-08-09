import pandas as pd
import os
from datetime import datetime
from collections import defaultdict

def analyze_all_customer_data():
    """전체 고객 데이터 분석"""

    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025.xlsm'

    if not os.path.exists(excel_path):
        print(f"엑셀 파일을 찾을 수 없습니다: {excel_path}")
        return

    print(f"엑셀 파일 분석 중: {excel_path}")
    xls = pd.ExcelFile(excel_path)

    # 전체 고객 목록 수집
    all_customers = set()
    customer_data = defaultdict(lambda: {
        'service_count': 0,
        'first_date': None,
        'last_date': None,
        'packages': defaultdict(int),
        'services': defaultdict(int),
        'months': set()
    })

    # 월별 시트 분석
    monthly_sheets = [sheet for sheet in xls.sheet_names if '년' in sheet and '월' in sheet]
    print(f"\n월별 시트 {len(monthly_sheets)}개 발견")

    for sheet_name in monthly_sheets:
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

            # 고객별 데이터 수집
            for idx, row in df.iterrows():
                customer_name = row.get('성함')
                if pd.isna(customer_name) or customer_name == '성함':
                    continue

                customer_name = str(customer_name).strip()
                if not customer_name:
                    continue

                all_customers.add(customer_name)
                customer_data[customer_name]['service_count'] += 1
                customer_data[customer_name]['months'].add(sheet_name)

                # 날짜 처리
                service_date = row.get('날짜')
                if pd.notna(service_date):
                    if customer_data[customer_name]['first_date'] is None:
                        customer_data[customer_name]['first_date'] = service_date
                    customer_data[customer_name]['last_date'] = service_date

                # 패키지 정보 수집
                package_info = row.get('실행 패키지 \nor 프로모션 ', '')
                if pd.notna(package_info):
                    package_str = str(package_info).strip()
                    if package_str:
                        # 서비스 타입별 사용 정보 파싱
                        for service in ['브레인', '펄스', '림프', '레드']:
                            if service in package_str:
                                customer_data[customer_name]['services'][service] += 1

                # 잔여횟수 정보 수집
                for service in ['브레인', '펄스', '림프', '레드']:
                    remaining_col = None
                    usage_col = None

                    for col in df.columns:
                        if service in col and '잔여횟수' in col:
                            remaining_col = col
                        elif service in col and '이용횟수' in col:
                            usage_col = col

                    if remaining_col and pd.notna(row[remaining_col]):
                        try:
                            remaining = int(float(row[remaining_col]))
                            if remaining > 0:
                                customer_data[customer_name]['packages'][f'{service}_잔여'] = remaining
                        except:
                            pass

                    if usage_col and pd.notna(row[usage_col]):
                        usage_str = str(row[usage_col])
                        if '/' in usage_str:
                            try:
                                used, total = usage_str.split('/')
                                customer_data[customer_name]['packages'][f'{service}_사용'] = int(float(used))
                                customer_data[customer_name]['packages'][f'{service}_전체'] = int(float(total))
                            except:
                                pass

        except Exception as e:
            print(f"  {sheet_name} 처리 중 에러: {e}")

    # 전체 고객 관리대장 시트 분석
    if '전체 고객관리대장' in xls.sheet_names:
        df_all = pd.read_excel(excel_path, sheet_name='전체 고객관리대장', header=3)
        if '성함' in df_all.columns:
            for customer in df_all['성함'].dropna().unique():
                if customer and str(customer).strip():
                    all_customers.add(str(customer).strip())

    # 결과 출력
    print(f"\n=== 전체 고객 데이터 분석 결과 ===")
    print(f"총 고객 수: {len(all_customers)}명")
    print(f"서비스 이용 기록이 있는 고객: {len([c for c in customer_data if customer_data[c]['service_count'] > 0])}명")

    # 상위 10명 고객 정보
    sorted_customers = sorted(customer_data.items(),
                            key=lambda x: x[1]['service_count'],
                            reverse=True)[:10]

    print(f"\n서비스 이용 횟수 상위 10명:")
    for customer_name, data in sorted_customers:
        print(f"  {customer_name}: {data['service_count']}회 이용")
        if data['packages']:
            package_info = []
            for service in ['브레인', '펄스', '림프', '레드']:
                if f'{service}_전체' in data['packages']:
                    used = data['packages'].get(f'{service}_사용', 0)
                    total = data['packages'].get(f'{service}_전체', 0)
                    remaining = data['packages'].get(f'{service}_잔여', 0)
                    package_info.append(f"{service} {used}/{total}회 (잔여 {remaining})")
            if package_info:
                print(f"    패키지: {', '.join(package_info)}")

    # 데이터 저장
    summary_path = '/Users/vibetj/coding/center/docs/customer_data_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"전체 고객 데이터 분석 결과\n")
        f.write(f"분석 일시: {datetime.now()}\n")
        f.write(f"={'='*50}\n\n")
        f.write(f"총 고객 수: {len(all_customers)}명\n")
        f.write(f"서비스 이용 기록 고객: {len([c for c in customer_data if customer_data[c]['service_count'] > 0])}명\n\n")

        f.write("전체 고객 목록:\n")
        for customer in sorted(all_customers):
            service_count = customer_data[customer]['service_count']
            f.write(f"  - {customer}: {service_count}회 이용\n")

    print(f"\n분석 결과가 저장되었습니다: {summary_path}")

    return all_customers, customer_data

if __name__ == "__main__":
    print("전체 고객 데이터 분석 시작...")
    all_customers, customer_data = analyze_all_customer_data()
    print("\n분석 완료!")
