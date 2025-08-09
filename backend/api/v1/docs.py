from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import os
from pathlib import Path

from core.database import get_db
from models.user import User
from core.auth import get_current_active_user as get_current_user

router = APIRouter(
    prefix="/docs",
    tags=["documents"]
)

# 문서 경로 설정
DOCS_BASE_PATH = Path(__file__).parent.parent.parent.parent / "docs"

# 관리자만 접근 가능한 문서 목록
ADMIN_ONLY_DOCS = [
    "AI_RECOMMENDATION_ALGORITHM.md",
    "customer-questionnaire-simulation.html",
    "diet-simulation.html"
]

@router.get("/algorithm/{filename}")
def get_algorithm_document(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    알고리즘 문서 조회 (관리자 전용)
    """
    # 관리자 권한 확인
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근 가능한 문서입니다."
        )
    
    # 파일명 검증 (보안)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 파일명입니다."
        )
    
    # 허용된 문서인지 확인
    if filename not in ADMIN_ONLY_DOCS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문서를 찾을 수 없습니다."
        )
    
    # 파일 경로 구성
    file_path = DOCS_BASE_PATH / filename
    
    # 파일 존재 확인
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문서를 찾을 수 없습니다."
        )
    
    # 파일 읽기
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파일 타입에 따라 응답 형식 결정
        if filename.endswith('.html'):
            return {
                "filename": filename,
                "content": content,
                "type": "html"
            }
        elif filename.endswith('.md'):
            return {
                "filename": filename,
                "content": content,
                "type": "markdown"
            }
        else:
            return {
                "filename": filename,
                "content": content,
                "type": "text"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 읽기 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/list")
def list_algorithm_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict:
    """
    알고리즘 문서 목록 조회 (관리자 전용)
    """
    # 관리자 권한 확인
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근 가능합니다."
        )
    
    documents = []
    for doc in ADMIN_ONLY_DOCS:
        file_path = DOCS_BASE_PATH / doc
        if file_path.exists():
            documents.append({
                "filename": doc,
                "title": doc.replace('_', ' ').replace('.md', '').replace('.html', '').title(),
                "type": "html" if doc.endswith('.html') else "markdown"
            })
    
    return {
        "documents": documents,
        "total": len(documents)
    }