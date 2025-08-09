"""결제 엑셀 업로드 기능"""
from fastapi import HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, text
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import io
import re

from core.database import get_db
from models.payment import Payment as PaymentModel
from models.customer import Customer as CustomerModel
from schemas.payment import PaymentCreate
from api.v1.payments import router


def parse_korean_date(date_value) -> datetime:
    """한국어 날짜 형식 파싱 (예: 2025.05.27 또는 2025-05-27)"""
    if pd.isna(date_value) or not date_value:
        return None

    # pandas Timestamp나 datetime 객체인 경우
    if hasattr(date_value, 'date'):
        return date_value.date()

    # 문자열로 변환해서 처리
    date_str = str(date_value).strip()

    # 다양한 날짜 형식 처리
    for fmt in ['%Y.%m.%d', '%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%d %H:%M:%S']:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue

    return None


def clean_phone_number(phone: str) -> str:
    """전화번호 형식 정리"""
    if pd.isna(phone) or not phone:
        return ""

    # 숫자만 추출
    phone = re.sub(r'\D', '', str(phone))

    # 한국 휴대폰 번호 형식으로 변환
    if len(phone) == 11 and phone.startswith('010'):
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

    return phone


def parse_amount(amount: Any) -> float:
    """금액 파싱"""
    if pd.isna(amount) or amount == '':
        return 0.0

    # 문자열인 경우 쉼표 제거
    if isinstance(amount, str):
        amount = amount.replace(',', '').replace('원', '').strip()

    try:
        return float(amount)
    except:
        return 0.0


