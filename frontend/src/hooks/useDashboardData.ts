import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface DashboardStats {
  total_customers: number;
  today_revenue: number;
  monthly_revenue: number;
  last_30_days_revenue: number;
  active_packages: number;
  today_visits: number;
  new_customers: number;
}

interface PackageStats {
  active_purchases: number;
  total_remaining_sessions: number;
  expiring_this_month: number;
}

interface WeeklyStats {
  new_consultation_visits: number;
  conversion_rate: number;
  paying_customers: number;
  average_payment: number;
  weekly_revenue: number;
  week_start: string;
  week_end: string;
}

export function useDashboardData() {
  const [stats, setStats] = useState<DashboardStats>({
    total_customers: 0,
    today_revenue: 0,
    monthly_revenue: 0,
    last_30_days_revenue: 0,
    active_packages: 0,
    today_visits: 0,
    new_customers: 0
  });
  const [revenueData, setRevenueData] = useState<any[]>([]);
  const [monthlyRevenueData, setMonthlyRevenueData] = useState<any[]>([]);
  const [serviceData, setServiceData] = useState<any[]>([]);
  const [packageStats, setPackageStats] = useState<PackageStats>({
    active_purchases: 0,
    total_remaining_sessions: 0,
    expiring_this_month: 0
  });
  const [weeklyStats, setWeeklyStats] = useState<WeeklyStats>({
    new_consultation_visits: 0,
    conversion_rate: 0,
    paying_customers: 0,
    average_payment: 0,
    weekly_revenue: 0,
    week_start: '',
    week_end: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 🚀 1단계: 핵심 데이터 우선 로드 (통계 카드용)
      const [statsResponse, packageResponse, weeklyResponse] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/packages/purchases/stats'),
        api.get('/dashboard/weekly-stats')
      ]);

      // 핵심 데이터 즉시 설정 (사용자가 빨리 볼 수 있도록)
      setStats(statsResponse.data);
      setPackageStats(packageResponse.data);
      setWeeklyStats(weeklyResponse.data);
      
      // 로딩 상태 해제 (통계 카드가 먼저 표시됨)
      setLoading(false);

      // 🚀 2단계: 차트 데이터 지연 로드 (백그라운드에서)
      Promise.all([
        api.get('/dashboard/revenue-trend'),
        api.get('/dashboard/monthly-revenue'),
        api.get('/dashboard/service-usage-stats')
      ]).then(([trendResponse, monthlyResponse, serviceResponse]) => {
        const trendData = trendResponse.data.map((item: any) => ({
          date: new Date(item.date).getDate().toString(),
          revenue: item.revenue / 10000 // 만원 단위
        }));
        setRevenueData(trendData);
        
        const monthlyData = monthlyResponse.data.map((item: any) => ({
          month: `${item.month}월`,
          revenue: item.revenue / 10000 // 만원 단위
        }));
        setMonthlyRevenueData(monthlyData);
        
        setServiceData(serviceResponse.data);
      }).catch((error) => {
        console.error('Failed to fetch chart data:', error);
        // 차트 로딩 실패는 에러로 처리하지 않음 (통계는 이미 표시됨)
      });
      
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      setError('대시보드 데이터를 불러오는데 실패했습니다.');
      setLoading(false);
    }
  };

  return {
    stats,
    revenueData,
    monthlyRevenueData,
    serviceData,
    packageStats,
    weeklyStats,
    loading,
    error,
    refetch: fetchDashboardData
  };
}