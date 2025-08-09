-- AIBIO 센터 관리 시스템 데이터베이스 스키마
-- PostgreSQL 17

-- 1. 고객 마스터 테이블
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    first_visit_date DATE,
    region VARCHAR(100),
    referral_source VARCHAR(50),
    health_concerns TEXT,
    notes TEXT,
    assigned_staff VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 서비스 타입 테이블
CREATE TABLE IF NOT EXISTS service_types (
    service_type_id SERIAL PRIMARY KEY,
    service_name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT
);

-- 초기 서비스 타입 데이터
INSERT INTO service_types (service_name, description) VALUES
    ('brain', '브레인 서비스'),
    ('pulse', '펄스 서비스'),
    ('lymph', '림프 서비스'),
    ('red', '레드 서비스')
ON CONFLICT (service_name) DO NOTHING;

-- 3. 패키지 정보 테이블
CREATE TABLE IF NOT EXISTS packages (
    package_id SERIAL PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL,
    total_sessions INT,
    price DECIMAL(10,2),
    valid_days INT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 서비스 이용 내역 테이블
CREATE TABLE IF NOT EXISTS service_usage (
    usage_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    service_date DATE NOT NULL,
    service_type_id INT REFERENCES service_types(service_type_id),
    package_id INT REFERENCES packages(package_id),
    session_details TEXT,
    session_number INT,
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 패키지 구매 내역 테이블
CREATE TABLE IF NOT EXISTS package_purchases (
    purchase_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    package_id INT REFERENCES packages(package_id),
    purchase_date DATE NOT NULL,
    expiry_date DATE,
    total_sessions INT,
    used_sessions INT DEFAULT 0,
    remaining_sessions INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 결제 내역 테이블
CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) CHECK (payment_method IN ('card', 'transfer', 'cash')),
    card_holder_name VARCHAR(50),
    approval_number VARCHAR(50),
    payment_staff VARCHAR(50),
    purchase_type VARCHAR(20) CHECK (purchase_type IN ('new', 'renewal')),
    purchase_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 마케팅 리드 테이블
CREATE TABLE IF NOT EXISTS marketing_leads (
    lead_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    lead_date DATE NOT NULL,
    channel VARCHAR(50),
    db_entry_date DATE,
    phone_consult_date DATE,
    visit_consult_date DATE,
    registration_date DATE,
    status VARCHAR(20) CHECK (status IN ('new', 'phone_consult', 'visit_consult', 'registered', 'dropped')),
    converted_customer_id INT REFERENCES customers(customer_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 키트 관리 테이블
CREATE TABLE IF NOT EXISTS kit_management (
    kit_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    kit_type VARCHAR(50) NOT NULL,
    serial_number VARCHAR(50) UNIQUE,
    received_date DATE,
    result_received_date DATE,
    result_delivered_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. 사용자 (직원) 테이블
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) CHECK (role IN ('admin', 'manager', 'staff')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 감사 로그 테이블
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_service_usage_customer ON service_usage(customer_id);
CREATE INDEX idx_service_usage_date ON service_usage(service_date);
CREATE INDEX idx_payments_customer ON payments(customer_id);
CREATE INDEX idx_payments_date ON payments(payment_date);
CREATE INDEX idx_package_purchases_customer ON package_purchases(customer_id);
CREATE INDEX idx_marketing_leads_status ON marketing_leads(status);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

-- 트리거 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- customers 테이블에 트리거 적용
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE
    ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- users 테이블에 트리거 적용
CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 뷰: 고객별 서비스 이용 현황
CREATE OR REPLACE VIEW customer_service_summary AS
SELECT 
    c.customer_id,
    c.name,
    c.phone,
    COUNT(DISTINCT su.usage_id) as total_visits,
    MAX(su.service_date) as last_visit_date,
    COUNT(DISTINCT pp.purchase_id) as total_packages,
    SUM(pp.remaining_sessions) as total_remaining_sessions
FROM customers c
LEFT JOIN service_usage su ON c.customer_id = su.customer_id
LEFT JOIN package_purchases pp ON c.customer_id = pp.customer_id
GROUP BY c.customer_id, c.name, c.phone;

-- 뷰: 일별 매출 현황
CREATE OR REPLACE VIEW daily_revenue AS
SELECT 
    payment_date,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue,
    SUM(CASE WHEN payment_method = 'card' THEN amount ELSE 0 END) as card_revenue,
    SUM(CASE WHEN payment_method = 'transfer' THEN amount ELSE 0 END) as transfer_revenue,
    SUM(CASE WHEN payment_method = 'cash' THEN amount ELSE 0 END) as cash_revenue
FROM payments
GROUP BY payment_date
ORDER BY payment_date DESC;