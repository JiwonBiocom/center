#!/usr/bin/env python3
"""
CASCADE 옵션을 사용한 6/25 데이터 삭제
"""
import requests

BASE_URL = "http://localhost:8000"

# 6/25 생성 고객 ID 목록
june25_ids = [
    1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109,
    1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120,
    1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130,
    1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139, 1140,
    1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1151, 1156,
    1158, 1159, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167,
    1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177,
    1178, 1181, 1182, 1183, 1184, 1185
]

def delete_customers():
    print("🗑️  6/25 import 데이터 삭제 시작...")
    print(f"  삭제할 고객 수: {len(june25_ids)}명")

    success_count = 0
    failed_ids = []

    for customer_id in june25_ids:
        try:
            # cascade=true 파라미터 추가
            response = requests.delete(f"{BASE_URL}/api/v1/customers/{customer_id}?cascade=true")
            if response.status_code == 200:
                success_count += 1
                print(f"  ✅ ID {customer_id} 삭제 완료")
            else:
                failed_ids.append(customer_id)
                print(f"  ❌ ID {customer_id} 삭제 실패: {response.status_code}")
        except Exception as e:
            failed_ids.append(customer_id)
            print(f"  ❌ ID {customer_id} 에러: {e}")

    print(f"\n📊 삭제 결과:")
    print(f"  - 성공: {success_count}명")
    print(f"  - 실패: {len(failed_ids)}명")

    if failed_ids:
        print(f"  - 실패 ID: {failed_ids}")

def verify_result():
    """최종 결과 확인"""
    response = requests.get(f"{BASE_URL}/api/v1/customers?limit=1")
    data = response.json()
    total = data.get('total', 0)

    print(f"\n🔍 최종 확인:")
    print(f"  - 현재 전체 고객 수: {total}명")
    print(f"  - 원본 엑셀: 950명")
    print(f"  - 차이: {total - 950}명")

if __name__ == "__main__":
    delete_customers()
    verify_result()
