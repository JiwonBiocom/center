import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Users, User, Building2, Calendar, Bell, Database, FileText, Shield, Lock, MessageSquare, Award, Info } from 'lucide-react'
import '../lib/utils/diagnoseSettings' // 진단 도구 로드
import UserManagement from '../components/settings/UserManagement'
import SystemSettings from '../components/settings/SystemSettings'
import ServiceTypeManagement from '../components/settings/ServiceTypeManagement'
import ProfileSettings from '../components/settings/ProfileSettings'
import PasswordSettings from '../components/settings/PasswordSettings'
import NotificationSettings from '../components/settings/NotificationSettings'
import BackupSettings from '../components/settings/BackupSettings'
import ReportSettings from '../components/settings/ReportSettings'
import KakaoSettings from '../components/settings/KakaoSettings'
import MembershipSettings from '../components/settings/MembershipSettings'
import AboutSystem from '../components/settings/AboutSystem'
import MasterSettings from '../components/settings/MasterSettings'

export default function Settings() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')
  const isAdmin = user?.role === 'admin'
  const isMaster = user?.role === 'master'

  // 디버깅용 로그
  console.log('[Settings] Rendering with:', {
    user,
    userRole: user?.role,
    isAdmin,
    activeTab
  })

  // 컴포넌트 마운트 시 한 번만 실행
  useEffect(() => {
    console.log('[Settings] Component mounted');
    if (!user) {
      console.warn('[Settings] No user data available');
    }
  }, [])

  const tabs = [
    { id: 'profile', name: '개인 정보', icon: User, admin: false },
    { id: 'password', name: '비밀번호 변경', icon: Lock, admin: false },
    { id: 'about', name: '시스템 소개', icon: Info, admin: false },
    ...(isAdmin || isMaster ? [
      { id: 'users', name: '사용자 관리', icon: Users, admin: true },
      { id: 'system', name: '시스템 설정', icon: Building2, admin: true },
      { id: 'services', name: '서비스 타입 관리', icon: Calendar, admin: true },
      { id: 'membership', name: '회원 등급 관리', icon: Award, admin: true },
      { id: 'notifications', name: '알림 설정', icon: Bell, admin: true },
      { id: 'kakao', name: '카카오톡 설정', icon: MessageSquare, admin: true },
      { id: 'backup', name: '백업 및 복원', icon: Database, admin: true },
      { id: 'reports', name: '보고서 설정', icon: FileText, admin: true },
    ] : []),
    ...(isMaster ? [
      { id: 'master', name: '시스템 관리', icon: Shield, admin: true, master: true },
    ] : []),
  ]

  const renderContent = () => {
    console.log('[Settings] Rendering content for tab:', activeTab)

    try {
      switch (activeTab) {
        case 'profile':
          return <ProfileSettings />
        case 'password':
          return <PasswordSettings />
        case 'about':
          return <AboutSystem />
        case 'users':
          return isAdmin || isMaster ? <UserManagement /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'system':
          return isAdmin || isMaster ? <SystemSettings /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'services':
          return isAdmin || isMaster ? <ServiceTypeManagement /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'membership':
          return isAdmin || isMaster ? <MembershipSettings /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'notifications':
          return isAdmin || isMaster ? <NotificationSettings /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'kakao':
          return isAdmin || isMaster ? <KakaoSettings /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'backup':
          return isAdmin || isMaster ? <BackupSettings /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'reports':
          return isAdmin || isMaster ? <ReportSettings /> : <div className="text-gray-500">관리자 권한이 필요합니다.</div>
        case 'master':
          return isMaster ? <MasterSettings /> : <div className="text-gray-500">마스터 권한이 필요합니다.</div>
        default:
          return <div className="text-red-500">알 수 없는 탭: {activeTab}</div>
      }
    } catch (error) {
      console.error('[Settings] Error rendering content:', error)
      return <div className="text-red-500">컴포넌트 로드 중 오류가 발생했습니다: {error instanceof Error ? error.message : String(error)}</div>
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">설정</h1>
        <p className="text-gray-600 mt-2">시스템 설정을 관리하고 개인정보를 수정할 수 있습니다</p>
        {/* 디버깅용 사용자 정보 */}
        {user && (
          <div className="mt-4 p-4 bg-gray-100 rounded-md text-sm">
            <p>현재 사용자: {user.name} ({user.email})</p>
            <p>권한: {user.role}</p>
            <p>관리자 권한: {isAdmin ? '예' : '아니오'}</p>
            <p>마스터 권한: {isMaster ? '예' : '아니오'}</p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-12 min-h-[600px]">
          {/* 탭 메뉴 */}
          <div className="col-span-3 border-r border-gray-200 p-4">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-indigo-50 text-indigo-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {tab.name}
                    {tab.admin && !tab.master && (
                      <Shield className="w-4 h-4 ml-auto text-orange-500" />
                    )}
                    {tab.master && (
                      <Shield className="w-4 h-4 ml-auto text-red-500" />
                    )}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* 컨텐츠 영역 */}
          <div className="col-span-9 p-6">
            {renderContent() || (
              <div className="text-center text-gray-500">
                <p>표시할 컨텐츠가 없습니다.</p>
                <p className="text-sm mt-2">activeTab: {activeTab}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
