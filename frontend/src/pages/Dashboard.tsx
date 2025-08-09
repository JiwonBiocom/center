import { TrendingUp, Users, Calendar, Package, UserPlus } from 'lucide-react';
import { useDashboardData } from '../hooks/useDashboardData';
// import MobileDashboard from '../components/mobile/MobileDashboard';
import DashboardHeader from '../components/dashboard/DashboardHeader';
import DashboardSkeleton from '../components/dashboard/DashboardSkeleton';
import StatCard from '../components/dashboard/StatCard';
import LeadStrategySection from '../components/dashboard/LeadStrategySection';
import CustomerSatisfactionSection from '../components/dashboard/CustomerSatisfactionSection';
import WeeklyStatusSection from '../components/dashboard/WeeklyStatusSection';
import MonthlyRevenueChart from '../components/dashboard/charts/MonthlyRevenueChart';
import DailyRevenueChart from '../components/dashboard/charts/DailyRevenueChart';
import ServiceUsageChart from '../components/dashboard/charts/ServiceUsageChart';

export default function Dashboard() {
  const isMobileView = false; // 모바일 모드 비활성화
  const {
    stats,
    revenueData,
    monthlyRevenueData,
    serviceData,
    weeklyStats,
    loading,
    error
  } = useDashboardData();

  const statCards = [
    {
      title: '전체 고객',
      value: `${stats.total_customers.toLocaleString()}명`,
      icon: Users,
      color: 'bg-blue-500'
    },
    {
      title: '최근 30일 매출',
      value: `₩${stats.last_30_days_revenue.toLocaleString()}`,
      icon: TrendingUp,
      color: 'bg-green-500'
    },
    {
      title: '활성 패키지',
      value: `${stats.active_packages.toLocaleString()}개`,
      icon: Package,
      color: 'bg-orange-500'
    },
    {
      title: '오늘 방문',
      value: `${stats.today_visits.toLocaleString()}명`,
      icon: Calendar,
      color: 'bg-pink-500'
    },
    {
      title: '신규 고객 (월)',
      value: `${stats.new_customers.toLocaleString()}명`,
      icon: UserPlus,
      color: 'bg-indigo-500'
    }
  ]

  // 모바일 대시보드 비활성화
  // if (isMobileView) {
  //   return <MobileDashboard />;
  // }

  if (loading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="p-8">
      <DashboardHeader />
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {statCards.map((card, index) => (
          <StatCard key={index} {...card} />
        ))}
      </div>

      <LeadStrategySection />
      
      <WeeklyStatusSection weeklyData={weeklyStats} />
      
      <CustomerSatisfactionSection />

      {/* 월별 매출 차트 - 전체 너비 */}
      <div className="mt-8">
        <MonthlyRevenueChart data={monthlyRevenueData} />
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <DailyRevenueChart data={revenueData} />
        <ServiceUsageChart data={serviceData} />
      </div>
    </div>
  )
}