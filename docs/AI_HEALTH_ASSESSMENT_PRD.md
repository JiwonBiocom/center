# AIBIO AI 기반 건강 평가 및 추천 시스템 PRD

## 1. 개요

### 1.1 프로젝트 목적
태블릿 기반의 인터랙티브 문진 시스템을 통해 고객의 건강 상태를 종합적으로 평가하고, AI가 인바디 데이터와 문진 정보를 분석하여 최적의 서비스, 영양제, 식단을 추천하는 통합 시스템 구축

### 1.2 핵심 가치
- **효율성**: 10-15분 내 완료 가능한 스마트 문진
- **정확성**: AI 기반 다차원 건강 상태 분석
- **개인화**: 고객별 맞춤 추천 시스템
- **통합성**: 인바디 데이터와 문진 정보의 유기적 연계

## 2. 시스템 아키텍처

### 2.1 데이터 플로우
```
고객 도착 → InBody 측정 → 태블릿 문진 → AI 분석 → 추천 생성 → 상담
```

### 2.2 핵심 구성요소
1. **태블릿 문진 앱**: 인터랙티브 문진 인터페이스
2. **AI 분석 엔진**: 데이터 통합 분석 및 추천
3. **상담자 대시보드**: 분석 결과 및 추천 확인
4. **고객 리포트**: 개인화된 건강 보고서

## 3. 인터랙티브 문진 시스템

### 3.1 문진 구조

#### 3.1.1 필수 문진 (5-7분)
1. **기본 정보** (1분)
   - 성별, 나이, 키, 체중
   - 방문 목적 (선택형)
   - 현재 복용 약물
   - 알레르기 정보

2. **핵심 건강 평가** (3-4분)
   - 수면 패턴 (질/시간/장애)
   - 스트레스 수준 (0-10 척도)
   - 피로도 평가 (신체/정신)
   - 통증 유무 및 부위
   - 소화 상태
   - 운동 빈도

3. **목표 설정** (1-2분)
   - 주요 개선 목표 (최대 3개 선택)
   - 기대하는 변화
   - 서비스 이용 가능 빈도

#### 3.1.2 선택적 심화 문진 (각 3-5분)
조건부 활성화 - 필수 문진 응답에 따라 자동 추천

**A. 스트레스/정신건강 모듈** (BAI/BDI 간소화)
- 트리거: 스트레스 7점 이상, 수면 장애, 정신적 피로
- 내용: 불안/우울 증상, 집중력, 기분 변화

**B. 소화기 건강 모듈**
- 트리거: 소화 불량, 복부 불편감
- 내용: 식습관, 배변 패턴, 음식 민감성

**C. 호르몬/대사 모듈**
- 트리거: 체중 변화, 피로, 여성 건강 이슈
- 내용: 체중 변화 패턴, 생리 주기(여성), 갑상선 증상

**D. 근골격계 모듈**
- 트리거: 통증 존재, 운동 제한
- 내용: 통증 세부사항, 자세 문제, 운동 이력

### 3.2 UX/UI 설계 원칙
- **진행률 표시**: 상단 프로그레스 바
- **스킵 옵션**: 민감한 질문은 건너뛰기 가능
- **시각적 피드백**: 슬라이더, 아이콘, 그래픽 활용
- **데이터 저장**: 자동 저장으로 중단 시 이어하기 가능

## 4. AI 분석 및 추천 알고리즘

### 4.1 세포 나이 계산
```python
# 위상각 기반 세포 나이 추정
def calculate_cellular_age(phase_angle, gender, chronological_age):
    # 성별/나이별 표준 위상각 참조
    standard_pa = get_standard_phase_angle(gender, chronological_age)
    
    # 위상각 차이를 나이 차이로 변환
    pa_difference = phase_angle - standard_pa
    age_adjustment = pa_difference * AGE_CONVERSION_FACTOR
    
    cellular_age = chronological_age - age_adjustment
    return cellular_age, age_adjustment
```

### 4.2 통합 건강 점수 산출
```python
def calculate_health_score(inbody_data, questionnaire_data):
    scores = {
        '신체구성': calculate_body_composition_score(inbody_data),
        '대사건강': calculate_metabolic_score(inbody_data, questionnaire_data),
        '스트레스': calculate_stress_score(questionnaire_data),
        '수면': calculate_sleep_score(questionnaire_data),
        '영양상태': calculate_nutrition_score(inbody_data, questionnaire_data)
    }
    
    # 가중 평균 계산
    weights = get_personalized_weights(questionnaire_data['goals'])
    total_score = weighted_average(scores, weights)
    
    return total_score, scores
```

### 4.3 서비스 추천 로직

#### 4.3.1 우선순위 매트릭스
| 건강 이슈 | 1순위 서비스 (2개) | 2순위 서비스 (1개) | 보조 서비스 |
|---------|-----------------|---------------|----------|
| 높은 스트레스 | 브레인피드백, 림프 | 펄스 | 호흡/명상 |
| 수면 장애 | 브레인피드백, 펄스 | 림프 | 아로마 |
| 근육 피로 | 펄스, 레드 | 림프 | 스트레칭 |
| 순환 문제 | 림프, 레드 | AI바이크 | 펄스 |
| 체중 관리 | 펄스, AI바이크 | 레드 | 영양 상담 |
| 식욕 문제 | 브레인피드백, 펄스 | 레드 | 영양 상담 |

