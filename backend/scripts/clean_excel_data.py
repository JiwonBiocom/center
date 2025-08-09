#!/usr/bin/env python3
"""
엑셀 데이터 정제 스크립트
- 전화번호 정규화
- 중복 데이터 처리
- 날짜 형식 통일
- 데이터 유효성 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import re
from datetime import datetime
import logging
from typing import Optional, Tuple

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExcelDataCleaner:
    """엑셀 데이터 정제 클래스"""
    
    def __init__(self):
        self.base_path = 'docs/AIBIO 관리대장 파일모음'
        
    def clean_phone_number(self, phone: any) -> Optional[str]:
        """전화번호 정규화"""
        if pd.isna(phone) or phone == '' or phone is None:
            return None
            
        # 문자열로 변환
        phone_str = str(phone).strip()
        
        # 숫자만 추출
        numbers = re.sub(r'[^0-9]', '', phone_str)
        
        # 010으로 시작하는 11자리 번호
        if len(numbers) == 11 and numbers.startswith('010'):
            return f"{numbers[:3]}-{numbers[3:7]}-{numbers[7:]}"
        # 010으로 시작하는 10자리 (0 누락)
        elif len(numbers) == 10 and numbers.startswith('10'):
            return f"0{numbers[:2]}-{numbers[2:6]}-{numbers[6:]}"
        # 서울 지역번호 (02)
        elif len(numbers) == 9 and numbers.startswith('2'):
            return f"02-{numbers[1:5]}-{numbers[5:]}"
        elif len(numbers) == 10 and numbers.startswith('02'):
            return f"02-{numbers[2:6]}-{numbers[6:]}"
        # 기타 지역번호
        elif len(numbers) == 10 and numbers.startswith('0'):
            return f"{numbers[:3]}-{numbers[3:6]}-{numbers[6:]}"
        
        logger.warning(f"정규화 실패한 전화번호: {phone_str}")
        return phone_str
    
    def extract_birth_year(self, text: str) -> Optional[int]:
        """텍스트에서 생년 추출"""
        if pd.isna(text) or not text:
            return None
            
        text = str(text)
        
        # 패턴 매칭
        patterns = [
            (r'(\d{4})년생', lambda m: int(m.group(1))),
            (r'(\d{2})년생', lambda m: 1900 + int(m.group(1)) if int(m.group(1)) > 50 else 2000 + int(m.group(1))),
            (r'(\d{4})년', lambda m: int(m.group(1))),
            (r'(\d{2})년', lambda m: 1900 + int(m.group(1)) if int(m.group(1)) > 50 else 2000 + int(m.group(1))),
            (r'나이[:\s]*(\d+)', lambda m: datetime.now().year - int(m.group(1)) + 1),
        ]
        
        for pattern, converter in patterns:
            match = re.search(pattern, text)
            if match:
                year = converter(match)
                if 1900 <= year <= datetime.now().year:
                    return year
                    
        return None
    
    def infer_gender(self, name: str, notes: str = '') -> Optional[str]:
        """이름과 메모에서 성별 추론"""
        if pd.isna(name):
            return None
            
        # 메모에서 성별 키워드 찾기
        text = f"{name} {notes}".lower()
        if any(word in text for word in ['여성', '여자', '여']):
            return 'female'
        if any(word in text for word in ['남성', '남자', '남']):
            return 'male'
            
        # 이름으로 추론 (간단한 규칙)
        # 실제로는 더 정교한 로직이 필요하지만, 기본적인 패턴만 사용
        female_endings = ['희', '미', '은', '지', '영', '경', '화', '숙', '정', '순', '아', '연']
        for ending in female_endings:
            if name.endswith(ending):
                return 'female'
                
        return None
    
    def clean_customers_data(self) -> pd.DataFrame:
        """고객 데이터 정제"""
        logger.info("=== 고객 데이터 정제 시작 ===")
        
        # CSV 파일 읽기
        df = pd.read_csv(f'{self.base_path}/고객관리대장_전체고객.csv')
        logger.info(f"원본 데이터: {len(df)}건")
        
        # 1. 전화번호 정규화
        df['phone_clean'] = df['연락처'].apply(self.clean_phone_number)
        
        # 2. 날짜 형식 변환
        df['first_visit_date'] = pd.to_datetime(df['첫방문일'], errors='coerce')
        
        # 3. 중복 제거 (이름 + 전화번호)
        # 전화번호가 있는 경우 전화번호로, 없는 경우 이름으로 중복 체크
        df['dup_key'] = df.apply(
            lambda row: row['phone_clean'] if pd.notna(row['phone_clean']) else row['이름'], 
            axis=1
        )
        
        # 중복 데이터 처리 - 가장 최근 방문 기록 유지
        df = df.sort_values('first_visit_date', ascending=False)
        duplicates = df[df.duplicated('dup_key', keep='first')]
        if len(duplicates) > 0:
            logger.info(f"중복 제거: {len(duplicates)}건")
            df = df.drop_duplicates('dup_key', keep='first')
        
        # 4. 추가 정보 추출
        df['birth_year'] = df['비고'].apply(self.extract_birth_year)
        df['gender'] = df.apply(lambda row: self.infer_gender(row['이름'], row.get('비고', '')), axis=1)
        
        # 5. 필수 필드 검증
        df['is_valid'] = df['이름'].notna()
        invalid_count = len(df[~df['is_valid']])
        if invalid_count > 0:
            logger.warning(f"유효하지 않은 데이터: {invalid_count}건")
        
        logger.info(f"정제 완료: {len(df[df['is_valid']])}건")
        
        # 정제된 데이터 저장
        df.to_csv(f'{self.base_path}/고객관리대장_정제됨.csv', index=False, encoding='utf-8-sig')
        
        return df[df['is_valid']]
    
    def clean_leads_data(self) -> pd.DataFrame:
        """유입 고객 데이터 정제"""
        logger.info("\n=== 유입 고객 데이터 정제 시작 ===")
        
        # CSV 파일 읽기
        df = pd.read_csv(f'{self.base_path}/유입고객_DB리스트.csv')
        logger.info(f"원본 데이터: {len(df)}건")
        
        # 1. 전화번호 정규화
        df['phone_clean'] = df['연락처'].apply(self.clean_phone_number)
        
        # 2. 날짜 형식 변환
        date_columns = ['DB입력일', '전화상담일', '방문상담일', '등록일']
        for col in date_columns:
            if col in df.columns:
                df[f'{col}_clean'] = pd.to_datetime(df[col], errors='coerce')
        
        # 3. 상태 추론
        def infer_status(row):
            if pd.notna(row.get('등록일')):
                return 'converted'
            elif pd.notna(row.get('방문상담일')):
                return 'visit_consulted'
            elif pd.notna(row.get('전화상담일')):
                return 'phone_consulted'
            else:
                return 'new'
        
        df['status_inferred'] = df.apply(infer_status, axis=1)
        
        # 4. 가격 정보 처리
        df['price_informed_clean'] = df['가격안내'].apply(
            lambda x: True if pd.notna(x) and str(x).lower() in ['y', 'yes', 'o', '예', '네'] else False
        )
        
        # 5. 매출 금액 정제
        def clean_revenue(value):
            if pd.isna(value):
                return 0
            # 숫자만 추출
            numbers = re.sub(r'[^0-9]', '', str(value))
            return int(numbers) if numbers else 0
        
        df['revenue_clean'] = df['매출'].apply(clean_revenue)
        
        logger.info(f"정제 완료: {len(df)}건")
        
        # 정제된 데이터 저장
        df.to_csv(f'{self.base_path}/유입고객_정제됨.csv', index=False, encoding='utf-8-sig')
        
        return df
    
    def clean_kit_data(self) -> pd.DataFrame:
        """키트 수령 데이터 정제"""
        logger.info("\n=== 키트 수령 데이터 정제 시작 ===")
        
        # CSV 파일 읽기
        df = pd.read_csv(f'{self.base_path}/고객관리대장_키트고객.csv')
        logger.info(f"원본 데이터: {len(df)}건")
        
        # 1. 날짜 형식 변환
        date_columns = ['키트수령일', '결과지 수령일', '결과지 전달일']
        for col in date_columns:
            if col in df.columns:
                df[f'{col}_clean'] = pd.to_datetime(df[col], errors='coerce')
        
        # 2. 시리얼 번호 정규화
        df['serial_clean'] = df['시리얼번호'].apply(
            lambda x: str(x).strip().upper() if pd.notna(x) else None
        )
        
        # 3. 중복 시리얼 번호 체크
        duplicates = df[df.duplicated('serial_clean', keep=False) & df['serial_clean'].notna()]
        if len(duplicates) > 0:
            logger.warning(f"중복 시리얼 번호: {len(duplicates)}건")
        
        logger.info(f"정제 완료: {len(df)}건")
        
        # 정제된 데이터 저장
        df.to_csv(f'{self.base_path}/키트고객_정제됨.csv', index=False, encoding='utf-8-sig')
        
        return df
    
    def generate_summary_report(self):
        """정제 결과 요약 리포트 생성"""
        logger.info("\n=== 정제 결과 요약 ===")
        
        # 각 파일의 정제 결과 확인
        files = [
            ('고객관리대장_정제됨.csv', '고객'),
            ('유입고객_정제됨.csv', '유입 고객'),
            ('키트고객_정제됨.csv', '키트 수령')
        ]
        
        report = []
        for filename, label in files:
            try:
                df = pd.read_csv(f'{self.base_path}/{filename}')
                report.append(f"{label}: {len(df)}건")
                
                # 주요 통계
                if '고객' in label:
                    valid_phones = df['phone_clean'].notna().sum()
                    report.append(f"  - 유효한 전화번호: {valid_phones}건")
                    
                    if 'birth_year' in df.columns:
                        valid_birth = df['birth_year'].notna().sum()
                        report.append(f"  - 생년 정보: {valid_birth}건")
                        
                    if 'gender' in df.columns:
                        gender_counts = df['gender'].value_counts()
                        report.append(f"  - 성별: {dict(gender_counts)}")
                        
            except FileNotFoundError:
                report.append(f"{label}: 파일 없음")
        
        # 리포트 출력
        for line in report:
            logger.info(line)
        
        # 리포트 저장
        with open(f'{self.base_path}/정제_결과_요약.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))

def main():
    """메인 실행 함수"""
    cleaner = ExcelDataCleaner()
    
    try:
        # 1. 고객 데이터 정제
        customers_df = cleaner.clean_customers_data()
        
        # 2. 유입 고객 데이터 정제
        leads_df = cleaner.clean_leads_data()
        
        # 3. 키트 데이터 정제
        kit_df = cleaner.clean_kit_data()
        
        # 4. 요약 리포트 생성
        cleaner.generate_summary_report()
        
        logger.info("\n✅ 모든 데이터 정제가 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"데이터 정제 중 오류 발생: {str(e)}")
        raise

if __name__ == "__main__":
    main()