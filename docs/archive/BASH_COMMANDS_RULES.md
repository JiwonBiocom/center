# Bash 커맨드 실행 규칙

## 자동 실행 가능한 커맨드 (확인 불필요)

### 1. 프로세스 관리
- `ps aux | grep [process]` - 프로세스 확인
- `lsof -ti:[port]` - 포트 사용 확인
- `pkill -f [process]` - 프로세스 종료
- `kill -9 [pid]` - 특정 PID 종료
- `lsof -ti:[port] | xargs kill -9` - 포트 사용 프로세스 종료

### 2. 서버 관리
- `python main.py > backend.log 2>&1 &` - 백엔드 서버 재시작
- `npm run dev > frontend.log 2>&1 &` - 프론트엔드 서버 재시작
- `tail -f [logfile]` - 로그 확인
- `cat [logfile] | tail -n [lines]` - 로그 마지막 부분 확인

### 3. 파일 시스템 작업
- `ls -la` - 파일 목록 확인
- `pwd` - 현재 디렉토리 확인
- `cd [directory]` - 디렉토리 이동
- `cat [file]` - 파일 내용 확인
- `grep [pattern] [file]` - 파일 내 검색
- `find . -name "[pattern]"` - 파일 찾기

### 4. Git 작업
- `git status` - 상태 확인
- `git diff` - 변경사항 확인
- `git log --oneline -n [count]` - 커밋 로그 확인
- `git add .` 또는 `git add [file]` - 스테이징
- `git commit -m "[message]"` - 커밋

### 5. 스크립트 실행
- `python scripts/[script].py` - 파이썬 스크립트 실행
- `bash scripts/[script].sh` - 쉘 스크립트 실행

### 6. 네트워크 및 API 테스트
- `curl` 명령어 전체 - API 테스트
- `netstat -an | grep [port]` - 네트워크 상태 확인

### 7. 환경 확인
- `which [command]` - 명령어 위치 확인
- `echo $[VARIABLE]` - 환경변수 확인
- `env | grep [pattern]` - 환경변수 검색

## 확인이 필요한 커맨드

### 1. 위험한 작업
- `rm -rf` - 강제 삭제
- `drop database` - 데이터베이스 삭제
- `truncate` - 테이블 초기화
- 시스템 설정 변경 명령어

### 2. 민감한 정보
- 비밀번호가 포함된 명령어
- API 키가 노출되는 명령어
- 개인정보가 포함된 명령어

### 3. 대규모 변경
- 대량의 데이터 마이그레이션
- 전체 시스템 재시작
- 프로덕션 환경 변경

## 기본 원칙

1. **안전성**: 데이터 손실이나 시스템 장애를 일으킬 수 있는 명령어는 항상 확인
2. **효율성**: 일상적인 개발 작업에 필요한 명령어는 즉시 실행
3. **투명성**: 실행한 명령어와 결과는 항상 명확히 표시
4. **복구 가능성**: 위험한 작업 전에는 백업 확인

이 규칙은 개발 생산성을 높이면서도 안전성을 유지하기 위해 작성되었습니다.