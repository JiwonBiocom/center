import { lazy, Suspense } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './contexts/AuthContext'
import { NotificationProvider } from './contexts/NotificationContext'
import { tokenManager } from './lib/tokenManager'
import { useEffect } from 'react'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import Login from './pages/Login' // 로그인은 항상 필요하므로 즉시 로드

// Lazy load all pages
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Customers = lazy(() => import('./pages/Customers'))
const Services = lazy(() => import('./pages/Services'))
const Payments = lazy(() => import('./pages/Payments'))
const Packages = lazy(() => import('./pages/Packages'))
const CustomerLeads = lazy(() => import('./pages/CustomerLeads'))
const CustomerLeadCampaigns = lazy(() => import('./pages/CustomerLeadCampaigns'))
const CustomerLeadAnalytics = lazy(() => import('./pages/CustomerLeadAnalytics'))
const Kits = lazy(() => import('./pages/Kits'))
const StaffSchedule = lazy(() => import('./pages/StaffSchedule'))
const Reports = lazy(() => import('./pages/Reports'))
const Settings = lazy(() => import('./pages/Settings'))
const About = lazy(() => import('./pages/About'))
const Reservations = lazy(() => import('./pages/Reservations'))
const QuickSearch = lazy(() => import('./pages/QuickSearch'))
const MobileMenu = lazy(() => import('./pages/MobileMenu'))
const AlgorithmDocs = lazy(() => import('./pages/AlgorithmDocs'))
const TabletQuestionnaire = lazy(() => import('./pages/TabletQuestionnaire'))

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

// 로딩 컴포넌트
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">로딩 중...</p>
      </div>
    </div>
  )
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
                  <Route index element={
                    <Suspense fallback={<PageLoader />}>
                      <Dashboard />
                    </Suspense>
                  } />
                  <Route path="customers" element={
                    <Suspense fallback={<PageLoader />}>
                      <Customers />
                    </Suspense>
                  } />
                  <Route path="services" element={
                    <Suspense fallback={<PageLoader />}>
                      <Services />
                    </Suspense>
                  } />
                  <Route path="payments" element={
                    <Suspense fallback={<PageLoader />}>
                      <Payments />
                    </Suspense>
                  } />
                  <Route path="packages" element={
                    <Suspense fallback={<PageLoader />}>
                      <Packages />
                    </Suspense>
                  } />
                  <Route path="leads" element={
                    <Suspense fallback={<PageLoader />}>
                      <CustomerLeads />
                    </Suspense>
                  } />
                  <Route path="leads/campaigns" element={
                    <Suspense fallback={<PageLoader />}>
                      <CustomerLeadCampaigns />
                    </Suspense>
                  } />
                  <Route path="leads/analytics" element={
                    <Suspense fallback={<PageLoader />}>
                      <CustomerLeadAnalytics />
                    </Suspense>
                  } />
                  <Route path="kits" element={
                    <Suspense fallback={<PageLoader />}>
                      <Kits />
                    </Suspense>
                  } />
                  <Route path="staff-schedule" element={
                    <Suspense fallback={<PageLoader />}>
                      <StaffSchedule />
                    </Suspense>
                  } />
                  <Route path="reports" element={
                    <Suspense fallback={<PageLoader />}>
                      <Reports />
                    </Suspense>
                  } />
                  <Route path="settings" element={
                    <Suspense fallback={<PageLoader />}>
                      <Settings />
                    </Suspense>
                  } />
                  <Route path="about" element={
                    <Suspense fallback={<PageLoader />}>
                      <About />
                    </Suspense>
                  } />
                  <Route path="reservations" element={
                    <Suspense fallback={<PageLoader />}>
                      <Reservations />
                    </Suspense>
                  } />
                  <Route path="quick-search" element={
                    <Suspense fallback={<PageLoader />}>
                      <QuickSearch />
                    </Suspense>
                  } />
                  <Route path="mobile-menu" element={
                    <Suspense fallback={<PageLoader />}>
                      <MobileMenu />
                    </Suspense>
                  } />
                  <Route path="notifications" element={
                    <Suspense fallback={<PageLoader />}>
                      <div className="p-4"><h1>알림 페이지 (TBD)</h1></div>
                    </Suspense>
                  } />
                  <Route path="algorithm-docs" element={
                    <Suspense fallback={<PageLoader />}>
                      <AlgorithmDocs />
                    </Suspense>
                  } />
                  <Route path="tablet-questionnaire" element={
                    <Suspense fallback={<PageLoader />}>
                      <TabletQuestionnaire />
                    </Suspense>
                  } />
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