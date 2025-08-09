#!/usr/bin/env python3
"""
결제 데이터의 추가 필드 복구 스크립트
승인번호, 카드 명의자명, 결제 프로그램, 기타 메모 등을 복구
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
import sys
import os
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'restore_additional_fields_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AdditionalFieldsRestorer:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        self.stats = {
            'approval_numbers': 0,
            'card_holders': 0,
            'programs': 0,
            'notes': 0,
            'updated_records': 0
        }

    def backup_current_data(self):
        """현재 payments 테이블 백업"""
        logger.info("📦 추가 필드 복구 전 백업 생성 중...")

        backup_query = """
        CREATE TABLE IF NOT EXISTS payments_additional_backup AS
        SELECT
            payment_id,
            transaction_id,
            reference_type,
            notes,
            NOW() as backup_timestamp
        FROM payments
        """

        try:
            self.cur.execute("DROP TABLE IF EXISTS payments_additional_backup")
            self.cur.execute(backup_query)
            self.cur.execute("SELECT COUNT(*) as count FROM payments_additional_backup")
            count = self.cur.fetchone()['count']
            logger.info(f"✅ 백업 완료: {count}건")
            return True
        except Exception as e:
            logger.error(f"❌ 백업 실패: {e}")
            return False

    def load_excel_data(self, excel_path):
        """Excel 데이터 로드 및 전처리"""
        logger.info("📊 Excel 추가 필드 데이터 로드 중...")

        df = pd.read_excel(excel_path, sheet_name="전체 결제대장", skiprows=2)

        # 필요한 컬럼 선택
        df_clean = df[['고객명', '결제일자', '결제 금액', '카드 명의자명', '승인번호', '결제 프로그램', '기타']].copy()
        df_clean = df_clean.dropna(subset=['고객명', '결제일자', '결제 금액'])

        # 데이터 타입 정리
        df_clean['결제일자'] = pd.to_datetime(df_clean['결제일자']).dt.date
        df_clean['결제 금액'] = pd.to_numeric(df_clean['결제 금액'], errors='coerce')

        # 통계 계산
        self.stats['approval_numbers'] = df_clean['승인번호'].notna().sum()
        self.stats['card_holders'] = df_clean['카드 명의자명'].notna().sum()
        self.stats['programs'] = df_clean['결제 프로그램'].notna().sum()
        self.stats['notes'] = df_clean['기타'].notna().sum()

        logger.info(f"📈 복구 대상 데이터:")
        logger.info(f"   - 승인번호: {self.stats['approval_numbers']}건")
        logger.info(f"   - 카드 명의자명: {self.stats['card_holders']}건")
        logger.info(f"   - 결제 프로그램: {self.stats['programs']}건")
        logger.info(f"   - 기타 메모: {self.stats['notes']}건")

        return df_clean

    def add_card_holder_column(self):
        """카드 명의자명 컬럼 추가"""
        logger.info("🔧 카드 명의자명 컬럼 추가 중...")

        try:
            # 컬럼 존재 확인
            self.cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'payments' AND column_name = 'card_holder_name'
            """)

            if not self.cur.fetchone():
                self.cur.execute("""
                    ALTER TABLE payments
                    ADD COLUMN card_holder_name VARCHAR(100)
                """)
                logger.info("✅ card_holder_name 컬럼 추가 완료")
            else:
                logger.info("ℹ️  card_holder_name 컬럼 이미 존재")

        except Exception as e:
            logger.error(f"❌ 컬럼 추가 실패: {e}")
            raise

    def restore_additional_fields(self, df_excel, dry_run=False):
        """추가 필드 복구 실행"""
        logger.info(f"🔄 추가 필드 복구 {'시뮬레이션' if dry_run else '실행'} 중...")

        if not dry_run:
            # 카드 명의자명 컬럼 추가
            self.add_card_holder_column()

        # 스테이징 테이블 생성
        self.cur.execute("DROP TABLE IF EXISTS staging_additional_fields")
        self.cur.execute("""
            CREATE UNLOGGED TABLE staging_additional_fields (
                customer_name TEXT,
                payment_date DATE,
                amount NUMERIC(12,2),
                card_holder_name TEXT,
                approval_number TEXT,
                program_name TEXT,
                notes_text TEXT
            )
        """)

        # 데이터 삽입
        records = []
        for _, row in df_excel.iterrows():
            records.append((
                row['고객명'],
                row['결제일자'],
                row['결제 금액'],
                str(row['카드 명의자명']) if pd.notna(row['카드 명의자명']) else None,
                str(row['승인번호']) if pd.notna(row['승인번호']) else None,
                str(row['결제 프로그램']) if pd.notna(row['결제 프로그램']) else None,
                str(row['기타']) if pd.notna(row['기타']) else None
            ))

        execute_values(
            self.cur,
            """
            INSERT INTO staging_additional_fields
            (customer_name, payment_date, amount, card_holder_name, approval_number, program_name, notes_text)
            VALUES %s
            """,
            records
        )

        # 매칭 및 업데이트 대상 확인
        match_query = """
        WITH matches AS (
            SELECT
                p.payment_id,
                s.card_holder_name,
                s.approval_number,
                s.program_name,
                s.notes_text,
                COUNT(*) OVER (PARTITION BY p.payment_date, p.amount) as db_count,
                COUNT(*) OVER (PARTITION BY s.payment_date, s.amount) as excel_count
            FROM payments p
            JOIN staging_additional_fields s ON
                p.payment_date = s.payment_date
                AND p.amount = s.amount
        )
        SELECT
            payment_id,
            card_holder_name,
            approval_number,
            program_name,
            notes_text
        FROM matches
        WHERE db_count = 1 AND excel_count = 1  -- 1:1 매칭만 선택
        """

        self.cur.execute(match_query)
        matches = self.cur.fetchall()

        logger.info(f"📊 매칭 결과: {len(matches)}건 업데이트 가능")

        # 샘플 출력
        for match in matches[:3]:
            logger.info(f"   - Payment ID {match['payment_id']}: 카드명의자={match['card_holder_name']}, 승인번호={match['approval_number']}")

        if not dry_run and matches:
            logger.info("💾 UPDATE 실행 중...")

            try:
                # 개별 업데이트 실행
                update_count = 0

                for match in matches:
                    updates = []
                    params = {'payment_id': match['payment_id']}

                    if match['card_holder_name']:
                        updates.append("card_holder_name = %(card_holder_name)s")
                        params['card_holder_name'] = match['card_holder_name']

                    if match['approval_number']:
                        updates.append("transaction_id = %(approval_number)s")
                        params['approval_number'] = match['approval_number']

                    if match['program_name']:
                        updates.append("reference_type = %(program_name)s")
                        params['program_name'] = match['program_name']

                    if match['notes_text']:
                        updates.append("notes = %(notes_text)s")
                        params['notes_text'] = match['notes_text']

                    if updates:
                        update_query = f"""
                        UPDATE payments
                        SET {', '.join(updates)}
                        WHERE payment_id = %(payment_id)s
                        """

                        self.cur.execute(update_query, params)
                        update_count += 1

                self.stats['updated_records'] = update_count
                logger.info(f"✅ 추가 필드 업데이트 완료: {update_count}건")

            except Exception as e:
                logger.error(f"❌ UPDATE 실패: {e}")
                raise

        return len(matches)

    def validate_results(self):
        """결과 검증"""
        logger.info("✅ 추가 필드 복구 결과 검증 중...")

        # 필드별 데이터 개수 확인
        self.cur.execute("""
            SELECT
                COUNT(card_holder_name) as card_holders,
                COUNT(transaction_id) as approval_numbers,
                COUNT(reference_type) as programs,
                COUNT(notes) as notes_count
            FROM payments
        """)

        stats = self.cur.fetchone()

        logger.info("📊 복구 후 데이터 현황:")
        logger.info(f"   - 카드 명의자명: {stats['card_holders']}건")
        logger.info(f"   - 승인번호: {stats['approval_numbers']}건")
        logger.info(f"   - 결제 프로그램: {stats['programs']}건")
        logger.info(f"   - 메모: {stats['notes_count']}건")

        # 샘플 데이터 확인
        self.cur.execute("""
            SELECT
                payment_id,
                card_holder_name,
                transaction_id,
                reference_type,
                LEFT(notes, 50) as notes_preview
            FROM payments
            WHERE card_holder_name IS NOT NULL
               OR transaction_id IS NOT NULL
               OR reference_type IS NOT NULL
               OR notes IS NOT NULL
            LIMIT 5
        """)

        logger.info("\n샘플 복구 데이터:")
        for row in self.cur.fetchall():
            logger.info(f"   ID {row['payment_id']}: {row['card_holder_name']}, {row['transaction_id']}, {row['reference_type']}")

    def generate_report(self):
        """복구 보고서 생성"""
        report = f"""
# 결제 추가 필드 복구 보고서
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 복구 결과

### 대상 데이터
- 승인번호: {self.stats['approval_numbers']}건
- 카드 명의자명: {self.stats['card_holders']}건
- 결제 프로그램: {self.stats['programs']}건
- 기타 메모: {self.stats['notes']}건

### 실제 복구
- 업데이트된 결제: {self.stats['updated_records']}건

### 복구된 필드
1. transaction_id ← 승인번호
2. card_holder_name ← 카드 명의자명
3. reference_type ← 결제 프로그램
4. notes ← 기타 메모

## 🎯 개선 효과
- 결제 추적성 향상 (승인번호)
- 결제 확인 편의성 증대 (카드 명의자명)
- 서비스 분류 정확성 향상 (결제 프로그램)
- 특이사항 기록 보완 (메모)
"""
        return report

    def close(self):
        """연결 종료"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

def main():
    # DB 설정
    db_config = {
        'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
        'port': 6543,
        'database': 'postgres',
        'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
        'password': r'bico6819!!'
    }

    if len(sys.argv) < 2:
        print("사용법: python restore_additional_payment_fields.py <excel_file_path> [--dry-run]")
        sys.exit(1)

    excel_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    restorer = AdditionalFieldsRestorer(db_config)

    try:
        # 1. 백업
        if not restorer.backup_current_data():
            raise Exception("백업 실패")

        # 2. Excel 데이터 로드
        df_excel = restorer.load_excel_data(excel_path)

        # 3. 추가 필드 복구
        matched_count = restorer.restore_additional_fields(df_excel, dry_run=dry_run)

        if not dry_run:
            # 4. 커밋
            restorer.conn.commit()
            logger.info("✅ 트랜잭션 커밋 완료")

            # 5. 결과 검증
            restorer.validate_results()
        else:
            restorer.conn.rollback()
            logger.info("ℹ️  Dry-run 모드 - 변경사항 롤백")

        # 6. 보고서 생성
        report = restorer.generate_report()
        print("\n" + report)

        # 보고서 파일 저장
        report_path = f"additional_fields_restore_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"📄 보고서 저장: {report_path}")

    except Exception as e:
        logger.error(f"❌ 오류 발생: {e}")
        restorer.conn.rollback()

    finally:
        restorer.close()

if __name__ == "__main__":
    main()
