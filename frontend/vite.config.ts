import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

// TJ님 분석: 캐시 완전 초기화 모드 + 코드 스플리팅 최적화
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: './dist/stats.html',
      open: false, // 자동으로 열지 않음
      gzipSize: true,
      brotliSize: true,
    })
  ],
  server: {
    host: 'localhost',
    port: 5173
    // HMR 설정 완전 제거 - 기본값 사용
  },
  build: {
    sourcemap: true,
    // 코드 스플리팅 최적화
    rollupOptions: {
      output: {
        manualChunks: {
          // React 관련 라이브러리
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // UI 관련 라이브러리
          'ui-vendor': ['@headlessui/react', 'lucide-react'],
          // 데이터 관련 라이브러리
          'data-vendor': ['@tanstack/react-query', 'axios', 'date-fns'],
          // 차트 라이브러리 (가장 큰 번들)
          'chart-vendor': ['recharts'],
        }
      }
    }
  },
  resolve: {
    dedupe: ['react', 'react-dom'],
  },
  optimizeDeps: {
    force: true,           // 의존성 사전 번들링 강제 재실행
    include: ['react', 'react-dom', 'recharts']  // 명시적으로 포함
  }
})
