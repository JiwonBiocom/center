#!/usr/bin/env python3
"""Railway 배포 상태를 확인하는 스크립트"""

import requests
import subprocess
import json
import time
from datetime import datetime

def get_local_commit():
    """로컬 최신 커밋 SHA 가져오기"""
    result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True)
    return result.stdout.strip()

def check_railway_health():
    """Railway 배포 상태 확인"""
    url = "https://center-production-1421.up.railway.app/health"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        return None

def main():
    print("🚂 Railway 배포 상태 확인")
    print("=" * 50)

    local_commit = get_local_commit()
    print(f"📍 로컬 최신 커밋: {local_commit}")

    print("\n⏳ Railway 서버 확인 중...")
    health_data = check_railway_health()

    if health_data:
        deployed_commit = health_data.get('commit_sha', 'unknown')
        deploy_id = health_data.get('deploy_id', 'unknown')

        print(f"\n✅ Railway 서버 상태:")
        print(f"   - 상태: {health_data.get('status', 'unknown')}")
        print(f"   - 배포된 커밋: {deployed_commit}")
        print(f"   - 배포 ID: {deploy_id}")
        print(f"   - 빌드 시간: {health_data.get('build_time', 'unknown')}")

        # 환경변수 체크
        env_check = health_data.get('env_check', {})
        if env_check:
            print(f"\n📌 Railway 환경변수:")
            for key, value in env_check.items():
                print(f"   - {key}: {value}")

        # 짧은 SHA와 긴 SHA 모두 비교
        if deployed_commit.startswith(local_commit) or local_commit.startswith(deployed_commit[:7]):
            print(f"\n🎉 최신 버전이 정상적으로 배포되었습니다!")
            print(f"   - 커밋 SHA: {deployed_commit[:7]}")
        else:
            print(f"\n⚠️  경고: Railway가 구형 버전을 사용 중입니다!")
            print(f"   - 예상: {local_commit}")
            print(f"   - 실제: {deployed_commit[:7]}")
            print(f"\n💡 해결 방법:")
            print(f"   1. Railway 대시보드에서 'Clear build cache' 클릭")
            print(f"   2. 'Redeploy' 버튼 클릭")
            print(f"   3. 또는 railway up --service backend 실행")
    else:
        print("\n❌ Railway 서버에 연결할 수 없습니다.")
        print("   - 배포가 진행 중이거나")
        print("   - 서버가 다운되었을 수 있습니다.")

    # Response headers 확인
    print("\n📋 응답 헤더 확인:")
    try:
        response = requests.head(url, timeout=10)
        commit_header = response.headers.get('x-commit-sha', 'Not found')
        deploy_header = response.headers.get('x-deploy-id', 'Not found')
        print(f"   - x-commit-sha: {commit_header}")
        print(f"   - x-deploy-id: {deploy_header}")
    except:
        print("   - 헤더를 확인할 수 없습니다.")

if __name__ == "__main__":
    main()
