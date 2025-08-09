-- AIBIO Center Management System Database Schema
-- Supabase (PostgreSQL) 용 수정된 버전

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ENUM 타입 정의
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'staff');
CREATE TYPE customer_status AS ENUM ('active', 'inactive', 'dormant');
CREATE TYPE membership_level AS ENUM ('basic', 'silver', 'gold', 'platinum', 'vip');
CREATE TYPE payment_method AS ENUM ('cash', 'card', 'transfer', 'other');
CREATE TYPE payment_type AS ENUM ('package', 'single', 'additional', 'refund');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'cancelled', 'refunded');
CREATE TYPE reservation_status AS ENUM ('pending', 'confirmed', 'cancelled', 'completed', 'no_show');
CREATE TYPE campaign_type AS ENUM ('sms', 'email', 'kakao', 'push');
CREATE TYPE campaign_status AS ENUM ('draft', 'scheduled', 'sent', 'cancelled');
CREATE TYPE notification_type AS ENUM ('sms', 'email', 'kakao', 'push', 'system');
CREATE TYPE audit_action AS ENUM ('create', 'update', 'delete', 'view', 'export');

-- 1. company_info 테이블
CREATE TABLE IF NOT EXISTS company_info (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    business_hours JSON,
    holidays JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. users 테이블
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    role user_role NOT NULL DEFAULT 'staff',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. customers 테이블
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    first_visit_date DATE,
    region VARCHAR(100),
    referral_source VARCHAR(50),
    health_concerns TEXT,
    notes TEXT,
    assigned_staff VARCHAR(50),
    birth_year INTEGER,
    gender VARCHAR(10),
    email VARCHAR(100),
    address TEXT,
    emergency_contact VARCHAR(100),
    occupation VARCHAR(50),
    membership_level membership_level DEFAULT 'basic',
    customer_status customer_status DEFAULT 'active',
    preferred_time_slots JSONB,
    health_goals TEXT,
    last_visit_date DATE,
    total_visits INTEGER DEFAULT 0,
    average_visit_interval INTEGER,
    total_revenue DECIMAL(10, 2) DEFAULT 0,
    average_satisfaction DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. service_types 테이블
CREATE TABLE IF NOT EXISTS service_types (
    service_type_id SERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL UNIQUE,
    service_color VARCHAR(7),
    default_duration INTEGER,
    default_price INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. packages 테이블
CREATE TABLE IF NOT EXISTS packages (
    package_id SERIAL PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL,
    total_sessions INTEGER NOT NULL,
    valid_months INTEGER NOT NULL,
    base_price INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. service_usages 테이블
CREATE TABLE IF NOT EXISTS service_usages (
    usage_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    service_type_id INTEGER NOT NULL REFERENCES service_types(service_type_id),
    usage_date DATE NOT NULL,
    duration INTEGER,
    staff_id INTEGER REFERENCES users(user_id),
    notes TEXT,
    package_purchase_id INTEGER,
    session_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. payments 테이블
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    payment_date DATE NOT NULL,
    amount INTEGER NOT NULL,
    payment_method payment_method NOT NULL,
    payment_type payment_type NOT NULL,
    payment_status payment_status DEFAULT 'completed',
    transaction_id VARCHAR(100),
    reference_id INTEGER,
    reference_type VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. package_purchases 테이블
CREATE TABLE IF NOT EXISTS package_purchases (
    purchase_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    package_id INTEGER NOT NULL REFERENCES packages(package_id),
    purchase_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    total_sessions INTEGER NOT NULL,
    used_sessions INTEGER DEFAULT 0,
    remaining_sessions INTEGER NOT NULL,
    price_paid INTEGER NOT NULL,
    payment_id INTEGER REFERENCES payments(payment_id),
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. reservations 테이블
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    service_type_id INTEGER NOT NULL REFERENCES service_types(service_type_id),
    staff_id INTEGER REFERENCES users(user_id),
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    duration_minutes INTEGER NOT NULL,
    status reservation_status DEFAULT 'pending',
    customer_request TEXT,
    internal_memo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. notifications 테이블
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    type notification_type NOT NULL,
    title VARCHAR(200),
    message TEXT NOT NULL,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    template_id INTEGER,
    created_by INTEGER REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. audit_logs 테이블
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action audit_action NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_service_usages_customer ON service_usages(customer_id);
CREATE INDEX idx_service_usages_date ON service_usages(usage_date);
CREATE INDEX idx_payments_customer ON payments(customer_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_reservations_date ON reservations(reservation_date);
CREATE INDEX idx_reservations_customer ON reservations(customer_id);

-- 초기 데이터: 관리자 계정 (비밀번호: admin123)
INSERT INTO users (email, password_hash, name, role, is_active) 
VALUES (
    'admin@aibio.kr',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQeUjrktJrIa',
    '관리자',
    'admin',
    true
) ON CONFLICT (email) DO NOTHING;

-- 초기 데이터: 기본 서비스 타입
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

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 각 테이블에 업데이트 트리거 적용
CREATE TRIGGER update_company_info_updated_at BEFORE UPDATE ON company_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_service_types_updated_at BEFORE UPDATE ON service_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_packages_updated_at BEFORE UPDATE ON packages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_service_usages_updated_at BEFORE UPDATE ON service_usages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_package_purchases_updated_at BEFORE UPDATE ON package_purchases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reservations_updated_at BEFORE UPDATE ON reservations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();