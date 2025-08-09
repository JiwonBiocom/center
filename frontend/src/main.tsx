import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// 에러 로거 초기화 (가장 먼저 실행)
import './utils/errorLogger'

// HTTPS 체크 - 프로덕션에서 HTTP 요청 방지
import './utils/https-checker'

// Service Worker 등록 제거됨 (캐시 문제 해결 위해)
// ViewModeProvider 제거됨 (실제 사용되지 않아 에러 발생)

const root = createRoot(document.getElementById('root')!);
root.render(
  <StrictMode>
    <App />
  </StrictMode>,
)
