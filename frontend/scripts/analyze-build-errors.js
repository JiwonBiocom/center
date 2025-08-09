#!/usr/bin/env node

/**
 * Vite 빌드 및 런타임 에러 분석 스크립트
 * @vitejs/plugin-react preamble 에러를 감지하고 해결 방안을 제시
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🔍 Vite/React 설정 분석 시작...\n');

// 1. package.json 분석
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
console.log('📦 현재 설치된 패키지:');
console.log(`  - react: ${packageJson.dependencies.react}`);
console.log(`  - react-dom: ${packageJson.dependencies['react-dom']}`);
console.log(`  - @vitejs/plugin-react: ${packageJson.devDependencies['@vitejs/plugin-react']}`);
console.log(`  - vite: ${packageJson.devDependencies.vite}\n`);

// 2. vite.config.ts 분석
const viteConfigPath = path.join(process.cwd(), 'vite.config.ts');
const viteConfig = fs.readFileSync(viteConfigPath, 'utf8');

console.log('⚙️  Vite 설정 분석:');
if (viteConfig.includes('react()')) {
  console.log('  ✅ React 플러그인 활성화됨');
} else {
  console.log('  ❌ React 플러그인이 설정되지 않음');
}

// 3. React preamble 관련 파일 확인
console.log('\n🔍 React Preamble 관련 파일 확인:');

// App.tsx의 44번째 라인 확인
const appTsxPath = path.join(process.cwd(), 'src/App.tsx');
if (fs.existsSync(appTsxPath)) {
  const appContent = fs.readFileSync(appTsxPath, 'utf8');
  const lines = appContent.split('\n');
  console.log(`\nApp.tsx 44번째 라인 근처 (40-48):`)
  for (let i = 39; i < 48 && i < lines.length; i++) {
    console.log(`  ${i + 1}: ${lines[i]}`);
  }
}

// 4. 빌드 캐시 상태 확인
console.log('\n📁 빌드 캐시 상태:');
const nodeModulesVite = path.join(process.cwd(), 'node_modules/.vite');
if (fs.existsSync(nodeModulesVite)) {
  const stats = fs.statSync(nodeModulesVite);
  console.log(`  - .vite 캐시 존재 (수정일: ${stats.mtime})`);
  console.log('  - 캐시 삭제 권장: rm -rf node_modules/.vite');
} else {
  console.log('  - .vite 캐시 없음');
}

// 5. 해결 방안 제시
console.log('\n💡 @vitejs/plugin-react preamble 에러 해결 방안:\n');

console.log('1. 캐시 완전 초기화:');
console.log('   rm -rf node_modules/.vite');
console.log('   rm -rf dist');
console.log('   npm run dev\n');

console.log('2. React 플러그인 설정 수정 (vite.config.ts):');
console.log(`   plugins: [
     react({
       babel: {
         plugins: [
           ['@babel/plugin-transform-react-jsx', { runtime: 'automatic' }]
         ]
       }
     })
   ]\n`);

console.log('3. React 버전 다운그레이드 (안정성):');
console.log('   npm uninstall react react-dom');
console.log('   npm install react@18.3.1 react-dom@18.3.1\n');

console.log('4. Vite 플러그인 재설치:');
console.log('   npm uninstall @vitejs/plugin-react');
console.log('   npm install -D @vitejs/plugin-react@latest\n');

// 6. 실제 에러 재현 시도
console.log('🧪 에러 재현 테스트:');
try {
  // development 모드로 빌드 시도
  console.log('  - Development 빌드 테스트 중...');
  execSync('npx vite build --mode development', {
    stdio: 'pipe',
    env: { ...process.env, NODE_ENV: 'development' }
  });
  console.log('  ✅ Development 빌드 성공');
} catch (error) {
  console.log('  ❌ Development 빌드 실패');
  if (error.stdout) {
    const output = error.stdout.toString();
    if (output.includes('preamble')) {
      console.log('  🔥 Preamble 에러 감지됨!');
      console.log(output);
    }
  }
}

console.log('\n✅ 분석 완료');
console.log('\n🔧 권장 사항: 위의 해결 방안을 순서대로 시도해보세요.');
