#!/usr/bin/env python3
"""
전체 실제 데이터 자동 마이그레이션
Excel 파일들에서 모든 고객 데이터를 읽어서 Supabase에 자동 삽입
"""

import sys
import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from datetime import datetime, date
import re
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 엑셀 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"

# Supabase 연결 정보
DB_CONFIG = {
    'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
    'password': 'bico6819!!'
}

class FullDataMigrator:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.connect_db()
        
    def connect_db(self):
        """데이터베이스 연결"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Supabase 연결 성공")
        except Exception as e:
            logger.error(f"❌ DB 연결 실패: {e}")
            sys.exit(1)
    
    def clean_phone(self, phone):
        """전화번호 정제"""
        if pd.isna(phone) or not phone:
            return None
        
        # 숫자만 추출
        phone_str = str(phone).replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        phone_digits = re.sub(r'[^\d]', '', phone_str)
        
        if not phone_digits:
            return None
        
        # 010으로 시작하는 11자리로 정규화
        if len(phone_digits) == 10 and phone_digits.startswith('10'):
            phone_digits = '0' + phone_digits
        elif len(phone_digits) == 11 and phone_digits.startswith('010'):
            pass
        elif len(phone_digits) >= 10:
            # 앞의 숫자들 제거하고 뒤의 10-11자리만 사용
            phone_digits = phone_digits[-11:] if phone_digits[-11:].startswith('010') else phone_digits[-10:]
            if not phone_digits.startswith('010'):
                phone_digits = '0' + phone_digits
        else:
            return None
            
        if len(phone_digits) != 11:
            return None
            
        return f"{phone_digits[:3]}-{phone_digits[3:7]}-{phone_digits[7:]}"
    
    def parse_date(self, date_value):
        """날짜 파싱"""
        if pd.isna(date_value):
            return None
        
        try:
            if isinstance(date_value, (datetime, date)):
                return date_value.date() if isinstance(date_value, datetime) else date_value
            
            date_str = str(date_value).strip()
            if not date_str or date_str.lower() in ['none', 'nan', '']:
                return None
            
            # 다양한 날짜 형식 시도
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
            
            return None
        except:
            return None
    
    def parse_birth_year(self, birth_value):
        """생년 파싱"""
        if pd.isna(birth_value):
            return None
        
        try:
            if isinstance(birth_value, (int, float)):
                year = int(birth_value)
                if 1900 <= year <= 2010:
                    return year
            
            birth_str = str(birth_value).strip()
            if not birth_str:
                return None
            
            # 생년월일에서 연도 추출
            year_match = re.search(r'(19|20)\d{2}', birth_str)
            if year_match:
                year = int(year_match.group())
                if 1900 <= year <= 2010:
                    return year
            
            return None
        except:
            return None
    
    def normalize_gender(self, gender):
        """성별 정규화"""
        if pd.isna(gender):
            return None
        
        gender_str = str(gender).strip().lower()
        if gender_str in ['남', 'male', 'm', '남성', '남자']:
            return 'male'
        elif gender_str in ['여', 'female', 'f', '여성', '여자']:
            return 'female'
        return None
    
    def normalize_membership_level(self, level):
        """회원 등급 정규화"""
        if pd.isna(level):
            return 'basic'
        
        level_str = str(level).strip().lower()
        if level_str in ['플래티넘', 'platinum', 'vip']:
            return 'platinum'
        elif level_str in ['골드', 'gold']:
            return 'gold'
        elif level_str in ['실버', 'silver']:
            return 'silver'
        elif level_str in ['브론즈', 'bronze']:
            return 'bronze'
        else:
            return 'basic'
    
    def find_excel_files(self):
        """Excel 파일들 찾기"""
        excel_files = []
        
        if not os.path.exists(EXCEL_DIR):
            logger.warning(f"Excel 디렉토리가 없습니다: {EXCEL_DIR}")
            return excel_files
        
        for file in os.listdir(EXCEL_DIR):
            if file.endswith(('.xlsx', '.xls')):
                file_path = os.path.join(EXCEL_DIR, file)
                excel_files.append(file_path)
                logger.info(f"Excel 파일 발견: {file}")
        
        return excel_files
    
    def read_excel_data(self, file_path):
        """Excel 파일에서 데이터 읽기"""
        try:
            # 첫 번째 시트 읽기
            df = pd.read_excel(file_path, sheet_name=0)
            logger.info(f"✅ {os.path.basename(file_path)}: {len(df)}건 로드")
            return df
        except Exception as e:
            logger.error(f"❌ {os.path.basename(file_path)} 읽기 실패: {e}")
            return None
    
    def process_customer_data(self, df, source_file):
        """고객 데이터 처리 및 삽입"""
        success_count = 0
        error_count = 0
        
        logger.info(f"🔄 {source_file} 처리 시작...")
        
        for idx, row in df.iterrows():
            try:
                # 이름 확인 (필수)
                name_candidates = ['이름', '고객명', '성명', 'name', '고객이름']
                name = None
                for col in name_candidates:
                    if col in row and not pd.isna(row[col]):
                        name = str(row[col]).strip()
                        break
                
                if not name or name in ['', 'nan', 'None']:
                    continue
                
                # 전화번호 확인
                phone_candidates = ['전화번호', '핸드폰', '휴대폰', 'phone', '연락처']
                phone = None
                for col in phone_candidates:
                    if col in row:
                        phone = self.clean_phone(row[col])
                        if phone:
                            break
                
                if not phone:
                    logger.warning(f"전화번호 없음: {name}")
                    continue
                
                # 중복 확인
                self.cur.execute("SELECT customer_id FROM customers WHERE phone = %s", (phone,))
                if self.cur.fetchone():
                    continue  # 이미 존재하는 고객
                
                # 데이터 매핑
                customer_data = {
                    'name': name,
                    'phone': phone,
                    'first_visit_date': self.parse_date(row.get('첫방문일') or row.get('가입일') or row.get('등록일')),
                    'region': str(row.get('지역') or row.get('주소') or '').strip() or None,
                    'referral_source': str(row.get('유입경로') or row.get('추천인') or '').strip() or None,
                    'health_concerns': str(row.get('건강고민') or row.get('목표') or '').strip() or None,
                    'notes': str(row.get('메모') or row.get('특이사항') or '').strip() or None,
                    'assigned_staff': str(row.get('담당자') or row.get('트레이너') or '').strip() or None,
                    'birth_year': self.parse_birth_year(row.get('생년월일') or row.get('나이')),
                    'gender': self.normalize_gender(row.get('성별')),
                    'email': str(row.get('이메일') or '').strip() or None,
                    'address': str(row.get('주소') or row.get('거주지') or '').strip() or None,
                    'emergency_contact': str(row.get('비상연락처') or '').strip() or None,
                    'occupation': str(row.get('직업') or '').strip() or None,
                    'membership_level': self.normalize_membership_level(row.get('등급') or row.get('회원등급')),
                    'customer_status': 'active' if not pd.isna(row.get('상태')) and str(row.get('상태')).strip().lower() not in ['휴회', 'inactive', '비활성'] else 'active'
                }
                
                # 데이터 삽입
                insert_query = """
                INSERT INTO customers (
                    name, phone, first_visit_date, region, referral_source, 
                    health_concerns, notes, assigned_staff, birth_year, gender,
                    email, address, emergency_contact, occupation, 
                    membership_level, customer_status, created_at, updated_at
                ) VALUES (
                    %(name)s, %(phone)s, %(first_visit_date)s, %(region)s, %(referral_source)s,
                    %(health_concerns)s, %(notes)s, %(assigned_staff)s, %(birth_year)s, %(gender)s,
                    %(email)s, %(address)s, %(emergency_contact)s, %(occupation)s,
                    %(membership_level)s, %(customer_status)s, NOW(), NOW()
                )
                """
                
                self.cur.execute(insert_query, customer_data)
                success_count += 1
                
                if success_count % 50 == 0:
                    self.conn.commit()
                    logger.info(f"진행률: {success_count}명 처리 완료")
                
            except Exception as e:
                error_count += 1
                logger.error(f"고객 데이터 처리 실패 (행 {idx + 1}): {e}")
                continue
        
        # 최종 커밋
        try:
            self.conn.commit()
            logger.info(f"✅ {source_file} 완료: 성공 {success_count}명, 실패 {error_count}명")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ 커밋 실패: {e}")
        
        return success_count
    
    def run_migration(self):
        """전체 마이그레이션 실행"""
        logger.info("🚀 전체 데이터 마이그레이션 시작")
        
        # 기존 고객 수 확인
        self.cur.execute("SELECT COUNT(*) FROM customers")
        initial_count = self.cur.fetchone()['count']
        logger.info(f"기존 고객 수: {initial_count}명")
        
        # Excel 파일들 찾기
        excel_files = self.find_excel_files()
        if not excel_files:
            logger.warning("Excel 파일을 찾을 수 없습니다. 샘플 데이터를 생성합니다.")
            self.create_sample_data()
            return
        
        total_added = 0
        
        # 각 Excel 파일 처리
        for file_path in excel_files:
            df = self.read_excel_data(file_path)
            if df is not None and len(df) > 0:
                added = self.process_customer_data(df, os.path.basename(file_path))
                total_added += added
        
        # 최종 결과
        self.cur.execute("SELECT COUNT(*) FROM customers")
        final_count = self.cur.fetchone()['count']
        
        logger.info(f"🎉 마이그레이션 완료!")
        logger.info(f"기존: {initial_count}명 → 현재: {final_count}명")
        logger.info(f"추가된 고객: {total_added}명")
        
    def create_sample_data(self):
        """Excel 파일이 없을 경우 샘플 데이터 생성"""
        sample_customers = [
            ('김철수', '010-1234-5678', 'kim@example.com', 'male', '서울시 강남구'),
            ('박미영', '010-2345-6789', 'park@example.com', 'female', '서울시 서초구'),
            ('이준호', '010-3456-7890', 'lee@example.com', 'male', '서울시 송파구'),
            ('최유진', '010-4567-8901', 'choi@example.com', 'female', '경기도 성남시'),
            ('정민수', '010-5678-9012', 'jung@example.com', 'male', '서울시 마포구'),
        ]
        
        for name, phone, email, gender, address in sample_customers:
            try:
                self.cur.execute("""
                    INSERT INTO customers (name, phone, email, gender, address, membership_level, customer_status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, 'basic', 'active', NOW(), NOW())
                    ON CONFLICT (phone) DO NOTHING
                """, (name, phone, email, gender, address))
            except Exception as e:
                logger.error(f"샘플 데이터 생성 실패 ({name}): {e}")
        
        self.conn.commit()
        logger.info("✅ 샘플 데이터 생성 완료")
    
    def close(self):
        """연결 종료"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

def main():
    logger.info("=" * 60)
    logger.info("🔥 AIBIO 센터 전체 데이터 자동 마이그레이션")
    logger.info("=" * 60)
    
    migrator = FullDataMigrator()
    
    try:
        migrator.run_migration()
    except KeyboardInterrupt:
        logger.info("❌ 사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
    finally:
        migrator.close()

if __name__ == "__main__":
    main()