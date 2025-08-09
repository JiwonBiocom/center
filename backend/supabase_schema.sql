-- AIBIO Center Management System Database Schema
-- Generated for Supabase (PostgreSQL)
-- Note: Supabase 대시보드의 SQL Editor에서 실행하세요

-- Enable UUID extension (Supabase에서 기본 제공)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- company_info 테이블

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
)

;

-- customers 테이블

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
)

;

-- kakao_templates 테이블

CREATE TABLE kakao_templates (
	template_id SERIAL NOT NULL, 
	template_code VARCHAR(50) NOT NULL, 
	template_name VARCHAR(100) NOT NULL, 
	template_type VARCHAR(50), 
	content TEXT NOT NULL, 
	variables JSON, 
	is_active BOOLEAN, 
	approved_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (template_id), 
	UNIQUE (template_code)
)

;

-- kit_types 테이블

CREATE TABLE kit_types (
	kit_type_id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	code VARCHAR(50) NOT NULL, 
	description TEXT, 
	price INTEGER NOT NULL, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (kit_type_id), 
	UNIQUE (code)
)

;

-- notification_preferences 테이블

CREATE TABLE notification_preferences (
	preference_id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	notification_type VARCHAR(50), 
	in_app BOOLEAN, 
	email BOOLEAN, 
	sms BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (preference_id)
)

;

-- packages 테이블

CREATE TABLE packages (
	package_id SERIAL NOT NULL, 
	package_name VARCHAR(100) NOT NULL, 
	total_sessions INTEGER, 
	base_price INTEGER, 
	valid_months INTEGER, 
	description VARCHAR(500), 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (package_id)
)

;

-- questionnaire_templates 테이블

CREATE TABLE questionnaire_templates (
	template_id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	version VARCHAR(20) NOT NULL, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (template_id)
)

;

-- service_types 테이블

CREATE TABLE service_types (
	service_type_id SERIAL NOT NULL, 
	service_name VARCHAR(20) NOT NULL, 
	description TEXT, 
	default_duration INTEGER, 
	default_price INTEGER, 
	service_color VARCHAR(10), 
	PRIMARY KEY (service_type_id), 
	UNIQUE (service_name)
)

;

-- staff_schedules 테이블

CREATE TABLE staff_schedules (
	schedule_id SERIAL NOT NULL, 
	week_start_date DATE NOT NULL, 
	schedule_data TEXT NOT NULL, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	created_by VARCHAR(100), 
	updated_by VARCHAR(100), 
	PRIMARY KEY (schedule_id)
)

;

-- system_settings 테이블

CREATE TABLE system_settings (
	setting_id SERIAL NOT NULL, 
	setting_key VARCHAR(50) NOT NULL, 
	setting_value TEXT, 
	setting_type VARCHAR(20), 
	description TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (setting_id), 
	UNIQUE (setting_key)
)

;

-- users 테이블

CREATE TABLE users (
	user_id SERIAL NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	role VARCHAR(20), 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (user_id)
)

;

-- audit_logs 테이블

