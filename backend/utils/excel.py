"""엑셀 파일 처리 유틸리티"""
import io
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session


class ExcelHandler:
    """엑셀 파일 가져오기/내보내기 핸들러"""

    # 파일 업로드 제한
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.xlsm'}  # .xlsm 형식 추가
    MAX_ROWS = 10000  # 최대 행 수 제한

    @staticmethod
    def clean_phone(phone: str) -> Optional[str]:
        """전화번호 정제"""
        if not phone or pd.isna(phone):
            return None

        # 숫자만 추출
        phone_str = str(phone)
        numbers = re.sub(r'[^0-9]', '', phone_str)

        # 한국 전화번호 형식으로 변환
        if len(numbers) == 11 and numbers.startswith('010'):
            return f"{numbers[:3]}-{numbers[3:7]}-{numbers[7:]}"
        elif len(numbers) == 10 and numbers.startswith('010'):
            return f"{numbers[:3]}-{numbers[3:6]}-{numbers[6:]}"

        return numbers if numbers else None

    @staticmethod
    def parse_date(date_value: Any) -> Optional[datetime]:
        """날짜 파싱"""
        if not date_value or pd.isna(date_value):
            return None

        # pandas Timestamp 처리
        if isinstance(date_value, pd.Timestamp):
            return date_value.to_pydatetime()

        # datetime 객체인 경우
        if isinstance(date_value, datetime):
            return date_value

        # 엑셀 숫자 형식 날짜 처리 (Excel serial date)
        if isinstance(date_value, (int, float)):
            try:
                # Excel date serial number를 datetime으로 변환
                # Excel의 기준일은 1900-01-01 (Windows) 또는 1904-01-01 (Mac)
                # 주로 Windows 형식 사용
                excel_base_date = datetime(1900, 1, 1)
                # Excel에서 1900-02-29를 잘못 처리하는 버그 보정
                if date_value > 59:
                    date_value -= 1
                return excel_base_date + pd.Timedelta(days=date_value - 1)
            except:
                pass

        # 문자열 날짜 처리
        if isinstance(date_value, str):
            # 공백 제거 및 정규화
            date_value = date_value.strip()
            
            # 한글 제거 및 정규화
            date_value = date_value.replace('년', '-').replace('월', '-').replace('일', '')
            date_value = date_value.replace('.', '-').replace('/', '-')
            # 연속된 구분자 제거
            date_value = re.sub(r'-+', '-', date_value)
            date_value = date_value.strip('-')

            # 더 많은 날짜 형식 지원
            date_formats = [
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%d/%m/%Y',
                '%Y.%m.%d',
                '%d.%m.%Y',
                '%Y년 %m월 %d일',
                '%Y년%m월%d일',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d %H:%M:%S',
                '%d-%m-%Y',
                '%d.%m.%Y',
                '%m/%d/%Y',
                '%m-%d-%Y',
                # 추가 형식들
                '%y-%m-%d',  # 2자리 연도
                '%y/%m/%d',
                '%d-%m-%y',
                '%d/%m/%y',
                '%Y%m%d',     # 구분자 없는 형식
                '%y%m%d',
                '%m-%d-%y',
                '%m/%d/%y',
                # 한국식 추가
                '%Y.%m.%d.',
                '%Y. %m. %d.',
                '%Y. %m. %d',
                # 엑셀에서 자주 나타나는 형식
                '%-m/%-d/%Y',  # 0 패딩 없는 월/일
                '%-d/%-m/%Y',
                '%Y-%-m-%-d',
                '%Y/%-m/%-d'
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue

        # pandas의 to_datetime 함수로 최종 시도 (더 유연한 옵션 사용)
        try:
            result = pd.to_datetime(date_value, dayfirst=False, yearfirst=True)
            if pd.notna(result):
                return result.to_pydatetime() if hasattr(result, 'to_pydatetime') else result
        except:
            # dayfirst=True로 재시도
            try:
                result = pd.to_datetime(date_value, dayfirst=True, yearfirst=False)
                if pd.notna(result):
                    return result.to_pydatetime() if hasattr(result, 'to_pydatetime') else result
            except:
                pass

        return None

    @staticmethod
    def parse_year(date_value: Any) -> Optional[int]:
        """날짜에서 연도만 추출"""
        if not date_value or pd.isna(date_value):
            return None

        # 숫자인 경우 (연도만 입력된 경우)
        if isinstance(date_value, (int, float)):
            year = int(date_value)
            if 1900 <= year <= 2100:
                return year
            return None

        # 날짜 파싱 시도
        parsed_date = ExcelHandler.parse_date(date_value)
        if parsed_date:
            return parsed_date.year

        # 문자열에서 4자리 연도 찾기
        if isinstance(date_value, str):
            import re
            year_match = re.search(r'(19|20)\d{2}', str(date_value))
            if year_match:
                return int(year_match.group())

        return None

    @staticmethod
    def clean_string(value: Any) -> Optional[str]:
        """문자열 정제"""
        if not value or pd.isna(value):
            return None
        return str(value).strip()

    @staticmethod
    def clean_number(value: Any) -> Optional[float]:
        """숫자 정제"""
        if not value or pd.isna(value):
            return None

        try:
            # 쉼표 제거
            if isinstance(value, str):
                value = value.replace(',', '')
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    async def read_excel_file(file: UploadFile) -> pd.DataFrame:
        """엑셀 파일 읽기"""
        # 파일 확장자 검증
        if not file.filename:
            raise HTTPException(status_code=400, detail="파일명이 없습니다")

        file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_ext not in ExcelHandler.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 형식입니다. {', '.join(ExcelHandler.ALLOWED_EXTENSIONS)}만 가능합니다"
            )

        try:
            # 파일 크기 확인을 위해 먼저 읽기
            contents = await file.read()
            file_size = len(contents)

            # 파일 크기 제한 확인
            if file_size > ExcelHandler.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"파일 크기가 {ExcelHandler.MAX_FILE_SIZE // (1024*1024)}MB를 초과합니다"
                )

            # 빈 파일 확인
            if file_size == 0:
                raise HTTPException(status_code=400, detail="빈 파일입니다")

            # 엑셀 파일 읽기
            df = pd.read_excel(io.BytesIO(contents))

            # 행 수 제한 확인
            if len(df) > ExcelHandler.MAX_ROWS:
                raise HTTPException(
                    status_code=400,
                    detail=f"데이터가 너무 많습니다. 최대 {ExcelHandler.MAX_ROWS}행까지만 가능합니다"
                )

            # 빈 데이터프레임 확인
            if df.empty:
                raise HTTPException(status_code=400, detail="엑셀 파일에 데이터가 없습니다")

            return df
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"엑셀 파일 읽기 실패: {str(e)}")

    @staticmethod
    def create_excel_response(df: pd.DataFrame, filename: str) -> bytes:
        """DataFrame을 엑셀 파일로 변환"""
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')

            # 열 너비 자동 조정
            worksheet = writer.sheets['Sheet1']
            for column in df:
                column_length = max(df[column].astype(str).map(len).max(), len(column))
                col_idx = df.columns.get_loc(column)
                worksheet.column_dimensions[chr(65 + col_idx)].width = min(column_length + 2, 50)

        output.seek(0)
        return output.getvalue()


class ExcelValidator:
    """엑셀 데이터 검증"""

    @staticmethod
    def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
        """필수 컬럼 검증"""
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
            )

    @staticmethod
    def validate_data_types(df: pd.DataFrame, column_types: Dict[str, type]) -> None:
        """데이터 타입 검증"""
        for column, expected_type in column_types.items():
            if column not in df.columns:
                continue

            if expected_type == datetime:
                # 날짜 타입 검증
                try:
                    pd.to_datetime(df[column])
                except:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{column} 컬럼의 날짜 형식이 올바르지 않습니다"
                    )
            elif expected_type in (int, float):
                # 숫자 타입 검증
                try:
                    pd.to_numeric(df[column])
                except:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{column} 컬럼에 숫자가 아닌 값이 있습니다"
                    )

    @staticmethod
    def check_duplicates(df: pd.DataFrame, key_columns: List[str]) -> List[Dict[str, Any]]:
        """중복 데이터 확인"""
        duplicates = df[df.duplicated(subset=key_columns, keep=False)]

        if not duplicates.empty:
            duplicate_records = []
            for _, row in duplicates.iterrows():
                duplicate_records.append({
                    col: row[col] for col in key_columns
                })
            return duplicate_records

        return []
