import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import SessionLocal

def add_master_role():
    """user_role enum에 master 추가"""
    db = SessionLocal()

    try:
        # 현재 enum 값 확인
        result = db.execute(text("""
            SELECT enum_range(NULL::user_role) as enum_values;
        """))
        current_values = result.fetchone()[0]
        print(f"현재 user_role enum 값: {current_values}")

        # master가 이미 있는지 확인
        if 'master' in current_values:
            print("✅ 'master' role이 이미 존재합니다.")
            return

        # master role 추가
        print("'master' role을 추가합니다...")

        # ALTER TYPE은 트랜잭션 내에서 실행할 수 없으므로 별도로 실행
        db.rollback()  # 현재 트랜잭션 종료
        db.execute(text("COMMIT"))  # 명시적 커밋

        db.execute(text("""
            ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'master' AFTER 'admin';
        """))

        print("✅ 'master' role이 성공적으로 추가되었습니다.")

        # 다시 확인
        result = db.execute(text("""
            SELECT enum_range(NULL::user_role) as enum_values;
        """))
        new_values = result.fetchone()[0]
        print(f"업데이트된 user_role enum 값: {new_values}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== user_role enum에 master 추가 ===")
    add_master_role()
