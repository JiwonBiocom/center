"""
문진 관련 API 엔드포인트
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime

from core.database import get_db
from core.auth import get_current_user
from models.user import User
from models.questionnaire import (
    QuestionnaireTemplate, Question, QuestionnaireResponse, 
    Answer, QuestionnaireSection, QuestionType
)
from schemas.questionnaire import (
    QuestionnaireTemplate as QuestionnaireTemplateSchema,
    Question as QuestionSchema,
    StartQuestionnaireRequest,
    QuestionnaireResponse as QuestionnaireResponseSchema,
    QuestionnaireProgress,
    SubmitAnswerRequest,
    SubmitAnswersBatchRequest,
    CompleteQuestionnaireRequest,
    Answer as AnswerSchema
)

router = APIRouter(
    prefix="/questionnaire",
    tags=["questionnaire"]
)


@router.get("/templates", response_model=List[QuestionnaireTemplateSchema])
def get_questionnaire_templates(
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    문진 템플릿 목록 조회
    """
    query = db.query(QuestionnaireTemplate)
    
    if is_active is not None:
        query = query.filter(QuestionnaireTemplate.is_active == is_active)
    
    templates = query.all()
    return templates


@router.get("/templates/{template_id}", response_model=QuestionnaireTemplateSchema)
def get_questionnaire_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 문진 템플릿 상세 조회 (질문 포함)
    """
    template = db.query(QuestionnaireTemplate)\
        .options(joinedload(QuestionnaireTemplate.questions))\
        .filter(QuestionnaireTemplate.template_id == template_id)\
        .first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문진 템플릿을 찾을 수 없습니다."
        )
    
    # 질문을 순서대로 정렬
    template.questions.sort(key=lambda x: x.order_index)
    
    return template


@router.post("/start", response_model=QuestionnaireResponseSchema)
def start_questionnaire(
    request: StartQuestionnaireRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    문진 시작
    """
    # 템플릿 확인
    template = db.query(QuestionnaireTemplate)\
        .filter(QuestionnaireTemplate.template_id == request.template_id)\
        .first()
    
    if not template or not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효한 문진 템플릿을 찾을 수 없습니다."
        )
    
    # 기존 미완료 문진 확인
    existing_response = db.query(QuestionnaireResponse)\
        .filter(
            and_(
                QuestionnaireResponse.customer_id == request.customer_id,
                QuestionnaireResponse.template_id == request.template_id,
                QuestionnaireResponse.is_completed == False
            )
        )\
        .first()
    
    if existing_response:
        # 기존 미완료 문진이 있으면 계속 진행
        return existing_response
    
    # 새 문진 응답 생성
    new_response = QuestionnaireResponse(
        customer_id=request.customer_id,
        template_id=request.template_id,
        device_id=request.device_id,
        app_version=request.app_version
    )
    
    db.add(new_response)
    db.commit()
    db.refresh(new_response)
    
    return new_response


@router.get("/responses/{response_id}", response_model=QuestionnaireResponseSchema)
def get_questionnaire_response(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    문진 응답 조회
    """
    response = db.query(QuestionnaireResponse)\
        .options(
            joinedload(QuestionnaireResponse.answers)
            .joinedload(Answer.question)
        )\
        .filter(QuestionnaireResponse.response_id == response_id)\
        .first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문진 응답을 찾을 수 없습니다."
        )
    
    return response


@router.get("/responses/{response_id}/progress", response_model=QuestionnaireProgress)
def get_questionnaire_progress(
    response_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    문진 진행 상태 조회
    """
    response = db.query(QuestionnaireResponse)\
        .filter(QuestionnaireResponse.response_id == response_id)\
        .first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문진 응답을 찾을 수 없습니다."
        )
    
    # 전체 질문 수
    total_questions = db.query(Question)\
        .filter(Question.template_id == response.template_id)\
        .count()
    
    # 답변한 질문 수
    answered_questions = db.query(Answer)\
        .filter(Answer.response_id == response_id)\
        .count()
    
    # 다음 질문 찾기
    answered_question_ids = db.query(Answer.question_id)\
        .filter(Answer.response_id == response_id)\
        .subquery()
    
    next_question = db.query(Question)\
        .filter(
            and_(
                Question.template_id == response.template_id,
                ~Question.question_id.in_(answered_question_ids)
            )
        )\
        .order_by(Question.order_index)\
        .first()
    
    # 현재 섹션 결정
    current_section = QuestionnaireSection.BASIC
    if next_question:
        current_section = next_question.section
    
    # 예상 남은 시간 계산 (질문당 평균 30초)
    remaining_questions = total_questions - answered_questions
    estimated_time_remaining = remaining_questions * 30
    
    return QuestionnaireProgress(
        response_id=response_id,
        current_section=current_section,
        answered_questions=answered_questions,
        total_questions=total_questions,
        completion_rate=(answered_questions / total_questions * 100) if total_questions > 0 else 0,
        next_question=next_question,
        estimated_time_remaining=estimated_time_remaining
    )


