#!/usr/bin/env python3
"""
결제 담당자 데이터 복구 스크립트
방안 1: 기존 데이터 UPDATE 방식으로 구현
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import sys
import os
from datetime import datetime
import logging
import hashlib
import json

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'restore_payment_staff_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PaymentStaffRestorer:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        self.stats = {
            'total_excel_records': 0,
            'total_db_records': 0,
            'matched_records': 0,
            'updated_records': 0,
            'failed_matches': [],
            'duplicate_keys': []
        }

    def backup_current_data(self):
        """현재 payments 테이블 백업"""
        logger.info("📦 현재 payment_staff 데이터 백업 중...")

        backup_query = """
        CREATE TABLE IF NOT EXISTS payments_staff_backup AS
        SELECT
            payment_id,
            customer_id,
            payment_date,
            amount,
            payment_staff,
            NOW() as backup_timestamp
        FROM payments
        """

        try:
            self.cur.execute("DROP TABLE IF EXISTS payments_staff_backup")
            self.cur.execute(backup_query)
            self.cur.execute("SELECT COUNT(*) as count FROM payments_staff_backup")
            count = self.cur.fetchone()['count']
            logger.info(f"✅ 백업 완료: {count}건")
            return True
        except Exception as e:
            logger.error(f"❌ 백업 실패: {e}")
            return False

    def load_excel_to_staging(self, excel_path):
        """Excel 데이터를 스테이징 테이블로 로드"""
        logger.info("📊 Excel 데이터 로드 중...")

        # Excel 읽기
        df = pd.read_excel(excel_path, sheet_name="전체 결제대장", skiprows=2)

        # 필요한 컬럼만 선택
        df_clean = df[['고객명', '결제일자', '결제 금액', '결제 담당자']].copy()
        df_clean = df_clean.dropna(subset=['고객명', '결제일자', '결제 금액'])

        # 컬럼명 변경
        df_clean.columns = ['customer_name', 'payment_date', 'amount', 'payment_staff']

        # 데이터 타입 정리
        df_clean['payment_date'] = pd.to_datetime(df_clean['payment_date']).dt.date
        df_clean['amount'] = pd.to_numeric(df_clean['amount'], errors='coerce')

        self.stats['total_excel_records'] = len(df_clean)
        logger.info(f"📈 Excel 레코드 수: {len(df_clean)}건")

        # 스테이징 테이블 생성
        self.cur.execute("DROP TABLE IF EXISTS staging_payment_staff")
        self.cur.execute("""
            CREATE UNLOGGED TABLE staging_payment_staff (
                customer_name TEXT,
                payment_date DATE,
                amount NUMERIC(12,2),
                payment_staff TEXT
            )
        """)

        # 데이터 삽입
        records = df_clean.to_records(index=False).tolist()
        execute_values(
            self.cur,
            """
            INSERT INTO staging_payment_staff
            (customer_name, payment_date, amount, payment_staff)
            VALUES %s
            """,
            records
        )

        logger.info(f"✅ 스테이징 테이블 로드 완료")
        return df_clean

    def validate_staging_data(self):
        """스테이징 데이터 검증"""
        logger.info("🔍 스테이징 데이터 검증 중...")

        # 1. 중복 키 확인
        duplicate_query = """
        SELECT customer_name, payment_date, amount, COUNT(*) as cnt
        FROM staging_payment_staff
        GROUP BY customer_name, payment_date, amount
        HAVING COUNT(*) > 1
        """

        self.cur.execute(duplicate_query)
        duplicates = self.cur.fetchall()

        if duplicates:
            logger.warning(f"⚠️  중복 키 발견: {len(duplicates)}개")
            self.stats['duplicate_keys'] = duplicates
            for dup in duplicates[:5]:  # 처음 5개만 출력
                logger.warning(f"   - {dup['customer_name']} / {dup['payment_date']} / {dup['amount']}원 ({dup['cnt']}건)")

        # 2. NULL 값 체크
        self.cur.execute("""
            SELECT
                SUM(CASE WHEN payment_staff IS NULL THEN 1 ELSE 0 END) as null_staff,
                SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) as null_name
            FROM staging_payment_staff
        """)
        null_stats = self.cur.fetchone()

        if null_stats['null_staff'] > 0:
            logger.warning(f"⚠️  담당자 NULL: {null_stats['null_staff']}건")

        # 3. 통계 정보
        self.cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT customer_name) as unique_customers,
                COUNT(DISTINCT payment_staff) as unique_staff,
                SUM(amount) as total_amount
            FROM staging_payment_staff
        """)
        stats = self.cur.fetchone()

        logger.info(f"📊 스테이징 통계:")
        logger.info(f"   - 전체 건수: {stats['total']}")
        logger.info(f"   - 고유 고객: {stats['unique_customers']}")
        logger.info(f"   - 고유 담당자: {stats['unique_staff']}")
        logger.info(f"   - 총 금액: {stats['total_amount']:,.0f}원")

        return len(duplicates) == 0

    def create_matching_keys(self):
        """매칭을 위한 키 생성"""
        logger.info("🔑 매칭 키 생성 중...")

        # 날짜와 금액으로만 매칭 (고객명은 일치하지 않을 수 있음)
        self.cur.execute("""
            CREATE TEMP TABLE payment_keys AS
            SELECT
                p.payment_id,
                p.payment_date,
                p.amount,
                p.payment_staff as current_staff,
                c.name as db_customer_name
            FROM payments p
            LEFT JOIN customers c ON p.customer_id = c.customer_id
        """)

        self.cur.execute("SELECT COUNT(*) as count FROM payment_keys")
        count = self.cur.fetchone()['count']
        self.stats['total_db_records'] = count
        logger.info(f"✅ DB 결제 레코드: {count}건")

    def execute_update(self, dry_run=False):
        """UPDATE 실행"""
        logger.info(f"🔄 UPDATE {'시뮬레이션' if dry_run else '실행'} 중...")

        # 매칭 및 업데이트 대상 확인 - 날짜와 금액으로만 매칭
        match_query = """
        WITH date_amount_matches AS (
            SELECT
                pk.payment_id,
                pk.payment_date,
                pk.amount,
                pk.current_staff,
                pk.db_customer_name,
                s.customer_name as excel_customer_name,
                s.payment_staff as new_staff,
                COUNT(*) OVER (PARTITION BY pk.payment_date, pk.amount) as db_count,
                COUNT(*) OVER (PARTITION BY s.payment_date, s.amount) as excel_count
            FROM payment_keys pk
            JOIN staging_payment_staff s ON
                pk.payment_date = s.payment_date
                AND pk.amount = s.amount
        )
        SELECT
            payment_id,
            payment_date,
            amount,
            current_staff,
            new_staff,
            db_customer_name,
            excel_customer_name
        FROM date_amount_matches
        WHERE db_count = 1 AND excel_count = 1  -- 1:1 매칭만 선택
          AND current_staff != new_staff
        """

        self.cur.execute(match_query)
        matches = self.cur.fetchall()
        self.stats['matched_records'] = len(matches)

        logger.info(f"📊 매칭 결과: {len(matches)}건 업데이트 필요")

        # 샘플 출력
        for match in matches[:5]:
            logger.info(f"   - DB:{match['db_customer_name']} / Excel:{match['excel_customer_name']} ({match['payment_date']}): {match['current_staff']} → {match['new_staff']}")

        if not dry_run and matches:
            # 트랜잭션 시작
            logger.info("💾 UPDATE 트랜잭션 시작...")

            try:
                # 변경 이력 저장
                self.cur.execute("""
                    CREATE TABLE IF NOT EXISTS payment_staff_changes (
                        payment_id INTEGER,
                        old_staff TEXT,
                        new_staff TEXT,
                        changed_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # 변경 이력 기록
                change_records = [(m['payment_id'], m['current_staff'], m['new_staff']) for m in matches]
                execute_values(
                    self.cur,
                    "INSERT INTO payment_staff_changes (payment_id, old_staff, new_staff) VALUES %s",
                    change_records
                )

                # UPDATE 실행 - 날짜와 금액 기반 매칭
                update_query = """
                WITH date_amount_matches AS (
                    SELECT
                        p.payment_id,
                        s.payment_staff as new_staff,
                        COUNT(*) OVER (PARTITION BY p.payment_date, p.amount) as db_count,
                        COUNT(*) OVER (PARTITION BY s.payment_date, s.amount) as excel_count
                    FROM payments p
                    JOIN staging_payment_staff s ON
                        p.payment_date = s.payment_date
                        AND p.amount = s.amount
                    WHERE p.payment_staff != s.payment_staff
                )
                UPDATE payments
                SET payment_staff = dam.new_staff
                FROM date_amount_matches dam
                WHERE payments.payment_id = dam.payment_id
                  AND dam.db_count = 1
                  AND dam.excel_count = 1
                """

                self.cur.execute(update_query)
                self.stats['updated_records'] = self.cur.rowcount

                logger.info(f"✅ UPDATE 완료: {self.stats['updated_records']}건")

            except Exception as e:
                logger.error(f"❌ UPDATE 실패: {e}")
                raise

        # 미매칭 레코드 확인 - 날짜와 금액 기준
        self.cur.execute("""
            SELECT customer_name, payment_date, amount, payment_staff
            FROM staging_payment_staff s
            WHERE NOT EXISTS (
                SELECT 1 FROM payment_keys pk
                WHERE pk.payment_date = s.payment_date
                    AND pk.amount = s.amount
            )
        """)
        unmatched = self.cur.fetchall()

        if unmatched:
            logger.warning(f"⚠️  미매칭 레코드: {len(unmatched)}건")
            self.stats['failed_matches'] = unmatched[:10]  # 처음 10개만 저장

    def validate_results(self):
        """결과 검증"""
        logger.info("✅ 결과 검증 중...")

        # 담당자 분포 확인
        self.cur.execute("""
            SELECT payment_staff, COUNT(*) as count
            FROM payments
            GROUP BY payment_staff
            ORDER BY count DESC
        """)

        staff_dist = self.cur.fetchall()

        logger.info("📊 업데이트 후 담당자 분포:")
        for staff in staff_dist:
            logger.info(f"   - {staff['payment_staff']}: {staff['count']}건")

        # 해시 기반 검증 (샘플)
        self.cur.execute("""
            SELECT
                MD5(STRING_AGG(payment_staff || payment_date::text || amount::text, '|' ORDER BY payment_id)) as db_hash
            FROM payments
            WHERE payment_date >= '2025-01-01'
        """)
        db_hash = self.cur.fetchone()['db_hash']

        logger.info(f"🔐 DB 데이터 해시: {db_hash[:16]}...")

    def generate_report(self):
        """최종 보고서 생성"""
        report = f"""
# 결제 담당자 데이터 복구 보고서
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 실행 결과

### 데이터 통계
- Excel 레코드: {self.stats['total_excel_records']}건
- DB 레코드: {self.stats['total_db_records']}건
- 매칭 성공: {self.stats['matched_records']}건
- 실제 업데이트: {self.stats['updated_records']}건

### 이슈 사항
- 중복 키: {len(self.stats['duplicate_keys'])}개
- 미매칭: {len(self.stats['failed_matches'])}건

### 권장 조치
"""
        if self.stats['failed_matches']:
            report += "\n1. 미매칭 레코드 수동 확인 필요"
            report += "\n2. 고객명 불일치 또는 금액 변경 케이스 검토"

        if self.stats['duplicate_keys']:
            report += "\n3. 중복 키 해결을 위한 추가 식별자 필요"

        return report

    def rollback(self):
        """롤백 실행"""
        logger.warning("⚠️  롤백 실행 중...")

        self.cur.execute("""
            UPDATE payments p
            SET payment_staff = b.payment_staff
            FROM payments_staff_backup b
            WHERE p.payment_id = b.payment_id
        """)

        logger.info("✅ 롤백 완료")

    def close(self):
        """연결 종료"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

def main():
    # DB 설정 - Supabase 연결 정보
    db_config = {
        'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
        'password': r'bico6819!!'
    }

    if len(sys.argv) < 2:
        print("사용법: python restore_payment_staff.py <excel_file_path> [--dry-run]")
        sys.exit(1)

    excel_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    restorer = PaymentStaffRestorer(db_config)

    try:
        # 1. 백업
        if not restorer.backup_current_data():
            raise Exception("백업 실패")

        # 2. Excel 로드
        restorer.load_excel_to_staging(excel_path)

        # 3. 검증
        if not restorer.validate_staging_data():
            logger.warning("⚠️  데이터 검증 경고 발생")

        # 4. 매칭 키 생성
        restorer.create_matching_keys()

        # 5. UPDATE 실행
        restorer.execute_update(dry_run=dry_run)

        if not dry_run:
            # 6. 커밋
            restorer.conn.commit()
            logger.info("✅ 트랜잭션 커밋 완료")

            # 7. 결과 검증
            restorer.validate_results()
        else:
            restorer.conn.rollback()
            logger.info("ℹ️  Dry-run 모드 - 변경사항 롤백")

        # 8. 보고서 생성
        report = restorer.generate_report()
        print("\n" + report)

        # 보고서 파일 저장
        report_path = f"payment_staff_restore_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"📄 보고서 저장: {report_path}")

    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        restorer.conn.rollback()

        if input("\n롤백하시겠습니까? (y/N): ").lower() == 'y':
            restorer.rollback()
            restorer.conn.commit()

    finally:
        restorer.close()

if __name__ == "__main__":
    main()
