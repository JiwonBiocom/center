# 미사용 API 엔드포인트

분석 날짜: 2025-06-21

## 요약
- 백엔드 총 API 엔드포인트: 119개
- 프론트엔드에서 사용 중: 약 85개
- 미사용 엔드포인트: 34개

## 미사용 엔드포인트 목록

### 1. Debug API (debug_api.py)
1. [debug_api.py] GET /simple-test - 가장 단순한 테스트 API
2. [debug_api.py] GET /db-test - 데이터베이스 연결 테스트
3. [debug_api.py] GET /customers-raw - Raw SQL로 고객 데이터 조회

### 2. Debug Payments (debug_payments.py)
4. [debug_payments.py] GET /test - 결제 테스트 API

### 3. Test Simple Customers (test_simple_customers.py)
5. [test_simple_customers.py] GET /simple - 간단한 고객 조회 테스트
6. [test_simple_customers.py] GET /simple-count - 고객 수 조회 테스트

### 4. Docs API (docs.py)
7. [docs.py] GET /list - 문서 목록 조회

### 5. Reports API
8. [reports/customer.py] GET /generate/customer-analysis - 고객 분석 보고서 생성
9. [reports/revenue.py] GET /generate/monthly-revenue - 월별 수익 보고서 생성
10. [reports/service.py] GET /trends - 서비스 트렌드 분석
11. [reports/export.py] GET /revenue - 수익 내보내기

### 6. Dashboard Optimized (dashboard_optimized.py)
12. [dashboard_optimized.py] GET /stats-optimized - 최적화된 통계
13. [dashboard_optimized.py] GET /weekly-stats-optimized - 최적화된 주간 통계
14. [dashboard_optimized.py] GET /monthly-revenue-optimized - 최적화된 월별 수익

### 7. Dashboard (dashboard.py)
15. [dashboard.py] GET /recent-activities - 최근 활동 내역

### 8. Customers API
16. [customers.py] GET /stats/by-region - 지역별 고객 통계
17. [customers.py] GET /stats/by-referral - 추천별 고객 통계

### 9. InBody API
18. [inbody.py] GET /customer/{customer_id}/chart-data - 고객별 인바디 차트 데이터

### 10. Leads API (leads.py)
19. [leads.py] GET /stats/funnel - 리드 퍼널 통계
20. [leads.py] GET /stats/by-channel - 채널별 리드 통계
21. [leads.py] POST /import/excel - 리드 엑셀 가져오기
22. [leads.py] GET /export/excel - 리드 엑셀 내보내기
23. [leads.py] POST /{lead_id}/convert - 리드 전환

### 11. Notifications API
24. [notifications.py] POST /broadcast - 브로드캐스트 알림
25. [notifications.py] GET /settings - 알림 설정 조회
26. [notifications.py] PUT /settings - 알림 설정 수정
27. [notifications.py] POST /test/package-expiry - 패키지 만료 알림 테스트

### 12. SMS API
28. [sms.py] GET /history - SMS 발송 이력

### 13. Staff Schedule API
29. [staff_schedule.py] GET / - 전체 스태프 스케줄 조회
30. [staff_schedule.py] POST / - 스태프 스케줄 생성

### 14. Reservations API
31. [reservations/calendar.py] GET / - 예약 캘린더 조회 (경로 없음)
32. [reservations/notifications.py] POST /send-reminders - 예약 리마인더 발송
33. [reservations/slots.py] GET /available - 예약 가능 슬롯 조회

### 15. Payments Fixed API (payments_fixed.py)
34. [payments_fixed.py] GET /stats - 결제 통계 (다른 버전)

## 권장사항

### 1. 즉시 삭제 가능
- debug_api.py 전체
- debug_payments.py 전체
- test_simple_customers.py 전체
- dashboard_optimized.py (기존 dashboard.py와 중복)
- payments_fixed.py (payments.py와 중복)

### 2. 확인 후 삭제 검토
- leads.py 전체 (customer_leads.py로 통합됨)
- 사용하지 않는 reports API 엔드포인트들

### 3. 유지 고려
- staff_schedule.py (향후 스태프 관리 기능 구현 시 필요)
- notifications의 broadcast 기능 (대량 알림 발송 시 필요)
- SMS history (발송 이력 관리 필요 시)

### 4. 프론트엔드 구현 필요
- 인바디 차트 데이터 시각화
- 지역별/추천별 고객 통계 대시보드
- 스태프 스케줄 관리 페이지
