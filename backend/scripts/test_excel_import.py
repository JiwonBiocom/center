import requests
import os
from pathlib import Path

# 테스트할 파일들
test_files = [
    '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025_테스트.xlsx',
    '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025_테스트.xlsm'
]

# API 엔드포인트
url = 'http://localhost:8000/api/v1/customers/import/excel/'

for file_path in test_files:
    if not os.path.exists(file_path):
        print(f"파일이 존재하지 않습니다: {file_path}")
        continue

    print(f"\n{'='*60}")
    print(f"테스트 파일: {Path(file_path).name}")
    print(f"{'='*60}")

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, files=files)

        print(f"상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공적으로 처리됨")
            print(f"   - 성공: {data.get('success_count', 0)}건")
            print(f"   - 실패: {data.get('error_count', 0)}건")
            if data.get('errors'):
                print(f"   - 에러 내역:")
                for error in data['errors'][:5]:
                    print(f"     • {error}")
        else:
            print(f"❌ 처리 실패")
            print(f"   에러: {response.text}")

    except Exception as e:
        print(f"❌ 예외 발생: {str(e)}")

print("\n테스트 완료!")
