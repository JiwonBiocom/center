# 데이터베이스 보호 가이드

## 문제 원인
`core/init_db.py` 파일에 모든 테이블을 삭제하는 코드가 포함되어 있어, 실수로 실행 시 모든 데이터가 삭제됩니다.

## 즉시 조치사항

### 1. init_db.py 파일 수정
```python
# 기존 위험한 코드
await conn.run_sync(Base.metadata.drop_all)  # 삭제해야 함!

# 안전한 코드로 변경
# await conn.run_sync(Base.metadata.drop_all)  # 주석 처리
```

### 2. 프로덕션 환경 보호
- `.env` 파일에 환경 변수 추가:
  ```
  ENVIRONMENT=production  # 또는 development
  ```

- init_db.py에 안전장치 추가:
  ```python
  if os.getenv('ENVIRONMENT') == 'production':
      raise Exception("Cannot drop tables in production!")
  ```

### 3. 백업 전략
- 매일 자동 백업 설정
- 중요 작업 전 수동 백업
- 백업 파일을 다른 위치에 보관

### 4. 권한 관리
- 프로덕션 데이터베이스 접근 권한 제한
- 위험한 스크립트는 별도 폴더로 이동
- 실행 권한 제한

### 5. 모니터링
- 데이터베이스 변경 로그 활성화
- 테이블 삭제 시 알림 설정
- 정기적인 데이터 무결성 체크

## 권장 폴더 구조
```
backend/
├── scripts/
│   ├── safe/          # 안전한 스크립트
│   └── dangerous/     # 위험한 스크립트 (init_db.py 등)
└── core/
    └── init_db.py     # 삭제하거나 안전하게 수정
```

## 긴급 복구 방법
1. 최근 백업 확인
2. 백업에서 복원
3. 복원 불가 시 Excel 파일에서 재마이그레이션

## 체크리스트
- [ ] init_db.py 파일 수정 또는 삭제
- [ ] 환경 변수 설정
- [ ] 백업 시스템 구축
- [ ] 팀원들에게 주의사항 공유
- [ ] 위험한 스크립트 격리