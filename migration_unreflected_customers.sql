
-- 미반영 고객 테이블 생성
CREATE TABLE IF NOT EXISTS unreflected_customers (
    id SERIAL PRIMARY KEY,
    original_customer_id INTEGER,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    first_visit_date DATE,
    region VARCHAR(100),
    referral_source VARCHAR(100),
    health_concerns TEXT,
    notes TEXT,
    assigned_staff VARCHAR(50),
    birth_year INTEGER,
    gender VARCHAR(10),
    address TEXT,
    emergency_contact VARCHAR(20),
    occupation VARCHAR(100),
    data_source VARCHAR(200),
    import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    import_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_unreflected_name ON unreflected_customers(name);
CREATE INDEX IF NOT EXISTS idx_unreflected_phone ON unreflected_customers(phone);
CREATE INDEX IF NOT EXISTS idx_unreflected_status ON unreflected_customers(status);


-- 미반영 고객 데이터 INSERT

INSERT INTO unreflected_customers (
    original_customer_id, name, phone, email, first_visit_date,
    region, referral_source, health_concerns, notes, assigned_staff,
    birth_year, gender, address, emergency_contact, occupation,
    data_source, import_date
) VALUES (
    1140, '김형기', NULL, NULL, NULL, NULL, '엑셀업로드', NULL, '엑셀 업로드 (2025-06-25)', NULL, NULL, NULL, NULL, NULL, NULL, '월별 이용현황 import (6/25)', '2025-06-25T05:08:47.486999'
);
INSERT INTO unreflected_customers (
    original_customer_id, name, phone, email, first_visit_date,
    region, referral_source, health_concerns, notes, assigned_staff,
    birth_year, gender, address, emergency_contact, occupation,
    data_source, import_date
) VALUES (
    1137, '유정희', NULL, NULL, NULL, NULL, '엑셀업로드', NULL, '엑셀 업로드 (2025-06-25)', NULL, NULL, NULL, NULL, NULL, NULL, '월별 이용현황 import (6/25)', '2025-06-25T05:08:47.486999'
);
INSERT INTO unreflected_customers (
    original_customer_id, name, phone, email, first_visit_date,
    region, referral_source, health_concerns, notes, assigned_staff,
    birth_year, gender, address, emergency_contact, occupation,
    data_source, import_date
) VALUES (
    1130, '허아인', NULL, NULL, NULL, NULL, 'NaN', NULL, '엑셀 업로드 (2025-06-25)', NULL, NULL, NULL, NULL, NULL, NULL, '월별 이용현황 import (6/25)', '2025-06-25T05:08:47.486999'
);
INSERT INTO unreflected_customers (
    original_customer_id, name, phone, email, first_visit_date,
    region, referral_source, health_concerns, notes, assigned_staff,
    birth_year, gender, address, emergency_contact, occupation,
    data_source, import_date
) VALUES (
    1125, '김라현', NULL, NULL, NULL, NULL, '엑셀업로드', NULL, '엑셀 업로드 (2025-06-25)', NULL, NULL, NULL, NULL, NULL, NULL, '월별 이용현황 import (6/25)', '2025-06-25T05:08:47.486999'
);
INSERT INTO unreflected_customers (
    original_customer_id, name, phone, email, first_visit_date,
    region, referral_source, health_concerns, notes, assigned_staff,
    birth_year, gender, address, emergency_contact, occupation,
    data_source, import_date
) VALUES (
    1129, '엄미나', NULL, NULL, NULL, NULL, '유튜브', NULL, '엑셀 업로드 (2025-06-25)', NULL, NULL, NULL, NULL, NULL, NULL, '월별 이용현황 import (6/25)', '2025-06-25T05:08:47.486999'
);
INSERT INTO unreflected_customers (
    original_customer_id, name, phone, email, first_visit_date,
    region, referral_source, health_concerns, notes, assigned_staff,
    birth_year, gender, address, emergency_contact, occupation,
    data_source, import_date
) VALUES (
    1092, '이은정', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Unknown', '2025-06-21T13:08:21.007682'
);

-- 총 6명의 미반영 고객 데이터
