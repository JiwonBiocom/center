import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import { NotificationProvider } from './contexts/NotificationContext'
import { tokenManager } from './lib/tokenManager'
import { useEffect } from 'react'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Customers from './pages/Customers'
import Services from './pages/Services'
import Payments from './pages/Payments'
import Packages from './pages/Packages'
import CustomerLeads from './pages/CustomerLeads'
import CustomerLeadCampaigns from './pages/CustomerLeadCampaigns'
import CustomerLeadAnalytics from './pages/CustomerLeadAnalytics'
import Kits from './pages/Kits'
import StaffSchedule from './pages/StaffSchedule'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import About from './pages/About'
import Reservations from './pages/Reservations'
import Login from './pages/Login'
import QuickSearch from './pages/QuickSearch'
import MobileMenu from './pages/MobileMenu'
import AlgorithmDocs from './pages/AlgorithmDocs'
import TabletQuestionnaire from './pages/TabletQuestionnaire'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token')
  return token ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  useEffect(() => {
    // 토큰 자동 갱신 설정
    tokenManager.setupAutoRefresh()
    // 다중 탭 동기화 설정
    tokenManager.setupTabSync()
  }, [])

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <NotificationProvider>
            <Router>
                <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Layout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Dashboard />} />
                  <Route path="customers" element={<Customers />} />
                  <Route path="services" element={<Services />} />
                  <Route path="payments" element={<Payments />} />
                  <Route path="packages" element={<Packages />} />
                  <Route path="leads" element={<CustomerLeads />} />
                  <Route path="leads/campaigns" element={<CustomerLeadCampaigns />} />
                  <Route path="leads/analytics" element={<CustomerLeadAnalytics />} />
                  <Route path="kits" element={<Kits />} />
                  <Route path="staff-schedule" element={<StaffSchedule />} />
                  <Route path="reports" element={<Reports />} />
                  <Route path="settings" element={<Settings />} />
                  <Route path="about" element={<About />} />
                  <Route path="reservations" element={<Reservations />} />
                  <Route path="quick-search" element={<QuickSearch />} />
                  <Route path="mobile-menu" element={<MobileMenu />} />
                  <Route path="notifications" element={<div className="p-4"><h1>알림 페이지 (TBD)</h1></div>} />
                  <Route path="algorithm-docs" element={<AlgorithmDocs />} />
                  <Route path="tablet-questionnaire" element={<TabletQuestionnaire />} />
                </Route>
                </Routes>
              </Router>
          </NotificationProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App