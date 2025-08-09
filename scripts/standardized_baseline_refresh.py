#!/usr/bin/env python3
"""
표준화된 스키마 베이스라인 재생성 절차

TJ님 제안에 따른 단계별 베이스라인 업데이트 프로세스:
1. 모든 마이그레이션 적용 확인
2. 예외 규칙 적용하여 스키마 추출
3. 베이스라인 안전 업데이트
4. 검증 및 커밋 가이드
"""

import os
import sys
import json
import subprocess
import psycopg2
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 추가
sys.path.append(str(Path(__file__).parent.parent))

def check_prerequisites():
    """전제 조건 확인"""
    issues = []
    
    # 1. DATABASE_URL 확인
    if not os.getenv('DATABASE_URL'):
        issues.append("❌ DATABASE_URL 환경변수가 설정되지 않았습니다")
    
    # 2. Git 상태 확인  
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            issues.append("⚠️  Git working directory가 깨끗하지 않습니다 (커밋되지 않은 변경사항 존재)")
    except subprocess.CalledProcessError:
        issues.append("❌ Git 명령어 실행 실패")
    
    # 3. 필수 파일들 확인
    required_files = [
        'backend/alembic/alembic.ini',
        'ci/schema_drift_config.yml'
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"❌ 필수 파일이 없습니다: {file_path}")
    
    return issues

def run_migrations():
    """마이그레이션 실행 및 확인"""
    print("🔄 Step 1: 마이그레이션 상태 확인 및 적용...")
    
    try:
        # 현재 마이그레이션 상태 확인
        os.chdir('backend')
        result = subprocess.run(['alembic', 'current'], 
                              capture_output=True, text=True, check=True)
        current_revision = result.stdout.strip()
        print(f"   현재 마이그레이션: {current_revision}")
        
        # 최신 마이그레이션으로 업그레이드
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, check=True)
        print("   ✅ 마이그레이션 적용 완료")
        
        os.chdir('..')
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 마이그레이션 실패: {e}")
        print(f"   출력: {e.stdout}")
        print(f"   에러: {e.stderr}")
        return False

def extract_filtered_schema():
    """예외 규칙을 적용하여 스키마 추출"""
    print("🔄 Step 2: 필터링된 스키마 추출...")
    
    from check_schema_against_baseline import get_current_schema, should_ignore_table
    
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    
    try:
        # 전체 스키마 조회 (필터링 적용됨)
        schema = get_current_schema(conn)
        
        print(f"   📊 추출된 테이블 수: {len(schema)}개")
        
        # 무시된 테이블 통계
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """)
            all_tables = [row[0] for row in cur.fetchall()]
        
        ignored_tables = [t for t in all_tables if should_ignore_table(t)]
        print(f"   ⏭️  무시된 테이블 수: {len(ignored_tables)}개")
        
        if ignored_tables:
            print("   무시된 테이블 목록:")
            for table in sorted(ignored_tables):
                print(f"      - {table}")
        
        return schema
        
    finally:
        conn.close()

def update_baseline_safely(schema_data):
    """안전한 베이스라인 업데이트"""
    print("🔄 Step 3: 베이스라인 안전 업데이트...")
    
    baseline_path = Path('ci/schema_baseline.json')
    
    # 백업 생성
    if baseline_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = baseline_path.with_suffix(f'.backup.{timestamp}.json')
        backup_path.write_text(baseline_path.read_text(), encoding='utf-8')
        print(f"   📦 기존 베이스라인 백업: {backup_path}")
    
    # 새 베이스라인 구성
    new_baseline = {
        "version": "2.0",
        "generated_at": datetime.now().isoformat(),
        "database": "production",
        "generation_method": "standardized_refresh",
        "exclusion_rules_applied": True,
        "tables": {}
    }
    
    # 스키마 데이터를 베이스라인 형식으로 변환
    for table_name, columns in schema_data.items():
        new_baseline["tables"][table_name] = {
            "columns": [
                {
                    "name": col["name"],
                    "type": col["type"], 
                    "nullable": col["nullable"],
                    "default": None,
                    "max_length": None,
                    "precision": None,
                    "scale": None
                }
                for col in columns
            ],
            "indexes": [],
            "foreign_keys": []
        }
    
    # 새 베이스라인 저장
    baseline_path.parent.mkdir(exist_ok=True)
    with open(baseline_path, 'w', encoding='utf-8') as f:
        json.dump(new_baseline, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ 새 베이스라인 저장 완료: {baseline_path}")
    
    # 통계 출력
    stats = {
        'tables': len(new_baseline['tables']),
        'total_columns': sum(len(table['columns']) for table in new_baseline['tables'].values())
    }
    
    print(f"   📊 베이스라인 통계:")
    print(f"      - 테이블: {stats['tables']}개")
    print(f"      - 총 컬럼: {stats['total_columns']}개")

def verify_baseline():
    """베이스라인 검증"""
    print("🔄 Step 4: 베이스라인 검증...")
    
    try:
        # 스키마 드리프트 검사 실행
        result = subprocess.run(['python', 'scripts/check_schema_against_baseline.py'], 
                              capture_output=True, text=True, check=True)
        
        if "No schema drift detected" in result.stdout:
            print("   ✅ 베이스라인 검증 통과: 드리프트 없음")
            return True
        else:
            print("   ⚠️  베이스라인 검증 실패:")
            print(f"   {result.stdout}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 검증 중 오류 발생: {e}")
        return False

def show_commit_guide():
    """커밋 가이드 출력"""
    print("\n🎯 Step 5: 커밋 가이드")
    print("   다음 명령어로 변경사항을 커밋하세요:")
    print()
    print("   git add ci/schema_baseline.json ci/schema_drift_config.yml")
    print("   git commit -m 'chore: standardized schema baseline refresh")
    print()
    print("   - Applied exclusion rules for staging/backup tables")
    print("   - Updated baseline with current production schema") 
    print("   - Verified no schema drift after refresh'")
    print()
    print("   git push origin main")

def main():
    """메인 실행 함수"""
    print("🚀 표준화된 스키마 베이스라인 재생성 프로세스 시작")
    print("=" * 60)
    
    # 0. 전제 조건 확인
    print("🔍 전제 조건 확인...")
    issues = check_prerequisites()
    if issues:
        print("❌ 전제 조건 확인 실패:")
        for issue in issues:
            print(f"   {issue}")
        return 1
    print("   ✅ 모든 전제 조건 충족")
    
    # 1. 마이그레이션 실행
    if not run_migrations():
        print("❌ 마이그레이션 단계 실패")
        return 1
    
    # 2. 필터링된 스키마 추출
    try:
        schema_data = extract_filtered_schema()
    except Exception as e:
        print(f"❌ 스키마 추출 실패: {e}")
        return 1
    
    # 3. 베이스라인 안전 업데이트
    try:
        update_baseline_safely(schema_data)
    except Exception as e:
        print(f"❌ 베이스라인 업데이트 실패: {e}")
        return 1
    
    # 4. 베이스라인 검증
    if not verify_baseline():
        print("❌ 베이스라인 검증 실패")
        return 1
    
    # 5. 커밋 가이드
    show_commit_guide()
    
    print("\n🎉 표준화된 베이스라인 재생성이 완료되었습니다!")
    print("   이제 Git 커밋을 수행하여 변경사항을 저장하세요.")
    
    return 0

if __name__ == "__main__":
    exit(main())