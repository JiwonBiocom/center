import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../../lib/api';
import { 
  BarChart3, TrendingUp, Calendar, Clock, 
  DollarSign, Activity, Target, AlertCircle 
} from 'lucide-react';
import { format, differenceInDays } from 'date-fns';
import { ko } from 'date-fns/locale';

interface AnalyticsTabProps {
  customerId: number;
}

interface Analytics {
  visit_summary: {
    total_visits: number;
    first_visit: string;
    last_visit: string;
    visit_frequency: number;
    average_interval_days: number;
  };
  service_summary: {
    most_used_service: string;
    service_counts: Record<string, number>;
    total_sessions: number;
  };
  revenue_summary: {
    total_revenue: number;
    average_per_visit: number;
    revenue_by_month: Array<{
      month: string;
      revenue: number;
    }>;
  };
  patterns: {
    preferred_time: string;
    preferred_day: string;
    cancellation_rate: number;
    no_show_rate: number;
  };
}

export default function AnalyticsTab({ customerId }: AnalyticsTabProps) {
  const [dateRange, setDateRange] = useState('6months');

  // 고객 분석 데이터 조회
  const { data: analytics, isLoading, error } = useQuery<Analytics>({
    queryKey: ['customer-analytics', customerId, dateRange],
    queryFn: async () => {
      const response = await api.get(`/customers/${customerId}/analytics`, {
        params: { period: dateRange }
      });
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !analytics || !analytics.visit_summary || !analytics.service_summary || !analytics.revenue_summary || !analytics.patterns) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600">분석 데이터를 불러오는데 실패했습니다.</p>
        {error && <p className="text-sm text-gray-500 mt-2">오류: {(error as any).message || '알 수 없는 오류'}</p>}
      </div>
    );
  }

  // 서비스별 색상 매핑
  const serviceColors: Record<string, string> = {
    '브레인': '#8B5CF6',
    '펄스': '#3B82F6',
    '림프': '#10B981',
    '레드': '#EF4444',
    'AI바이크': '#F59E0B'
  };

  // 방문 주기 계산
  const getVisitFrequencyText = (avgDays: number) => {
    if (avgDays <= 7) return '주 1회 이상';
    if (avgDays <= 14) return '2주에 1회';
    if (avgDays <= 30) return '월 1회';
    if (avgDays <= 90) return '분기 1회';
    return '비정기적';
  };

  return (
    <div className="space-y-6">
      {/* 기간 선택 */}
      <div className="flex justify-end">
        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="1month">최근 1개월</option>
          <option value="3months">최근 3개월</option>
          <option value="6months">최근 6개월</option>
          <option value="1year">최근 1년</option>
          <option value="all">전체 기간</option>
        </select>
      </div>

      {/* 핵심 지표 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <Calendar className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold">{analytics.visit_summary.total_visits}회</span>
          </div>
          <p className="text-sm text-gray-600">총 방문 횟수</p>
          <p className="text-xs text-gray-500 mt-1">
            {getVisitFrequencyText(analytics.visit_summary.average_interval_days)}
          </p>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <Activity className="h-8 w-8 text-green-600" />
            <span className="text-2xl font-bold">{analytics.service_summary.total_sessions}회</span>
          </div>
          <p className="text-sm text-gray-600">총 서비스 이용</p>
          <p className="text-xs text-gray-500 mt-1">
            주로 {analytics.service_summary.most_used_service} 이용
          </p>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="h-8 w-8 text-yellow-600" />
            <span className="text-2xl font-bold">
              {analytics.revenue_summary.total_revenue.toLocaleString()}원
            </span>
          </div>
          <p className="text-sm text-gray-600">총 구매 금액</p>
          <p className="text-xs text-gray-500 mt-1">
            방문당 평균 {analytics.revenue_summary.average_per_visit.toLocaleString()}원
          </p>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between mb-4">
            <Clock className="h-8 w-8 text-purple-600" />
            <span className="text-2xl font-bold">
              {(() => {
                if (!analytics.visit_summary.last_visit) {
                  return '없음';
                }
                const lastVisitDate = new Date(analytics.visit_summary.last_visit);
                // Check if date is invalid or default (1970-01-01)
                if (lastVisitDate.getFullYear() <= 1970 || isNaN(lastVisitDate.getTime())) {
                  return '없음';
                }
                return `${differenceInDays(new Date(), lastVisitDate)}일`;
              })()}
            </span>
          </div>
          <p className="text-sm text-gray-600">마지막 방문 후</p>
          <p className="text-xs text-gray-500 mt-1">
            {(() => {
              if (!analytics.visit_summary.last_visit) {
                return '방문 기록 없음';
              }
              const lastVisitDate = new Date(analytics.visit_summary.last_visit);
              // Check if date is invalid or default (1970-01-01)
              if (lastVisitDate.getFullYear() <= 1970 || isNaN(lastVisitDate.getTime())) {
                return '방문 기록 없음';
              }
              return format(lastVisitDate, 'yyyy-MM-dd', { locale: ko });
            })()}
          </p>
        </div>
      </div>

      {/* 서비스 이용 분포 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          서비스별 이용 현황
        </h4>
        <div className="space-y-4">
          {Object.entries(analytics.service_summary.service_counts)
            .sort(([, a], [, b]) => b - a)
            .map(([service, count]) => {
              const percentage = (count / analytics.service_summary.total_sessions) * 100;
              return (
                <div key={service}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium">{service}</span>
                    <span className="text-sm text-gray-600">{count}회 ({percentage.toFixed(1)}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${percentage}%`,
                        backgroundColor: serviceColors[service] || '#6B7280'
                      }}
                    />
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* 월별 매출 추이 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          월별 구매 추이
        </h4>
        <div className="space-y-3">
          {analytics.revenue_summary.revenue_by_month.map((item) => {
            const maxRevenue = Math.max(...analytics.revenue_summary.revenue_by_month.map(m => m.revenue));
            const percentage = maxRevenue > 0 ? (item.revenue / maxRevenue) * 100 : 0;
            
            return (
              <div key={item.month}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium">
                    {format(new Date(item.month), 'yyyy년 MM월', { locale: ko })}
                  </span>
                  <span className="text-sm font-semibold">
                    {item.revenue.toLocaleString()}원
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 행동 패턴 분석 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Target className="h-5 w-5" />
            행동 패턴
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">선호 시간대</span>
              <span className="font-medium">{analytics.patterns.preferred_time || '정보 없음'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">선호 요일</span>
              <span className="font-medium">{analytics.patterns.preferred_day || '정보 없음'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">예약 취소율</span>
              <span className="font-medium">{analytics.patterns.cancellation_rate.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">노쇼율</span>
              <span className="font-medium">{analytics.patterns.no_show_rate.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4">고객 인사이트</h4>
          <div className="space-y-2 text-sm text-gray-600">
            {analytics.visit_summary.average_interval_days <= 14 && (
              <p>• 정기적으로 방문하는 충성 고객입니다.</p>
            )}
            {analytics.revenue_summary.average_per_visit > 100000 && (
              <p>• 높은 객단가를 보이는 VIP 고객입니다.</p>
            )}
            {analytics.service_summary.total_sessions > 50 && (
              <p>• 장기간 서비스를 이용한 단골 고객입니다.</p>
            )}
            {differenceInDays(new Date(), new Date(analytics.visit_summary.last_visit)) > 30 && (
              <p className="text-yellow-600">• 최근 방문이 뜸한 상태입니다. 관리가 필요합니다.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
