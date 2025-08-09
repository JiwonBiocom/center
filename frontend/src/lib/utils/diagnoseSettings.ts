// 설정 페이지 진단 유틸리티
import { api } from '../api';

// 컴포넌트를 정적으로 import
import ProfileSettings from '../../components/settings/ProfileSettings';
import PasswordSettings from '../../components/settings/PasswordSettings';
import UserManagement from '../../components/settings/UserManagement';
import SystemSettings from '../../components/settings/SystemSettings';
import ServiceTypeManagement from '../../components/settings/ServiceTypeManagement';
import NotificationSettings from '../../components/settings/NotificationSettings';
import BackupSettings from '../../components/settings/BackupSettings';
import ReportSettings from '../../components/settings/ReportSettings';
import KakaoSettings from '../../components/settings/KakaoSettings';

// 컴포넌트 매핑 객체
const settingsComponents = {
  ProfileSettings,
  PasswordSettings,
  UserManagement,
  SystemSettings,
  ServiceTypeManagement,
  NotificationSettings,
  BackupSettings,
  ReportSettings,
  KakaoSettings
};

export async function diagnoseSettings() {
  console.log('=== 설정 페이지 진단 시작 ===');
  
  // 1. 경로 확인
  console.log('1. 현재 경로:', window.location.pathname);
  
  // 2. API 연결 확인
  console.log('\n2. API 연결 테스트:');
  try {
    const response = await api.get('/api/v1/auth/me');
    if (response.status === 200) {
      console.log('✅ API 연결 성공');
      console.log('현재 사용자:', response.data.email);
    } else {
      console.error('❌ API 응답 오류:', response.status, response.statusText);
    }
  } catch (error) {
    console.error('❌ API 연결 실패:', error);
  }
  
  // 3. 컴포넌트 import 확인
  console.log('\n3. 컴포넌트 로드 테스트:');
  const components = [
    'ProfileSettings',
    'PasswordSettings',
    'UserManagement',
    'SystemSettings',
    'ServiceTypeManagement',
    'NotificationSettings',
    'BackupSettings',
    'ReportSettings',
    'KakaoSettings'
  ] as const;
  
  for (const comp of components) {
    const Component = settingsComponents[comp];
    if (Component) {
      console.log(`✅ ${comp}: 로드 성공`);
    } else {
      console.error(`❌ ${comp}: 컴포넌트를 찾을 수 없음`);
    }
  }
  
  // 4. React 상태 확인
  console.log('\n4. React 상태:');
  const reactRoot = document.getElementById('root');
  if (reactRoot) {
    console.log('✅ React root 요소 발견');
    console.log('자식 요소 수:', reactRoot.children.length);
  } else {
    console.error('❌ React root 요소를 찾을 수 없음');
  }
  
  // 5. 라우터 정보
  console.log('\n5. 라우터 정보:');
  console.log('pathname:', window.location.pathname);
  console.log('search:', window.location.search);
  console.log('hash:', window.location.hash);
  
  // 6. localStorage 확인
  console.log('\n6. localStorage 데이터:');
  console.log('token 존재:', !!localStorage.getItem('token'));
  console.log('user 존재:', !!localStorage.getItem('user'));
  console.log('refreshToken 존재:', !!localStorage.getItem('refreshToken'));
  
  console.log('\n=== 진단 완료 ===');
}

// 개발 환경에서 전역으로 노출
if (import.meta.env.DEV) {
  (window as any).diagnoseSettings = diagnoseSettings;
}