#!/usr/bin/env python3
"""
데이터 마이그레이션 검증 스크립트
Excel/CSV 데이터를 DB로 마이그레이션한 후 데이터 무결성을 검증합니다.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime
import json
from typing import Dict, List, Tuple, Any

# DB 연결 정보 (환경변수에서 읽도록 개선 필요)
DB_CONFIG = {
    'host': 'aws-0-ap-northeast-2.pooler.supabase.com',
    'port': 6543,
    'database': 'postgres',
    'user': 'postgres.wvcxzyvmwwrbjpeuyvuh',
    'password': 'bico6819!!'
}

class MigrationValidator:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)

    def get_excel_statistics(self, file_path: str, sheet_name: str = None) -> Dict[str, Any]:
        """Excel 파일의 통계 정보 추출"""
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2)
        else:
            df = pd.read_excel(file_path, skiprows=2)

        stats = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'unique_values': {}
        }

        # 주요 컬럼의 고유값 개수
        for col in df.columns:
            if df[col].dtype == 'object':
                stats['unique_values'][col] = df[col].nunique()

        return stats

    def get_db_statistics(self, table_name: str) -> Dict[str, Any]:
        """DB 테이블의 통계 정보 추출"""
        # 전체 행 수
        self.cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        total_rows = self.cur.fetchone()['count']

        # 컬럼 정보
        self.cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = self.cur.fetchall()

        # NULL 값 카운트
        null_counts = {}
        for col in columns:
            col_name = col['column_name']
            self.cur.execute(f"SELECT COUNT(*) as count FROM {table_name} WHERE {col_name} IS NULL")
            null_counts[col_name] = self.cur.fetchone()['count']

        return {
            'total_rows': total_rows,
            'columns': [col['column_name'] for col in columns],
            'null_counts': null_counts
        }

    def validate_payment_migration(self, excel_path: str) -> Tuple[Dict, List[str]]:
        """결제 데이터 마이그레이션 검증"""
        print("📊 결제 데이터 마이그레이션 검증 시작...")

        # Excel 데이터 읽기
        df_all = pd.read_excel(excel_path, sheet_name="전체 결제대장", skiprows=2)

        # 검증 결과
        issues = []
        stats = {
            'excel': {
                'total_rows': len(df_all),
                'unique_customers': df_all['고객명'].nunique(),
                'unique_staff': df_all['결제 담당자'].nunique(),
                'staff_distribution': df_all['결제 담당자'].value_counts().to_dict()
            }
        }

        # DB 데이터 검증
        self.cur.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT customer_id) as unique_customers,
                COUNT(DISTINCT payment_staff) as unique_staff
            FROM payments
        """)
        db_stats = self.cur.fetchone()
        stats['db'] = dict(db_stats)

        # 담당자 분포 확인
        self.cur.execute("""
            SELECT payment_staff, COUNT(*) as count
            FROM payments
            GROUP BY payment_staff
            ORDER BY count DESC
        """)
        staff_dist = {row['payment_staff']: row['count'] for row in self.cur.fetchall()}
        stats['db']['staff_distribution'] = staff_dist

        # 문제점 검출
        if stats['excel']['unique_staff'] > stats['db']['unique_staff']:
            issues.append(f"❌ 담당자 다양성 손실: Excel {stats['excel']['unique_staff']}명 → DB {stats['db']['unique_staff']}명")

        if len(staff_dist) == 1 and '직원' in staff_dist:
            issues.append("❌ 모든 담당자가 '직원'으로 하드코딩됨")

        # 샘플 데이터 비교 (김준호 사례)
        kimjunho_excel = df_all[df_all['고객명'] == '김준호']
        if not kimjunho_excel.empty:
            excel_staff = kimjunho_excel['결제 담당자'].unique()

            self.cur.execute("""
                SELECT DISTINCT p.payment_staff
                FROM payments p
                JOIN customers c ON p.customer_id = c.customer_id
                WHERE c.name = '김준호'
            """)
            db_staff = [row['payment_staff'] for row in self.cur.fetchall()]

            if set(excel_staff) != set(db_staff):
                issues.append(f"❌ 김준호 담당자 불일치: Excel {excel_staff} → DB {db_staff}")

        return stats, issues

    def generate_report(self, stats: Dict, issues: List[str]) -> str:
        """검증 보고서 생성"""
        report = f"""
# 데이터 마이그레이션 검증 보고서
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 통계 요약

### Excel 데이터
- 전체 행 수: {stats['excel']['total_rows']}
- 고유 고객 수: {stats['excel']['unique_customers']}
- 고유 담당자 수: {stats['excel']['unique_staff']}
- 담당자 분포: {json.dumps(stats['excel']['staff_distribution'], ensure_ascii=False, indent=2)}

### DB 데이터
- 전체 행 수: {stats['db']['total']}
- 고유 고객 수: {stats['db']['unique_customers']}
- 고유 담당자 수: {stats['db']['unique_staff']}
- 담당자 분포: {json.dumps(stats['db']['staff_distribution'], ensure_ascii=False, indent=2)}

## 🚨 발견된 문제점
"""
        if issues:
            for issue in issues:
                report += f"\n{issue}"
        else:
            report += "\n✅ 문제점이 발견되지 않았습니다."

        return report

    def close(self):
        """연결 종료"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

def main():
    if len(sys.argv) < 2:
        print("사용법: python validate_migration.py <excel_file_path>")
        sys.exit(1)

    excel_path = sys.argv[1]

    validator = MigrationValidator()
    try:
        stats, issues = validator.validate_payment_migration(excel_path)
        report = validator.generate_report(stats, issues)

        print(report)

        # 보고서 파일로 저장
        report_path = f"migration_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 보고서 저장됨: {report_path}")

    finally:
        validator.close()

if __name__ == "__main__":
    main()
