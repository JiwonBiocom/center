#!/usr/bin/env python3
"""
문진 폴더의 PDF 파일 내용을 추출하는 스크립트
"""

import os
import sys
from pathlib import Path
import PyPDF2

# 문진 폴더 경로
FOLDER_PATH = Path("/Users/vibetj/coding/center/docs/문진")
OUTPUT_DIR = Path("/Users/vibetj/coding/center/docs/문진/extracted_texts")

def extract_pdf(file_path):
    """PDF 파일에서 텍스트 추출"""
    try:
        content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    content.append(f"\n=== 페이지 {page_num + 1} ===\n")
                    content.append(text)
        
        return "\n".join(content)
    except Exception as e:
        return f"오류 발생: {str(e)}"

def main():
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # PDF 파일 처리
    pdf_files = list(FOLDER_PATH.glob("*.pdf"))
    
    print(f"\n발견된 PDF 파일: {len(pdf_files)}개")
    
    for file_path in pdf_files:
        print(f"\n처리 중: {file_path.name}")
        content = extract_pdf(file_path)
        
        # 출력 파일명 생성
        output_file = OUTPUT_DIR / f"{file_path.stem}.txt"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"=== {file_path.name} 내용 추출 ===\n\n")
            f.write(content)
        
        print(f"저장됨: {output_file}")

if __name__ == "__main__":
    main()