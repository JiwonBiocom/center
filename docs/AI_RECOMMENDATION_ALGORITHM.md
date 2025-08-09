# AIBIO AI 추천 알고리즘 상세 설계

## 1. 개요
인바디 데이터와 문진 정보를 통합 분석하여 개인 맞춤형 건강 솔루션을 추천하는 AI 알고리즘

## 2. 핵심 데이터 구조

### 2.1 입력 데이터
```python
class HealthAssessmentInput:
    # InBody 데이터
    inbody: {
        'weight': float,
        'muscle_mass': float,
        'body_fat_percentage': float,
        'visceral_fat': int,
        'phase_angle': float,
        'basal_metabolic_rate': float,
        'body_water': float,
        'protein': float,
        'mineral': float,
        'segmental_muscle': dict,  # 부위별 근육량
        'segmental_fat': dict      # 부위별 체지방
    }
    
    # 기본 정보
    demographics: {
        'age': int,
        'gender': str,
        'height': float,
        'occupation': str,
        'lifestyle': str  # sedentary, moderate, active
    }
    
    # 문진 데이터
    questionnaire: {
        'sleep_quality': int,      # 1-10
        'sleep_hours': float,
        'stress_level': int,       # 1-10
        'fatigue_physical': int,   # 1-10
        'fatigue_mental': int,     # 1-10
        'pain_areas': list,
        'digestive_issues': list,
        'exercise_frequency': int,  # 주당 횟수
        'medical_conditions': list,
        'medications': list,
        'goals': list  # 최대 3개
    }
```

### 2.2 출력 데이터
```python
class HealthRecommendation:
    # 건강 평가
    health_assessment: {
        'cellular_age': float,
        'age_gap': float,  # 실제나이 - 세포나이
        'overall_score': float,  # 0-100
        'category_scores': dict,  # 카테고리별 점수
        'risk_factors': list,
        'strengths': list
    }
    
    # 서비스 추천
    service_recommendations: [
        {
            'service': str,
            'priority': int,  # 1-5
            'frequency': str,  # 주 X회
            'duration': int,  # 분
            'reason': str,
            'expected_benefits': list
        }
    ]
    
    # 영양제 추천
    supplement_recommendations: [
        {
            'name': str,
            'category': str,
            'dosage': str,
            'timing': str,  # 아침/점심/저녁
            'priority': str,  # high/medium/low
            'reason': str,
            'duration': str  # 3개월/6개월/지속
        }
    ]
    
    # 식단 추천
    diet_recommendations: {
        'calorie_target': int,
        'macro_ratios': {
            'carbs': float,
            'protein': float,
            'fat': float
        },
        'meal_plan': dict,
        'recommended_foods': list,
        'avoid_foods': list,
        'hydration_target': float  # 리터
    }
```

## 3. 세포 나이 계산 알고리즘

### 3.1 위상각 기반 계산
```python
def calculate_cellular_age(phase_angle: float, age: int, gender: str) -> tuple:
    """
    위상각을 기반으로 세포 나이 계산
    
    Returns:
        (cellular_age, confidence_score)
    """
    # 성별/연령별 표준 위상각 테이블
    PHASE_ANGLE_STANDARDS = {
        'male': {
            '20-29': 7.2,
            '30-39': 6.9,
            '40-49': 6.5,
            '50-59': 6.1,
            '60-69': 5.7,
            '70+': 5.3
        },
        'female': {
            '20-29': 6.3,
            '30-39': 6.1,
            '40-49': 5.9,
            '50-59': 5.6,
            '60-69': 5.3,
            '70+': 5.0
        }
    }
    
    # 연령대 결정
    age_group = get_age_group(age)
    standard_pa = PHASE_ANGLE_STANDARDS[gender][age_group]
    
    # 위상각 차이 계산
    pa_difference = phase_angle - standard_pa
    
    # 위상각 1도 차이 = 약 5년의 생물학적 나이 차이
    age_adjustment = pa_difference * 5
    
    # 세포 나이 계산
    cellular_age = age - age_adjustment
    
    # 신뢰도 계산 (위상각이 정상 범위에 가까울수록 높음)
    confidence = calculate_confidence(pa_difference)
    
    return cellular_age, confidence
```

