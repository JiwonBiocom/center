-- 로컬 결제 데이터 마이그레이션 (payment_type 포함)
-- 생성일: 2025-06-21
-- 총 데이터: 412건

BEGIN;

-- 임시 테이블 생성 (중복 방지)
CREATE TEMP TABLE temp_payments AS
SELECT * FROM payments WHERE 1=0;

-- 결제 데이터 삽입
INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(618, '2024-01-03', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(488, '2024-01-03', 150000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(951, '2024-01-03', 344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(681, '2024-01-03', 100000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(681, '2024-01-03', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(460, '2024-01-03', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(460, '2024-01-03', 1000000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(626, '2024-01-07', 600000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(582, '2024-01-10', 600000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(437, '2024-01-13', 26000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(892, '2024-01-15', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(696, '2024-01-15', 344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(697, '2024-01-15', 1044000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(574, '2024-01-16', 1290000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(700, '2024-01-17', 1314000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(780, '2024-01-18', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(702, '2024-01-19', 1044000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(704, '2024-01-20', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(705, '2024-01-21', 1244000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(706, '2024-01-22', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(460, '2024-01-22', 600000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(707, '2024-01-22', 35900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(707, '2024-01-22', 344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(618, '2024-01-23', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(200, '2024-01-25', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(707, '2024-01-25', 150000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(711, '2024-01-26', 644000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(365, '2024-01-26', 1500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(712, '2024-01-27', 1634000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(543, '2024-01-27', 2600000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(714, '2024-01-27', 644000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(714, '2024-01-27', 544000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(714, '2024-01-27', -544000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(705, '2024-01-28', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(315, '2024-01-28', 344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(637, '2024-01-28', 1290000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(780, '2024-01-29', 35900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(588, '2024-01-30', 960000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(437, '2024-01-30', 1850000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(437, '2024-01-30', -1850000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(437, '2024-01-30', 1850000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(952, '2024-01-30', 344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(574, '2024-01-31', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(315, '2024-01-31', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(625, '2024-01-31', 2250000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(717, '2024-01-31', 26000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(719, '2024-02-04', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(953, '2024-02-05', 900000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(953, '2024-02-05', 17800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(954, '2024-02-05', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(721, '2024-02-06', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(721, '2024-02-06', 26000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(954, '2024-02-06', 344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(722, '2024-02-07', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(723, '2024-02-09', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(953, '2024-02-09', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(724, '2024-02-10', 344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(725, '2024-02-13', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(460, '2024-02-13', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(726, '2024-02-14', 363800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(681, '2024-02-14', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(955, '2024-02-15', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(955, '2024-02-15', -300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(955, '2024-02-15', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(728, '2024-02-18', 48000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(956, '2024-02-18', 750000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(729, '2024-02-18', 36000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(530, '2024-02-20', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(730, '2024-02-21', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(668, '2024-02-21', 26000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(957, '2024-02-26', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(702, '2024-02-27', 16900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(689, '2024-02-28', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(958, '2024-02-28', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(734, '2024-02-28', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(731, '2024-02-29', 52000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(736, '2024-03-02', 309900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(956, '2024-03-02', -750000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(956, '2024-03-02', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(959, '2024-03-03', 309900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(697, '2024-03-04', 284000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(697, '2024-03-04', -1044000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(738, '2024-03-04', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(739, '2024-03-05', 1290000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(740, '2024-03-07', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(702, '2024-03-08', 150000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(741, '2024-03-11', 18900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(739, '2024-03-12', 1000000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(744, '2024-03-13', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(960, '2024-03-13', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(747, '2024-03-14', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(746, '2024-03-14', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(745, '2024-03-14', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(749, '2024-03-15', 68900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(752, '2024-03-16', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(751, '2024-03-16', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(750, '2024-03-16', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(729, '2024-03-20', 2840000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(738, '2024-03-20', 45000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(745, '2024-03-21', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(754, '2024-03-22', 36000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(752, '2024-03-23', 590000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(961, '2024-03-23', 45900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(756, '2024-03-23', 1890000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(758, '2024-03-24', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(759, '2024-03-25', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(962, '2024-03-25', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(574, '2024-03-30', -300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(752, '2024-03-30', 360000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(752, '2024-03-30', 240000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(761, '2024-03-30', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(740, '2024-04-01', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(762, '2024-04-02', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(765, '2024-04-04', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(763, '2024-04-05', 609900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(764, '2024-04-05', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(766, '2024-04-06', 105300, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(770, '2024-04-09', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(769, '2024-04-09', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(765, '2024-04-10', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(771, '2024-04-11', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(773, '2024-04-11', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(772, '2024-04-11', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(765, '2024-04-11', 1990000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(952, '2024-04-12', -344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(952, '2024-04-12', 104000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(774, '2024-04-17', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(729, '2024-04-18', -2840000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(729, '2024-04-18', 830000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(765, '2024-04-18', 700000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(775, '2024-04-19', 108000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(772, '2024-04-19', 36000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(963, '2024-04-21', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(781, '2024-04-23', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(784, '2024-04-24', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(964, '2024-04-24', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(432, '2024-04-25', -552000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(774, '2024-04-28', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(785, '2024-04-28', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(549, '2024-04-28', 1290000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(714, '2024-04-29', -644000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(714, '2024-04-29', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(714, '2024-04-29', 432000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(786, '2024-04-30', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(772, '2024-05-02', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(965, '2024-05-04', 119000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(965, '2024-05-04', -344000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(787, '2024-05-05', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(686, '2024-05-08', -644000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(686, '2024-05-08', 456000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(787, '2024-05-09', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(788, '2024-05-10', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(789, '2024-05-10', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(790, '2024-05-13', 88700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(966, '2024-05-13', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(794, '2024-05-14', 5580, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(794, '2024-05-14', 50220, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(795, '2024-05-14', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(792, '2024-05-14', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(793, '2024-05-14', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(796, '2024-05-16', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(797, '2024-05-16', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(618, '2024-05-17', -300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(798, '2024-05-17', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(799, '2024-05-18', 59000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(800, '2024-05-18', 1290000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(801, '2024-05-19', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(802, '2024-05-20', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(805, '2024-05-21', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(801, '2024-05-22', 600000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(806, '2024-05-23', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(806, '2024-05-23', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(807, '2024-05-23', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(809, '2024-05-24', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(810, '2024-05-25', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(811, '2024-05-27', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(813, '2024-05-28', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(814, '2024-05-29', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(815, '2024-05-29', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(816, '2024-05-30', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(817, '2024-05-30', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(818, '2024-06-01', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(820, '2024-06-04', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(821, '2024-06-05', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(823, '2024-06-08', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(824, '2024-06-10', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(825, '2024-06-13', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(826, '2024-06-16', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(827, '2024-06-27', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(829, '2024-06-29', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(830, '2024-07-06', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(830, '2024-07-06', 360000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(831, '2024-07-07', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(557, '2024-07-07', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(967, '2024-07-15', 95400, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(968, '2024-07-20', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(839, '2024-07-23', 78800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(839, '2024-07-27', 360000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(830, '2024-07-27', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(841, '2024-07-27', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(842, '2024-07-29', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(839, '2024-07-30', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(843, '2024-07-30', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(844, '2024-08-03', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(557, '2024-08-03', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(830, '2024-08-05', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(847, '2024-08-08', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(847, '2024-08-08', 360000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(848, '2024-08-10', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(830, '2024-08-17', 80000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(588, '2024-08-19', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(477, '2024-08-20', 600000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(847, '2024-08-21', 36000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(847, '2024-08-21', -360000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(969, '2024-08-21', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(507, '2024-08-28', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(507, '2024-08-28', 1500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(851, '2024-08-29', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(852, '2024-09-02', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(853, '2024-09-02', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(739, '2024-09-05', 39000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(549, '2024-09-08', 600000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(507, '2024-09-10', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(970, '2024-09-11', 2000000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(557, '2024-09-14', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(549, '2024-09-22', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(855, '2024-09-25', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(855, '2024-09-25', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(971, '2024-09-30', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(856, '2024-10-04', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(518, '2024-10-07', 300000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(857, '2024-10-10', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(363, '2024-10-11', 360000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(436, '2024-10-15', 360000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(972, '2024-10-17', 330000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(210, '2024-10-17', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(972, '2024-10-17', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(210, '2024-10-17', 330000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(973, '2024-10-17', 929700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(858, '2024-10-17', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(973, '2024-10-21', 1290000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(859, '2024-10-22', 319800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(861, '2024-10-23', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(861, '2024-10-23', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(860, '2024-10-23', 2229700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(862, '2024-10-26', 36000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(864, '2024-10-31', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(557, '2024-11-02', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(867, '2024-11-09', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(871, '2024-11-12', 45900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(870, '2024-11-13', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(872, '2024-11-13', 45900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(869, '2024-11-13', 2476900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(873, '2024-11-15', 1789900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(874, '2024-11-16', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(876, '2024-11-17', 700000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(878, '2024-11-18', 2495700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(881, '2024-11-21', 2000000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(881, '2024-11-21', 1891400, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(879, '2024-11-21', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(882, '2024-11-23', 2538800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(883, '2024-11-24', 55900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(884, '2024-11-24', 101700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(885, '2024-11-25', 1006900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(885, '2024-11-28', 1006900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(888, '2024-11-30', 1780000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(890, '2024-12-01', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(891, '2024-12-02', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(889, '2024-12-04', 3760000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(893, '2024-12-07', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(894, '2024-12-07', 65700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(895, '2024-12-09', 10000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(896, '2024-12-10', 45900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(892, '2024-12-11', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(859, '2024-12-13', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(897, '2024-12-19', 60000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(899, '2024-12-21', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(974, '2024-12-26', 1780000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(886, '2024-12-29', 5148000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(887, '2024-12-29', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(900, '2025-01-02', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(869, '2025-01-03', 2080000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(901, '2025-01-05', 101700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(901, '2025-01-07', 2528900, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(902, '2025-01-08', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(903, '2025-01-09', 65700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(904, '2025-01-10', 55800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(905, '2025-01-13', 36000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(507, '2025-01-23', 13500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(906, '2025-01-25', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(877, '2025-02-04', 2509000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(907, '2025-02-07', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(882, '2025-02-08', 2210000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(909, '2025-02-13', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(617, '2025-02-19', 59400, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(911, '2025-02-19', 1780000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(756, '2025-02-22', 3000000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(436, '2025-02-25', 1440000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(912, '2025-02-25', 49500, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(739, '2025-02-26', 1440000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(972, '2025-02-27', 420000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(210, '2025-02-27', 840000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(588, '2025-02-27', 1440000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(914, '2025-03-04', 5148000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(914, '2025-03-04', 184800, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(383, '2025-03-05', 1260000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(507, '2025-03-06', 1000000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(507, '2025-03-06', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(507, '2025-03-06', 2500000, 'card', 'one_time', 'completed', '2025-06-05 00:10:31'),
(975, '2025-05-02', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(976, '2025-05-02', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(625, '2025-05-03', 44000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(919, '2025-05-03', 285200, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(934, '2025-05-04', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(935, '2025-05-07', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(936, '2025-05-07', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(793, '2025-05-08', 1200000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(938, '2025-05-09', 1000000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(937, '2025-05-09', 10000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(939, '2025-05-09', 2519000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(940, '2025-05-12', 550000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(937, '2025-05-14', 10000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(941, '2025-05-14', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(942, '2025-05-15', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(943, '2025-05-16', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(919, '2025-05-17', 208600, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(940, '2025-05-18', -550000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(940, '2025-05-18', 55000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(932, '2025-05-18', 184800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(944, '2025-05-19', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(945, '2025-05-22', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(889, '2025-05-23', 171230, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(927, '2025-05-29', 246400, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(919, '2025-05-24', 34300, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(946, '2025-05-25', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(947, '2025-05-25', 1890000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(948, '2025-05-26', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(949, '2025-05-27', 1890000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(927, '2025-05-29', 47880, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(927, '2025-05-29', 50000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(950, '2025-05-29', 1780000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(922, '2025-04-01', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(923, '2025-04-04', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(924, '2025-04-05', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(617, '2025-04-08', -1780000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(617, '2025-04-08', 988000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(925, '2025-04-09', 2079000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(926, '2025-04-10', 60000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(859, '2025-04-11', 9900, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(927, '2025-04-16', 3000000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(928, '2025-04-16', 2519000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(929, '2025-04-18', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(977, '2025-04-21', 1020000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(927, '2025-04-22', 760000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(930, '2025-04-24', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(931, '2025-04-24', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(932, '2025-04-25', 2519000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(919, '2025-04-26', 21000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(443, '2025-04-26', 1320000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(588, '2025-04-27', 1188000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(933, '2025-04-27', 2500000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(488, '2025-04-29', 1890000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(914, '2025-03-04', 5148000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(914, '2025-03-04', 184800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(383, '2025-03-05', 1260000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(507, '2025-03-06', 1000000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(507, '2025-03-06', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(507, '2025-03-06', 2500000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(765, '2025-03-07', 540000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(859, '2025-03-07', 360000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(915, '2025-03-08', 2290000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(978, '2025-03-09', 1920000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(712, '2025-03-11', 1620000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(916, '2025-03-12', 3760000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(917, '2025-03-14', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(919, '2025-03-22', 1000000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(919, '2025-03-22', 1519000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(914, '2025-03-24', 554400, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(920, '2025-03-27', 4136000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(919, '2025-03-29', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(919, '2025-03-29', 118300, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(557, '2025-03-29', 208600, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(914, '2025-03-30', 578200, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(877, '2025-02-04', 2509000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(907, '2025-02-07', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(882, '2025-02-08', 2210000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(909, '2025-02-13', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(617, '2025-02-19', 59400, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(617, '2025-02-19', 1780000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(756, '2025-02-22', 3000000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(912, '2025-02-25', 49500, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(436, '2025-02-25', 1440000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(739, '2025-02-26', 1440000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(588, '2025-02-27', 1440000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(972, '2025-02-27', 420000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(210, '2025-02-27', 840000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(900, '2025-01-02', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(869, '2025-01-03', 2080000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(901, '2025-01-05', 101700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(901, '2025-01-07', 2528900, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(902, '2025-01-08', 29700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(868, '2025-01-09', -780000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(868, '2025-01-09', -538000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(903, '2025-01-09', 65700, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(904, '2025-01-10', 55800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(905, '2025-01-13', 36000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(905, '2025-01-13', 19800, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(557, '2025-01-18', 374000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(507, '2025-01-18', 4000000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(507, '2025-01-23', 500000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

INSERT INTO temp_payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at) VALUES
(507, '2025-01-23', 13500000, 'card', 'one_time', 'completed', '2025-06-05 00:11:05'),
(906, '2025-01-25', 39600, 'card', 'one_time', 'completed', '2025-06-05 00:11:05');

-- 중복을 제거하고 실제 테이블에 삽입
INSERT INTO payments (customer_id, payment_date, amount, payment_method, payment_type, payment_status, created_at)
SELECT DISTINCT t.customer_id, t.payment_date, t.amount, t.payment_method, t.payment_type, t.payment_status, t.created_at
FROM temp_payments t
LEFT JOIN payments p ON 
    p.customer_id = t.customer_id AND 
    p.payment_date = t.payment_date AND 
    p.amount = t.amount
WHERE p.payment_id IS NULL;

-- 결과 확인
SELECT COUNT(*) as total_payments FROM payments;

COMMIT;

-- 최종 통계 확인
SELECT 
    COUNT(*) as total_count,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(amount) as total_revenue,
    MIN(payment_date) as first_payment,
    MAX(payment_date) as last_payment
FROM payments;
