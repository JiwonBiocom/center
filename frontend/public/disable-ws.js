// WebSocket 완전 차단 스크립트
(function() {
  'use strict';
  
  console.log('🚫 WebSocket 완전 차단 모드 활성화');
  
  // WebSocket 생성자 완전 차단
  const originalWebSocket = window.WebSocket;
  window.WebSocket = function(...args) {
    console.warn('🚫 WebSocket 연결 차단됨:', args[0]);
    
    // 가짜 WebSocket 객체 반환 (즉시 실패)
    const fakeWS = {
      readyState: 3, // CLOSED
      close: () => {},
      send: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false
    };
    
    // 즉시 에러 이벤트 발생하지 않도록 지연
    setTimeout(() => {
      if (fakeWS.onerror) {
        fakeWS.onerror({ type: 'error', message: 'WebSocket disabled' });
      }
    }, 1);
    
    return fakeWS;
  };
  
  // EventSource도 차단 (SSE)
  if (window.EventSource) {
    const originalEventSource = window.EventSource;
    window.EventSource = function(...args) {
      console.warn('🚫 EventSource 연결 차단됨:', args[0]);
      return {
        readyState: 2, // CLOSED
        close: () => {},
        addEventListener: () => {},
        removeEventListener: () => {}
      };
    };
  }
  
  // Vite 클라이언트 WebSocket 연결 방지
  if (window.__vite_plugin_react_preamble_installed__) {
    console.log('🔧 Vite React 플러그인 감지됨 - WebSocket 우회 적용');
  }
  
  // 콘솔 에러 필터링 (WebSocket 관련만)
  const originalConsoleError = console.error;
  console.error = function(...args) {
    const message = args.join(' ');
    
    // WebSocket 관련 에러는 정보성 메시지로 변환
    if (message.includes('WebSocket') || message.includes('websocket')) {
      console.info('ℹ️ WebSocket 기능이 비활성화되어 있습니다:', ...args);
      return;
    }
    
    // HMR 관련 에러도 정보성 메시지로 변환
    if (message.includes('[vite]') && (message.includes('connect') || message.includes('websocket'))) {
      console.info('ℹ️ Vite HMR이 비활성화되어 있습니다. 수동 새로고침을 사용하세요.');
      return;
    }
    
    // 다른 에러는 정상 출력
    originalConsoleError.apply(console, args);
  };
  
  console.log('✅ WebSocket 차단 완료');
})();