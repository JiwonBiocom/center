import pandas as pd
import os
from datetime import datetime

def convert_excel_to_csv():
    """고객관리대장2025 엑셀 파일의 모든 시트를 CSV로 변환"""

    # 정확한 엑셀 파일 경로
    excel_path = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/고객관리대장2025.xlsm'

    if not os.path.exists(excel_path):
        print(f"엑셀 파일을 찾을 수 없습니다: {excel_path}")
        return

    print(f"엑셀 파일 발견: {excel_path}")

    try:
        # 엑셀 파일 열기
        xls = pd.ExcelFile(excel_path)
        print(f"\n시트 목록: {xls.sheet_names}")

        # 출력 디렉토리 생성
        output_dir = '/Users/vibetj/coding/center/docs/AIBIO 관리대장 파일모음/csv_export'
        os.makedirs(output_dir, exist_ok=True)

        # 각 시트를 CSV로 변환
        for sheet_name in xls.sheet_names:
            try:
                print(f"\n'{sheet_name}' 시트 처리 중...")

                # 시트 읽기
                df = pd.read_excel(excel_path, sheet_name=sheet_name)

                # 파일명 안전하게 만들기
                safe_sheet_name = sheet_name.replace('/', '_').replace(' ', '_')
                csv_filename = f"{safe_sheet_name}.csv"
                csv_path = os.path.join(output_dir, csv_filename)

                # CSV로 저장
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"  ✓ 저장됨: {csv_filename} ({len(df)}행)")

                # 이성윤 데이터 확인
                for col in df.columns:
                    if df[col].astype(str).str.contains('이성윤').any():
                        lee_count = df[df[col].astype(str).str.contains('이성윤')].shape[0]
                        print(f"    → 이성윤 데이터 {lee_count}건 발견 ('{col}' 컬럼)")

            except Exception as e:
                print(f"  ✗ '{sheet_name}' 시트 처리 중 에러: {e}")

        print(f"\n변환 완료! CSV 파일들이 다음 위치에 저장되었습니다:")
        print(f"{output_dir}")

        # 저장된 파일 목록
        saved_files = os.listdir(output_dir)
        print(f"\n저장된 파일들 ({len(saved_files)}개):")
        for file in saved_files:
            if file.endswith('.csv'):
                print(f"  - {file}")

    except Exception as e:
        print(f"엑셀 파일 처리 중 에러: {e}")

if __name__ == "__main__":
    print("고객관리대장2025 엑셀→CSV 변환 시작...")
    convert_excel_to_csv()
