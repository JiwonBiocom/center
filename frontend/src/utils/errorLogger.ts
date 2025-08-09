/**
 * 브라우저 에러를 실시간으로 로깅하는 유틸리티
 * @vitejs/plugin-react preamble 에러를 포함한 모든 에러 캡처
 */

interface ErrorLog {
  type: 'error' | 'unhandledRejection' | 'console.error';
  message: string;
  stack?: string;
  source?: string;
  line?: number;
  column?: number;
  timestamp: string;
  userAgent: string;
  url: string;
}

class ErrorLogger {
  private logs: ErrorLog[] = [];
  private originalConsoleError: typeof console.error;

  constructor() {
    this.originalConsoleError = console.error;
    this.setupErrorHandlers();
  }

  private setupErrorHandlers() {
    // 1. window.onerror 핸들러
    window.onerror = (message, source, lineno, colno, error) => {
      this.logError({
        type: 'error',
        message: String(message),
        stack: error?.stack,
        source,
        line: lineno,
        column: colno,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      });

      // 특별히 @vitejs/plugin-react 에러 감지
      if (String(message).includes('@vitejs/plugin-react')) {
        console.warn('🔥 Vite React Plugin 에러 감지됨!', {
          message,
          source,
          line: lineno
        });
        this.saveToLocalStorage();
      }

      return false; // 기본 에러 처리도 계속
    };

    // 2. unhandledRejection 핸들러
    window.addEventListener('unhandledrejection', (event) => {
      this.logError({
        type: 'unhandledRejection',
        message: event.reason?.toString() || 'Unknown rejection',
        stack: event.reason?.stack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      });
    });

    // 3. console.error 오버라이드
    console.error = (...args) => {
      const message = args.map(arg =>
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      ).join(' ');

      this.logError({
        type: 'console.error',
        message,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      });

      // @vitejs/plugin-react 에러 특별 처리
      if (message.includes('@vitejs/plugin-react') || message.includes('preamble')) {
        // 로컬 스토리지에 저장
        this.saveToLocalStorage();

        // 시각적 알림
        this.showErrorNotification('Vite React Plugin 에러가 감지되었습니다.');
      }

      // 원본 console.error 호출
      this.originalConsoleError.apply(console, args);
    };
  }

  private logError(error: ErrorLog) {
    this.logs.push(error);

    // 개발 환경에서만 콘솔에 출력
    if (import.meta.env.DEV) {
      console.log('[ErrorLogger]', error);
    }
  }

  private saveToLocalStorage() {
    try {
      localStorage.setItem('errorLogs', JSON.stringify(this.logs));
      localStorage.setItem('lastErrorTime', new Date().toISOString());
    } catch (e) {
      // 스토리지 가득 참 등의 에러 무시
    }
  }

  private showErrorNotification(message: string) {
    // 화면 상단에 에러 알림 표시
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ef4444;
      color: white;
      padding: 16px;
      border-radius: 8px;
      z-index: 9999;
      font-family: monospace;
      max-width: 400px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    // 5초 후 제거
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }

  // 수집된 에러 로그 조회
  public getLogs(): ErrorLog[] {
    return this.logs;
  }

  // 로컬 스토리지에서 이전 에러 로그 조회
  public getStoredLogs(): ErrorLog[] {
    try {
      const stored = localStorage.getItem('errorLogs');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  // 에러 로그 초기화
  public clearLogs() {
    this.logs = [];
    localStorage.removeItem('errorLogs');
    localStorage.removeItem('lastErrorTime');
  }

  // 특정 에러 타입만 필터링
  public getErrorsByType(type: string): ErrorLog[] {
    return this.logs.filter(log =>
      log.message.toLowerCase().includes(type.toLowerCase())
    );
  }
}

// 싱글톤 인스턴스
export const errorLogger = new ErrorLogger();

// 개발자 도구에서 접근 가능하도록 전역에 노출
if (import.meta.env.DEV) {
  (window as any).__errorLogger__ = errorLogger;
  console.log('💡 개발자 도구에서 __errorLogger__.getLogs()로 에러 로그를 확인할 수 있습니다.');
}
