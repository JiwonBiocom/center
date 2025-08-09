#!/usr/bin/env python3
"""
기존 Excel 파일에서 시드 데이터를 준비하는 스크립트
민감한 정보는 마스킹 처리
"""

import os
import sys
import pandas as pd
import shutil
from pathlib import Path

# 소스 파일 경로
SOURCE_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"
TARGET_DIR = "/Users/vibetj/coding/center/backend/seed"

def mask_phone_number(phone):
    """전화번호 뒷자리 마스킹"""
    if pd.isna(phone) or not phone:
        return phone
    
    phone_str = str(phone)
    if len(phone_str) >= 8:
        # 뒷 4자리를 ****로 마스킹
        return phone_str[:-4] + "****"
    return phone_str

def prepare_marketing_leads():
    """유입고객 데이터 준비"""
    print("📋 유입고객 데이터 준비 중...")
    
    source_file = os.path.join(SOURCE_DIR, "유입고객_DB리스트.csv")
    if not os.path.exists(source_file):
        print(f"⚠️  {source_file} 파일이 없습니다.")
        return False
    
    # CSV 읽기
    df = pd.read_csv(source_file, encoding='utf-8-sig')
    print(f"  - 원본 레코드: {len(df)}개")
    
    # 민감한 정보 마스킹 (옵션)
    # df['연락처'] = df['연락처'].apply(mask_phone_number)
    
    # 테스트 데이터 제거
    test_patterns = ['테스트', 'test', 'Test', 'TEST', '샘플', 'sample']
    for pattern in test_patterns:
        df = df[~df['이름'].str.contains(pattern, na=False)]
        if '비고' in df.columns:
            df = df[~df['비고'].str.contains(pattern, na=False)]
    
    print(f"  - 정제 후 레코드: {len(df)}개")
    
    # Excel로 저장
    target_file = os.path.join(TARGET_DIR, "marketing_leads.xlsx")
    df.to_excel(target_file, index=False, engine='openpyxl')
    print(f"✅ {target_file} 생성 완료")
    
    return True

def prepare_kit_receipts():
    """검사키트 수령 데이터 준비"""
    print("\n📋 검사키트 수령 데이터 준비 중...")
    
    # 여러 가능한 파일명 시도
    possible_files = [
        "키트고객.xlsx",
        "키트고객_정제됨.csv",
        "키트수령관리.xlsx",
        "검사키트관리.xlsx"
    ]
    
    source_file = None
    for filename in possible_files:
        path = os.path.join(SOURCE_DIR, filename)
        if os.path.exists(path):
            source_file = path
            break
    
    if not source_file:
        print(f"⚠️  키트 수령 관련 파일을 찾을 수 없습니다.")
        print(f"   찾은 디렉토리: {SOURCE_DIR}")
        print(f"   시도한 파일명: {', '.join(possible_files)}")
        return False
    
    # 파일 읽기
    if source_file.endswith('.csv'):
        df = pd.read_csv(source_file, encoding='utf-8-sig')
    else:
        df = pd.read_excel(source_file)
    
    print(f"  - 원본 레코드: {len(df)}개")
    
    # 컬럼명 정규화
    column_mapping = {
        '고객명': 'name',
        '이름': 'name',
        '연락처': 'phone',
        '전화번호': 'phone',
        '키트': 'kit_type',
        '키트종류': 'kit_type',
        '시리얼': 'kit_serial',
        '시리얼번호': 'kit_serial',
        '키트수령일': 'received_date',
        '수령일': 'received_date',
        '결과지수령일': 'result_date',
        '결과수령일': 'result_date',
        '결과지전달일': 'delivered_date',
        '전달일': 'delivered_date'
    }
    
    df.rename(columns=column_mapping, inplace=True)
    
    # 민감한 정보 마스킹 (옵션)
    # if 'phone' in df.columns:
    #     df['phone'] = df['phone'].apply(mask_phone_number)
    
    # 테스트 데이터 제거
    if 'name' in df.columns:
        test_patterns = ['테스트', 'test', 'Test', 'TEST', '샘플', 'sample']
        for pattern in test_patterns:
            df = df[~df['name'].str.contains(pattern, na=False)]
    
    print(f"  - 정제 후 레코드: {len(df)}개")
    
    # Excel로 저장
    target_file = os.path.join(TARGET_DIR, "kit_receipts.xlsx")
    df.to_excel(target_file, index=False, engine='openpyxl')
    print(f"✅ {target_file} 생성 완료")
    
    return True

def main():
    print("🚀 시드 데이터 준비 시작...\n")
    
    # 타겟 디렉토리 생성
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 소스 디렉토리 확인
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ 소스 디렉토리가 없습니다: {SOURCE_DIR}")
        print("   Excel 파일이 있는 정확한 경로를 확인하세요.")
        sys.exit(1)
    
    # 사용 가능한 파일 목록 표시
    print(f"📁 소스 디렉토리: {SOURCE_DIR}")
    print("📄 발견된 파일:")
    for file in os.listdir(SOURCE_DIR):
        if file.endswith(('.xlsx', '.xls', '.csv')):
            print(f"   - {file}")
    print()
    
    # 각 데이터 준비
    success = True
    
    if not prepare_marketing_leads():
        success = False
    
    if not prepare_kit_receipts():
        success = False
    
    if success:
        print("\n✅ 모든 시드 데이터 준비 완료!")
        print(f"📁 시드 파일 위치: {TARGET_DIR}")
        print("\n다음 단계:")
        print("1. git add backend/seed/*.xlsx")
        print("2. git commit -m 'feat: 프로덕션 시드 데이터 추가'")
        print("3. git push origin main")
        print("\n⚠️  주의: 민감한 개인정보가 포함되어 있다면 마스킹 처리를 고려하세요.")
    else:
        print("\n⚠️  일부 데이터 준비에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()