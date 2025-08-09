-- AIBIO Center Management System Database Schema - Part 1
-- Supabase 대시보드의 SQL Editor에서 실행하세요

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. company_info 테이블
CREATE TABLE company_info (
    company_id SERIAL NOT NULL, 
    company_name VARCHAR(100) NOT NULL, 
    address TEXT, 
    phone VARCHAR(20), 
    email VARCHAR(100), 
    business_hours JSON, 
    holidays JSON, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (company_id)
);

-- 2. users 테이블 (중요!)
CREATE TABLE users (
    user_id SERIAL NOT NULL, 
    email VARCHAR(100) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    role VARCHAR(20) NOT NULL, 
    is_active BOOLEAN NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (user_id), 
    UNIQUE (email)
);

-- 3. customers 테이블
CREATE TABLE customers (
    customer_id SERIAL NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    phone VARCHAR(20), 
    first_visit_date DATE, 
    region VARCHAR(100), 
    referral_source VARCHAR(50), 
    health_concerns TEXT, 
    notes TEXT, 
    assigned_staff VARCHAR(50), 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    birth_year INTEGER, 
    gender VARCHAR(10), 
    email VARCHAR(100), 
    address TEXT, 
    emergency_contact VARCHAR(100), 
    occupation VARCHAR(50), 
    membership_level VARCHAR(20), 
    customer_status VARCHAR(20), 
    preferred_time_slots JSONB, 
    health_goals TEXT, 
    last_visit_date DATE, 
    total_visits INTEGER, 
    average_visit_interval INTEGER, 
    total_revenue DECIMAL(10, 2), 
    average_satisfaction DECIMAL(3, 2), 
    PRIMARY KEY (customer_id)
);

-- 4. service_types 테이블
CREATE TABLE service_types (
    service_type_id SERIAL NOT NULL, 
    service_name VARCHAR(100) NOT NULL, 
    service_color VARCHAR(7), 
    default_duration INTEGER, 
    default_price INTEGER, 
    is_active BOOLEAN, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (service_type_id), 
    UNIQUE (service_name)
);

-- 5. packages 테이블
CREATE TABLE packages (
    package_id SERIAL NOT NULL, 
    package_name VARCHAR(100) NOT NULL, 
    total_sessions INTEGER NOT NULL, 
    valid_months INTEGER NOT NULL, 
    base_price INTEGER NOT NULL, 
    is_active BOOLEAN, 
    description TEXT, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (package_id)
);

-- 6. payments 테이블
CREATE TABLE payments (
    payment_id SERIAL NOT NULL, 
    customer_id INTEGER NOT NULL, 
    payment_date DATE NOT NULL, 
    amount INTEGER NOT NULL, 
    payment_method VARCHAR(50) NOT NULL, 
    payment_type VARCHAR(50) NOT NULL, 
    payment_status VARCHAR(20), 
    transaction_id VARCHAR(100), 
    reference_id INTEGER, 
    reference_type VARCHAR(50), 
    notes TEXT, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
    PRIMARY KEY (payment_id), 
    CONSTRAINT fk_payments_customers FOREIGN KEY(customer_id) REFERENCES customers (customer_id)
);

-- 관리자 계정 생성 (비밀번호: admin123)
INSERT INTO users (email, password_hash, name, role, is_active) 
VALUES (
    'admin@aibio.kr',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQeUjrktJrIa',
    '관리자',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- 기본 서비스 타입 생성
INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active)
VALUES 
    ('상담', '#FF6B6B', 30, 50000, true),
    ('발가락케어', '#4ECDC4', 60, 80000, true),
    ('종아리케어', '#45B7D1', 60, 70000, true),
    ('뱃살케어', '#F8961E', 90, 120000, true),
    ('등케어', '#90BE6D', 60, 90000, true),
    ('DNA검사', '#C77DFF', 30, 150000, true),
    ('인바디측정', '#7209B7', 15, 20000, true)
ON CONFLICT (service_name) DO NOTHING;