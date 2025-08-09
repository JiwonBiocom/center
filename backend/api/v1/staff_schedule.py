from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import json

from core.database import get_db
from models.staff_schedule import StaffSchedule
from schemas.staff_schedule import (
    StaffScheduleCreate,
    StaffScheduleUpdate,
    StaffScheduleResponse,
    WeeklyScheduleData
)

router = APIRouter()

def get_week_start_date(target_date: date = None) -> date:
    """주어진 날짜가 속한 주의 월요일 반환"""
    if target_date is None:
        target_date = date.today()

    # 월요일을 주의 시작으로 (weekday() 0=월요일)
    days_since_monday = target_date.weekday()
    week_start = target_date - timedelta(days=days_since_monday)
    return week_start

@router.get("/current", response_model=StaffScheduleResponse)
def get_current_week_schedule(db: Session = Depends(get_db)):
    """현재 주 근무표 조회"""
    week_start = get_week_start_date()

    schedule = db.query(StaffSchedule).filter(
        StaffSchedule.week_start_date == week_start,
        StaffSchedule.is_active == True
    ).first()

    if not schedule:
        # 기본 근무표 생성
        default_schedule = get_default_schedule_data()

        new_schedule = StaffSchedule(
            week_start_date=week_start,
            schedule_data=json.dumps(default_schedule, ensure_ascii=False),
            created_by="system"
        )
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
        schedule = new_schedule

    # JSON 데이터 파싱
    schedule_dict = schedule.__dict__.copy()
    schedule_dict['schedule_data'] = json.loads(schedule.schedule_data)

    return StaffScheduleResponse(**schedule_dict)

@router.get("/week/{week_start_date}", response_model=StaffScheduleResponse)
def get_week_schedule(
    week_start_date: date,
    db: Session = Depends(get_db)
):
    """특정 주 근무표 조회"""
    schedule = db.query(StaffSchedule).filter(
        StaffSchedule.week_start_date == week_start_date,
        StaffSchedule.is_active == True
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="해당 주의 근무표를 찾을 수 없습니다")

    # JSON 데이터 파싱
    schedule_dict = schedule.__dict__.copy()
    schedule_dict['schedule_data'] = json.loads(schedule.schedule_data)

    return StaffScheduleResponse(**schedule_dict)

@router.post("/", response_model=StaffScheduleResponse)
@router.post("", response_model=StaffScheduleResponse)  # non-trailing slash 버전
def create_schedule(
    schedule_data: StaffScheduleCreate,
    db: Session = Depends(get_db)
):
    """새 근무표 생성"""
    # 기존 근무표가 있는지 확인
    existing = db.query(StaffSchedule).filter(
        StaffSchedule.week_start_date == schedule_data.week_start_date,
        StaffSchedule.is_active == True
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="해당 주의 근무표가 이미 존재합니다")

    new_schedule = StaffSchedule(
        week_start_date=schedule_data.week_start_date,
        schedule_data=json.dumps(schedule_data.schedule_data, ensure_ascii=False),
        created_by=schedule_data.created_by
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    # JSON 데이터 파싱
    schedule_dict = new_schedule.__dict__.copy()
    schedule_dict['schedule_data'] = json.loads(new_schedule.schedule_data)

    return StaffScheduleResponse(**schedule_dict)

@router.put("/{schedule_id}", response_model=StaffScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule_update: StaffScheduleUpdate,
    db: Session = Depends(get_db)
):
    """근무표 수정"""
    schedule = db.query(StaffSchedule).filter(
        StaffSchedule.schedule_id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="근무표를 찾을 수 없습니다")

    if schedule_update.schedule_data is not None:
        schedule.schedule_data = json.dumps(schedule_update.schedule_data, ensure_ascii=False)

    if schedule_update.updated_by is not None:
        schedule.updated_by = schedule_update.updated_by

    schedule.updated_at = datetime.now()

    db.commit()
    db.refresh(schedule)

    # JSON 데이터 파싱
    schedule_dict = schedule.__dict__.copy()
    schedule_dict['schedule_data'] = json.loads(schedule.schedule_data)

    return StaffScheduleResponse(**schedule_dict)

@router.get("/", response_model=List[StaffScheduleResponse])
def get_schedules(
    start_date: Optional[date] = Query(None, description="조회 시작일"),
    end_date: Optional[date] = Query(None, description="조회 종료일"),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db)
):
    """근무표 목록 조회"""
    query = db.query(StaffSchedule).filter(StaffSchedule.is_active == True)

    if start_date:
        query = query.filter(StaffSchedule.week_start_date >= start_date)
    if end_date:
        query = query.filter(StaffSchedule.week_start_date <= end_date)

    schedules = query.order_by(StaffSchedule.week_start_date.desc()).limit(limit).all()

    result = []
    for schedule in schedules:
        schedule_dict = schedule.__dict__.copy()
        schedule_dict['schedule_data'] = json.loads(schedule.schedule_data)
        result.append(StaffScheduleResponse(**schedule_dict))

    return result

