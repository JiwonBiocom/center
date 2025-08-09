#!/usr/bin/env python3
"""
문진 폴더의 엑셀 파일 내용을 추출하는 스크립트
"""

import os
import sys
from pathlib import Path
import pandas as pd

# 문진 폴더 경로
FOLDER_PATH = Path("/Users/vibetj/coding/center/docs/문진")
OUTPUT_DIR = Path("/Users/vibetj/coding/center/docs/문진/extracted_texts")

def extract_excel(file_path):
    """엑셀 파일에서 내용 추출"""
    try:
        content = []
        
        # 모든 시트 읽기
        xls = pd.ExcelFile(file_path)
        
        for sheet_name in xls.sheet_names:
            content.append(f"\n=== 시트: {sheet_name} ===\n")
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 데이터프레임 정보
            content.append(f"행 수: {len(df)}, 열 수: {len(df.columns)}")
            content.append(f"컬럼: {', '.join(df.columns.tolist())}")
            
            # 상위 10개 행 표시
            content.append("\n[상위 10개 행]")
            content.append(df.head(10).to_string(index=False))
            
            # 각 컬럼의 고유값 수 표시
            content.append("\n[컬럼별 고유값 수]")
            for col in df.columns:
                unique_count = df[col].nunique()
                content.append(f"{col}: {unique_count}개")
        
        return "\n".join(content)
    except Exception as e:
        return f"오류 발생: {str(e)}"

def main():
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # 엑셀 파일 처리
    excel_files = list(FOLDER_PATH.glob("*.xlsx"))
    
    print(f"\n발견된 엑셀 파일: {len(excel_files)}개")
    
    for file_path in excel_files:
        print(f"\n처리 중: {file_path.name}")
        content = extract_excel(file_path)
        
        # 출력 파일명 생성
        output_file = OUTPUT_DIR / f"{file_path.stem}.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"=== {file_path.name} 내용 추출 ===\n\n")
            f.write(content)
        
        print(f"저장됨: {output_file}")

if __name__ == "__main__":
    main()