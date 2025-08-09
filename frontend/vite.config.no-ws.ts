import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 🔇 WebSocket 없는 개발 설정 (극단적 해결책)
export default defineConfig({
  plugins: [react()],
  server: {
    host: 'localhost',
    port: 5173,
    strictPort: true,
    hmr: false,  // HMR 완전 비활성화
    watch: {
      usePolling: true,   // 폴링 방식으로 파일 변경 감지
      interval: 1000,     // 1초마다 체크
      ignored: [
        '**/node_modules/**',
        '**/.git/**',
        '**/dist/**'
      ]
    },
    // CORS 설정
    cors: true
  },
  // 빠른 리로드를 위한 최적화
  build: {
    sourcemap: true,
    minify: false,  // 개발 시 압축 안함
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          query: ['@tanstack/react-query']
        }
      }
    }
  },
  // 종속성 최적화
  optimizeDeps: {
    include: [
      'react', 
      'react-dom', 
      'react-router-dom',
      '@tanstack/react-query'
    ],
    force: true
  }
})