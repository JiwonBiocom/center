#!/usr/bin/env python3
"""
간단한 로딩 시간 측정
"""
import time
import requests

# API 성능 측정
print("🚀 고객 관리 API 성능 측정")
print("=" * 50)

# 1. 기본 정렬 (최근 방문 순) 테스트
params = {
    "skip": 0,
    "limit": 20,
    "sort_by": "last_visit_date",
    "sort_order": "desc"
}

times = []
for i in range(10):
    start = time.time()
    response = requests.get("http://localhost:8000/api/v1/customers/", params=params)
    elapsed = time.time() - start
    times.append(elapsed)
    print(f"시도 {i+1}: {elapsed:.3f}초 (상태: {response.status_code})")

avg_time = sum(times) / len(times)
min_time = min(times)
max_time = max(times)

print(f"\n📊 결과 분석:")
print(f"평균 응답 시간: {avg_time:.3f}초")
print(f"최소 응답 시간: {min_time:.3f}초")
print(f"최대 응답 시간: {max_time:.3f}초")

# 성능 평가
if avg_time < 0.1:
    evaluation = "⚡ 매우 빠름 (100ms 미만)"
    recommendation = "현재 성능이 매우 우수합니다."
elif avg_time < 0.3:
    evaluation = "✅ 빠름 (300ms 미만)"
    recommendation = "사용자가 지연을 거의 느끼지 못하는 수준입니다."
elif avg_time < 0.5:
    evaluation = "🔶 보통 (500ms 미만)"
    recommendation = "약간의 최적화가 필요할 수 있습니다."
elif avg_time < 1.0:
    evaluation = "⚠️ 느림 (1초 미만)"
    recommendation = "사용자가 지연을 느낄 수 있습니다. 최적화 필요."
else:
    evaluation = "❌ 매우 느림 (1초 이상)"
    recommendation = "심각한 성능 문제. 즉시 최적화 필요."

print(f"\n평가: {evaluation}")
print(f"권장사항: {recommendation}")

# 데이터 확인
if response.status_code == 200:
    data = response.json()
    print(f"\n📊 데이터 정보:")
    print(f"반환된 고객 수: {len(data.get('data', []))}개")
    print(f"전체 고객 수: {data.get('total', 'N/A')}명")
    
    # 첫 번째 고객의 방문일 확인 (정렬 확인)
    if data.get('data'):
        first_customer = data['data'][0]
        print(f"\n🔍 정렬 확인 (첫 번째 고객):")
        print(f"이름: {first_customer.get('name')}")
        print(f"최근 방문일: {first_customer.get('last_visit_date', '없음')}")
        
        # 정렬이 제대로 되었는지 확인
        if len(data['data']) > 1:
            dates_sorted = True
            for i in range(len(data['data']) - 1):
                current = data['data'][i].get('last_visit_date')
                next_item = data['data'][i+1].get('last_visit_date')
                if current and next_item and current < next_item:
                    dates_sorted = False
                    break
            
            if dates_sorted:
                print("✅ 최근 방문일 기준 내림차순 정렬 확인")
            else:
                print("❌ 정렬 순서 문제 발견")

# 2. 정렬 없는 기본 조회와 비교
print("\n" + "=" * 50)
print("🔍 정렬 없는 기본 조회와 비교")

params_no_sort = {"skip": 0, "limit": 20}
start = time.time()
response_no_sort = requests.get("http://localhost:8000/api/v1/customers/", params=params_no_sort)
elapsed_no_sort = time.time() - start

print(f"정렬 없음: {elapsed_no_sort:.3f}초")
print(f"정렬 있음: {avg_time:.3f}초")
print(f"차이: {abs(avg_time - elapsed_no_sort):.3f}초")

if abs(avg_time - elapsed_no_sort) < 0.01:
    print("✅ 정렬로 인한 성능 영향 거의 없음")