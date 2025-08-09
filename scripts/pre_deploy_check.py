#!/usr/bin/env python3
"""
배포 전 필수 체크 스크립트

이 스크립트는 배포 전에 반드시 실행되어야 합니다.
Enum 불일치나 API 경로 문제가 있으면 배포를 중단합니다.
"""
import subprocess
import sys
import os

def run_check(command, description):
    """체크 명령 실행"""
    print(f"\n🔍 {description}...")
    print("=" * 60)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ {description} FAILED!")
        print(result.stdout)
        print(result.stderr)
        return False
    
    print(result.stdout)
    print(f"✅ {description} PASSED!")
    return True

def main():
    print("🚀 Pre-deployment Checks")
    print("=" * 80)
    
    checks = [
        ("python scripts/check_enum_values.py", "Enum Consistency Check"),
        ("python scripts/check_api_routes.py", "API Route Consistency Check"),
        ("python -m py_compile backend/**/*.py", "Python Syntax Check"),
    ]
    
    all_passed = True
    
    for command, description in checks:
        if not run_check(command, description):
            all_passed = False
    
    print("\n" + "=" * 80)
    
    if all_passed:
        print("✅ All pre-deployment checks PASSED!")
        print("🚀 Safe to deploy!")
        sys.exit(0)
    else:
        print("❌ Pre-deployment checks FAILED!")
        print("🛑 DO NOT DEPLOY! Fix the issues above first.")
        sys.exit(1)

if __name__ == "__main__":
    # Railway/Vercel 환경에서는 스킵 (프로덕션 빌드 시)
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("VERCEL"):
        print("⏭️  Skipping pre-deploy checks in production build")
        sys.exit(0)
    
    main()