#!/usr/bin/env python3
"""
로컬 DB에서 결제 데이터를 CSV로 추출
실행: python scripts/export_payments_to_csv.py
"""
import csv
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

# 환경 변수 로드
load_dotenv()

def export_payments():
    """로컬 DB에서 결제 데이터 추출"""
    
    # 로컬 DATABASE_URL 사용
    local_db_url = os.getenv("DATABASE_URL")
    if not local_db_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return False
    
    try:
        engine = create_engine(local_db_url)
        
        # payments 테이블 데이터 확인
        with engine.begin() as conn:
            # 먼저 테이블 존재 여부와 데이터 개수 확인
            count_result = conn.execute(text("SELECT COUNT(*) as count FROM payments"))
            payment_count = count_result.scalar()
            
            print(f"📊 로컬 DB payments 테이블: {payment_count}개 레코드")
            
            if payment_count == 0:
                print("⚠️ 로컬 DB에 결제 데이터가 없습니다.")
                return False
            
            # 데이터 추출 쿼리
            sql_query = """
            SELECT
                p.payment_id,
                p.customer_id,
                p.payment_date,
                p.amount,
                p.payment_method,
                p.created_at
            FROM payments p
            JOIN customers c ON p.customer_id = c.customer_id
            ORDER BY p.payment_id
            """
            
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
            
            # CSV 파일 생성
            csv_dir = Path("backend/seed")
            csv_dir.mkdir(exist_ok=True)
            csv_path = csv_dir / "payments.csv"
            
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # 헤더 작성
                writer.writerow(["payment_id", "customer_id", "payment_date", "amount", "payment_method", "created_at"])
                
                # 데이터 작성
                for row in rows:
                    writer.writerow([
                        row.payment_id,
                        row.customer_id,
                        row.payment_date.isoformat() if row.payment_date else None,
                        float(row.amount) if row.amount else 0,
                        row.payment_method,
                        row.created_at.isoformat() if row.created_at else None
                    ])
            
            print(f"✅ CSV 파일 생성 완료: {csv_path}")
            print(f"📁 파일 크기: {csv_path.stat().st_size / 1024:.1f} KB")
            print(f"📊 추출된 레코드: {len(rows)}개")
            
            # 샘플 데이터 표시
            if rows:
                print("\n📋 샘플 데이터 (첫 5개):")
                for i, row in enumerate(rows[:5]):
                    print(f"  {i+1}. ID:{row.payment_id} | {row.payment_date} | ₩{row.amount:,} | {row.payment_method}")
            
            return True
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 로컬 DB → CSV 추출 도구")
    print("=" * 50)
    
    success = export_payments()
    
    if success:
        print("\n🎉 추출 완료!")
        print("💡 다음 단계:")
        print("   1. git add backend/seed/payments.csv")
        print("   2. git commit -m 'feat: 로컬 결제 데이터 CSV 추출'")
        print("   3. GitHub Actions로 Supabase 로드 실행")
    else:
        print("\n❌ 추출 실패. 로컬 DB 상태를 확인하세요.")

if __name__ == "__main__":
    main()