### 3.2 보정 요인 적용
```python
def apply_correction_factors(base_cellular_age: float, health_data: dict) -> float:
    """
    추가 건강 지표를 통한 세포 나이 보정
    """
    corrections = []
    
    # 체지방률 보정
    if health_data['body_fat_percentage'] > 30:
        corrections.append(2.0)  # 2년 추가
    elif health_data['body_fat_percentage'] < 15:
        corrections.append(-1.5)  # 1.5년 감소
    
    # 근육량 보정
    muscle_ratio = health_data['muscle_mass'] / health_data['weight']
    if muscle_ratio > 0.45:
        corrections.append(-2.0)
    elif muscle_ratio < 0.35:
        corrections.append(1.5)
    
    # 생활습관 보정
    if health_data['exercise_frequency'] >= 4:
        corrections.append(-1.0)
    if health_data['sleep_quality'] >= 8:
        corrections.append(-0.5)
    if health_data['stress_level'] >= 8:
        corrections.append(1.0)
    
    # 최종 보정값 적용 (최대 ±5년)
    total_correction = min(max(sum(corrections), -5), 5)
    
    return base_cellular_age + total_correction
```

## 4. 통합 건강 점수 계산

### 4.1 카테고리별 점수 산출
```python
def calculate_category_scores(data: HealthAssessmentInput) -> dict:
    scores = {}
    
    # 1. 신체 구성 점수 (0-100)
    scores['body_composition'] = calculate_body_composition_score(
        bmi=calculate_bmi(data.inbody['weight'], data.demographics['height']),
        body_fat=data.inbody['body_fat_percentage'],
        muscle_mass=data.inbody['muscle_mass'],
        visceral_fat=data.inbody['visceral_fat']
    )
    
    # 2. 대사 건강 점수
    scores['metabolic_health'] = calculate_metabolic_score(
        bmr=data.inbody['basal_metabolic_rate'],
        phase_angle=data.inbody['phase_angle'],
        protein=data.inbody['protein'],
        age=data.demographics['age']
    )
    
    # 3. 스트레스 관리 점수
    scores['stress_management'] = calculate_stress_score(
        stress_level=data.questionnaire['stress_level'],
        sleep_quality=data.questionnaire['sleep_quality'],
        mental_fatigue=data.questionnaire['fatigue_mental']
    )
    
    # 4. 체력 및 활력 점수
    scores['vitality'] = calculate_vitality_score(
        physical_fatigue=data.questionnaire['fatigue_physical'],
        exercise_frequency=data.questionnaire['exercise_frequency'],
        muscle_mass=data.inbody['muscle_mass']
    )
    
    # 5. 영양 상태 점수
    scores['nutrition'] = calculate_nutrition_score(
        body_water=data.inbody['body_water'],
        protein=data.inbody['protein'],
        mineral=data.inbody['mineral']
    )
    
    return scores
```

### 4.2 가중치 적용
```python
def calculate_weighted_score(scores: dict, goals: list) -> float:
    """
    개인 목표에 따른 가중치 적용
    """
    # 기본 가중치
    base_weights = {
        'body_composition': 0.25,
        'metabolic_health': 0.25,
        'stress_management': 0.20,
        'vitality': 0.20,
        'nutrition': 0.10
    }
    
    # 목표별 가중치 조정
    goal_weight_adjustments = {
        '체중감량': {'body_composition': 0.35, 'metabolic_health': 0.30},
        '스트레스관리': {'stress_management': 0.40, 'vitality': 0.15},
        '체력향상': {'vitality': 0.35, 'body_composition': 0.30},
        '수면개선': {'stress_management': 0.35, 'vitality': 0.25},
        '근육증가': {'body_composition': 0.40, 'nutrition': 0.20}
    }
    
    # 가중치 적용
    weights = base_weights.copy()
    for goal in goals:
        if goal in goal_weight_adjustments:
            for key, adjustment in goal_weight_adjustments[goal].items():
                weights[key] = adjustment
    
    # 정규화
    total_weight = sum(weights.values())
    weights = {k: v/total_weight for k, v in weights.items()}
    
    # 최종 점수 계산
    weighted_score = sum(scores[k] * weights[k] for k in scores)
    
    return weighted_score
```

## 5. 서비스 추천 알고리즘

