#!/usr/bin/env python3
"""
API 경로 일관성 검증

FastAPI의 redirect_slashes 설정과 프론트엔드 API 호출 경로의 일치 여부를 검증합니다.
"""
import re
import sys
from pathlib import Path
from typing import Set, Tuple, List

def check_fastapi_settings() -> Tuple[bool, str]:
    """FastAPI 설정 확인"""
    main_path = Path('backend/main.py')
    if not main_path.exists():
        return False, "main.py not found"
    
    content = main_path.read_text()
    
    # redirect_slashes 설정 찾기
    match = re.search(r'redirect_slashes\s*=\s*(True|False)', content)
    if match:
        redirect_slashes = match.group(1) == 'True'
        return redirect_slashes, f"redirect_slashes={match.group(1)}"
    
    return True, "redirect_slashes=True (default)"

def find_backend_routes() -> Set[str]:
    """백엔드 라우트 찾기"""
    routes = set()
    
    # API 라우터 파일들 검색
    api_path = Path('backend/api')
    if not api_path.exists():
        return routes
    
    for py_file in api_path.rglob('*.py'):
        content = py_file.read_text()
        
        # 라우트 패턴 찾기
        # @router.get("/path") or @router.post("/path")
        route_patterns = [
            r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in route_patterns:
            matches = re.findall(pattern, content)
            for method, path in matches:
                routes.add(f"{method.upper()} {path}")
    
    return routes

def find_frontend_api_calls() -> Set[str]:
    """프론트엔드 API 호출 찾기"""
    api_calls = set()
    
    # 프론트엔드 소스 파일들 검색
    frontend_path = Path('frontend/src')
    if not frontend_path.exists():
        return api_calls
    
    for ts_file in frontend_path.rglob('*'):
        if ts_file.suffix not in ['.ts', '.tsx']:
            continue
            
        content = ts_file.read_text()
        
        # API 호출 패턴 찾기
        # api.get('/path'), api.post('/path'), etc.
        api_patterns = [
            r'api\.(get|post|put|delete|patch)\s*\(\s*[`"\']([^`"\']+)[`"\']',
            r'fetch\s*\(\s*[`"\']([^`"\']+)[`"\'].*method:\s*["\'](\w+)["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    if pattern.startswith('api'):
                        method, path = match
                    else:
                        path, method = match
                    # /api/v1 제거
                    if path.startswith('/api/v1'):
                        path = path[7:]
                    api_calls.add(f"{method.upper()} {path}")
        
    return api_calls

def check_route_consistency(backend_routes: Set[str], frontend_calls: Set[str], redirect_slashes: bool) -> List[str]:
    """라우트 일관성 검증"""
    issues = []
    
    for call in frontend_calls:
        method, path = call.split(' ', 1)
        
        # 정확한 매치 확인
        if call in backend_routes:
            continue
        
        # trailing slash 처리 확인
        if path.endswith('/'):
            alt_call = f"{method} {path[:-1]}"
        else:
            alt_call = f"{method} {path}/"
        
        if alt_call in backend_routes:
            if not redirect_slashes:
                issues.append(f"Trailing slash mismatch: Frontend calls '{call}' but backend has '{alt_call}'")
        else:
            # 와일드카드 경로 확인 (예: /customers/{id})
            found = False
            for route in backend_routes:
                if route.startswith(f"{method} "):
                    route_path = route.split(' ', 1)[1]
                    # 파라미터 패턴 변환: {id} -> \d+
                    pattern = re.sub(r'\{[^}]+\}', r'[^/]+', route_path)
                    if re.match(f"^{pattern}$", path):
                        found = True
                        break
            
            if not found and path not in ['/health', '/docs', '/openapi.json']:
                issues.append(f"Frontend calls '{call}' but no matching backend route found")
    
    return issues

def load_whitelist() -> Set[str]:
    """화이트리스트 로드"""
    whitelist_file = Path('scripts/route_checker_ignore.txt')
    if whitelist_file.exists():
        whitelist = set()
        for line in whitelist_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                whitelist.add(line)
        return whitelist
    return set()

def save_whitelist_template(issues: List[str]):
    """화이트리스트 템플릿 생성"""
    template_file = Path('scripts/route_checker_ignore_template.txt')
    
    content = """# API Route Checker 화이트리스트 템플릿
# 
# 이 파일에 나열된 경로는 route checker에서 무시됩니다.
# 실제로 사용하지 않는 경로는 주석 처리하지 말고 프론트엔드 코드에서 제거하세요.
#
# 사용법:
# 1. 이 파일을 route_checker_ignore.txt로 복사
# 2. 실제로 필요한 경로만 주석 해제
# 3. 나머지는 프론트엔드에서 제거

# === 동적 경로 패턴 (백엔드에 있지만 패턴이 다른 경우) ===
# GET /customers/?search=${searchTerm}  # 백엔드: GET /customers
# POST /customers/  # 백엔드: POST /customers (trailing slash)

# === 개발 중/계획된 API ===
# POST /settings/backup/create
# POST /notifications/test
# GET /settings/kakao/keys

# === 삭제 예정 (레거시) ===
"""
    
    # 경로만 추출
    route_issues = []
    for issue in issues:
        if "Frontend calls" in issue:
            match = re.search(r"'([^']+)'", issue)
            if match:
                route_issues.append(match.group(1))
    
    # 중복 제거 및 정렬
    unique_routes = sorted(set(route_issues))
    
    for route in unique_routes:
        content += f"\n# {route}"
    
    template_file.write_text(content)
    print(f"\n📝 화이트리스트 템플릿 생성됨: {template_file}")
    print("   필요한 경로만 주석 해제하여 route_checker_ignore.txt로 저장하세요.")

def main():
    print("🔍 Checking API Route Consistency...")
    print("=" * 60)
    
    # FastAPI 설정 확인
    redirect_slashes, setting_info = check_fastapi_settings()
    print(f"⚙️  FastAPI setting: {setting_info}")
    
    if not redirect_slashes:
        print("⚠️  Warning: redirect_slashes=False requires exact path matching!")
    
    # 라우트 수집
    backend_routes = find_backend_routes()
    frontend_calls = find_frontend_api_calls()
    
    print(f"\n📊 Found {len(backend_routes)} backend routes")
    print(f"📊 Found {len(frontend_calls)} frontend API calls")
    
    # 화이트리스트 로드
    whitelist = load_whitelist()
    if whitelist:
        print(f"📋 Loaded {len(whitelist)} whitelisted routes")
        # 화이트리스트 경로 필터링
        frontend_calls = {call for call in frontend_calls if call not in whitelist}
    
    # 일관성 검증
    issues = check_route_consistency(backend_routes, frontend_calls, redirect_slashes)
    
    if issues:
        print("\n❌ Route consistency issues found:")
        for issue in issues[:20]:  # 처음 20개만 표시
            print(f"   - {issue}")
        
        if len(issues) > 20:
            print(f"   ... and {len(issues) - 20} more issues")
        
        # 화이트리스트 템플릿 생성
        save_whitelist_template(issues)
        
        print("\n🔧 Fix these issues to prevent 404 errors in production!")
        sys.exit(1)
    else:
        print("\n✅ All API routes are consistent!")
        sys.exit(0)

if __name__ == "__main__":
    main()