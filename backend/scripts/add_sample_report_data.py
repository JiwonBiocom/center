#!/usr/bin/env python3
"""Add sample data for testing reports functionality"""
from datetime import datetime, timedelta, date
import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from models.customer import Customer
from models.payment import Payment
from models.service import ServiceType, ServiceUsage
from models.package import Package

def add_sample_report_data():
    """Add sample data for reports"""
    db = SessionLocal()
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Get existing customers or create new ones
        customers = db.query(Customer).limit(10).all()
        if len(customers) < 10:
            print("Creating sample customers...")
            for i in range(10 - len(customers)):
                customer = Customer(
                    name=f"테스트고객{i+1}",
                    phone=f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                    first_visit_date=date.today() - timedelta(days=random.randint(30, 365)),
                    region="서울",
                    referral_source=random.choice(["지인소개", "인터넷", "블로그", "직접방문"]),
                    assigned_staff=random.choice(["김직원", "이직원", "박직원", "최직원"])
                )
                db.add(customer)
                customers.append(customer)
            db.commit()
            customers = db.query(Customer).all()
        
        # Add service types if not exist
        service_types = db.query(ServiceType).all()
        if not service_types:
            print("Creating service types...")
            service_names = ["바이오해킹", "IV테라피", "압력치료", "산소치료", "줄기세포"]
            for name in service_names:
                service_type = ServiceType(
                    service_name=name,
                    description=f"{name} 서비스"
                )
                db.add(service_type)
            db.commit()
            service_types = db.query(ServiceType).all()
        
        # Add payments for the last 12 months
        print("Adding sample payments...")
        staff_names = ["김직원", "이직원", "박직원", "최직원"]
        payment_methods = ["card", "transfer", "cash"]
        
        for month in range(12):
            month_date = date.today() - timedelta(days=30 * month)
            num_payments = random.randint(20, 40)
            
            for _ in range(num_payments):
                payment_date = month_date.replace(day=random.randint(1, 28))
                customer = random.choice(customers)
                
                payment = Payment(
                    customer_id=customer.customer_id,
                    payment_date=payment_date,
                    amount=random.choice([300000, 500000, 800000, 1000000, 1500000, 2000000]),
                    payment_method=random.choice(payment_methods),
                    payment_staff=random.choice(staff_names),
                    purchase_type=random.choice(["new", "renewal"]),
                    purchase_order=random.randint(1, 5)
                )
                db.add(payment)
        
        # Add service usage data
        print("Adding sample service usage...")
        packages = db.query(Package).all()
        
        for month in range(3):  # Last 3 months
            month_date = date.today() - timedelta(days=30 * month)
            
            for _ in range(random.randint(50, 100)):
                service_date = month_date.replace(day=random.randint(1, 28))
                customer = random.choice(customers)
                service_type = random.choice(service_types)
                
                usage = ServiceUsage(
                    customer_id=customer.customer_id,
                    service_date=service_date,
                    service_type_id=service_type.service_type_id,
                    package_id=packages[0].package_id if packages else None,
                    session_number=random.randint(1, 10),
                    created_by=random.choice(staff_names)
                )
                db.add(usage)
        
        db.commit()
        
        # Print summary
        total_payments = db.query(Payment).count()
        total_usage = db.query(ServiceUsage).count()
        
        print(f"\n✅ Sample data added successfully!")
        print(f"   - Total payments: {total_payments}")
        print(f"   - Total service usage: {total_usage}")
        print(f"   - Customers: {len(customers)}")
        print(f"   - Service types: {len(service_types)}")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding sample report data...")
    add_sample_report_data()