### 5.1 이슈 기반 매핑
```python
def map_issues_to_services(health_data: dict) -> list:
    """
    건강 이슈를 서비스로 매핑
    """
    service_mapping = []
    
    # 스트레스/수면 문제
    if health_data['stress_level'] >= 7 or health_data['sleep_quality'] <= 5:
        service_mapping.append({
            'service': '브레인피드백',
            'score': health_data['stress_level'] + (10 - health_data['sleep_quality']),
            'reason': '스트레스 감소 및 수면 질 개선'
        })
    
    # 근육 피로/통증
    if health_data['fatigue_physical'] >= 7 or len(health_data['pain_areas']) > 0:
        service_mapping.append({
            'service': '펄스',
            'score': health_data['fatigue_physical'] + len(health_data['pain_areas']) * 2,
            'reason': '근육 피로 회복 및 통증 완화'
        })
    
    # 순환/부종 문제
    if health_data['body_water'] < 50 or '부종' in health_data['symptoms']:
        service_mapping.append({
            'service': '림프',
            'score': 8,
            'reason': '림프 순환 개선 및 부종 감소'
        })
    
    # 체중/체지방 관리
    if health_data['body_fat_percentage'] > 25 or '체중감량' in health_data['goals']:
        service_mapping.append({
            'service': 'AI바이크',
            'score': min(health_data['body_fat_percentage'] - 20, 10),
            'reason': '유산소 운동을 통한 체지방 감소'
        })
        service_mapping.append({
            'service': '레드',
            'score': 7,
            'reason': '지방 분해 촉진'
        })
    
    return sorted(service_mapping, key=lambda x: x['score'], reverse=True)
```

### 5.2 시너지 최적화
```python
def optimize_service_combination(primary_services: list, constraints: dict) -> list:
    """
    서비스 조합 최적화
    """
    # 시너지 매트릭스
    SYNERGY_MATRIX = {
        ('브레인피드백', '림프'): 1.3,    # 30% 시너지
        ('AI바이크', '레드'): 1.25,       # 25% 시너지
        ('펄스', '림프'): 1.2,            # 20% 시너지
        ('브레인피드백', '펄스'): 1.15    # 15% 시너지
    }
    
    # 제약 조건
    max_services = constraints.get('max_services', 3)
    total_time = constraints.get('total_time', 120)  # 분
    
    # 조합 생성 및 평가
    best_combination = []
    best_score = 0
    
    for r in range(1, min(len(primary_services), max_services) + 1):
        for combo in itertools.combinations(primary_services[:5], r):
            score = sum(s['score'] for s in combo)
            
            # 시너지 보너스 적용
            for i, s1 in enumerate(combo):
                for s2 in combo[i+1:]:
                    key = tuple(sorted([s1['service'], s2['service']]))
                    if key in SYNERGY_MATRIX:
                        score *= SYNERGY_MATRIX[key]
            
            # 시간 제약 확인
            total_duration = sum(SERVICE_DURATION[s['service']] for s in combo)
            if total_duration <= total_time and score > best_score:
                best_score = score
                best_combination = combo
    
    return list(best_combination)
```

## 6. 영양제 추천 알고리즘

