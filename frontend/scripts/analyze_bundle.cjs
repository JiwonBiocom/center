#!/usr/bin/env node
/**
 * 번들 크기 분석 스크립트
 */
const fs = require('fs');
const path = require('path');

// dist 폴더의 JavaScript 파일 찾기
const distPath = path.join(__dirname, '..', 'dist', 'assets');
const files = fs.readdirSync(distPath);
const jsFile = files.find(file => file.endsWith('.js') && file.includes('index'));

if (!jsFile) {
  console.error('JavaScript 번들 파일을 찾을 수 없습니다.');
  process.exit(1);
}

const filePath = path.join(distPath, jsFile);
const content = fs.readFileSync(filePath, 'utf8');
const stats = fs.statSync(filePath);

console.log('📊 번들 분석 결과');
console.log('=====================================');
console.log(`파일명: ${jsFile}`);
console.log(`파일 크기: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
console.log(`문자 수: ${content.length.toLocaleString()}`);

// 주요 라이브러리 감지
const libraries = [
  { name: 'React', pattern: /React\./g },
  { name: 'React DOM', pattern: /ReactDOM/g },
  { name: 'Recharts', pattern: /recharts/gi },
  { name: 'Lucide Icons', pattern: /lucide-react/gi },
  { name: 'Date-fns', pattern: /date-fns/gi },
  { name: 'Axios', pattern: /axios/gi },
  { name: 'React Query', pattern: /@tanstack\/react-query/gi },
  { name: 'React Router', pattern: /react-router/gi },
  { name: 'Tailwind', pattern: /tailwind/gi },
  { name: 'React Hook Form', pattern: /react-hook-form/gi },
];

console.log('\n🔍 감지된 라이브러리:');
console.log('=====================================');

libraries.forEach(lib => {
  const matches = content.match(lib.pattern);
  if (matches && matches.length > 0) {
    console.log(`- ${lib.name}: ${matches.length}회 발견`);
  }
});

// 큰 코드 블록 찾기
console.log('\n📦 의심스러운 큰 코드 블록:');
console.log('=====================================');

// Recharts 관련 코드 찾기
const rechartsPattern = /function\s+\w*[Cc]hart[\w\s\S]{1000,}/g;
const chartMatches = content.match(rechartsPattern);
if (chartMatches) {
  console.log(`- 차트 관련 함수: ${chartMatches.length}개 (매우 큰 크기)`);
}

// 긴 문자열 찾기 (Base64, SVG 등)
const longStrings = content.match(/"[^"]{5000,}"/g);
if (longStrings) {
  console.log(`- 5000자 이상 문자열: ${longStrings.length}개`);
}

// 최적화 제안
console.log('\n💡 최적화 제안:');
console.log('=====================================');
console.log('1. 코드 스플리팅: 라우트별로 번들을 분리');
console.log('2. Recharts 대체: 더 가벼운 차트 라이브러리 고려');
console.log('3. Tree Shaking: 사용하지 않는 아이콘/컴포넌트 제거');
console.log('4. Dynamic Import: 무거운 컴포넌트는 필요할 때 로드');