CREATE TABLE audit_logs (
	log_id SERIAL NOT NULL, 
	user_id INTEGER, 
	action VARCHAR(50) NOT NULL, 
	entity_type VARCHAR(50), 
	entity_id INTEGER, 
	details JSON, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (log_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
)

;

-- customer_analytics 테이블

CREATE TABLE customer_analytics (
	analytics_id SERIAL NOT NULL, 
	customer_id INTEGER, 
	analysis_date DATE NOT NULL, 
	visit_frequency VARCHAR(20), 
	consistency_score INTEGER, 
	most_used_service VARCHAR(20), 
	ltv_estimate DECIMAL(10, 2), 
	churn_risk VARCHAR(20), 
	churn_probability INTEGER, 
	retention_score INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (analytics_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
)

;

-- customer_preferences 테이블

CREATE TABLE customer_preferences (
	preference_id SERIAL NOT NULL, 
	customer_id INTEGER, 
	preferred_services TEXT[], 
	preferred_time VARCHAR(20), 
	preferred_intensity VARCHAR(20), 
	health_interests TEXT[], 
	communication_preference VARCHAR(20), 
	marketing_consent BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (preference_id), 
	UNIQUE (customer_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
)

;

-- inbody_records 테이블

CREATE TABLE inbody_records (
	record_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	measurement_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	weight FLOAT, 
	body_fat_percentage FLOAT, 
	skeletal_muscle_mass FLOAT, 
	extracellular_water_ratio FLOAT, 
	phase_angle FLOAT, 
	visceral_fat_level INTEGER, 
	notes TEXT, 
	measured_by VARCHAR(100), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (record_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
)

;

-- kit_management 테이블

CREATE TABLE kit_management (
	kit_id SERIAL NOT NULL, 
	customer_id INTEGER, 
	kit_type VARCHAR(50) NOT NULL, 
	kit_type_id INTEGER, 
	serial_number VARCHAR(50), 
	received_date DATE, 
	result_received_date DATE, 
	result_delivered_date DATE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (kit_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(kit_type_id) REFERENCES kit_types (kit_type_id), 
	UNIQUE (serial_number)
)

;

-- kit_receipts 테이블

CREATE TABLE kit_receipts (
	kit_id SERIAL NOT NULL, 
	customer_id INTEGER, 
	kit_type VARCHAR(100), 
	serial_number VARCHAR(100), 
	receipt_date DATE, 
	result_received_date DATE, 
	result_delivered_date DATE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (kit_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
)

;

-- marketing_leads 테이블

CREATE TABLE marketing_leads (
	lead_id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	phone VARCHAR(20), 
	lead_date DATE NOT NULL, 
	age INTEGER, 
	region VARCHAR(50), 
	lead_channel VARCHAR(50), 
	carrot_id VARCHAR(100), 
	ad_watched VARCHAR(100), 
	price_informed BOOLEAN, 
	ab_test_group VARCHAR(20), 
	db_entry_date DATE, 
	phone_consult_date DATE, 
	visit_consult_date DATE, 
	registration_date DATE, 
	db_channel VARCHAR(50), 
	phone_consult_result VARCHAR(100), 
	remind_date DATE, 
	visit_cancelled BOOLEAN, 
	visit_cancel_reason TEXT, 
	is_reregistration_target BOOLEAN, 
	last_service_date DATE, 
	reregistration_proposal_date DATE, 
	purchased_product VARCHAR(200), 
	no_registration_reason TEXT, 
	notes TEXT, 
	revenue DECIMAL(10, 2), 
	status VARCHAR(20), 
	assigned_staff_id INTEGER, 
	converted_customer_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (lead_id), 
	FOREIGN KEY(assigned_staff_id) REFERENCES users (user_id), 
	FOREIGN KEY(converted_customer_id) REFERENCES customers (customer_id)
)

;

-- notification_settings 테이블

CREATE TABLE notification_settings (
	user_id INTEGER NOT NULL, 
	email_enabled BOOLEAN, 
	sms_enabled BOOLEAN, 
	push_enabled BOOLEAN, 
	package_alerts BOOLEAN, 
	appointment_reminders BOOLEAN, 
	payment_notifications BOOLEAN, 
	system_notifications BOOLEAN, 
	marketing_notifications BOOLEAN, 
	quiet_hours_enabled BOOLEAN, 
	quiet_hours_start VARCHAR(5), 
	quiet_hours_end VARCHAR(5), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
)

;

-- notifications 테이블

CREATE TABLE notifications (
	notification_id SERIAL NOT NULL, 
	user_id INTEGER, 
	type notificationtype NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	message TEXT NOT NULL, 
	is_read BOOLEAN, 
	is_sent BOOLEAN, 
	priority notificationpriority, 
	action_url VARCHAR(500), 
	related_id INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	read_at TIMESTAMP WITHOUT TIME ZONE, 
	scheduled_for TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (notification_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
)

;

-- package_purchases 테이블

CREATE TABLE package_purchases (
	purchase_id SERIAL NOT NULL, 
	customer_id INTEGER, 
	package_id INTEGER, 
	purchase_date DATE NOT NULL, 
	expiry_date DATE, 
	total_sessions INTEGER, 
	used_sessions INTEGER, 
	remaining_sessions INTEGER, 
	notes VARCHAR, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (purchase_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(package_id) REFERENCES packages (package_id)
)

;

-- payments 테이블

CREATE TABLE payments (
	payment_id SERIAL NOT NULL, 
	payment_number VARCHAR(20), 
	customer_id INTEGER, 
	payment_date DATE NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	payment_method VARCHAR(20), 
	payment_type VARCHAR(20), 
	payment_status VARCHAR(20), 
	payment_staff VARCHAR(50), 
	transaction_id VARCHAR(100), 
	card_holder_name VARCHAR(100), 
	reference_id INTEGER, 
	reference_type VARCHAR(50), 
	notes VARCHAR(500), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (payment_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id)
)

;

-- questions 테이블

CREATE TABLE questions (
	question_id SERIAL NOT NULL, 
	template_id INTEGER, 
	section questionnairesection NOT NULL, 
	question_type questiontype NOT NULL, 
	question_code VARCHAR(50) NOT NULL, 
	question_text TEXT NOT NULL, 
	question_subtext TEXT, 
	order_index INTEGER NOT NULL, 
	is_required BOOLEAN, 
	condition_logic JSON, 
	options JSON, 
	validation_rules JSON, 
	ui_config JSON, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (question_id), 
	FOREIGN KEY(template_id) REFERENCES questionnaire_templates (template_id), 
	UNIQUE (question_code)
)

;

-- reregistration_campaigns 테이블

CREATE TABLE reregistration_campaigns (
	campaign_id SERIAL NOT NULL, 
	campaign_name VARCHAR(100) NOT NULL, 
	campaign_type VARCHAR(50), 
	start_date DATE NOT NULL, 
	end_date DATE, 
	target_criteria TEXT, 
	message_template TEXT, 
	target_count INTEGER, 
	success_count INTEGER, 
	notes TEXT, 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE, 
	created_by INTEGER, 
	PRIMARY KEY (campaign_id), 
	FOREIGN KEY(created_by) REFERENCES users (user_id)
)

;

-- reservation_slots 테이블

CREATE TABLE reservation_slots (
	slot_id SERIAL NOT NULL, 
	staff_id INTEGER, 
	day_of_week INTEGER, 
	start_time TIME WITHOUT TIME ZONE NOT NULL, 
	end_time TIME WITHOUT TIME ZONE NOT NULL, 
	is_available BOOLEAN, 
	specific_date DATE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (slot_id), 
	FOREIGN KEY(staff_id) REFERENCES users (user_id)
)

;

-- reservations 테이블

CREATE TABLE reservations (
	reservation_id SERIAL NOT NULL, 
	customer_id INTEGER NOT NULL, 
	service_type_id INTEGER NOT NULL, 
	staff_id INTEGER, 
	reservation_date DATE NOT NULL, 
	reservation_time TIME WITHOUT TIME ZONE NOT NULL, 
	duration_minutes INTEGER, 
	status reservationstatus NOT NULL, 
	customer_request TEXT, 
	internal_memo TEXT, 
	reminder_sent BOOLEAN, 
	confirmation_sent BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	created_by VARCHAR(50), 
	cancelled_at TIMESTAMP WITHOUT TIME ZONE, 
	cancelled_by VARCHAR(50), 
	cancel_reason TEXT, 
	PRIMARY KEY (reservation_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(service_type_id) REFERENCES service_types (service_type_id), 
	FOREIGN KEY(staff_id) REFERENCES users (user_id)
)

;

-- service_usage 테이블

CREATE TABLE service_usage (
	usage_id SERIAL NOT NULL, 
	customer_id INTEGER, 
	service_date DATE NOT NULL, 
	service_type_id INTEGER, 
	package_id INTEGER, 
	session_details TEXT, 
	session_number INTEGER, 
	created_by VARCHAR(50), 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (usage_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(service_type_id) REFERENCES service_types (service_type_id), 
	FOREIGN KEY(package_id) REFERENCES packages (package_id)
)

;

-- campaign_targets 테이블

CREATE TABLE campaign_targets (
	target_id SERIAL NOT NULL, 
	campaign_id INTEGER, 
	lead_id INTEGER, 
	contact_date DATE, 
	contact_result VARCHAR(200), 
	converted BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (target_id), 
	FOREIGN KEY(campaign_id) REFERENCES reregistration_campaigns (campaign_id), 
	FOREIGN KEY(lead_id) REFERENCES marketing_leads (lead_id)
)

;

-- kakao_message_logs 테이블

CREATE TABLE kakao_message_logs (
	log_id SERIAL NOT NULL, 
	reservation_id INTEGER, 
	customer_id INTEGER, 
	template_code VARCHAR(50), 
	phone_number VARCHAR(20), 
	message_type VARCHAR(20), 
	status VARCHAR(20), 
	message_id VARCHAR(100), 
	content TEXT, 
	variables_used JSON, 
	sent_at TIMESTAMP WITHOUT TIME ZONE, 
	delivered_at TIMESTAMP WITHOUT TIME ZONE, 
	read_at TIMESTAMP WITHOUT TIME ZONE, 
	error_code VARCHAR(50), 
	error_message TEXT, 
	fallback_status VARCHAR(20), 
	fallback_sent_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (log_id), 
	FOREIGN KEY(reservation_id) REFERENCES reservations (reservation_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id)
)

;

-- lead_consultation_history 테이블

CREATE TABLE lead_consultation_history (
	history_id SERIAL NOT NULL, 
	lead_id INTEGER, 
	consultation_date TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	consultation_type VARCHAR(50) NOT NULL, 
	result VARCHAR(255), 
	notes TEXT, 
	next_action VARCHAR(100), 
	created_by INTEGER, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (history_id), 
	FOREIGN KEY(lead_id) REFERENCES marketing_leads (lead_id), 
	FOREIGN KEY(created_by) REFERENCES users (user_id)
)

;

-- questionnaire_responses 테이블

CREATE TABLE questionnaire_responses (
	response_id SERIAL NOT NULL, 
	customer_id INTEGER, 
	template_id INTEGER, 
	inbody_record_id INTEGER, 
	started_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	completed_at TIMESTAMP WITH TIME ZONE, 
	is_completed BOOLEAN, 
	completion_rate FLOAT, 
	device_id VARCHAR(100), 
	app_version VARCHAR(20), 
	ai_analysis JSON, 
	health_scores JSON, 
	recommendations JSON, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (response_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(template_id) REFERENCES questionnaire_templates (template_id), 
	FOREIGN KEY(inbody_record_id) REFERENCES inbody_records (record_id)
)

;

-- answers 테이블

CREATE TABLE answers (
	answer_id SERIAL NOT NULL, 
	response_id INTEGER, 
	question_id INTEGER, 
	answer_value TEXT, 
	answer_number FLOAT, 
	answer_json JSON, 
	answer_date TIMESTAMP WITHOUT TIME ZONE, 
	answered_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	time_spent_seconds INTEGER, 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (answer_id), 
	FOREIGN KEY(response_id) REFERENCES questionnaire_responses (response_id), 
	FOREIGN KEY(question_id) REFERENCES questions (question_id)
)

;

-- questionnaire_analyses 테이블

CREATE TABLE questionnaire_analyses (
	analysis_id SERIAL NOT NULL, 
	response_id INTEGER, 
	overall_health_score FLOAT, 
	body_composition_score FLOAT, 
	metabolic_health_score FLOAT, 
	stress_score FLOAT, 
	sleep_score FLOAT, 
	nutrition_score FLOAT, 
	recommended_services JSON, 
	recommended_supplements JSON, 
	recommended_diet JSON, 
	detailed_analysis JSON, 
	risk_factors JSON, 
	improvement_areas JSON, 
	analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT now(), 
	PRIMARY KEY (analysis_id), 
	FOREIGN KEY(response_id) REFERENCES questionnaire_responses (response_id)
)

;

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_company_info_ix_company_info_company_id ON company_info (company_id);
CREATE INDEX IF NOT EXISTS idx_customers_ix_customers_customer_id ON customers (customer_id);
CREATE INDEX IF NOT EXISTS idx_customers_ix_customers_phone ON customers (phone);
CREATE INDEX IF NOT EXISTS idx_kakao_templates_ix_kakao_templates_template_id ON kakao_templates (template_id);
CREATE INDEX IF NOT EXISTS idx_kit_types_ix_kit_types_kit_type_id ON kit_types (kit_type_id);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_ix_notification_preferences_preference_id ON notification_preferences (preference_id);
CREATE INDEX IF NOT EXISTS idx_packages_ix_packages_package_id ON packages (package_id);
CREATE INDEX IF NOT EXISTS idx_questionnaire_templates_ix_questionnaire_templates_template_id ON questionnaire_templates (template_id);
CREATE INDEX IF NOT EXISTS idx_service_types_ix_service_types_service_type_id ON service_types (service_type_id);
CREATE INDEX IF NOT EXISTS idx_staff_schedules_ix_staff_schedules_week_start_date ON staff_schedules (week_start_date);
CREATE INDEX IF NOT EXISTS idx_staff_schedules_ix_staff_schedules_schedule_id ON staff_schedules (schedule_id);
CREATE INDEX IF NOT EXISTS idx_system_settings_ix_system_settings_setting_id ON system_settings (setting_id);
CREATE INDEX IF NOT EXISTS idx_users_ix_users_user_id ON users (user_id);
CREATE INDEX IF NOT EXISTS idx_users_ix_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ix_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ix_audit_logs_created_at ON audit_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ix_audit_logs_log_id ON audit_logs (log_id);
CREATE INDEX IF NOT EXISTS idx_customer_analytics_ix_customer_analytics_analytics_id ON customer_analytics (analytics_id);
CREATE INDEX IF NOT EXISTS idx_customer_preferences_ix_customer_preferences_preference_id ON customer_preferences (preference_id);
CREATE INDEX IF NOT EXISTS idx_inbody_records_ix_inbody_records_record_id ON inbody_records (record_id);
CREATE INDEX IF NOT EXISTS idx_kit_management_ix_kit_management_kit_id ON kit_management (kit_id);
CREATE INDEX IF NOT EXISTS idx_kit_receipts_ix_kit_receipts_kit_id ON kit_receipts (kit_id);
CREATE INDEX IF NOT EXISTS idx_kit_receipts_ix_kit_receipts_serial_number ON kit_receipts (serial_number);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_ix_marketing_leads_lead_channel ON marketing_leads (lead_channel);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_ix_marketing_leads_db_channel ON marketing_leads (db_channel);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_ix_marketing_leads_lead_id ON marketing_leads (lead_id);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_ix_marketing_leads_phone ON marketing_leads (phone);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_ix_marketing_leads_status ON marketing_leads (status);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_ix_marketing_leads_is_reregistration_target ON marketing_leads (is_reregistration_target);
CREATE INDEX IF NOT EXISTS idx_marketing_leads_ix_marketing_leads_assigned_staff_id ON marketing_leads (assigned_staff_id);
CREATE INDEX IF NOT EXISTS idx_notifications_ix_notifications_is_read ON notifications (is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_ix_notifications_scheduled_for ON notifications (scheduled_for);
CREATE INDEX IF NOT EXISTS idx_notifications_ix_notifications_notification_id ON notifications (notification_id);
CREATE INDEX IF NOT EXISTS idx_notifications_ix_notifications_type ON notifications (type);
CREATE INDEX IF NOT EXISTS idx_notifications_ix_notifications_created_at ON notifications (created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_ix_notifications_user_id ON notifications (user_id);
CREATE INDEX IF NOT EXISTS idx_package_purchases_ix_package_purchases_purchase_id ON package_purchases (purchase_id);
CREATE INDEX IF NOT EXISTS idx_package_purchases_ix_package_purchases_customer_id ON package_purchases (customer_id);
CREATE INDEX IF NOT EXISTS idx_payments_ix_payments_payment_date ON payments (payment_date);
CREATE INDEX IF NOT EXISTS idx_payments_ix_payments_payment_id ON payments (payment_id);
CREATE INDEX IF NOT EXISTS idx_payments_ix_payments_payment_number ON payments (payment_number);
CREATE INDEX IF NOT EXISTS idx_payments_ix_payments_customer_id ON payments (customer_id);
CREATE INDEX IF NOT EXISTS idx_questions_ix_questions_question_id ON questions (question_id);
CREATE INDEX IF NOT EXISTS idx_reregistration_campaigns_ix_reregistration_campaigns_campaign_id ON reregistration_campaigns (campaign_id);
CREATE INDEX IF NOT EXISTS idx_reservation_slots_ix_reservation_slots_slot_id ON reservation_slots (slot_id);
CREATE INDEX IF NOT EXISTS idx_reservations_ix_reservations_reservation_date ON reservations (reservation_date);
CREATE INDEX IF NOT EXISTS idx_reservations_ix_reservations_status ON reservations (status);
CREATE INDEX IF NOT EXISTS idx_reservations_ix_reservations_reservation_id ON reservations (reservation_id);
CREATE INDEX IF NOT EXISTS idx_service_usage_ix_service_usage_service_date ON service_usage (service_date);
CREATE INDEX IF NOT EXISTS idx_service_usage_ix_service_usage_usage_id ON service_usage (usage_id);
CREATE INDEX IF NOT EXISTS idx_campaign_targets_ix_campaign_targets_target_id ON campaign_targets (target_id);
CREATE INDEX IF NOT EXISTS idx_kakao_message_logs_ix_kakao_message_logs_log_id ON kakao_message_logs (log_id);
CREATE INDEX IF NOT EXISTS idx_lead_consultation_history_ix_lead_consultation_history_history_id ON lead_consultation_history (history_id);
CREATE INDEX IF NOT EXISTS idx_questionnaire_responses_ix_questionnaire_responses_response_id ON questionnaire_responses (response_id);
CREATE INDEX IF NOT EXISTS idx_answers_ix_answers_answer_id ON answers (answer_id);
CREATE INDEX IF NOT EXISTS idx_questionnaire_analyses_ix_questionnaire_analyses_analysis_id ON questionnaire_analyses (analysis_id);

-- 초기 데이터 삽입
-- 관리자 계정 (비밀번호: admin123)

INSERT INTO users (email, password_hash, name, role, is_active, created_at) 
VALUES (
    'admin@aibio.kr',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpfQeUjrktJrIa',
    '관리자',
    'admin',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- 기본 서비스 타입

INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('상담', '#FF6B6B', 30, 50000, true, NOW())
ON CONFLICT (service_name) DO NOTHING;

INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('발가락케어', '#4ECDC4', 60, 80000, true, NOW())
ON CONFLICT (service_name) DO NOTHING;

INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('종아리케어', '#45B7D1', 60, 70000, true, NOW())
ON CONFLICT (service_name) DO NOTHING;

INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('뱃살케어', '#F8961E', 90, 120000, true, NOW())
ON CONFLICT (service_name) DO NOTHING;

INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('등케어', '#90BE6D', 60, 90000, true, NOW())
ON CONFLICT (service_name) DO NOTHING;

INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('DNA검사', '#C77DFF', 30, 150000, true, NOW())
ON CONFLICT (service_name) DO NOTHING;

INSERT INTO service_types (service_name, service_color, default_duration, default_price, is_active, created_at)
VALUES ('인바디측정', '#7209B7', 15, 20000, true, NOW())
ON CONFLICT (service_name) DO NOTHING;


-- Row Level Security 정책 (선택사항)
-- Supabase 대시보드에서 RLS를 활성화하고 정책을 설정할 수 있습니다.
-- 예시:
-- ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Users can view all customers" ON customers FOR SELECT USING (true);