### 6.1 바이오컴 제품 기반 영양제 추천
```python
def recommend_biocom_supplements(health_data: dict, age_gap: float) -> list:
    """
    바이오컴 제품 기반 맞춤형 영양제 추천
    """
    recommendations = []
    
    # 1. 세포 나이 기반 항산화 추천
    if age_gap > 3:
        recommendations.append({
            'product': '슈퍼슬로우 & 화이트샷',
            'category': '항산화/세포보호',
            'reason': f'세포 나이가 {age_gap:.1f}년 높음. SOD 효소로 활성산소 제거',
            'priority': 'high',
            'dosage': '1일 1포',
            'timing': '아침 식후',
            'score': 10
        })
        
        if age_gap > 5:
            recommendations.append({
                'product': 'CoQ10-DMG 300/300',
                'category': '에너지대사/항산화',
                'reason': '세포 에너지 생성 촉진, 심혈관 건강',
                'priority': 'high',
                'dosage': '1일 1정',
                'timing': '아침 공복',
                'score': 9
            })
    
    # 2. 스트레스/정신 건강
    if health_data['stress_level'] >= 7:
        recommendations.append({
            'product': '바이오 밸런스',
            'category': '종합미네랄/스트레스',
            'reason': '마그네슘과 L-테아닌으로 스트레스 완화',
            'priority': 'high',
            'dosage': '1일 3정',
            'timing': '아침 식후',
            'score': 9
        })
        
        if health_data['sleep_quality'] <= 5:
            recommendations.append({
                'product': '뉴로마스터',
                'category': '뇌기능/수면',
                'reason': '은행잎추출물과 L-트립토판으로 수면 개선',
                'priority': 'medium',
                'dosage': '1일 2정',
                'timing': '저녁 식후',
                'score': 7
            })
    
    # 3. 면역/알레르기
    if health_data.get('allergies') or health_data.get('immune_issues'):
        recommendations.append({
            'product': '다래케어',
            'category': '면역조절',
            'reason': '면역과민반응 개선, 알레르기 증상 완화',
            'priority': 'high',
            'dosage': '1일 6정',
            'timing': '아침 3정, 저녁 3정',
            'score': 8
        })
    
    # 4. 소화/장 건강
    if health_data.get('digestive_issues') or health_data.get('bloating'):
        recommendations.append({
            'product': '클린밸런스',
            'category': '장건강',
            'reason': '19종 유산균으로 장내 환경 개선',
            'priority': 'high',
            'dosage': '1일 1포',
            'timing': '아침 공복',
            'score': 8
        })
        
        recommendations.append({
            'product': 'Enzyme Benefits™',
            'category': '소화효소',
            'reason': '소화 개선 및 영양소 흡수 증진',
            'priority': 'medium',
            'dosage': '매 식사 시 1-2정',
            'timing': '식사 중',
            'score': 6
        })
    
    # 5. 체중/대사 관리
    if '체중감량' in health_data.get('goals', []) or health_data.get('blood_sugar_issues'):
        recommendations.append({
            'product': '끝판왕 혈당 영양제',
            'category': '혈당조절',
            'reason': '혈당 안정화로 체중 관리 지원',
            'priority': 'high',
            'dosage': '1일 2정',
            'timing': '저녁 식후',
            'score': 8
        })
        
        if health_data.get('body_fat_percentage', 0) > 25:
            recommendations.append({
                'product': 'Adipo-Leptin Benefits™',
                'category': '체지방감소',
                'reason': '지방 연소 촉진 및 식욕 조절',
                'priority': 'medium',
                'dosage': '1일 2정',
                'timing': '점심 식후',
                'score': 7
            })
    
    # 6. 피부/모발
    if health_data.get('hair_loss') or health_data.get('skin_issues'):
        recommendations.append({
            'product': '풍성밸런스',
            'category': '모발건강',
            'reason': '비오틴과 케라틴으로 모발 영양 공급',
            'priority': 'medium',
            'dosage': '1일 2정',
            'timing': '저녁 식후',
            'score': 6
        })
        
        recommendations.append({
            'product': '방탄젤리',
            'category': '피부건강',
            'reason': '콜라겐과 히알루론산으로 피부 탄력',
            'priority': 'medium',
            'dosage': '1일 1포',
            'timing': '저녁 식후',
            'score': 6
        })
    
    return recommendations
```

