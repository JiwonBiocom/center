#!/usr/bin/env python3
"""
패키지 마스터 데이터 마이그레이션
로컬 SQLite → Supabase PostgreSQL
"""
import sqlite3
import psycopg2
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Supabase 연결 URL"""
    # GitHub Actions에서 사용한 것과 동일
    return "postgresql://postgres.wvcxzyvmwwrbjpeuyvuh:bico6819!!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def migrate_packages():
    """패키지 데이터 마이그레이션"""
    
    print("🚀 패키지 마스터 데이터 마이그레이션 시작")
    print("=" * 70)
    
    # 로컬 DB 연결
    local_db = Path("backend/aibio_center.db")
    if not local_db.exists():
        print("❌ 로컬 DB를 찾을 수 없습니다.")
        return False
    
    local_conn = sqlite3.connect(local_db)
    local_cursor = local_conn.cursor()
    
    # Supabase 연결
    try:
        remote_conn = psycopg2.connect(get_database_url())
        remote_cursor = remote_conn.cursor()
        
        # 1. 로컬 패키지 데이터 조회
        print("\n📋 로컬 패키지 데이터 조회 중...")
        local_cursor.execute("""
            SELECT package_id, package_name, total_sessions, price, 
                   valid_days, description, created_at, is_active
            FROM packages
            ORDER BY package_id
        """)
        
        local_packages = local_cursor.fetchall()
        print(f"✅ 로컬에서 {len(local_packages)}개 패키지 발견")
        
        # 2. 현재 온라인 패키지 확인
        remote_cursor.execute("SELECT COUNT(*) FROM packages")
        online_count = remote_cursor.fetchone()[0]
        print(f"📊 현재 온라인 패키지: {online_count}개")
        
        # 3. 패키지 데이터 표시
        print("\n📦 마이그레이션할 패키지 목록:")
        print("-" * 70)
        for pkg in local_packages:
            print(f"ID: {pkg[0]} | {pkg[1]}")
            print(f"   - 횟수: {pkg[2]}회 | 가격: ₩{pkg[3]:,} | 유효기간: {pkg[4]}일")
            print(f"   - 설명: {pkg[5]}")
            print(f"   - 활성: {'✅' if pkg[7] else '❌'}")
        
        # 4. 사용자 확인
        print("\n" + "=" * 70)
        print("⚠️  주의: 기존 온라인 패키지 데이터가 대체됩니다!")
        print("계속하시려면 'yes'를 입력하세요:")
        
        confirm = input().strip().lower()
        if confirm != 'yes':
            print("❌ 마이그레이션 취소됨")
            return False
        
        # 5. 기존 데이터 삭제 (선택적)
        print("\n🗑️  기존 패키지 데이터 삭제 중...")
        remote_cursor.execute("DELETE FROM packages")
        
        # 6. 새 데이터 삽입
        print("\n📥 패키지 데이터 삽입 중...")
        insert_query = """
            INSERT INTO packages 
            (package_id, package_name, total_sessions, price, valid_days, 
             description, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        success_count = 0
        for pkg in local_packages:
            try:
                # package_id를 그대로 사용
                remote_cursor.execute(insert_query, (
                    pkg[0],  # package_id
                    pkg[1],  # package_name
                    pkg[2],  # total_sessions
                    float(pkg[3]),  # price
                    pkg[4],  # valid_days
                    pkg[5],  # description
                    bool(pkg[7]),  # is_active
                    pkg[6] or 'NOW()'  # created_at
                ))
                success_count += 1
                print(f"   ✅ {pkg[1]} 추가됨")
            except Exception as e:
                print(f"   ❌ {pkg[1]} 실패: {e}")
        
        # 7. 시퀀스 재설정
        remote_cursor.execute("""
            SELECT setval('packages_package_id_seq', 
                         (SELECT MAX(package_id) FROM packages), true)
        """)
        
        # 8. 커밋
        remote_conn.commit()
        print(f"\n✅ 마이그레이션 완료! {success_count}개 패키지 추가됨")
        
        # 9. 검증
        remote_cursor.execute("""
            SELECT package_name, total_sessions, price 
            FROM packages 
            ORDER BY price DESC
        """)
        
        print("\n📊 온라인 패키지 확인:")
        for pkg in remote_cursor.fetchall():
            print(f"   - {pkg[0]}: {pkg[1]}회, ₩{pkg[2]:,.0f}")
        
        # 연결 종료
        local_conn.close()
        remote_cursor.close()
        remote_conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    migrate_packages()