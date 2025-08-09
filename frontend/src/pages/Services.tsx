import { useState, useEffect } from 'react';
import { Calendar, TrendingUp, BarChart3, Download } from 'lucide-react';
import { api } from '../lib/api';
import ServiceCalendar from '../components/services/ServiceCalendar';
import ServiceList from '../components/services/ServiceList';
import ServiceStatsCard from '../components/services/ServiceStatsCard';
import { useServiceData } from '../hooks/useServiceData';

interface ServiceStats {
  total_services: number;
  unique_customers: number;
  most_popular_service: string;
  total_revenue: number;
  average_daily_services: number;
}

export default function Services() {
  const [stats, setStats] = useState<ServiceStats | null>(null);
  const [viewMode, setViewMode] = useState<'calendar' | 'analytics'>('calendar');
  
  const {
    usages,
    loading,
    selectedDate,
    calendarData,
    currentYear,
    currentMonth,
    setSelectedDate,
    handleMonthChange,
    handleExcelExport
  } = useServiceData();

  useEffect(() => {
    fetchServiceStats();
  }, [currentYear, currentMonth]);

  const fetchServiceStats = async () => {
    try {
      const response = await api.get('/api/v1/services/stats', {
        params: {
          year: currentYear,
          month: currentMonth
        }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch service stats:', error);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <p className="text-gray-500">로딩 중...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">서비스 분석</h1>
        <div className="flex items-center space-x-4">
          {/* 뷰 모드 토글 */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('calendar')}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'calendar'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Calendar className="h-4 w-4 mr-2" />
              캘린더
            </button>
            <button
              onClick={() => setViewMode('analytics')}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'analytics'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              분석
            </button>
          </div>
          
          <button
            onClick={handleExcelExport}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Download className="h-4 w-4 mr-2" />
            엑셀 다운로드
          </button>
        </div>
      </div>

      {/* 통계 카드 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <ServiceStatsCard
            title="총 서비스"
            value={stats.total_services}
            icon={<TrendingUp className="h-5 w-5" />}
            color="blue"
          />
          <ServiceStatsCard
            title="고객 수"
            value={stats.unique_customers}
            icon={<TrendingUp className="h-5 w-5" />}
            color="green"
          />
          <ServiceStatsCard
            title="인기 서비스"
            value={stats.most_popular_service || 'N/A'}
            icon={<BarChart3 className="h-5 w-5" />}
            color="purple"
            isText
          />
          <ServiceStatsCard
            title="총 매출"
            value={`${stats.total_revenue.toLocaleString()}원`}
            icon={<TrendingUp className="h-5 w-5" />}
            color="yellow"
            isText
          />
          <ServiceStatsCard
            title="일평균 서비스"
            value={Math.round(stats.average_daily_services * 10) / 10}
            icon={<BarChart3 className="h-5 w-5" />}
            color="indigo"
          />
        </div>
      )}

      {/* 메인 컨텐츠 */}
      {viewMode === 'calendar' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ServiceCalendar
              currentYear={currentYear}
              currentMonth={currentMonth}
              selectedDate={selectedDate}
              calendarData={calendarData}
              onDateSelect={setSelectedDate}
              onMonthChange={handleMonthChange}
            />
          </div>

          <ServiceList
            selectedDate={selectedDate}
            usages={usages}
          />
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">서비스 분석 차트</h3>
          <div className="text-center text-gray-500">
            <BarChart3 className="h-16 w-16 mx-auto mb-4 text-gray-300" />
            <p>상세 분석 차트는 향후 추가 예정입니다.</p>
            <p className="text-sm">현재는 기본 통계 정보를 제공합니다.</p>
          </div>
        </div>
      )}
    </div>
  );
}