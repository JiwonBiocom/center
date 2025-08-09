import { Link, Outlet, useLocation } from 'react-router-dom'
import { Home, Users, FileText, Package, CreditCard, BarChart3, UserPlus, LogOut } from 'lucide-react'

const navigation = [
  { name: '대시보드', href: '/', icon: Home },
  { name: '고객 관리', href: '/customers', icon: Users },
  { name: '리포트', href: '/reports', icon: BarChart3 },
  { name: '서비스 관리', href: '/services', icon: FileText },
  { name: '패키지 관리', href: '/packages', icon: Package },
  { name: '결제 관리', href: '/payments', icon: CreditCard },
  { name: '리드 관리', href: '/leads', icon: UserPlus },
]

export default function Layout() {
  const location = useLocation()

  const handleLogout = () => {
    // TODO: Implement logout
    window.location.href = '/login'
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <div className="flex flex-col h-0 flex-1 bg-gray-800">
            <div className="flex items-center h-16 flex-shrink-0 px-4 bg-gray-900">
              <h1 className="text-xl font-semibold text-white">AIBIO Center</h1>
            </div>
            <div className="flex-1 flex flex-col overflow-y-auto">
              <nav className="flex-1 px-2 py-4 space-y-1">
                {navigation.map((item) => {
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`
                        group flex items-center px-2 py-2 text-sm font-medium rounded-md
                        ${isActive
                          ? 'bg-gray-900 text-white'
                          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                        }
                      `}
                    >
                      <item.icon
                        className={`
                          mr-3 flex-shrink-0 h-6 w-6
                          ${isActive ? 'text-gray-300' : 'text-gray-400 group-hover:text-gray-300'}
                        `}
                      />
                      {item.name}
                    </Link>
                  )
                })}
              </nav>
              <div className="flex-shrink-0 flex bg-gray-700 p-4">
                <button
                  onClick={handleLogout}
                  className="flex items-center text-sm font-medium text-gray-300 hover:text-white"
                >
                  <LogOut className="mr-3 h-5 w-5" />
                  로그아웃
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className="md:hidden">
        <div className="fixed inset-0 flex z-40">
          {/* Mobile sidebar - add toggle functionality as needed */}
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden">
        <div className="md:hidden pl-1 pt-1 sm:pl-3 sm:pt-3">
          {/* Mobile menu button */}
        </div>
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <Outlet />
        </main>
      </div>
    </div>
  )
}