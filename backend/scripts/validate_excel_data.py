"""
엑셀 데이터 검증 스크립트
마이그레이션 전에 데이터 품질을 확인합니다.
"""

import pandas as pd
import os
from collections import Counter

EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

def analyze_customer_data():
    """고객 데이터 분석"""
    file_path = os.path.join(EXCEL_DIR, "고객관리대장2025.xlsm")
    
    try:
        df = pd.read_excel(file_path, sheet_name="전체 고객관리대장")
        
        print("=== 고객 데이터 분석 ===")
        print(f"총 고객 수: {len(df)}")
        
        # 누락 데이터 확인
        print("\n누락 데이터:")
        for col in ['성함', '연락처', '거주지역', '방문경로']:
            if col in df.columns:
                missing = df[col].isna().sum()
                print(f"  - {col}: {missing}건 ({missing/len(df)*100:.1f}%)")
        
        # 중복 확인
        if '성함' in df.columns and '연락처' in df.columns:
            duplicates = df.duplicated(subset=['성함', '연락처'], keep=False)
            print(f"\n중복 데이터: {duplicates.sum()}건")
        
        # 지역 분포
        if '거주지역' in df.columns:
            print("\n지역 분포 (상위 10개):")
            region_counts = df['거주지역'].value_counts().head(10)
            for region, count in region_counts.items():
                print(f"  - {region}: {count}건")
        
        # 유입 경로 분포
        if '방문경로' in df.columns:
            print("\n유입 경로 분포:")
            channel_counts = df['방문경로'].value_counts()
            for channel, count in channel_counts.items():
                print(f"  - {channel}: {count}건")
                
    except Exception as e:
        print(f"오류 발생: {e}")

def analyze_payment_data():
    """결제 데이터 분석"""
    file_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    try:
        xl = pd.ExcelFile(file_path)
        
        print("\n=== 결제 데이터 분석 ===")
        print(f"시트 수: {len(xl.sheet_names)}")
        
        total_payments = 0
        total_amount = 0
        
        for sheet_name in xl.sheet_names:
            if sheet_name == "전체매출":
                continue
                
            df = pd.read_excel(xl, sheet_name=sheet_name)
            if not df.empty:
                total_payments += len(df)
                
                # 금액 합계 계산
                if '결제 금액' in df.columns:
                    amounts = df['결제 금액'].apply(lambda x: 
                        float(str(x).replace(',', '').replace('원', '')) if pd.notna(x) else 0
                    )
                    total_amount += amounts.sum()
        
        print(f"총 결제 건수: {total_payments}건")
        print(f"총 매출액: {total_amount:,.0f}원")
        
    except Exception as e:
        print(f"오류 발생: {e}")

def analyze_lead_data():
    """리드 데이터 분석"""
    file_path = os.path.join(EXCEL_DIR, "유입 고객 DB 리스트.xlsx")
    
    try:
        df = pd.read_excel(file_path, sheet_name="신규")
        
        print("\n=== 리드 데이터 분석 ===")
        print(f"총 리드 수: {len(df)}")
        
        # 전환 퍼널 분석
        if all(col in df.columns for col in ['DB입력', '전화상담', '방문상담', '등록']):
            db_entry = df['DB입력'].notna().sum()
            phone_consult = df['전화상담'].notna().sum()
            visit_consult = df['방문상담'].notna().sum()
            registered = df['등록'].notna().sum()
            
            print("\n전환 퍼널:")
            print(f"  - DB입력: {db_entry}건")
            print(f"  - 전화상담: {phone_consult}건 ({phone_consult/db_entry*100:.1f}%)")
            print(f"  - 방문상담: {visit_consult}건 ({visit_consult/phone_consult*100:.1f}%)")
            print(f"  - 등록: {registered}건 ({registered/visit_consult*100:.1f}%)")
        
        # 채널별 분석
        if '유입' in df.columns:
            print("\n채널별 리드:")
            channel_counts = df['유입'].value_counts()
            for channel, count in channel_counts.items():
                print(f"  - {channel}: {count}건")
                
    except Exception as e:
        print(f"오류 발생: {e}")

def check_data_consistency():
    """데이터 일관성 확인"""
    print("\n=== 데이터 일관성 확인 ===")
    
    # 고객 이름 목록
    customer_file = os.path.join(EXCEL_DIR, "고객관리대장2025.xlsm")
    payment_file = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
    
    try:
        # 고객 파일에서 이름 추출
        df_customers = pd.read_excel(customer_file, sheet_name="전체 고객관리대장")
        customer_names = set(df_customers['성함'].dropna().unique())
        
        # 결제 파일에서 이름 추출
        xl_payments = pd.ExcelFile(payment_file)
        payment_names = set()
        
        for sheet_name in xl_payments.sheet_names:
            if sheet_name != "전체매출":
                df = pd.read_excel(xl_payments, sheet_name=sheet_name)
                if '고객명' in df.columns:
                    payment_names.update(df['고객명'].dropna().unique())
        
        # 차이 분석
        only_in_customer = customer_names - payment_names
        only_in_payment = payment_names - customer_names
        
        print(f"고객 파일에만 있는 이름: {len(only_in_customer)}개")
        print(f"결제 파일에만 있는 이름: {len(only_in_payment)}개")
        
        if len(only_in_payment) > 0:
            print("\n결제 파일에만 있는 고객 (상위 10명):")
            for name in list(only_in_payment)[:10]:
                print(f"  - {name}")
                
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    print("AIBIO 엑셀 데이터 검증 시작\n")
    
    analyze_customer_data()
    analyze_payment_data()
    analyze_lead_data()
    check_data_consistency()
    
    print("\n검증 완료!")