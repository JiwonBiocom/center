#!/usr/bin/env node
/**
 * OpenAPI 스키마에서 TypeScript 타입 생성
 * 
 * 백엔드의 OpenAPI 스키마를 읽어 TypeScript 타입을 자동 생성합니다.
 */
import { exec } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const openApiPath = path.join(__dirname, '..', 'openapi.json');
const outputPath = path.join(__dirname, '..', 'src', 'types', 'api-generated.ts');

// 타입 생성 함수
async function generateTypes() {
  console.log('🔄 TypeScript 타입 생성 시작...');

  // openapi.json 파일 존재 확인
  if (!fs.existsSync(openApiPath)) {
    console.error('❌ openapi.json 파일을 찾을 수 없습니다.');
    console.log('💡 백엔드에서 먼저 OpenAPI 스키마를 생성해주세요:');
    console.log('   cd ../backend && python scripts/generate_openapi.py');
    process.exit(1);
  }

  // 출력 디렉토리 생성
  const outputDir = path.dirname(outputPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // openapi-typescript 실행
  const command = `npx openapi-typescript ${openApiPath} -o ${outputPath}`;
  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error('❌ 타입 생성 중 오류 발생:', error);
      return;
    }

    if (stderr) {
      console.warn('⚠️ 경고:', stderr);
    }

    console.log('✅ TypeScript 타입이 생성되었습니다:', outputPath);

    // 생성된 파일에 헤더 추가
    const content = fs.readFileSync(outputPath, 'utf8');
    const header = `/**
 * 자동 생성된 TypeScript 타입 정의
 * 
 * ⚠️ 이 파일은 자동으로 생성됩니다. 직접 수정하지 마세요!
 * 
 * 생성 명령: npm run generate:types
 * 소스: ../backend/openapi.json
 * 생성일: ${new Date().toISOString()}
 */

`;

    fs.writeFileSync(outputPath, header + content);

    // 타입 요약 정보 출력
    const typeCount = (content.match(/export (interface|type) /g) || []).length;
    console.log(`📊 총 ${typeCount}개의 타입이 생성되었습니다.`);

    // 인덱스 파일 생성
    createIndexFile();
  });
}

// types/index.ts 파일 업데이트
function createIndexFile() {
  const indexPath = path.join(__dirname, '..', 'src', 'types', 'index.ts');
  const indexContent = `/**
 * 타입 정의 인덱스 파일
 */

// 자동 생성된 API 타입
export * from './api-generated';

// 수동으로 정의한 타입들
export * from './models';
export * from './forms';
export * from './common';

// API 응답 타입 alias
import { paths, components } from './api-generated';

export type APIComponents = components;
export type APIPaths = paths;

// 자주 사용하는 타입 alias
export type Customer = components['schemas']['Customer'];
export type CustomerCreate = components['schemas']['CustomerCreate'];
export type CustomerUpdate = components['schemas']['CustomerUpdate'];

export type Service = components['schemas']['ServiceUsage'];
export type ServiceCreate = components['schemas']['ServiceUsageCreate'];

export type Payment = components['schemas']['Payment'];
export type PaymentCreate = components['schemas']['PaymentCreate'];

export type Package = components['schemas']['Package'];
export type PackageCreate = components['schemas']['PackageCreate'];

export type User = components['schemas']['User'];
export type UserLogin = components['schemas']['UserLogin'];

// API 응답 타입
export type APIResponse<T = any> = components['schemas']['APIResponse'];
export type PaginatedResponse<T = any> = components['schemas']['PaginatedResponse'];
export type ErrorResponse = components['schemas']['ErrorResponse'];
`;

  fs.writeFileSync(indexPath, indexContent);
  console.log('✅ 타입 인덱스 파일이 업데이트되었습니다:', indexPath);
}

// 메인 실행
generateTypes().catch(console.error);