@router.post("/responses/{response_id}/answers", response_model=AnswerSchema)
def submit_answer(
    response_id: int,
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    단일 답변 제출
    """
    # 응답 확인
    response = db.query(QuestionnaireResponse)\
        .filter(QuestionnaireResponse.response_id == response_id)\
        .first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문진 응답을 찾을 수 없습니다."
        )
    
    if response.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 완료된 문진입니다."
        )
    
    # 질문 확인
    question = db.query(Question)\
        .filter(Question.question_id == request.question_id)\
        .first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="질문을 찾을 수 없습니다."
        )
    
    # 기존 답변 확인 (중복 방지)
    existing_answer = db.query(Answer)\
        .filter(
            and_(
                Answer.response_id == response_id,
                Answer.question_id == request.question_id
            )
        )\
        .first()
    
    if existing_answer:
        # 기존 답변 업데이트
        answer = existing_answer
    else:
        # 새 답변 생성
        answer = Answer(
            response_id=response_id,
            question_id=request.question_id,
            time_spent_seconds=request.time_spent_seconds
        )
        db.add(answer)
    
    # 답변 값 설정 (질문 유형에 따라)
    if question.question_type in [QuestionType.TEXT, QuestionType.SINGLE_CHOICE]:
        answer.answer_value = str(request.answer) if request.answer else None
    elif question.question_type in [QuestionType.NUMBER, QuestionType.SCALE]:
        answer.answer_number = float(request.answer) if request.answer else None
    elif question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.BODY_MAP]:
        # 배열 답변을 딕셔너리로 감싸서 저장
        if request.answer:
            if isinstance(request.answer, list):
                answer.answer_json = {"selected": request.answer}
            else:
                answer.answer_json = request.answer
        else:
            answer.answer_json = None
    elif question.question_type == QuestionType.DATE:
        answer.answer_date = request.answer if request.answer else None
    
    # 완료율 업데이트
    total_questions = db.query(Question)\
        .filter(Question.template_id == response.template_id)\
        .count()
    
    answered_questions = db.query(Answer)\
        .filter(Answer.response_id == response_id)\
        .count()
    
    if not existing_answer:
        answered_questions += 1
    
    response.completion_rate = (answered_questions / total_questions * 100) if total_questions > 0 else 0
    
    db.commit()
    db.refresh(answer)
    
    # 질문 정보 포함하여 반환
    answer.question = question
    
    return answer


@router.post("/responses/{response_id}/answers/batch", response_model=List[AnswerSchema])
def submit_answers_batch(
    response_id: int,
    request: SubmitAnswersBatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    여러 답변 일괄 제출 (오프라인 동기화용)
    """
    answers = []
    
    for answer_request in request.answers:
        try:
            answer = submit_answer(
                response_id=response_id,
                request=answer_request,
                db=db,
                current_user=current_user
            )
            answers.append(answer)
        except HTTPException as e:
            # 개별 답변 실패 시 계속 진행
            print(f"답변 제출 실패: {e.detail}")
            continue
    
    return answers


@router.post("/responses/{response_id}/complete")
def complete_questionnaire(
    response_id: int,
    request: CompleteQuestionnaireRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    문진 완료 처리
    """
    response = db.query(QuestionnaireResponse)\
        .filter(QuestionnaireResponse.response_id == response_id)\
        .first()
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문진 응답을 찾을 수 없습니다."
        )
    
    if response.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 완료된 문진입니다."
        )
    
    # 필수 질문 답변 확인
    if not request.force_complete:
        required_questions = db.query(Question)\
            .filter(
                and_(
                    Question.template_id == response.template_id,
                    Question.is_required == True
                )
            )\
            .all()
        
        answered_question_ids = db.query(Answer.question_id)\
            .filter(Answer.response_id == response_id)\
            .all()
        answered_question_ids = [id[0] for id in answered_question_ids]
        
        missing_required = [
            q for q in required_questions 
            if q.question_id not in answered_question_ids
        ]
        
        if missing_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"필수 질문 {len(missing_required)}개가 답변되지 않았습니다."
            )
    
    # 완료 처리
    response.is_completed = True
    response.completed_at = datetime.now()
    response.completion_rate = 100.0
    
    db.commit()
    
    # TODO: AI 분석 트리거
    # analyze_questionnaire.delay(response_id)
    
    return {
        "message": "문진이 완료되었습니다.",
        "response_id": response_id,
        "completed_at": response.completed_at
    }


@router.get("/customers/{customer_id}/responses", response_model=List[QuestionnaireResponseSchema])
def get_customer_questionnaire_responses(
    customer_id: int,
    is_completed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    특정 고객의 문진 응답 목록 조회 (답변 포함)
    """
    query = db.query(QuestionnaireResponse)\
        .filter(QuestionnaireResponse.customer_id == customer_id)\
        .options(
            joinedload(QuestionnaireResponse.answers)
            .joinedload(Answer.question)
        )
    
    if is_completed is not None:
        query = query.filter(QuestionnaireResponse.is_completed == is_completed)
    
    responses = query.order_by(QuestionnaireResponse.started_at.desc()).all()
    
    return responses