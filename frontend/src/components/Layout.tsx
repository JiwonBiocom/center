import { useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { Home, Users, Calendar, CreditCard, Package, TrendingUp, Settings, LogOut, TestTube, CalendarCheck, BarChart3, Info, Menu, X, Brain, Calculator, Tablet } from 'lucide-react'
import NotificationBell from './NotificationBell'
import MobileTabBar from './mobile/MobileTabBar'
import { useAuth } from '../contexts/AuthContext'
import { tokenManager } from '../lib/tokenManager'

export default function Layout() {
  const location = useLocation()
  const { user } = useAuth()
  const isMobileView = false // 모바일 모드 비활성화
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // console.log('Layout render - isMobileView:', isMobileView)

  const handleLogout = () => {
    tokenManager.handleLogout()
  }

  const baseMenuItems = [
    { path: '/', name: '대시보드', icon: Home },
    { path: '/customers', name: '고객 관리', icon: Users },
    { path: '/reservations', name: '예약 관리', icon: CalendarCheck },
    { path: '/services', name: '서비스 이용', icon: Calendar },
    { path: '/payments', name: '결제 관리', icon: CreditCard },
    { path: '/packages', name: '패키지 관리', icon: Package },
    { path: '/leads', name: '유입고객 관리', icon: TrendingUp },
    { path: '/kits', name: '검사키트 관리', icon: TestTube },
    { path: '/staff-schedule', name: '직원 근무표', icon: Calendar },
    { path: '/reports', name: '보고서 (개발중)', icon: BarChart3 },
  ]

  const adminMenuItems = [
    { path: '/algorithm-docs', name: '알고리즘', icon: Brain },
    { path: '/tablet-questionnaire', name: '태블릿 문진 (개발중)', icon: Tablet },
    { path: '/settings', name: '설정', icon: Settings },
  ]

  const generalMenuItems = [
    { path: '/about', name: '시스템 소개', icon: Info },
  ]

  // 마스터 전용 메뉴
  const masterMenuItems = [
    { path: '/master', name: '시스템 관리', icon: Settings },
  ]

  // 사용자 권한에 따른 메뉴 구성
  const menuItems = [
    ...baseMenuItems,
    ...(user?.role === 'admin' || user?.role === 'master' ? adminMenuItems : []),
    ...(user?.role === 'master' ? masterMenuItems : []),
    ...generalMenuItems
  ]



  return (
    <div className="min-h-screen bg-gray-50 flex relative">
      {/* Mobile Header */}
      {isMobileView && (
        <div className="fixed top-0 left-0 right-0 bg-white shadow-sm z-40">
          <div className="flex items-center justify-between p-4">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
            <img src="/aibio-logo.png" alt="AIBIO" className="h-8" />
            <NotificationBell />
          </div>
        </div>
      )}

      {/* Sidebar - Desktop always visible, Mobile slide-in */}
      <div className={`
        ${isMobileView ? 'fixed inset-y-0 left-0 z-50' : 'relative'}
        w-64 bg-white shadow-md flex flex-col h-screen transform transition-transform duration-300 ease-in-out
        ${isMobileView && !isMobileMenuOpen ? '-translate-x-full' : 'translate-x-0'}
      `}>
        <Link
          to="/"
          className="block p-6 hover:bg-gray-50 transition-colors flex-shrink-0"
          onClick={() => isMobileView && setIsMobileMenuOpen(false)}
        >
          <img src="/aibio-logo.png" alt="AIBIO" className="h-10 w-auto" />
          <p className="text-sm text-gray-500 mt-2">관리 시스템</p>
        </Link>

        <nav className="mt-6 flex-1 overflow-y-auto min-h-0">
          <div className="pb-4">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => isMobileView && setIsMobileMenuOpen(false)}
                  className={`flex items-center px-6 py-3 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-50 text-indigo-600 border-r-2 border-indigo-600'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3 flex-shrink-0" />
                  <span className="truncate">{item.name}</span>
                </Link>
              )
            })}
          </div>
        </nav>

        <div className="p-4 border-t bg-white flex-shrink-0 space-y-2">
          <button
            onClick={handleLogout}
            className="flex items-center w-full text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
          >
            <LogOut className="w-5 h-5 mr-3 flex-shrink-0" />
            <span className="truncate">로그아웃</span>
          </button>
        </div>
      </div>

      {/* Overlay for mobile menu */}
      {isMobileView && isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Main Content */}
      <div className={`flex-1 flex flex-col ${isMobileView ? 'pt-16' : ''}`}>
        {/* Desktop Header */}
        {!isMobileView && (
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-800">
                {menuItems.find(item => item.path === location.pathname)?.name || '페이지'}
              </h2>

              <div className="flex items-center gap-4">
                <NotificationBell />

                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center text-white font-medium">
                    {user?.name?.charAt(0) || 'A'}
                  </div>
                  <span className="text-sm text-gray-700">{user?.name || '관리자'}</span>
                </div>
              </div>
            </div>
          </header>
        )}

        {/* Page Content */}
        <div className={`flex-1 overflow-auto ${isMobileView ? 'pb-16' : ''}`}>
          <Outlet />
        </div>
      </div>

      {/* Mobile Tab Bar */}
      {isMobileView && <MobileTabBar />}
    </div>
  )
}
