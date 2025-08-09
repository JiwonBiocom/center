#!/usr/bin/env python3
"""
모든 API 엔드포인트를 동기 방식으로 수정하는 스크립트
"""
import os
import re

# API 파일 목록
api_files = [
    'backend/api/v1/customers.py',
    'backend/api/v1/services.py', 
    'backend/api/v1/payments.py',
    'backend/api/v1/packages.py',
    'backend/api/v1/leads.py',
    'backend/api/v1/reports.py'
]

def fix_async_to_sync(content):
    """async 코드를 sync로 변환"""
    # Import 문 수정
    content = content.replace('from sqlalchemy.ext.asyncio import AsyncSession', 'from sqlalchemy.orm import Session')
    
    # async def -> def
    content = re.sub(r'async\s+def\s+', 'def ', content)
    
    # await 제거
    content = re.sub(r'await\s+', '', content)
    
    # AsyncSession -> Session
    content = content.replace('AsyncSession', 'Session')
    
    # db.execute() 호출 패턴 수정
    content = re.sub(r'result\s*=\s*db\.execute\((.*?)\)', r'result = db.execute(\1)', content, flags=re.DOTALL)
    
    # .scalars() 패턴 수정
    content = re.sub(r'\.scalars\(\)\.all\(\)', '.scalars().all()', content)
    
    return content

def main():
    fixed_count = 0
    
    for file_path in api_files:
        if not os.path.exists(file_path):
            print(f"파일 없음: {file_path}")
            continue
            
        print(f"\n처리 중: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # async 키워드가 있는지 확인
        if 'async ' in content or 'await ' in content or 'AsyncSession' in content:
            # 수정 전 백업
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 수정
            fixed_content = fix_async_to_sync(content)
            
            # 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"✅ 수정 완료: {file_path}")
            fixed_count += 1
        else:
            print(f"⏭️  이미 동기 방식: {file_path}")
    
    print(f"\n총 {fixed_count}개 파일 수정 완료")

if __name__ == "__main__":
    main()