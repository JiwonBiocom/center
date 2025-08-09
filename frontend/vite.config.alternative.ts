import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 🚀 HMR 활성화 고성능 설정 (UI/스타일 개발용)
export default defineConfig({
  plugins: [react()],
  server: {
    host: 'localhost',
    port: 5173,
    strictPort: true,
    hmr: {
      protocol: 'ws',
      host: '127.0.0.1',    // IP 주소 직접 사용
      port: 24678,          // WebSocket 전용 포트
      clientPort: 24678,    // 브라우저 연결 포트
      overlay: false,       // 에러 오버레이 비활성화
      skipSSLVerify: true   // SSL 검증 건너뛰기
    },
    watch: {
      usePolling: false,  // inotify 사용 (더 효율적)
      interval: 300,      // 폴링 간격 단축
      ignored: [
        '**/node_modules/**',
        '**/.git/**',
        '**/dist/**',
        '**/.next/**'
      ]
    },
    // CORS 및 프록시 설정
    cors: true,
    force: true  // 종속성 사전 번들링 강제
  },
  // 빌드 최적화
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom']
        }
      }
    }
  },
  // 종속성 최적화
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom'],
    force: true
  }
})