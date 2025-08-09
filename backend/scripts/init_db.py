import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, Base
from models import user, customer, service, payment, package, lead, kit, audit

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")