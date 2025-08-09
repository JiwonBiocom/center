"""직접 DB 쿼리 테스트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import joinedload
from core.database import SessionLocal
from models.customer_extended import MarketingLead
from utils.response_formatter import paginate_query

def test_query():
    db = SessionLocal()
    try:
        print("1. 기본 쿼리 테스트")
        query = db.query(MarketingLead)
        count = query.count()
        print(f"   총 레코드 수: {count}")
        
        print("\n2. joinedload 추가")
        query = db.query(MarketingLead).options(
            joinedload(MarketingLead.assigned_staff),
            joinedload(MarketingLead.converted_customer)
        )
        count = query.count()
        print(f"   조인 후 레코드 수: {count}")
        
        print("\n3. 정렬 추가")
        query = query.order_by(MarketingLead.created_at.desc())
        first = query.first()
        if first:
            print(f"   첫 번째 레코드: {first.name}")
        
        print("\n4. paginate_query 테스트")
        try:
            result = paginate_query(query, 1, 5)
            print(f"   페이지네이션 성공: {len(result['items'])}개 항목")
            
            # 관계 필드 접근 테스트
            for item in result["items"][:2]:
                print(f"\n   - {item.name}")
                if hasattr(item, 'assigned_staff'):
                    print(f"     assigned_staff 존재: {item.assigned_staff is not None}")
                    if item.assigned_staff:
                        print(f"     담당자: {item.assigned_staff.name}")
                else:
                    print("     assigned_staff 속성 없음")
                    
        except Exception as e:
            print(f"   페이지네이션 에러: {str(e)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_query()