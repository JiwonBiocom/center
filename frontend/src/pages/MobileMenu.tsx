import { Link } from 'react-router-dom';
import { 
  Users, Calendar, CreditCard, Package, TrendingUp, 
  TestTube, CalendarCheck, BarChart3, Settings, Info,
  LogOut, ChevronRight
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { tokenManager } from '../lib/tokenManager';

export default function MobileMenu() {
  const { user } = useAuth();
  
  const handleLogout = () => {
    tokenManager.handleLogout();
  };

  const menuGroups = [
    {
      title: '주요 기능',
      items: [
        { path: '/customers', name: '고객 관리', icon: Users },
        { path: '/reservations', name: '예약 관리', icon: CalendarCheck },
        { path: '/services', name: '서비스 이용', icon: Calendar },
        { path: '/payments', name: '결제 관리', icon: CreditCard },
      ]
    },
    {
      title: '관리 기능',
      items: [
        { path: '/packages', name: '패키지 관리', icon: Package },
        { path: '/leads', name: '유입고객 관리', icon: TrendingUp },
        { path: '/kits', name: '검사키트 관리', icon: TestTube },
        { path: '/staff-schedule', name: '직원 근무표', icon: Calendar },
      ]
    },
    {
      title: '기타',
      items: [
        { path: '/reports', name: '보고서', icon: BarChart3 },
        { path: '/settings', name: '설정', icon: Settings },
        { path: '/about', name: '시스템 소개', icon: Info },
      ]
    }
  ];

  return (
    <div className="p-4 pb-20 bg-gray-50 min-h-screen">
      {/* 사용자 정보 */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-4 flex items-center">
        <div className="w-12 h-12 bg-indigo-500 rounded-full flex items-center justify-center text-white font-bold text-lg mr-3">
          {user?.name?.charAt(0) || 'A'}
        </div>
        <div>
          <p className="font-semibold">{user?.name || '관리자'}</p>
          <p className="text-sm text-gray-600">{user?.email || 'admin@aibio.com'}</p>
        </div>
      </div>

      {/* 메뉴 그룹 */}
      {menuGroups.map((group, groupIndex) => (
        <div key={groupIndex} className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2 px-1">{group.title}</h3>
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            {group.items.map((item, index) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center justify-between p-4 hover:bg-gray-50 transition-colors ${
                    index !== group.items.length - 1 ? 'border-b border-gray-100' : ''
                  }`}
                >
                  <div className="flex items-center">
                    <Icon className="w-5 h-5 text-gray-600 mr-3" />
                    <span className="font-medium text-gray-900">{item.name}</span>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </Link>
              );
            })}
          </div>
        </div>
      ))}

      {/* 로그아웃 버튼 */}
      <button
        onClick={handleLogout}
        className="w-full bg-white rounded-lg shadow-sm p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center">
          <LogOut className="w-5 h-5 text-red-600 mr-3" />
          <span className="font-medium text-red-600">로그아웃</span>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </button>
    </div>
  );
}