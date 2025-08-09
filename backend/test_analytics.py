import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api.v1.customer_leads import get_lead_analytics
from models.user import User

# Create a mock user
class MockUser:
    user_id = 1
    email = "admin@aibio.com"
    role = "admin"

def test_analytics():
    db = SessionLocal()
    try:
        # Call the analytics function directly
        result = get_lead_analytics(
            date_from=None,
            date_to=None,
            db=db,
            current_user=MockUser()
        )
        print("Success!")
        print(f"Total leads: {result['overview']['total_leads']}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_analytics()