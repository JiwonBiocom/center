import { Link, useLocation } from 'react-router-dom';
import { Home, Calendar, Search, Bell, Menu } from 'lucide-react';

export default function MobileTabBar() {
  const location = useLocation();
  
  const tabs = [
    { path: '/', icon: Home, label: '홈' },
    { path: '/reservations', icon: Calendar, label: '예약' },
    { path: '/quick-search', icon: Search, label: '검색' },
    { path: '/notifications', icon: Bell, label: '알림' },
    { path: '/mobile-menu', icon: Menu, label: '메뉴' },
  ];
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 lg:hidden">
      <div className="flex justify-around items-center h-16 px-2">
        {tabs.map(tab => {
          const Icon = tab.icon;
          const isActive = location.pathname === tab.path;
          
          return (
            <Link
              key={tab.path}
              to={tab.path}
              className={`flex flex-col items-center justify-center flex-1 h-full transition-colors ${
                isActive 
                  ? 'text-indigo-600' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Icon className={`w-5 h-5 mb-1 ${isActive ? 'stroke-2' : ''}`} />
              <span className="text-xs font-medium">{tab.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}