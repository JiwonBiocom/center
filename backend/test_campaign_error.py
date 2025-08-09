#!/usr/bin/env python3
"""Test campaign stats endpoint to see detailed error"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from core.config import settings
from core.database import SessionLocal
from models.lead_management import ReregistrationCampaign, CampaignTarget
from sqlalchemy import func, Integer
from sqlalchemy.orm import Session

def test_campaign_stats():
    db = SessionLocal()
    try:
        # 동일한 쿼리 실행
        total_campaigns = db.query(ReregistrationCampaign).count()
        print(f"Total campaigns: {total_campaigns}")
        
        active_campaigns = db.query(ReregistrationCampaign).filter(
            ReregistrationCampaign.is_active == True
        ).count()
        print(f"Active campaigns: {active_campaigns}")
        
        # 문제가 되는 쿼리
        print("\nTesting problematic query...")
        try:
            targets_stats = db.query(
                func.count(CampaignTarget.target_id).label('total_targets'),
                func.sum(func.cast(CampaignTarget.converted, Integer)).label('total_conversions')
            ).first()
            print(f"Query result: {targets_stats}")
            print(f"Total targets: {targets_stats.total_targets}")
            print(f"Total conversions: {targets_stats.total_conversions}")
        except Exception as e:
            print(f"Error in query: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        db.close()

if __name__ == "__main__":
    test_campaign_stats()