### 6.2 바이오컴 제품 우선순위 결정
```python
def prioritize_biocom_supplements(recommendations: list, max_supplements: int = 5) -> list:
    """
    바이오컴 제품 우선순위 결정 및 최적 조합
    """
    # 점수순으로 정렬
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    # 카테고리별 중복 제거 (같은 카테고리에서는 점수가 높은 것만)
    selected = []
    categories_included = set()
    
    for rec in recommendations:
        # 필수 제품은 무조건 포함
        if rec['priority'] == 'high' and len(selected) < max_supplements:
            selected.append(rec)
            categories_included.add(rec['category'])
        # 중간 우선순위는 카테고리 중복 확인
        elif rec['priority'] == 'medium' and rec['category'] not in categories_included and len(selected) < max_supplements:
            selected.append(rec)
            categories_included.add(rec['category'])
    
    # 시너지 효과를 고려한 조합 최적화
    optimized = optimize_supplement_combination(selected)
    
    return optimized

def optimize_supplement_combination(supplements: list) -> list:
    """
    영양제 간 시너지 효과 고려한 최적 조합
    """
    # 시너지 조합
    synergy_pairs = {
        ('슈퍼슬로우 & 화이트샷', 'CoQ10-DMG 300/300'): 1.3,  # 항산화 시너지
        ('클린밸런스', 'Enzyme Benefits™'): 1.2,  # 소화/흡수 시너지
        ('바이오 밸런스', '뉴로마스터'): 1.2,  # 스트레스/수면 시너지
        ('끝판왕 혈당 영양제', 'Adipo-Leptin Benefits™'): 1.25  # 대사 시너지
    }
    
    # 복용 시간 분산
    timing_groups = {
        'morning_empty': [],  # 아침 공복
        'morning_meal': [],   # 아침 식후
        'lunch': [],          # 점심 식후
        'dinner': [],         # 저녁 식후
        'with_meal': []       # 식사 중
    }
    
    for supp in supplements:
        if '공복' in supp['timing']:
            timing_groups['morning_empty'].append(supp)
        elif '아침' in supp['timing']:
            timing_groups['morning_meal'].append(supp)
        elif '점심' in supp['timing']:
            timing_groups['lunch'].append(supp)
        elif '저녁' in supp['timing']:
            timing_groups['dinner'].append(supp)
        elif '식사' in supp['timing']:
            timing_groups['with_meal'].append(supp)
    
    return supplements
```

## 7. 식단 추천 알고리즘

### 7.1 칼로리 및 매크로 계산
```python
def calculate_nutrition_targets(health_data: dict) -> dict:
    """
    개인별 영양 목표 계산
    """
    # 기초대사율 기반 칼로리 계산
    bmr = health_data['basal_metabolic_rate']
    activity_factor = get_activity_factor(health_data['exercise_frequency'])
    
    # 목표별 칼로리 조정
    calorie_adjustment = 0
    if '체중감량' in health_data['goals']:
        calorie_adjustment = -500  # 500kcal 적자
    elif '근육증가' in health_data['goals']:
        calorie_adjustment = 300   # 300kcal 잉여
    
    daily_calories = (bmr * activity_factor) + calorie_adjustment
    
    # 매크로 비율 결정
    if '체중감량' in health_data['goals']:
        macro_ratios = {'carbs': 0.35, 'protein': 0.35, 'fat': 0.30}
    elif '근육증가' in health_data['goals']:
        macro_ratios = {'carbs': 0.40, 'protein': 0.30, 'fat': 0.30}
    else:
        macro_ratios = {'carbs': 0.45, 'protein': 0.25, 'fat': 0.30}
    
    # 체중 기반 단백질 최소량 확인
    min_protein = health_data['weight'] * 0.8  # 체중 1kg당 0.8g
    protein_calories = daily_calories * macro_ratios['protein']
    if protein_calories / 4 < min_protein:
        macro_ratios['protein'] = (min_protein * 4) / daily_calories
        # 탄수화물 비율 조정
        macro_ratios['carbs'] = 1 - macro_ratios['protein'] - macro_ratios['fat']
    
    return {
        'daily_calories': round(daily_calories),
        'macro_grams': {
            'carbs': round(daily_calories * macro_ratios['carbs'] / 4),
            'protein': round(daily_calories * macro_ratios['protein'] / 4),
            'fat': round(daily_calories * macro_ratios['fat'] / 9)
        },
        'macro_ratios': macro_ratios,
        'meal_distribution': {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.30,
            'snacks': 0.10
        }
    }
```