@router.post("/import/excel")
@router.post("/import/excel/")
async def import_payments_from_excel(
    file: UploadFile = File(...),
    sheet: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """엑셀 파일에서 결제 데이터 가져오기"""
    try:
        # 파일 타입 검증
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="엑셀 파일(.xlsx, .xls)만 업로드 가능합니다."
            )

        # 파일 읽기
        contents = await file.read()
        excel_file = io.BytesIO(contents)

        # 엑셀 파일의 모든 시트 확인
        all_sheets = pd.ExcelFile(excel_file).sheet_names
        print(f"📋 발견된 시트: {all_sheets}")

        # 시트 이름을 파라미터로 받거나 기본값 사용
        target_sheet = sheet

        # 대상 시트 찾기
        df = None
        sheet_name = None

        if target_sheet and target_sheet in all_sheets:
            # 특정 시트 지정된 경우
            try:
                temp_df = pd.read_excel(excel_file, sheet_name=target_sheet, header=None)
                for i in range(min(5, len(temp_df))):
                    if '결제일자' in str(temp_df.iloc[i].values) or '고객명' in str(temp_df.iloc[i].values):
                        df = pd.read_excel(excel_file, sheet_name=target_sheet, header=i)
                        sheet_name = target_sheet
                        break
            except:
                pass
        else:
            # 기본 동작: 우선순위에 따라 찾기
            preferred_sheets = ['2025년 5월', '전체 결제대장', '전체매출']

            for preferred in preferred_sheets:
                if preferred in all_sheets:
                    try:
                        temp_df = pd.read_excel(excel_file, sheet_name=preferred, header=None)
                        for i in range(min(5, len(temp_df))):
                            if '결제일자' in str(temp_df.iloc[i].values) or '고객명' in str(temp_df.iloc[i].values):
                                df = pd.read_excel(excel_file, sheet_name=preferred, header=i)
                                sheet_name = preferred
                                break
                        if df is not None:
                            break
                    except:
                        continue

        # 우선 시트가 없으면 기존 방식으로 찾기
        if df is None:
            for sheet in all_sheets:
                try:
                    temp_df = pd.read_excel(excel_file, sheet_name=sheet, header=None)
                    # 헤더 행 찾기 (보통 2-3번째 행)
                    for i in range(min(5, len(temp_df))):
                        if '결제일자' in str(temp_df.iloc[i].values) or '번호' in str(temp_df.iloc[i].values):
                            df = pd.read_excel(excel_file, sheet_name=sheet, header=i)
                            sheet_name = sheet
                            break
                    if df is not None:
                        break
                except:
                    continue

        if df is None:
            raise HTTPException(
                status_code=400,
                detail="유효한 결제 데이터를 찾을 수 없습니다. 엑셀 파일 형식을 확인해주세요."
            )

        print(f"✅ '{sheet_name}' 시트에서 데이터 발견")
        print(f"📊 컬럼: {df.columns.tolist()}")

        # 결과 정보
        success_count = 0
        error_count = 0
        duplicate_count = 0
        errors = []

        # 데이터 처리
        for idx, row in df.iterrows():
            try:
                # 필수 필드 확인
                if pd.isna(row.get('고객명')) or pd.isna(row.get('결제일자')):
                    continue

                # 고객명과 전화번호로 고객 찾기
                customer_name = str(row.get('고객명', '')).strip()
                customer_phone = clean_phone_number(row.get('고객전화번호', ''))

                # 고객 조회 (전화번호 우선, 없으면 이름으로)
                customer = None
                if customer_phone:
                    customer = db.query(CustomerModel).filter(CustomerModel.phone == customer_phone).first()

                if not customer:
                    customer = db.query(CustomerModel).filter(CustomerModel.name == customer_name).first()

                if not customer:
                    # 고객이 없으면 생성
                    customer = CustomerModel(
                        name=customer_name,
                        phone=customer_phone,
                        referral_source=row.get('유입', '엑셀업로드'),
                        customer_status='active',
                        notes=f"엑셀 업로드 ({datetime.now().strftime('%Y-%m-%d')})"
                    )
                    db.add(customer)
                    db.flush()

                # 결제 방법 매핑 - 강력한 매핑
                approval_str = str(row.get('승인번호', '')).strip()

                # 승인번호로 추정 (한국어 값 처리)
                if approval_str in ['계좌이체', '무통장입금', '이체']:
                    payment_method = 'transfer'
                elif approval_str in ['현금', 'CASH']:
                    payment_method = 'cash'
                elif approval_str in ['제로페이', 'ZEROPAY']:
                    payment_method = 'other'
                elif approval_str == '':
                    payment_method = 'card'  # 빈 값은 카드로 가정
                else:
                    # 숫자로 된 승인번호나 기타는 모두 카드
                    payment_method = 'card'

                # 승인번호 처리
                approval_number = str(row.get('승인번호', '')).strip()
                if approval_number == 'nan' or approval_number == '계좌이체':
                    approval_number = ''

                # 결제 데이터 생성 (다양한 컬럼명 대응)
                payment_date = parse_korean_date(row.get('결제일자') or row.get('날짜'))
                amount = parse_amount(row.get('결제 금액') or row.get('결제금액') or row.get('금액', 0))

                # 날짜가 없으면 건너뛰기 (금액은 음수도 허용 - 환불)
                if not payment_date:
                    continue

                # 중복 체크 (같은 날짜, 같은 고객, 같은 금액)
                existing = db.execute(
                    select(PaymentModel).where(
                        PaymentModel.customer_id == customer.customer_id,
                        PaymentModel.payment_date == payment_date,
                        PaymentModel.amount == amount
                    )
                ).scalar_one_or_none()

                if existing:
                    duplicate_count += 1
                    continue

                # 결제 프로그램명으로 payment_type 추정
                program_name = str(row.get('결제 프로그램', '')).lower()
                if '패키지' in program_name:
                    payment_type = 'package'
                elif '추가' in program_name:
                    payment_type = 'additional'
                elif '환불' in program_name:
                    payment_type = 'refund'
                else:
                    payment_type = 'single'  # 기본값

                # 결제 상태 결정 (음수 금액은 환불/취소로 처리)
                if amount < 0:
                    payment_status = 'refunded'
                else:
                    payment_status = 'completed'

                # reference_type 처리 (결제 프로그램) - 50자 제한
                reference_type_value = str(row.get('결제 프로그램') or row.get('프로그램명') or '').replace('\n', ' ').strip()
                if not reference_type_value or reference_type_value == 'nan':
                    reference_type_value = None  # 빈 문자열 대신 NULL 저장
                elif len(reference_type_value) > 50:
                    reference_type_value = reference_type_value[:47] + "..."  # 50자로 잘라내기

                # 결제 생성 - raw SQL로 enum 타입 처리
                sql = text("""
                    INSERT INTO payments (
                        customer_id, payment_date, amount, payment_method, payment_type,
                        payment_status, payment_staff, transaction_id, card_holder_name,
                        reference_type, notes
                    ) VALUES (
                        :customer_id, :payment_date, :amount,
                        CAST(:payment_method AS payment_method),
                        CAST(:payment_type AS payment_type),
                        CAST(:payment_status AS payment_status),
                        :payment_staff, :transaction_id, :card_holder_name,
                        :reference_type, :notes
                    )
                """)

                db.execute(sql, {
                    'customer_id': customer.customer_id,
                    'payment_date': payment_date,
                    'amount': amount,
                    'payment_method': payment_method,
                    'payment_type': payment_type,
                    'payment_status': payment_status,
                    'payment_staff': row.get('결제 담당자') or row.get('담당자') or '',
                    'transaction_id': approval_number,
                    'card_holder_name': row.get('카드 명의자명') or row.get('카드명의자') or '',
                    'reference_type': reference_type_value,
                    'notes': f"엑셀 업로드 ({sheet_name})"
                })
                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"행 {idx + 1}: {str(e)}")
                # 트랜잭션 롤백
                db.rollback()
                if len(errors) > 10:  # 에러가 너무 많으면 중단
                    errors.append("... 이하 생략 (에러가 너무 많음)")
                    break

        # 커밋
        db.commit()

        # 결과 반환
        return {
            "success": True,
            "message": f"엑셀 업로드 완료",
            "sheet_name": sheet_name,
            "total_rows": len(df),
            "success_count": success_count,
            "duplicate_count": duplicate_count,
            "error_count": error_count,
            "errors": errors[:10] if errors else []
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 엑셀 업로드 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"엑셀 파일 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/import/excel/all")
@router.post("/import/excel/all/")
async def import_all_sheets_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """엑셀 파일의 모든 시트에서 결제 데이터 가져오기"""
    try:
        # 파일 타입 검증
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="엑셀 파일(.xlsx, .xls)만 업로드 가능합니다."
            )

        # 파일 읽기
        contents = await file.read()
        excel_file = io.BytesIO(contents)

        # 엑셀 파일의 모든 시트 확인
        all_sheets = pd.ExcelFile(excel_file).sheet_names
        print(f"📋 총 {len(all_sheets)}개 시트 발견")

        # 결과 정보
        total_success = 0
        total_duplicate = 0
        total_error = 0
        sheet_results = []

        # 각 시트 처리
        for sheet_name in all_sheets:
            if sheet_name in ['전체매출']:  # 스킵할 시트
                continue

            try:
                # 헤더 찾기
                temp_df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                header_row = None

                for i in range(min(5, len(temp_df))):
                    if '결제일자' in str(temp_df.iloc[i].values) or '고객명' in str(temp_df.iloc[i].values):
                        header_row = i
                        break

                if header_row is None:
                    continue

                # 데이터 읽기
                df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row)

                # 유효한 데이터만 필터링
                valid_data = df[pd.notna(df.get('고객명')) & pd.notna(df.get('결제일자'))]

                if len(valid_data) == 0:
                    continue

                # 시트별 처리 (기존 import_payments_from_excel 로직 재사용)
                success_count = 0
                duplicate_count = 0
                error_count = 0

                for idx, row in valid_data.iterrows():
                    try:
                        # 고객명과 전화번호로 고객 찾기
                        customer_name = str(row.get('고객명', '')).strip()
                        customer_phone = clean_phone_number(row.get('고객전화번호', ''))

                        # 고객 조회
                        customer = None
                        if customer_phone:
                            customer = db.query(CustomerModel).filter(CustomerModel.phone == customer_phone).first()
                        if not customer:
                            customer = db.query(CustomerModel).filter(CustomerModel.name == customer_name).first()

                        if not customer:
                            # 고객이 없으면 생성
                            customer = CustomerModel(
                                name=customer_name,
                                phone=customer_phone,
                                referral_source=row.get('유입', '엑셀업로드'),
                                customer_status='active',
                                notes=f"엑셀 업로드 ({datetime.now().strftime('%Y-%m-%d')})"
                            )
                            db.add(customer)
                            db.flush()

                        # 결제 방법 매핑
                        approval_str = str(row.get('승인번호', '')).strip()
                        if approval_str in ['계좌이체', '무통장입금', '이체']:
                            payment_method = 'transfer'
                        elif approval_str in ['현금', 'CASH']:
                            payment_method = 'cash'
                        elif approval_str in ['제로페이', 'ZEROPAY']:
                            payment_method = 'other'
                        else:
                            payment_method = 'card'

                        # 승인번호 처리
                        approval_number = str(row.get('승인번호', '')).strip()
                        if approval_number == 'nan' or approval_number == '계좌이체':
                            approval_number = ''

                        # 결제 데이터 생성
                        payment_date = parse_korean_date(row.get('결제일자') or row.get('날짜'))
                        amount = parse_amount(row.get('결제 금액') or row.get('결제금액') or row.get('금액', 0))

                        if not payment_date:
                            continue

                        # 중복 체크
                        existing = db.query(PaymentModel).filter(
                            PaymentModel.customer_id == customer.customer_id,
                            PaymentModel.payment_date == payment_date,
                            PaymentModel.amount == amount
                        ).first()

                        if existing:
                            duplicate_count += 1
                            continue

                        # payment_type과 status 설정
                        program_name = str(row.get('결제 프로그램', '')).lower()
                        if '패키지' in program_name:
                            payment_type = 'package'
                        elif '추가' in program_name:
                            payment_type = 'additional'
                        elif '환불' in program_name:
                            payment_type = 'refund'
                        else:
                            payment_type = 'single'

                        payment_status = 'refunded' if amount < 0 else 'completed'

                        # reference_type 처리
                        reference_type_value = str(row.get('결제 프로그램') or '').replace('\n', ' ').strip()
                        if not reference_type_value or reference_type_value == 'nan':
                            reference_type_value = None
                        elif len(reference_type_value) > 50:
                            reference_type_value = reference_type_value[:47] + "..."

                        # SQL로 결제 생성
                        sql = text("""
                            INSERT INTO payments (
                                customer_id, payment_date, amount, payment_method, payment_type,
                                payment_status, payment_staff, transaction_id, card_holder_name,
                                reference_type, notes
                            ) VALUES (
                                :customer_id, :payment_date, :amount,
                                CAST(:payment_method AS payment_method),
                                CAST(:payment_type AS payment_type),
                                CAST(:payment_status AS payment_status),
                                :payment_staff, :transaction_id, :card_holder_name,
                                :reference_type, :notes
                            )
                        """)

                        db.execute(sql, {
                            'customer_id': customer.customer_id,
                            'payment_date': payment_date,
                            'amount': amount,
                            'payment_method': payment_method,
                            'payment_type': payment_type,
                            'payment_status': payment_status,
                            'payment_staff': row.get('결제 담당자') or '',
                            'transaction_id': approval_number,
                            'card_holder_name': row.get('카드 명의자명') or '',
                            'reference_type': reference_type_value,
                            'notes': f"엑셀 업로드 ({sheet_name})"
                        })
                        success_count += 1

                    except Exception as e:
                        error_count += 1
                        db.rollback()

                # 시트별 결과 저장
                if success_count > 0 or duplicate_count > 0:
                    sheet_results.append({
                        'sheet': sheet_name,
                        'total': len(valid_data),
                        'success': success_count,
                        'duplicate': duplicate_count,
                        'error': error_count
                    })

                    total_success += success_count
                    total_duplicate += duplicate_count
                    total_error += error_count

            except Exception as e:
                print(f"❌ {sheet_name} 시트 처리 에러: {str(e)}")
                continue

        # 최종 커밋
        db.commit()

        # 결과 반환
        return {
            "success": True,
            "message": f"전체 시트 업로드 완료",
            "total_sheets": len(sheet_results),
            "total_success": total_success,
            "total_duplicate": total_duplicate,
            "total_error": total_error,
            "sheet_results": sheet_results
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 전체 업로드 에러: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"엑셀 파일 처리 중 오류가 발생했습니다: {str(e)}"
        )
