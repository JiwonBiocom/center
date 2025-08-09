from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from models.customer import Customer
import os
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()

# 고객 상태별 통계
status_stats = session.query(
    Customer.customer_status,
    func.count(Customer.customer_id).label('count')
).group_by(Customer.customer_status).all()

print("=== 고객 상태별 통계 ===")
for stat in status_stats:
    print(f"{stat.customer_status}: {stat.count}명")

# 위험도별 통계
risk_stats = session.query(
    Customer.risk_level,
    func.count(Customer.customer_id).label('count')
).group_by(Customer.risk_level).all()

print("\n=== 위험도별 통계 ===")
for stat in risk_stats:
    print(f"{stat.risk_level}: {stat.count}명")

# 회원 등급별 통계
membership_stats = session.query(
    Customer.membership_level,
    func.count(Customer.customer_id).label('count')
).group_by(Customer.membership_level).all()

print("\n=== 회원 등급별 통계 ===")
for stat in membership_stats:
    print(f"{stat.membership_level}: {stat.count}명")

# 최근 방문 고객 확인
recent_customers = session.query(Customer).filter(
    Customer.last_visit_date.isnot(None)
).order_by(Customer.last_visit_date.desc()).limit(10).all()

print("\n=== 최근 방문 고객 (상위 10명) ===")
for customer in recent_customers:
    print(f"{customer.name}: 마지막 방문 {customer.last_visit_date}, 총 {customer.total_visits}회 방문")

session.close()