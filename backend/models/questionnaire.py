"""
문진 관련 데이터베이스 모델
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from core.database import Base


class QuestionType(str, Enum):
    """질문 유형"""
    SINGLE_CHOICE = "single_choice"     # 단일 선택
    MULTIPLE_CHOICE = "multiple_choice" # 다중 선택
    SCALE = "scale"                     # 척도 (0-10)
    TEXT = "text"                       # 텍스트 입력
    NUMBER = "number"                   # 숫자 입력
    DATE = "date"                       # 날짜 선택
    BODY_MAP = "body_map"              # 신체 부위 선택


class QuestionnaireSection(str, Enum):
    """문진 섹션 구분"""
    BASIC = "basic"                     # 기본 정보
    HEALTH_STATUS = "health_status"     # 핵심 건강 평가
    GOALS = "goals"                     # 목표 설정
    STRESS_MENTAL = "stress_mental"     # 스트레스/정신건강
    DIGESTIVE = "digestive"             # 소화기 건강
    HORMONE_METABOLIC = "hormone"       # 호르몬/대사
    MUSCULOSKELETAL = "musculoskeletal" # 근골격계


class QuestionnaireTemplate(Base):
    """문진 템플릿"""
    __tablename__ = "questionnaire_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(20), nullable=False, default="1.0")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    questions = relationship("Question", back_populates="template", cascade="all, delete-orphan")
    responses = relationship("QuestionnaireResponse", back_populates="template")


class Question(Base):
    """문진 질문"""
    __tablename__ = "questions"

    question_id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("questionnaire_templates.template_id"))
    section = Column(SQLEnum(QuestionnaireSection), nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    question_code = Column(String(50), unique=True, nullable=False)  # 예: BASIC_001
    question_text = Column(Text, nullable=False)
    question_subtext = Column(Text)  # 부가 설명
    
    # 질문 순서 및 조건
    order_index = Column(Integer, nullable=False)
    is_required = Column(Boolean, default=True)
    condition_logic = Column(JSON)  # 조건부 표시 로직
    
    # 답변 옵션 (선택형 질문용)
    options = Column(JSON)  # [{value: "1", label: "예", score: 1}, ...]
    
    # 유효성 검사 규칙
    validation_rules = Column(JSON)  # {min: 0, max: 10, pattern: "..."}
    
    # UI 힌트
    ui_config = Column(JSON)  # {widget: "slider", showLabels: true, ...}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    template = relationship("QuestionnaireTemplate", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


class QuestionnaireResponse(Base):
    """문진 응답 세션"""
    __tablename__ = "questionnaire_responses"

    response_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    template_id = Column(Integer, ForeignKey("questionnaire_templates.template_id"))
    inbody_record_id = Column(Integer, ForeignKey("inbody_records.record_id"), nullable=True)  # 인바디 측정 연결
    
    # 세션 정보
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    is_completed = Column(Boolean, default=False)
    completion_rate = Column(Float, default=0.0)  # 완료율 (0-100)
    
    # 디바이스 정보
    device_id = Column(String(100))
    app_version = Column(String(20))
    
    # 분석 결과
    ai_analysis = Column(JSON)  # AI 분석 결과
    health_scores = Column(JSON)  # 건강 점수
    recommendations = Column(JSON)  # 추천 사항
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", backref="questionnaire_responses")
    template = relationship("QuestionnaireTemplate", back_populates="responses")
    answers = relationship("Answer", back_populates="response", cascade="all, delete-orphan")
    inbody_record = relationship("InBodyRecord", backref="questionnaire_response", uselist=False)


class Answer(Base):
    """개별 답변"""
    __tablename__ = "answers"

    answer_id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("questionnaire_responses.response_id"))
    question_id = Column(Integer, ForeignKey("questions.question_id"))
    
    # 답변 값 (타입에 따라 다른 필드 사용)
    answer_value = Column(Text)  # 텍스트, 단일 선택
    answer_number = Column(Float)  # 숫자, 척도
    answer_json = Column(JSON)  # 다중 선택, 신체 부위 맵
    answer_date = Column(DateTime)  # 날짜
    
    # 메타데이터
    answered_at = Column(DateTime(timezone=True), server_default=func.now())
    time_spent_seconds = Column(Integer)  # 답변 소요 시간
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    response = relationship("QuestionnaireResponse", back_populates="answers")
    question = relationship("Question", back_populates="answers")


class QuestionnaireAnalysis(Base):
    """문진 분석 결과 (추후 AI 분석용)"""
    __tablename__ = "questionnaire_analyses"

    analysis_id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("questionnaire_responses.response_id"))
    
    # 건강 점수
    overall_health_score = Column(Float)
    body_composition_score = Column(Float)
    metabolic_health_score = Column(Float)
    stress_score = Column(Float)
    sleep_score = Column(Float)
    nutrition_score = Column(Float)
    
    # AI 추천
    recommended_services = Column(JSON)  # 추천 서비스 목록
    recommended_supplements = Column(JSON)  # 추천 영양제
    recommended_diet = Column(JSON)  # 추천 식단
    
    # 상세 분석
    detailed_analysis = Column(JSON)  # 상세 분석 결과
    risk_factors = Column(JSON)  # 위험 요인
    improvement_areas = Column(JSON)  # 개선 필요 영역
    
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    response = relationship("QuestionnaireResponse", backref="analysis", uselist=False)