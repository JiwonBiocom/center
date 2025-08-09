"""
문진 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """질문 유형"""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BODY_MAP = "body_map"


class QuestionnaireSection(str, Enum):
    """문진 섹션"""
    BASIC = "basic"
    HEALTH_STATUS = "health_status"
    GOALS = "goals"
    STRESS_MENTAL = "stress_mental"
    DIGESTIVE = "digestive"
    HORMONE_METABOLIC = "hormone"
    MUSCULOSKELETAL = "musculoskeletal"


# Option 스키마
class QuestionOption(BaseModel):
    """질문 선택지"""
    value: str
    label: str
    score: Optional[float] = None
    next_question: Optional[str] = None  # 조건부 다음 질문


# Question 스키마
class QuestionBase(BaseModel):
    """질문 기본 정보"""
    section: QuestionnaireSection
    question_type: QuestionType
    question_code: str
    question_text: str
    question_subtext: Optional[str] = None
    order_index: int
    is_required: bool = True
    options: Optional[List[QuestionOption]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    ui_config: Optional[Dict[str, Any]] = None
    condition_logic: Optional[Dict[str, Any]] = None


class QuestionCreate(QuestionBase):
    """질문 생성"""
    template_id: int


class QuestionUpdate(BaseModel):
    """질문 수정"""
    question_text: Optional[str] = None
    question_subtext: Optional[str] = None
    order_index: Optional[int] = None
    is_required: Optional[bool] = None
    options: Optional[List[QuestionOption]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    ui_config: Optional[Dict[str, Any]] = None


class Question(QuestionBase):
    """질문 응답"""
    question_id: int
    template_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Answer 스키마
class AnswerBase(BaseModel):
    """답변 기본 정보"""
    question_id: int
    answer_value: Optional[str] = None
    answer_number: Optional[float] = None
    answer_json: Optional[Union[Dict[str, Any], List[str]]] = None  # 리스트도 허용
    answer_date: Optional[datetime] = None
    time_spent_seconds: Optional[int] = None


class AnswerCreate(AnswerBase):
    """답변 생성"""
    pass


class Answer(AnswerBase):
    """답변 응답"""
    answer_id: int
    response_id: int
    answered_at: datetime
    question: Optional[Question] = None

    class Config:
        from_attributes = True


# QuestionnaireResponse 스키마
class QuestionnaireResponseBase(BaseModel):
    """문진 응답 기본 정보"""
    customer_id: int
    template_id: int
    device_id: Optional[str] = None
    app_version: Optional[str] = None


class QuestionnaireResponseCreate(QuestionnaireResponseBase):
    """문진 응답 생성"""
    pass


class QuestionnaireResponseUpdate(BaseModel):
    """문진 응답 업데이트"""
    is_completed: Optional[bool] = None
    completion_rate: Optional[float] = None
    completed_at: Optional[datetime] = None


class QuestionnaireResponse(QuestionnaireResponseBase):
    """문진 응답"""
    response_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    is_completed: bool = False
    completion_rate: float = 0.0
    answers: List[Answer] = []

    class Config:
        from_attributes = True


# 문진 템플릿 스키마
class QuestionnaireTemplateBase(BaseModel):
    """문진 템플릿 기본 정보"""
    name: str
    description: Optional[str] = None
    version: str = "1.0"
    is_active: bool = True


class QuestionnaireTemplateCreate(QuestionnaireTemplateBase):
    """문진 템플릿 생성"""
    pass


class QuestionnaireTemplate(QuestionnaireTemplateBase):
    """문진 템플릿"""
    template_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    questions: List[Question] = []

    class Config:
        from_attributes = True


# 문진 진행 상태
class QuestionnaireProgress(BaseModel):
    """문진 진행 상태"""
    response_id: int
    current_section: QuestionnaireSection
    answered_questions: int
    total_questions: int
    completion_rate: float
    next_question: Optional[Question] = None
    estimated_time_remaining: int  # 예상 남은 시간 (초)


# 문진 분석 결과
class HealthScore(BaseModel):
    """건강 점수"""
    category: str
    score: float = Field(..., ge=0, le=100)
    description: str
    recommendations: List[str] = []


class QuestionnaireAnalysisResult(BaseModel):
    """문진 분석 결과"""
    response_id: int
    overall_health_score: float = Field(..., ge=0, le=100)
    health_scores: List[HealthScore]
    recommended_services: List[Dict[str, Any]]
    recommended_supplements: List[Dict[str, Any]]
    risk_factors: List[str] = []
    improvement_areas: List[str] = []
    analyzed_at: datetime


# 문진 시작 요청
class StartQuestionnaireRequest(BaseModel):
    """문진 시작 요청"""
    customer_id: int
    template_id: int = 1  # 기본 템플릿
    device_id: str
    app_version: str = "1.0.0"


# 답변 제출
class SubmitAnswerRequest(BaseModel):
    """답변 제출 요청"""
    question_id: int
    answer: Union[str, float, List[str], Dict[str, Any], None]
    time_spent_seconds: int = 0

    @validator('answer')
    def validate_answer(cls, v, values):
        """답변 유효성 검사"""
        # 실제 구현에서는 question_type에 따라 검증
        return v


# 일괄 답변 제출
class SubmitAnswersBatchRequest(BaseModel):
    """여러 답변 일괄 제출"""
    answers: List[SubmitAnswerRequest]


# 문진 완료 요청
class CompleteQuestionnaireRequest(BaseModel):
    """문진 완료 요청"""
    response_id: int
    force_complete: bool = False  # 필수 답변 미완료 시 강제 완료