### 7.2 식품 추천
```python
def recommend_foods(health_profile: dict, nutrition_targets: dict) -> dict:
    """
    건강 상태별 식품 추천
    """
    recommendations = {
        'power_foods': [],      # 적극 권장
        'good_foods': [],       # 권장
        'limit_foods': [],      # 제한
        'avoid_foods': []       # 피하기
    }
    
    # 항염증 식품 (세포 나이가 높은 경우)
    if health_profile['age_gap'] > 3:
        recommendations['power_foods'].extend([
            '연어 (오메가3)',
            '블루베리 (항산화)',
            '아보카도 (건강한 지방)',
            '브로콜리 (설포라판)',
            '녹차 (카테킨)'
        ])
    
    # 스트레스 감소 식품
    if health_profile['stress_level'] >= 7:
        recommendations['power_foods'].extend([
            '다크 초콜릿 (70% 이상)',
            '견과류 (마그네슘)',
            '캐모마일 차',
            '시금치 (엽산)'
        ])
    
    # 체중 관리 식품
    if '체중감량' in health_profile['goals']:
        recommendations['good_foods'].extend([
            '닭가슴살 (저지방 단백질)',
            '퀴노아 (복합 탄수화물)',
            '그릭 요거트 (프로바이오틱스)',
            '채소 스틱 (저칼로리 간식)'
        ])
        recommendations['avoid_foods'].extend([
            '정제 설탕',
            '트랜스 지방',
            '가공식품',
            '알코올'
        ])
    
    # 소화 개선 식품
    if health_profile.get('digestive_issues'):
        recommendations['power_foods'].extend([
            '김치 (프로바이오틱스)',
            '생강차 (소화 촉진)',
            '파파야 (소화 효소)'
        ])
        recommendations['limit_foods'].extend([
            '유제품 (유당 불내증 가능성)',
            '글루텐 (민감성 고려)',
            '매운 음식'
        ])
    
    return recommendations
```

## 8. 통합 추천 생성

### 8.1 최종 추천 조합
```python
def generate_final_recommendations(
    health_assessment: dict,
    service_recommendations: list,
    supplement_recommendations: list,
    diet_recommendations: dict
) -> HealthRecommendation:
    """
    모든 추천을 통합하여 최종 보고서 생성
    """
    # 우선순위 조정
    if health_assessment['age_gap'] > 5:
        # 세포 나이가 많이 높은 경우 항산화 우선
        boost_antioxidant_priority(supplement_recommendations)
    
    # 상충되는 추천 조정
    recommendations = resolve_conflicts(
        services=service_recommendations,
        supplements=supplement_recommendations,
        diet=diet_recommendations
    )
    
    # 실행 계획 생성
    implementation_plan = create_implementation_plan(
        recommendations=recommendations,
        constraints=get_user_constraints()
    )
    
    return HealthRecommendation(
        health_assessment=health_assessment,
        service_recommendations=recommendations['services'],
        supplement_recommendations=recommendations['supplements'],
        diet_recommendations=recommendations['diet'],
        implementation_plan=implementation_plan
    )
```

## 9. 머신러닝 모델 통합 (향후)

### 9.1 추천 정확도 개선
```python
class RecommendationMLModel:
    """
    고객 피드백 기반 추천 개선 모델
    """
    def __init__(self):
        self.model = self._build_model()
        self.feature_encoder = self._build_encoder()
    
    def _build_model(self):
        # 신경망 기반 추천 모델
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(num_services, activation='sigmoid')
        ])
        return model
    
    def predict_service_effectiveness(self, user_profile: dict) -> dict:
        """
        사용자 프로파일 기반 서비스 효과 예측
        """
        features = self.feature_encoder.transform(user_profile)
        predictions = self.model.predict(features)
        
        return {
            service: float(pred) 
            for service, pred in zip(SERVICE_LIST, predictions[0])
        }
    
    def update_from_feedback(self, user_id: str, feedback: dict):
        """
        고객 피드백으로 모델 업데이트
        """
        # 피드백 데이터 수집 및 재학습
        pass
```

## 10. 평가 지표

### 10.1 알고리즘 성능 지표
- **추천 수용률**: 추천된 서비스/제품의 실제 구매율
- **고객 만족도**: 추천 후 피드백 점수
- **건강 개선도**: 3개월/6개월 후 건강 지표 변화
- **재방문율**: 추천 받은 고객의 재방문 비율

### 10.2 건강 개선 추적
```python
def track_health_improvements(customer_id: str, period_months: int) -> dict:
    """
    건강 지표 개선 추적
    """
    baseline = get_baseline_data(customer_id)
    current = get_current_data(customer_id)
    
    improvements = {
        'cellular_age_change': current['cellular_age'] - baseline['cellular_age'],
        'body_fat_change': current['body_fat'] - baseline['body_fat'],
        'muscle_mass_change': current['muscle_mass'] - baseline['muscle_mass'],
        'stress_level_change': current['stress_level'] - baseline['stress_level'],
        'sleep_quality_change': current['sleep_quality'] - baseline['sleep_quality']
    }
    
    return calculate_improvement_score(improvements)
```