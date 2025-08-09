#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import engine
from models.user import User

def check_user_role(email: str):
    with Session(engine) as db:
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User: {user.email}")
            print(f"Name: {user.name}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
        else:
            print(f"User not found: {email}")

if __name__ == "__main__":
    check_user_role("taejun@biocom.kr")
    print("\n--- All users with their roles ---")
    with Session(engine) as db:
        users = db.query(User).all()
        for user in users:
            print(f"{user.email}: role={user.role}, active={user.is_active}")