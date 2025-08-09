#!/usr/bin/env python3
"""
OpenAPI 스키마 생성 스크립트

FastAPI 애플리케이션에서 OpenAPI 스키마를 추출하여 파일로 저장합니다.
이는 프론트엔드에서 TypeScript 타입을 자동 생성하는 데 사용됩니다.
"""
import json
import sys
import os

# 백엔드 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


def generate_openapi_schema():
    """OpenAPI 스키마를 생성하고 파일로 저장"""
    # OpenAPI 스키마 가져오기
    openapi_schema = app.openapi()
    
    # 타입 생성에 도움이 되는 추가 정보 추가
    openapi_schema["info"]["x-generated-at"] = "2025-06-10"
    openapi_schema["info"]["x-generator"] = "generate_openapi.py"
    
    # 응답 스키마에 대한 설명 추가
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]
        
        # APIResponse 스키마에 설명 추가
        if "APIResponse" in schemas:
            schemas["APIResponse"]["description"] = "표준 API 응답 형식"
            
        if "PaginatedResponse" in schemas:
            schemas["PaginatedResponse"]["description"] = "페이지네이션이 적용된 응답 형식"
            
        if "ErrorResponse" in schemas:
            schemas["ErrorResponse"]["description"] = "에러 응답 형식"
    
    # 스키마를 파일로 저장
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "openapi.json"
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI 스키마가 생성되었습니다: {output_path}")
    
    # 프론트엔드 디렉토리에도 복사
    frontend_output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "frontend",
        "openapi.json"
    )
    
    os.makedirs(os.path.dirname(frontend_output_path), exist_ok=True)
    
    with open(frontend_output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI 스키마가 프론트엔드에 복사되었습니다: {frontend_output_path}")
    
    # 생성된 엔드포인트 요약
    paths = openapi_schema.get("paths", {})
    print(f"\n📊 총 {len(paths)} 개의 엔드포인트가 문서화되었습니다.")
    
    # 태그별 엔드포인트 수 계산
    tag_counts = {}
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                tags = details.get("tags", ["untagged"])
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\n태그별 엔드포인트 수:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {tag}: {count}개")


if __name__ == "__main__":
    generate_openapi_schema()