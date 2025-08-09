import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from core.auth import get_password_hash
from models.user import User

def create_taejun_master():
    """TaeJun 마스터 계정 생성"""
    db = SessionLocal()

    try:
        email = "taejun@biocom.kr"

        # 기존 사용자 확인
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            # 기존 사용자를 마스터로 업그레이드
            existing_user.role = "master"
            existing_user.password_hash = get_password_hash("admin1234")
            db.commit()
            print(f"✅ 사용자 {email}이(가) 마스터 권한으로 업그레이드되었습니다.")
            print(f"   비밀번호가 'admin1234'로 재설정되었습니다.")
        else:
            # 신규 마스터 사용자 생성
            new_user = User(
                email=email,
                name="TaeJun",
                password_hash=get_password_hash("admin1234"),
                role="master",
                is_active=True
            )
            db.add(new_user)
            db.commit()
            print(f"✅ 마스터 사용자가 성공적으로 생성되었습니다!")
            print(f"   이메일: {email}")
            print(f"   비밀번호: admin1234")
            print(f"   권한: master")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=== TaeJun 마스터 계정 생성 ===")
    create_taejun_master()
