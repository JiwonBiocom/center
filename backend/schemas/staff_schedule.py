from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Dict, Any
import json

class StaffScheduleBase(BaseModel):
    week_start_date: date
    schedule_data: Dict[str, Any]

class StaffScheduleCreate(StaffScheduleBase):
    created_by: Optional[str] = None

class StaffScheduleUpdate(BaseModel):
    schedule_data: Optional[Dict[str, Any]] = None
    updated_by: Optional[str] = None

class StaffScheduleResponse(StaffScheduleBase):
    schedule_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True

class WeeklyScheduleData(BaseModel):
    """주간 근무표 데이터 구조"""
    staff_info: Dict[str, Dict[str, str]]  # 직원별 근무 정보
    time_table: Dict[str, Dict[str, str]]  # 시간별 근무표
    
    class Config:
        schema_extra = {
            "example": {
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
                        "월": "풀타임",
                        "화": "예림",
                        "수": "예림",
                        "목": "예림",
                        "금": "",
                        "토": "",
                        "일": "예림"
                    },
                    "승우": {
                        "월": "지원",
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
                    }
                }
            }
        }