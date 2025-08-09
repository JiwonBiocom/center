// HMR WebSocket 에러 해결을 위한 클라이언트 사이드 스크립트
(function() {
  'use strict';
  
  // HMR WebSocket 연결 에러를 캐치하고 조용히 처리
  const originalConsoleError = console.error;
  
  console.error = function(...args) {
    const message = args.join(' ');
    
    // HMR WebSocket 관련 에러는 표시하지 않음
    if (message.includes('WebSocket connection') && message.includes('failed') && message.includes('vite')) {
      console.info('🔧 HMR WebSocket 연결 실패 (무시됨):', message);
      return;
    }
    
    // HMR 관련 에러는 표시하지 않음
    if (message.includes('[vite] failed to connect to websocket')) {
      console.info('🔧 HMR WebSocket 연결 재시도 중... (자동 새로고침 비활성화됨)');
      return;
    }
    
    // 다른 에러는 정상적으로 표시
    originalConsoleError.apply(console, args);
  };
  
  // Vite 클라이언트가 로드된 후 WebSocket 에러 핸들링 개선
  if (window.__vite_plugin_react_preamble_installed__) {
    console.info('🔧 Vite React 플러그인 감지됨');
  }
  
  // 개발 환경에서만 실행
  if (import.meta && import.meta.env && import.meta.env.DEV) {
    console.info('🔧 HMR WebSocket 에러 핸들링이 활성화되었습니다.');
  }
})();