#### 4.3.2 시너지 효과 고려
```python
def recommend_service_combination(primary_issues, available_time):
    base_services = get_primary_services(primary_issues)
    
    # 시너지 효과가 높은 조합 우선
    synergy_combinations = [
        ('브레인피드백', '림프'),  # 스트레스 + 순환
        ('AI바이크', '레드'),      # 유산소 + 회복
        ('펄스', '림프')          # 근육 + 림프순환
    ]
    
    return optimize_combination(base_services, synergy_combinations, available_time)
```

### 4.4 영양제 추천 알고리즘

#### 4.4.1 기본 추천 로직
```python
def recommend_supplements(health_scores, age_gap, questionnaire_data):
    recommendations = []
    
    # 세포 나이가 실제 나이보다 높은 경우
    if age_gap > 3:
        recommendations.append({
            'category': '항산화',
            'items': ['코엔자임Q10', 'NAD+', '글루타치온'],
            'priority': 'high'
        })
    
    # 스트레스 점수가 높은 경우
    if health_scores['스트레스'] < 60:
        recommendations.append({
            'category': '스트레스 관리',
            'items': ['마그네슘', 'L-테아닌', '아쉬와간다'],
            'priority': 'high'
        })
    
    # 수면 질이 낮은 경우
    if health_scores['수면'] < 60:
        recommendations.append({
            'category': '수면 개선',
            'items': ['멜라토닌', '마그네슘 글리시네이트', 'GABA'],
            'priority': 'medium'
        })
    
    return prioritize_supplements(recommendations, max_items=5)
```

### 4.5 식단 추천 시스템

#### 4.5.1 개인화 식단 프로파일
```python
def create_diet_profile(inbody_data, health_scores, preferences):
    profile = {
        'calorie_target': calculate_calorie_needs(inbody_data),
        'macro_ratio': determine_macro_ratio(health_scores, goals),
        'meal_timing': optimize_meal_timing(questionnaire_data),
        'food_recommendations': [],
        'avoid_foods': []
    }
    
    # 건강 상태별 식품 추천
    if health_scores['inflammation'] > 70:
        profile['food_recommendations'].extend(['오메가3 풍부 생선', '녹색 채소'])
        profile['avoid_foods'].extend(['가공식품', '정제 설탕'])
    
    return profile
```

## 5. 리포트 생성

### 5.1 고객 리포트 구성
1. **종합 건강 점수**: 시각적 대시보드
2. **세포 나이 분석**: 실제 나이 vs 세포 나이
3. **주요 건강 이슈**: 우선순위별 정리
4. **맞춤 추천**:
   - 추천 서비스 및 이용 순서
   - 영양제 추천 (우선순위별)
   - 식단 가이드라인
5. **목표 달성 로드맵**: 3개월/6개월 계획

### 5.2 상담자용 대시보드
- 고객 건강 프로파일 요약
- AI 추천 근거 설명
- 대화 가이드 및 주의사항
- 패키지 구성 제안

## 6. 구현 로드맵

### Phase 1 (1-2개월): MVP
- 태블릿 문진 앱 기본 기능
- 필수 문진만 구현
- 기본 AI 추천 (서비스만)

### Phase 2 (3-4개월): 확장
- 선택적 심화 문진 추가
- 영양제/식단 추천 추가
- 리포트 생성 자동화

### Phase 3 (5-6개월): 고도화
- 추천 정확도 개선 (ML 모델)
- 고객 피드백 반영 시스템
- 장기 추적 및 효과 분석

## 7. 성공 지표 (KPI)

1. **효율성 지표**
   - 평균 문진 완료 시간: < 15분
   - 문진 완료율: > 95%

2. **만족도 지표**
   - 추천 서비스 수용률: > 80%
   - 고객 만족도: > 4.5/5

3. **비즈니스 지표**
   - 패키지 구매 전환율 증가: +30%
   - 고객 재방문율 증가: +40%

## 8. 기술 요구사항

### 8.1 프론트엔드 (태블릿 앱)
- React Native 또는 Flutter
- 오프라인 모드 지원
- 다국어 지원 (한/영)

### 8.2 백엔드
- FastAPI (Python)
- PostgreSQL
- Redis (캐싱)

### 8.3 AI/ML
- TensorFlow/PyTorch
- 추천 시스템: Collaborative Filtering + Content-based
- 자연어 처리: 증상 키워드 추출

## 9. 보안 및 개인정보보호
- 의료 정보 암호화 저장
- HIPAA 준수 고려
- 데이터 보관 기간 설정
- 고객 동의 관리 시스템

## 10. 향후 확장 계획
- 웨어러블 기기 연동
- 실시간 건강 모니터링
- AI 챗봇 상담 보조
- 예측 분석 (질병 위험도)