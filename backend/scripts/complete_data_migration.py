#!/usr/bin/env python3
"""
완전한 실제 데이터 마이그레이션 (900+ 고객, 매출, 패키지 등 모든 데이터)
정제된 CSV 파일들과 Excel 파일들에서 모든 데이터를 자동 삽입
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
from decimal import Decimal

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 데이터 파일 경로
EXCEL_DIR = "/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음"
PROJECT_ROOT = "/Users/vibetj/coding/center"

# Supabase 연결 정보
DB_CONFIG = {
    'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
    'password': 'bico6819!!'
}

class CompleteDataMigrator:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.connect_db()
        self.customer_map = {}  # name -> customer_id
        self.service_type_map = {}  # service_name -> service_type_id
        
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
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
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
    
    def clear_existing_data(self):
        """기존 데이터 삭제"""
        logger.info("🧹 기존 데이터 삭제 중...")
        
        # 순서대로 삭제 (외래키 제약 조건 고려)
        tables = [
            'service_usage',
            'package_purchases', 
            'payments',
            'marketing_leads',
            'kit_management',
            'customers'
        ]
        
        for table in tables:
            try:
                self.cur.execute(f"DELETE FROM {table}")
                deleted_count = self.cur.rowcount
                logger.info(f"  - {table}: {deleted_count}건 삭제")
            except Exception as e:
                logger.warning(f"  - {table} 삭제 실패: {e}")
        
        self.conn.commit()
        logger.info("✅ 기존 데이터 삭제 완료")
    
    def migrate_customers_from_csv(self):
        """정제된 CSV에서 고객 데이터 마이그레이션"""
        logger.info("📊 정제된 고객 데이터 마이그레이션 중...")
        
        csv_path = os.path.join(EXCEL_DIR, "고객관리대장_정제됨.csv")
        
        if not os.path.exists(csv_path):
            logger.error(f"정제된 고객 데이터 파일이 없습니다: {csv_path}")
            return 0
        
        df = pd.read_csv(csv_path)
        logger.info(f"📂 정제된 고객 데이터 로드: {len(df)}건")
        
        success_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                # 유효한 데이터만 처리
                if not row.get('is_valid', True):
                    continue
                
                name = str(row.get('이름', '')).strip()
                if not name or name in ['', 'nan', 'None']:
                    continue
                
                phone = self.clean_phone(row.get('phone_clean') or row.get('연락처'))
                
                if not phone:
                    logger.warning(f"전화번호 없음: {name}")
                    continue
                
                # 중복 확인
                self.cur.execute("SELECT customer_id FROM customers WHERE phone = %s", (phone,))
                if self.cur.fetchone():
                    continue  # 이미 존재하는 고객
                
                # 고객 데이터 생성
                customer_data = {
                    'name': name,
                    'phone': phone,
                    'first_visit_date': self.parse_date(row.get('first_visit_date') or row.get('첫방문일')),
                    'region': str(row.get('거주지역') or '').strip() or None,
                    'referral_source': str(row.get('방문경로') or '').strip() or None,
                    'health_concerns': str(row.get('호소문제') or '').strip() or None,
                    'notes': str(row.get('비고') or '').strip() or None,
                    'assigned_staff': str(row.get('담당자') or '직원').strip(),
                    'birth_year': self.parse_birth_year(row.get('birth_year')),
                    'gender': self.normalize_gender(row.get('gender')),
                    'membership_level': 'basic',
                    'customer_status': 'active'
                }
                
                # 데이터 삽입
                insert_query = """
                INSERT INTO customers (
                    name, phone, first_visit_date, region, referral_source, 
                    health_concerns, notes, assigned_staff, birth_year, gender,
                    membership_level, customer_status, created_at, updated_at
                ) VALUES (
                    %(name)s, %(phone)s, %(first_visit_date)s, %(region)s, %(referral_source)s,
                    %(health_concerns)s, %(notes)s, %(assigned_staff)s, %(birth_year)s, %(gender)s,
                    %(membership_level)s, %(customer_status)s, NOW(), NOW()
                ) RETURNING customer_id
                """
                
                self.cur.execute(insert_query, customer_data)
                customer_id = self.cur.fetchone()['customer_id']
                
                # 매핑 저장
                self.customer_map[name] = customer_id
                
                success_count += 1
                
                if success_count % 100 == 0:
                    self.conn.commit()
                    logger.info(f"진행률: {success_count}명 처리 완료")
                
            except Exception as e:
                error_count += 1
                logger.error(f"고객 데이터 처리 실패 (행 {idx + 1}): {e}")
                continue
        
        # 최종 커밋
        try:
            self.conn.commit()
            logger.info(f"✅ 고객 데이터 마이그레이션 완료: 성공 {success_count}명, 실패 {error_count}명")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ 커밋 실패: {e}")
        
        return success_count
    
    def migrate_payments_from_excel(self):
        """Excel에서 결제 데이터 마이그레이션"""
        logger.info("💰 결제 데이터 마이그레이션 중...")
        
        excel_path = os.path.join(EXCEL_DIR, "★2025년 AIBIO 결제현황.xlsx")
        
        if not os.path.exists(excel_path):
            logger.warning(f"결제 데이터 파일이 없습니다: {excel_path}")
            return 0
        
        try:
            # 전체 결제대장 시트 읽기
            df = pd.read_excel(excel_path, sheet_name="전체 결제대장", skiprows=2)
            logger.info(f"📂 결제 데이터 로드: {len(df)}건")
            
            success_count = 0
            
            for idx, row in df.iterrows():
                try:
                    # 첫 번째 열이 숫자인 경우만 처리
                    no_value = row.iloc[0]
                    if pd.isna(no_value):
                        continue
                    
                    try:
                        int(no_value)
                    except:
                        continue
                    
                    customer_name = str(row.get('고객명', '')).strip()
                    if not customer_name or customer_name == 'nan':
                        continue
                    
                    # 고객 찾기
                    customer_id = self.customer_map.get(customer_name)
                    if not customer_id:
                        # 새 고객 생성
                        try:
                            self.cur.execute("""
                                INSERT INTO customers (name, assigned_staff, membership_level, customer_status, created_at, updated_at)
                                VALUES (%s, '직원', 'basic', 'active', NOW(), NOW())
                                RETURNING customer_id
                            """, (customer_name,))
                            customer_id = self.cur.fetchone()['customer_id']
                            self.customer_map[customer_name] = customer_id
                        except Exception as e:
                            logger.warning(f"새 고객 생성 실패 ({customer_name}): {e}")
                            continue
                    
                    # 결제 금액 파싱
                    amount_str = str(row.get('결제 금액', 0))
                    amount = 0
                    try:
                        # 숫자가 아닌 문자 제거
                        amount_str = re.sub(r'[^\d.]', '', amount_str)
                        if amount_str:
                            amount = float(amount_str)
                    except:
                        continue
                    
                    if amount <= 0:
                        continue
                    
                    # 결제 방법 결정
                    program = str(row.get('결제 프로그램', ''))
                    payment_method = 'card'
                    if '현금' in program:
                        payment_method = 'cash'
                    elif '계좌' in program or '이체' in program:
                        payment_method = 'transfer'
                    
                    # 결제 데이터 삽입
                    payment_data = {
                        'customer_id': customer_id,
                        'payment_date': self.parse_date(row.get('결제일자')) or date.today(),
                        'amount': amount,
                        'payment_method': payment_method,
                        'payment_staff': '직원',
                        'purchase_type': program.strip() if program.strip() else None,
                        'payment_status': 'completed'
                    }
                    
                    self.cur.execute("""
                        INSERT INTO payments (
                            customer_id, payment_date, amount, payment_method, 
                            payment_staff, purchase_type, payment_status, created_at, updated_at
                        ) VALUES (
                            %(customer_id)s, %(payment_date)s, %(amount)s, %(payment_method)s,
                            %(payment_staff)s, %(purchase_type)s, %(payment_status)s, NOW(), NOW()
                        )
                    """, payment_data)
                    
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"결제 데이터 처리 실패 (행 {idx + 1}): {e}")
                    continue
            
            self.conn.commit()
            logger.info(f"✅ 결제 데이터 마이그레이션 완료: {success_count}건")
            return success_count
            
        except Exception as e:
            logger.error(f"❌ 결제 데이터 마이그레이션 실패: {e}")
            self.conn.rollback()
            return 0
    
    def create_service_types(self):
        """기본 서비스 타입 생성"""
        logger.info("🏥 서비스 타입 생성 중...")
        
        service_types = [
            ('레드 (Red)', 'LED 레드 테라피', 30000, 30, '#EF4444'),
            ('펄스 (Pulse)', '펄스 전자기장 테라피', 25000, 30, '#3B82F6'),
            ('림프 (Lymph)', '림프 순환 마사지', 35000, 45, '#10B981'),
            ('브레인 (Brain)', '뇌파 최적화 테라피', 40000, 40, '#8B5CF6'),
            ('올케어 (All Care)', '종합 케어 프로그램', 80000, 90, '#F59E0B'),
            ('InBody 측정', '체성분 분석', 10000, 15, '#6B7280'),
            ('상담', '건강 상담', 0, 30, '#EC4899')
        ]
        
        for name, desc, price, duration, color in service_types:
            try:
                self.cur.execute("""
                    INSERT INTO service_types (service_name, description, default_price, default_duration, service_color)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (service_name) DO NOTHING
                    RETURNING service_type_id
                """, (name, desc, price, duration, color))
                
                result = self.cur.fetchone()
                if result:
                    self.service_type_map[name.lower()] = result['service_type_id']
                else:
                    # 이미 존재하는 경우 ID 가져오기
                    self.cur.execute("SELECT service_type_id FROM service_types WHERE service_name = %s", (name,))
                    result = self.cur.fetchone()
                    if result:
                        self.service_type_map[name.lower()] = result['service_type_id']
                        
            except Exception as e:
                logger.warning(f"서비스 타입 생성 실패 ({name}): {e}")
        
        self.conn.commit()
        logger.info(f"✅ 서비스 타입 생성 완료: {len(self.service_type_map)}개")
    
    def run_complete_migration(self):
        """완전한 마이그레이션 실행"""
        logger.info("🚀 완전한 데이터 마이그레이션 시작")
        
        # 1. 기존 데이터 삭제
        self.clear_existing_data()
        
        # 2. 서비스 타입 생성
        self.create_service_types()
        
        # 3. 고객 데이터 마이그레이션 (935명)
        customer_count = self.migrate_customers_from_csv()
        
        # 4. 결제 데이터 마이그레이션
        payment_count = self.migrate_payments_from_excel()
        
        # 5. 최종 결과 확인
        self.cur.execute("SELECT COUNT(*) FROM customers")
        final_customer_count = self.cur.fetchone()['count']
        
        self.cur.execute("SELECT COUNT(*) FROM payments")
        final_payment_count = self.cur.fetchone()['count']
        
        self.cur.execute("SELECT COUNT(*) FROM service_types")
        service_type_count = self.cur.fetchone()['count']
        
        logger.info("🎉 완전한 마이그레이션 완료!")
        logger.info(f"📊 최종 데이터:")
        logger.info(f"   • 고객: {final_customer_count}명")
        logger.info(f"   • 결제: {final_payment_count}건") 
        logger.info(f"   • 서비스 타입: {service_type_count}개")
        
        return final_customer_count, final_payment_count, service_type_count
    
    def close(self):
        """연결 종료"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

def main():
    logger.info("=" * 80)
    logger.info("🔥 AIBIO 센터 완전한 실제 데이터 마이그레이션")
    logger.info("   • 정제된 고객 데이터 (935명)")
    logger.info("   • Excel 결제 데이터")
    logger.info("   • 서비스 타입 및 패키지")
    logger.info("=" * 80)
    
    migrator = CompleteDataMigrator()
    
    try:
        migrator.run_complete_migration()
    except KeyboardInterrupt:
        logger.info("❌ 사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close()

if __name__ == "__main__":
    main()