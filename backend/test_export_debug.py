"""엑셀 내보내기 디버그"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models.customer_extended import MarketingLead
import pandas as pd
from io import BytesIO
from datetime import date

def test_export():
    db = SessionLocal()
    try:
        # 데이터 조회
        leads = db.query(MarketingLead).limit(5).all()
        print(f"조회된 데이터: {len(leads)}개")
        
        # DataFrame 생성
        data = []
        for lead in leads:
            try:
                row = {
                    '이름': lead.name,
                    '연락처': lead.phone,
                    '나이': lead.age,
                    '거주지역': lead.region,
                    '유입경로': lead.lead_channel,
                    'DB작성 채널': lead.db_channel,
                    '당근아이디': lead.carrot_id,
                    '시청 광고': lead.ad_watched,
                    '가격안내': '예' if lead.price_informed else '아니오',
                    'DB입력일': lead.db_entry_date,
                    '전화상담일': lead.phone_consult_date,
                    '방문상담일': lead.visit_consult_date,
                    '등록일': lead.registration_date,
                    '구매상품': lead.purchased_product,
                    '미등록사유': lead.no_registration_reason,
                    '비고': lead.notes,
                    '매출': lead.revenue
                }
                data.append(row)
                print(f"✅ {lead.name} 처리 완료")
            except Exception as e:
                print(f"❌ {lead.name} 처리 실패: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n변환된 데이터: {len(data)}개")
        
        # DataFrame 생성
        df = pd.DataFrame(data)
        print(f"DataFrame 생성 완료: {df.shape}")
        
        # Excel 파일 생성
        output = BytesIO()
        df.to_excel(output, index=False)
        print(f"Excel 파일 생성 완료: {len(output.getvalue())} bytes")
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_export()