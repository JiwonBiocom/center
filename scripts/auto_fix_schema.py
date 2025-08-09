#!/usr/bin/env python3
"""
자동 스키마 수정 스크립트
실행 시 데이터베이스와 ORM 모델을 비교하여 자동으로 수정 SQL을 생성하고 적용
"""

import os
import sys
import subprocess
from datetime import datetime
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# 부모 디렉토리를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# check_db_schema_diff의 핵심 로직을 직접 구현
def get_schema_differences():
    """데이터베이스와 ORM 모델의 차이를 확인"""
    from sqlalchemy import create_engine, inspect, MetaData
    from backend.core.database import Base
    from backend.models import customer, package, notification, user
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL not set")
    
    # 직접 연결 URL 사용
    direct_url = db_url.replace(":6543/postgres?", ":5432/postgres?")
    engine = create_engine(direct_url)
    inspector = inspect(engine)
    
    differences = {
        'missing_columns': [],
        'type_mismatches': [],
        'missing_tables': []
    }
    
    # 모든 모델 확인
    for table_name, table in Base.metadata.tables.items():
        if table_name not in inspector.get_table_names():
            differences['missing_tables'].append(table_name)
            continue
        
        # DB 컬럼
        db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        
        # 모델 컬럼
        for column in table.columns:
            col_name = column.name
            
            if col_name not in db_columns:
                differences['missing_columns'].append({
                    'table': table_name,
                    'column': col_name,
                    'type': column.type.__class__.__name__,
                    'nullable': column.nullable
                })
    
    return differences if any(differences.values()) else None

load_dotenv()

class SchemaAutoFixer:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not found in environment")
        
        # Supabase pooler URL을 직접 연결 URL로 변환
        self.direct_url = self.db_url.replace(":6543/postgres?", ":5432/postgres?")
        
    def execute_sql(self, sql_commands: list[str]) -> bool:
        """SQL 명령어 실행"""
        try:
            conn = psycopg2.connect(self.direct_url)
            cur = conn.cursor()
            
            for cmd in sql_commands:
                print(f"Executing: {cmd}")
                cur.execute(cmd)
            
            conn.commit()
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error executing SQL: {e}")
            return False
    
    def is_safe_change(self, sql_commands: list[str]) -> bool:
        """안전한 변경사항인지 확인"""
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'CASCADE']
        
        for cmd in sql_commands:
            cmd_upper = cmd.upper()
            for keyword in dangerous_keywords:
                if keyword in cmd_upper:
                    return False
        
        # ADD COLUMN, CREATE INDEX는 안전
        safe_patterns = ['ADD COLUMN', 'CREATE INDEX', 'ALTER COLUMN SET']
        has_safe_pattern = any(
            pattern in cmd.upper() 
            for cmd in sql_commands 
            for pattern in safe_patterns
        )
        
        return has_safe_pattern
    
    def run(self, auto_apply=False):
        """스키마 차이 감지 및 수정"""
        print("🔍 Checking schema differences...")
        
        # 스키마 차이 확인
        differences = get_schema_differences()
        
        if not differences:
            print("✅ No schema differences found!")
            return True
        
        print("\n⚠️ Schema differences detected:")
        print("-" * 50)
        
        fix_commands = []
        
        # 누락된 컬럼 추가
        for diff in differences['missing_columns']:
            table = diff['table']
            column = diff['column']
            dtype = diff['type']
            nullable = diff.get('nullable', True)
            
            # 데이터 타입 매핑
            sql_type = self._python_to_sql_type(dtype)
            null_clause = "" if nullable else " NOT NULL"
            
            cmd = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {sql_type}{null_clause};"
            fix_commands.append(cmd)
            
            # user_id 같은 특수 컬럼 처리
            if column == 'user_id' and table == 'notifications':
                fix_commands.append(f"UPDATE {table} SET {column} = 1 WHERE {column} IS NULL;")
                fix_commands.append(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column});")
        
        # 타입 불일치 수정
        for diff in differences.get('type_mismatches', []):
            # 타입 변경은 위험할 수 있으므로 주의 메시지만
            print(f"⚠️ Type mismatch in {diff['table']}.{diff['column']}: {diff['db_type']} vs {diff['model_type']}")
        
        if not fix_commands:
            print("No automatic fixes available.")
            return True
        
        print("\n📝 Generated fix SQL:")
        print("-" * 50)
        for cmd in fix_commands:
            print(cmd)
        print("-" * 50)
        
        # 안전성 검사
        if not self.is_safe_change(fix_commands):
            print("\n❌ Unsafe changes detected! Manual intervention required.")
            print("Please review and execute the SQL manually in Supabase.")
            return False
        
        # 자동 적용 여부
        if auto_apply or (os.getenv("ENVIRONMENT") == "development" and input("\nApply these changes? (y/N): ").lower() == 'y'):
            print("\n🔧 Applying fixes...")
            if self.execute_sql(fix_commands):
                print("✅ Schema fixed successfully!")
                
                # 성공 로그 기록
                self._log_success(fix_commands)
                return True
            else:
                return False
        else:
            print("\n💡 To apply these changes, run the SQL above in Supabase SQL Editor.")
            
            # GitHub Actions에서 실행 중이면 PR 코멘트용 출력
            if os.getenv("GITHUB_ACTIONS"):
                self._create_pr_comment(fix_commands)
            
            return False
    
    def _python_to_sql_type(self, python_type: str) -> str:
        """Python 타입을 SQL 타입으로 변환"""
        type_map = {
            'Integer': 'INTEGER',
            'String': 'VARCHAR',
            'Text': 'TEXT',
            'Boolean': 'BOOLEAN',
            'DateTime': 'TIMESTAMP',
            'Date': 'DATE',
            'Float': 'FLOAT',
            'Numeric': 'NUMERIC',
        }
        return type_map.get(python_type, 'VARCHAR')
    
    def _log_success(self, commands: list[str]):
        """성공 로그 기록"""
        log_file = "schema_fixes.log"
        with open(log_file, "a") as f:
            f.write(f"\n--- {datetime.now().isoformat()} ---\n")
            for cmd in commands:
                f.write(f"{cmd}\n")
    
    def _create_pr_comment(self, commands: list[str]):
        """GitHub PR 코멘트용 출력 생성"""
        print("\n::set-output name=schema_fix_sql::" + "\\n".join(commands))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-fix schema differences")
    parser.add_argument("--auto", action="store_true", help="Automatically apply safe fixes")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be done")
    
    args = parser.parse_args()
    
    fixer = SchemaAutoFixer()
    
    if args.dry_run:
        # Dry run 모드에서는 SQL만 생성
        differences = get_schema_differences()
        if differences:
            print("DRY RUN - Would execute:")
            # SQL 생성 로직만 실행
    else:
        success = fixer.run(auto_apply=args.auto)
        sys.exit(0 if success else 1)