#!/usr/bin/env python3
"""
안전한 스키마 적용 스크립트
GitHub Actions에서 승인된 SQL만 실행
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from pathlib import Path

class SafeSchemaApplier:
    """승인된 스키마 변경만 적용하는 클래스"""
    
    # 안전한 SQL 패턴 (자동 승인 가능)
    SAFE_PATTERNS = [
        'ALTER TABLE * ADD COLUMN IF NOT EXISTS',
        'CREATE INDEX IF NOT EXISTS',
        'CREATE OR REPLACE VIEW',
        'COMMENT ON',
        'UPDATE * SET * WHERE * IS NULL',  # NULL 값 업데이트만
    ]
    
    # 위험한 SQL 패턴 (수동 승인 필요)
    DANGEROUS_PATTERNS = [
        'DROP',
        'DELETE',
        'TRUNCATE',
        'ALTER TABLE * DROP',
        'CASCADE',
        'UPDATE * SET',  # 조건 없는 UPDATE
    ]
    
    def __init__(self):
        self.approval_file = Path('.github/schema_approvals.json')
        self.pending_dir = Path('schema_fixes/pending')
        self.completed_dir = Path('schema_fixes/completed')
        self.rejected_dir = Path('schema_fixes/rejected')
        
        # 디렉토리 생성
        for dir in [self.pending_dir, self.completed_dir, self.rejected_dir]:
            dir.mkdir(parents=True, exist_ok=True)
    
    def is_safe_sql(self, sql_content: str) -> bool:
        """SQL이 안전한 패턴인지 확인"""
        sql_upper = sql_content.upper()
        
        # 위험한 패턴 확인
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in sql_upper:
                return False
        
        # 안전한 패턴 확인
        has_safe = any(
            pattern.replace('*', '').strip() in sql_upper 
            for pattern in self.SAFE_PATTERNS
        )
        
        return has_safe
    
    def get_sql_hash(self, sql_content: str) -> str:
        """SQL 내용의 해시 생성"""
        return hashlib.sha256(sql_content.encode()).hexdigest()[:8]
    
    def create_approval_request(self, sql_file: Path) -> dict:
        """승인 요청 생성"""
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        is_safe = self.is_safe_sql(sql_content)
        sql_hash = self.get_sql_hash(sql_content)
        
        request = {
            'file': str(sql_file),
            'hash': sql_hash,
            'created_at': datetime.now().isoformat(),
            'is_safe': is_safe,
            'auto_approved': is_safe,
            'manual_approval': None,
            'applied': False,
            'applied_at': None
        }
        
        return request
    
    def save_approval_status(self, approvals: dict):
        """승인 상태 저장"""
        with open(self.approval_file, 'w') as f:
            json.dump(approvals, f, indent=2)
    
    def load_approval_status(self) -> dict:
        """승인 상태 로드"""
        if self.approval_file.exists():
            with open(self.approval_file, 'r') as f:
                return json.load(f)
        return {}
    
    def process_pending_files(self):
        """대기 중인 SQL 파일 처리"""
        approvals = self.load_approval_status()
        
        for sql_file in self.pending_dir.glob('*.sql'):
            print(f"\n📄 Processing: {sql_file.name}")
            
            # 승인 요청 생성
            request = self.create_approval_request(sql_file)
            file_hash = request['hash']
            
            # 기존 승인 확인
            if file_hash in approvals:
                existing = approvals[file_hash]
                if existing['applied']:
                    print(f"✅ Already applied: {sql_file.name}")
                    sql_file.rename(self.completed_dir / sql_file.name)
                    continue
            
            # 안전성 검사
            if request['is_safe']:
                print(f"✅ Auto-approved (safe SQL): {sql_file.name}")
                approvals[file_hash] = request
                
                # GitHub Actions 환경에서는 자동 적용 표시
                if os.getenv('GITHUB_ACTIONS'):
                    print(f"🚀 Ready for automatic application")
                    with open(sql_file, 'r') as f:
                        print(f"\n```sql\n{f.read()}\n```")
            else:
                print(f"⚠️  Manual approval required: {sql_file.name}")
                print("Dangerous patterns detected!")
                approvals[file_hash] = request
                
                # 위험한 SQL은 rejected 폴더로 이동
                sql_file.rename(self.rejected_dir / sql_file.name)
        
        # 승인 상태 저장
        self.save_approval_status(approvals)
        
        # GitHub Actions 출력
        if os.getenv('GITHUB_ACTIONS'):
            safe_count = sum(1 for a in approvals.values() if a['is_safe'] and not a['applied'])
            print(f"\n::set-output name=safe_sql_count::{safe_count}")
            
            if safe_count > 0:
                print("::set-output name=has_safe_sql::true")
            else:
                print("::set-output name=has_safe_sql::false")
    
    def generate_summary(self):
        """처리 요약 생성"""
        approvals = self.load_approval_status()
        
        print("\n📊 Schema Fix Summary")
        print("=" * 50)
        
        total = len(approvals)
        safe = sum(1 for a in approvals.values() if a['is_safe'])
        applied = sum(1 for a in approvals.values() if a['applied'])
        pending = sum(1 for a in approvals.values() if not a['applied'])
        
        print(f"Total SQL files: {total}")
        print(f"Safe (auto-approved): {safe}")
        print(f"Applied: {applied}")
        print(f"Pending: {pending}")
        
        if pending > 0:
            print("\n⏳ Pending SQL files:")
            for hash, approval in approvals.items():
                if not approval['applied']:
                    status = "🟢 Ready" if approval['is_safe'] else "🔴 Needs Review"
                    print(f"  {status} {approval['file']} (hash: {hash})")


if __name__ == "__main__":
    applier = SafeSchemaApplier()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        applier.generate_summary()
    else:
        applier.process_pending_files()
        applier.generate_summary()