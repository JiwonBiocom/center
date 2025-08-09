"""
문진 템플릿 및 기본 질문 데이터 초기화 스크립트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.database import engine
from models.questionnaire import (
    QuestionnaireTemplate, Question, QuestionnaireSection, QuestionType
)
import json


def init_questionnaire_data():
    """문진 템플릿 및 질문 데이터 초기화"""
    db = Session(engine)
    
    try:
        # 기존 템플릿 확인
        existing_template = db.query(QuestionnaireTemplate).filter(
            QuestionnaireTemplate.name == "AIBIO 건강 문진"
        ).first()
        
        if existing_template:
            print("이미 문진 템플릿이 존재합니다.")
            return
        
        # 1. 문진 템플릿 생성
        template = QuestionnaireTemplate(
            name="AIBIO 건강 문진",
            description="AIBIO 센터 기본 건강 평가 문진",
            version="1.0",
            is_active=True
        )
        db.add(template)
        db.flush()  # template_id 생성
        
        # 2. 질문 데이터 생성
        questions = []
        
        # 기본 정보 섹션
        questions.extend([
            {
                "section": QuestionnaireSection.BASIC,
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_code": "BASIC_001",
                "question_text": "성별을 선택해주세요",
                "order_index": 1,
                "is_required": True,
                "options": [
                    {"value": "male", "label": "남성"},
                    {"value": "female", "label": "여성"}
                ]
            },
            {
                "section": QuestionnaireSection.BASIC,
                "question_type": QuestionType.NUMBER,
                "question_code": "BASIC_002",
                "question_text": "만 나이를 입력해주세요",
                "question_subtext": "실제 나이를 입력해주세요",
                "order_index": 2,
                "is_required": True,
                "validation_rules": {"min": 1, "max": 120}
            },
            {
                "section": QuestionnaireSection.BASIC,
                "question_type": QuestionType.NUMBER,
                "question_code": "BASIC_003",
                "question_text": "키를 입력해주세요 (cm)",
                "order_index": 3,
                "is_required": True,
                "validation_rules": {"min": 50, "max": 250}
            },
            {
                "section": QuestionnaireSection.BASIC,
                "question_type": QuestionType.NUMBER,
                "question_code": "BASIC_004",
                "question_text": "체중을 입력해주세요 (kg)",
                "order_index": 4,
                "is_required": True,
                "validation_rules": {"min": 20, "max": 300}
            },
            {
                "section": QuestionnaireSection.BASIC,
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "question_code": "BASIC_005",
                "question_text": "방문 목적을 선택해주세요 (복수 선택 가능)",
                "order_index": 5,
                "is_required": True,
                "options": [
                    {"value": "weight_loss", "label": "체중 감량"},
                    {"value": "muscle_gain", "label": "근육 증가"},
                    {"value": "health_check", "label": "건강 검진"},
                    {"value": "fatigue", "label": "피로 개선"},
                    {"value": "stress", "label": "스트레스 관리"},
                    {"value": "nutrition", "label": "영양 상담"},
                    {"value": "other", "label": "기타"}
                ]
            },
            {
                "section": QuestionnaireSection.BASIC,
                "question_type": QuestionType.TEXT,
                "question_code": "BASIC_006",
                "question_text": "현재 복용 중인 약물이 있다면 적어주세요",
                "question_subtext": "없으면 '없음'이라고 적어주세요",
                "order_index": 6,
                "is_required": False
            },
            {
                "section": QuestionnaireSection.BASIC,
                "question_type": QuestionType.TEXT,
                "question_code": "BASIC_007",
                "question_text": "알레르기가 있다면 적어주세요",
                "question_subtext": "음식, 약물 알레르기 등",
                "order_index": 7,
                "is_required": False
            }
        ])
        
        # 핵심 건강 평가 섹션
        questions.extend([
            {
                "section": QuestionnaireSection.HEALTH_STATUS,
                "question_type": QuestionType.SCALE,
                "question_code": "HEALTH_001",
                "question_text": "최근 한 달간 수면의 질은 어떠셨나요?",
                "question_subtext": "0점(매우 나쁨) ~ 10점(매우 좋음)",
                "order_index": 10,
                "is_required": True,
                "validation_rules": {"min": 0, "max": 10},
                "ui_config": {"widget": "slider", "showLabels": True}
            },
            {
                "section": QuestionnaireSection.HEALTH_STATUS,
                "question_type": QuestionType.NUMBER,
                "question_code": "HEALTH_002",
                "question_text": "평균 수면 시간은 몇 시간인가요?",
                "order_index": 11,
                "is_required": True,
                "validation_rules": {"min": 0, "max": 24}
            },
            {
                "section": QuestionnaireSection.HEALTH_STATUS,
                "question_type": QuestionType.SCALE,
                "question_code": "HEALTH_003",
                "question_text": "현재 스트레스 수준은 어느 정도인가요?",
                "question_subtext": "0점(없음) ~ 10점(매우 심함)",
                "order_index": 12,
                "is_required": True,
                "validation_rules": {"min": 0, "max": 10},
                "ui_config": {"widget": "slider", "showLabels": True},
                "condition_logic": {
                    "trigger_conditions": {
                        "score": {"gte": 7},
                        "activate_sections": ["stress_mental"]
                    }
                }
            },
            {
                "section": QuestionnaireSection.HEALTH_STATUS,
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_code": "HEALTH_004",
                "question_text": "피로감은 주로 언제 느끼시나요?",
                "order_index": 13,
                "is_required": True,
                "options": [
                    {"value": "morning", "label": "아침"},
                    {"value": "afternoon", "label": "오후"},
                    {"value": "evening", "label": "저녁"},
                    {"value": "always", "label": "항상"},
                    {"value": "none", "label": "거의 없음"}
                ]
            },
            {
                "section": QuestionnaireSection.HEALTH_STATUS,
                "question_type": QuestionType.BODY_MAP,
                "question_code": "HEALTH_005",
                "question_text": "통증이 있는 부위를 표시해주세요",
                "question_subtext": "통증이 있는 모든 부위를 터치해주세요",
                "order_index": 14,
                "is_required": False,
                "ui_config": {"widget": "body_map", "allowMultiple": True}
            },
            {
                "section": QuestionnaireSection.HEALTH_STATUS,
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_code": "HEALTH_006",
                "question_text": "소화 상태는 어떠신가요?",
                "order_index": 15,
                "is_required": True,
                "options": [
                    {"value": "very_good", "label": "매우 좋음"},
                    {"value": "good", "label": "좋음"},
                    {"value": "normal", "label": "보통"},
                    {"value": "bad", "label": "나쁨"},
                    {"value": "very_bad", "label": "매우 나쁨"}
                ],
                "condition_logic": {
                    "trigger_conditions": {
                        "value": {"in": ["bad", "very_bad"]},
                        "activate_sections": ["digestive"]
                    }
                }
            },
            {
                "section": QuestionnaireSection.HEALTH_STATUS,
                "question_type": QuestionType.NUMBER,
                "question_code": "HEALTH_007",
                "question_text": "일주일에 운동은 몇 회 하시나요?",
                "order_index": 16,
                "is_required": True,
                "validation_rules": {"min": 0, "max": 7}
            }
        ])
        
        # 목표 설정 섹션
        questions.extend([
            {
                "section": QuestionnaireSection.GOALS,
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "question_code": "GOAL_001",
                "question_text": "개선하고 싶은 주요 목표를 선택해주세요 (최대 3개)",
                "order_index": 20,
                "is_required": True,
                "validation_rules": {"maxSelections": 3},
                "options": [
                    {"value": "weight_control", "label": "체중 조절"},
                    {"value": "body_composition", "label": "체성분 개선"},
                    {"value": "energy", "label": "활력 증진"},
                    {"value": "sleep_quality", "label": "수면 질 개선"},
                    {"value": "stress_management", "label": "스트레스 관리"},
                    {"value": "digestive_health", "label": "소화기 건강"},
                    {"value": "immune_system", "label": "면역력 강화"},
                    {"value": "skin_health", "label": "피부 건강"},
                    {"value": "cognitive_function", "label": "인지 기능 향상"}
                ]
            },
            {
                "section": QuestionnaireSection.GOALS,
                "question_type": QuestionType.TEXT,
                "question_code": "GOAL_002",
                "question_text": "기대하는 변화를 구체적으로 적어주세요",
                "order_index": 21,
                "is_required": False
            },
            {
                "section": QuestionnaireSection.GOALS,
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_code": "GOAL_003",
                "question_text": "센터 방문 가능 빈도는 어느 정도인가요?",
                "order_index": 22,
                "is_required": True,
                "options": [
                    {"value": "daily", "label": "매일"},
                    {"value": "3_times_week", "label": "주 3회 이상"},
                    {"value": "1_2_times_week", "label": "주 1-2회"},
                    {"value": "2_times_month", "label": "월 2회"},
                    {"value": "1_time_month", "label": "월 1회"},
                    {"value": "irregular", "label": "불규칙"}
                ]
            }
        ])
        
        # 스트레스/정신건강 모듈 (선택적)
        questions.extend([
            {
                "section": QuestionnaireSection.STRESS_MENTAL,
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_code": "STRESS_001",
                "question_text": "최근 2주간 우울감을 느낀 적이 있나요?",
                "order_index": 30,
                "is_required": False,
                "options": [
                    {"value": "never", "label": "전혀 없음"},
                    {"value": "few_days", "label": "며칠 정도"},
                    {"value": "half_days", "label": "절반 이상"},
                    {"value": "almost_everyday", "label": "거의 매일"}
                ]
            },
            {
                "section": QuestionnaireSection.STRESS_MENTAL,
                "question_type": QuestionType.SINGLE_CHOICE,
                "question_code": "STRESS_002",
                "question_text": "불안이나 초조함을 얼마나 자주 느끼시나요?",
                "order_index": 31,
                "is_required": False,
                "options": [
                    {"value": "never", "label": "전혀 없음"},
                    {"value": "sometimes", "label": "가끔"},
                    {"value": "often", "label": "자주"},
                    {"value": "always", "label": "항상"}
                ]
            }
        ])
        
        # Question 객체 생성 및 저장
        for q_data in questions:
            question = Question(
                template_id=template.template_id,
                section=q_data["section"],
                question_type=q_data["question_type"],
                question_code=q_data["question_code"],
                question_text=q_data["question_text"],
                question_subtext=q_data.get("question_subtext"),
                order_index=q_data["order_index"],
                is_required=q_data["is_required"],
                options=q_data.get("options"),
                validation_rules=q_data.get("validation_rules"),
                ui_config=q_data.get("ui_config"),
                condition_logic=q_data.get("condition_logic")
            )
            db.add(question)
        
        db.commit()
        print(f"문진 템플릿 '{template.name}' 및 {len(questions)}개 질문이 성공적으로 생성되었습니다.")
        
    except Exception as e:
        db.rollback()
        print(f"오류 발생: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_questionnaire_data()