"""직접 가져오기 테스트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import date
from io import BytesIO
from core.database import SessionLocal
from models.customer_extended import MarketingLead

def test_import_direct():
    # 테스트 데이터
    test_data = pd.DataFrame([
        {
            "이름": "직접테스트1",
            "연락처": "010-7777-7777",
            "나이": 30,
            "거주지역": "서울",
            "유입경로": "인스타그램",
            "DB작성 채널": "구글폼",
            "가격안내": "예",
            "DB입력일": date.today().strftime("%Y-%m-%d")
        }
    ])
    
    print("테스트 데이터:")
    print(test_data)
    
    # 컬럼 매핑
    column_mapping = {
        '이름': 'name',
        '연락처': 'phone',
        '나이': 'age',
        '거주지역': 'region',
        '유입경로': 'lead_channel',
        'DB작성 채널': 'db_channel',
        '당근아이디': 'carrot_id',
        '시청 광고': 'ad_watched',
        '가격안내': 'price_informed',
        'A/B 테스트': 'ab_test_group',
        'DB입력일': 'db_entry_date',
        '전화상담일': 'phone_consult_date',
        '방문상담일': 'visit_consult_date',
        '등록일': 'registration_date',
        '구매상품': 'purchased_product',
        '미등록사유': 'no_registration_reason',
        '비고': 'notes',
        '매출': 'revenue'
    }
    
    db = SessionLocal()
    try:
        for index, row in test_data.iterrows():
            print(f"\n행 {index + 1} 처리:")
            lead_data = {}
            
            for excel_col, db_col in column_mapping.items():
                if excel_col in row and pd.notna(row[excel_col]):
                    value = row[excel_col]
                    print(f"  {excel_col} -> {db_col}: {value}")
                    
                    # 가격안내 특별 처리
                    if db_col == 'price_informed':
                        lead_data[db_col] = value == '예'
                    else:
                        lead_data[db_col] = value
            
            # lead_date 설정
            if 'db_entry_date' in lead_data:
                lead_data['lead_date'] = lead_data['db_entry_date']
            else:
                lead_data['lead_date'] = date.today()
            
            print(f"\n변환된 데이터: {lead_data}")
            
            # 리드 생성 시도
            try:
                db_lead = MarketingLead(**lead_data)
                db.add(db_lead)
                db.commit()
                print(f"✅ 성공! ID: {db_lead.lead_id}")
            except Exception as e:
                print(f"❌ 실패: {str(e)}")
                import traceback
                traceback.print_exc()
                db.rollback()
                
    finally:
        db.close()

if __name__ == "__main__":
    test_import_direct()