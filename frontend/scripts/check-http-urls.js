#!/usr/bin/env node
/**
 * 빌드 전 HTTP URL 검증 스크립트
 * 소스 코드에 하드코딩된 HTTP API URL이 있으면 빌드 실패
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

console.log('🔍 Checking for hardcoded HTTP URLs...');

const patterns = [
  'http://center-production',
  'http://localhost:800[0-9]',
  'http://.*railway.app'
];

const srcDir = path.join(__dirname, '../src');
const files = glob.sync('**/*.{ts,tsx,js,jsx}', { cwd: srcDir });

let foundIssues = false;
const issues = [];

files.forEach(file => {
  const filePath = path.join(srcDir, file);
  const content = fs.readFileSync(filePath, 'utf8');
  
  patterns.forEach(pattern => {
    const regex = new RegExp(pattern, 'g');
    const matches = content.match(regex);
    
    if (matches && matches.length > 0) {
      // localhost는 개발 환경 기본값으로 허용
      if (pattern.includes('localhost') && content.includes('|| \'http://localhost:')) {
        return;
      }
      
      foundIssues = true;
      issues.push({
        file,
        pattern,
        matches: matches.slice(0, 3) // 최대 3개만 표시
      });
    }
  });
});

if (foundIssues) {
  console.error('\n❌ Found hardcoded HTTP URLs in source code:\n');
  issues.forEach(issue => {
    console.error(`  File: ${issue.file}`);
    console.error(`  Pattern: ${issue.pattern}`);
    console.error(`  Matches: ${issue.matches.join(', ')}\n`);
  });
  console.error('🚨 Build failed! Please use HTTPS URLs or environment variables.\n');
  process.exit(1);
} else {
  console.log('✅ No hardcoded HTTP URLs found in source code.');
  process.exit(0);
}