def get_default_schedule_data():
    """기본 근무표 데이터"""
    return {
        "staff_info": {
            "수경": {
                "월": "",
                "화": "센터 근무",
                "수": "센터 근무",
                "목": "센터 근무",
                "금": "센터 근무\n(8시퇴근)",
                "토": "센터 근무",
                "일": ""
            },
            "예림": {
                "월": "예림\n(풀타임)",
                "화": "예림",
                "수": "예림",
                "목": "예림",
                "금": "",
                "토": "",
                "일": "예림"
            },
            "승우": {
                "월": "승우\n(지원)",
                "화": "",
                "수": "",
                "목": "",
                "금": "승우\n(야간)",
                "토": "승우",
                "일": ""
            },
            "사무실": {
                "월": "승우\n(9시반~6시반)",
                "화": "승우",
                "수": "승우",
                "목": "",
                "금": "승우",
                "토": "승우",
                "일": ""
            }
        },
        "time_table": {
            "10": {
                "월": "예림\n(승우 지원)",
                "화": "수경",
                "수": "수경",
                "목": "수경",
                "금": "수경\n(승우 지원)",
                "토": "수경/승우",
                "일": "예림"
            },
            "11": {
                "월": "예림\n(승우 지원)",
                "화": "수경",
                "수": "수경",
                "목": "수경",
                "금": "수경\n(승우 지원)",
                "토": "수경/승우",
                "일": "예림"
            },
            "12": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경",
                "금": "수경\n(승우 지원)",
                "토": "수경/승우",
                "일": "예림"
            },
            "13": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경/예림",
                "금": "수경\n(승우 지원)",
                "토": "수경/승우",
                "일": "예림"
            },
            "14": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경/예림",
                "금": "수경\n(승우 지원)",
                "토": "수경/승우",
                "일": "예림"
            },
            "15": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경/예림",
                "금": "수경\n(승우 지원)",
                "토": "수경/승우",
                "일": "예림"
            },
            "16": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경/예림",
                "금": "수경\n(승우 지원)",
                "토": "수경/승우",
                "일": "예림"
            },
            "17": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경/예림",
                "금": "수경\n(승우 지원)",
                "토": "수경",
                "일": "예림"
            },
            "18": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경/예림",
                "금": "수경\n(승우 지원)",
                "토": "수경",
                "일": "예림"
            },
            "19": {
                "월": "예림\n(승우 지원)",
                "화": "수경/예림",
                "수": "수경/예림",
                "목": "수경/예림",
                "금": "수경\n(승우 지원)",
                "토": "-",
                "일": ""
            },
            "20": {
                "월": "예림",
                "화": "예림",
                "수": "예림",
                "목": "예림",
                "금": "승우",
                "토": "",
                "일": ""
            },
            "21": {
                "월": "예림",
                "화": "예림",
                "수": "예림",
                "목": "예림",
                "금": "승우",
                "토": "",
                "일": ""
            }
        }
    }
