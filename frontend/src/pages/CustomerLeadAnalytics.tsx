import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { BarChart3, TrendingUp, Users, CheckCircle, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

interface AnalyticsData {
  overview: {
    total_leads: number;
    converted_leads: number;
    conversion_rate: number;
    avg_conversion_days: number;
    active_leads: number;
    lost_leads: number;
  };
  channel_performance: Array<{
    channel: string;
    leads: number;
    conversions: number;
    conversion_rate: number;
    avg_days_to_convert: number;
  }>;
  monthly_trends: Array<{
    month: string;
    leads: number;
    conversions: number;
    conversion_rate: number;
  }>;
  funnel_analysis: {
    total_leads: number;
    db_entered: number;
    phone_consulted: number;
    visit_consulted: number;
    converted: number;
  };
  regional_stats: Array<{
    region: string;
    leads: number;
    conversion_rate: number;
  }>;
  campaign_performance: Array<{
    campaign_name: string;
    targets: number;
    conversions: number;
    conversion_rate: number;
    roi: number;
  }>;
}

export default function CustomerLeadAnalytics() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    from: new Date(new Date().setMonth(new Date().getMonth() - 3)).toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/customer-leads/analytics', {
        params: {
          date_from: dateRange.from,
          date_to: dateRange.to
        }
      });
      setAnalyticsData(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">분석 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">분석 데이터를 불러올 수 없습니다.</p>
        </div>
      </div>
    );
  }

  const { overview, channel_performance, monthly_trends, funnel_analysis, regional_stats } = analyticsData;

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">유입고객 분석 대시보드</h1>
            <p className="text-sm text-gray-600 mt-1">
              유입고객의 전환율과 성과를 분석합니다.
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">기간:</label>
              <input
                type="date"
                value={dateRange.from}
                onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
              <span className="text-gray-500">~</span>
              <input
                type="date"
                value={dateRange.to}
                onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
                className="px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
            </div>
            
            <Link
              to="/leads"
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
            >
              유입고객 관리로 돌아가기
            </Link>
          </div>
        </div>

        {/* 핵심 지표 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <Users className="w-8 h-8 text-blue-500" />
              <span className="text-2xl font-bold text-gray-900">{overview.total_leads}</span>
            </div>
            <p className="text-sm font-medium text-gray-600">총 유입고객</p>
            <p className="text-xs text-gray-500 mt-1">전체 기간</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <CheckCircle className="w-8 h-8 text-green-500" />
              <span className="text-2xl font-bold text-green-600">{overview.converted_leads}</span>
            </div>
            <p className="text-sm font-medium text-gray-600">전환 고객</p>
            <p className="text-xs text-gray-500 mt-1">등록 완료</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <TrendingUp className="w-8 h-8 text-indigo-500" />
              <span className="text-2xl font-bold text-indigo-600">{overview.conversion_rate}%</span>
            </div>
            <p className="text-sm font-medium text-gray-600">전환율</p>
            <p className="text-xs text-gray-500 mt-1">평균 {overview.avg_conversion_days}일 소요</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <Target className="w-8 h-8 text-orange-500" />
              <span className="text-2xl font-bold text-orange-600">{overview.active_leads}</span>
            </div>
            <p className="text-sm font-medium text-gray-600">진행중 리드</p>
            <p className="text-xs text-gray-500 mt-1">상담 진행중</p>
          </div>
        </div>

        {/* 깔때기 분석 */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">전환 깔때기 분석</h2>
          <div className="space-y-4">
            {[
              { label: '전체 유입', value: funnel_analysis.total_leads, color: 'bg-gray-200' },
              { label: 'DB 입력', value: funnel_analysis.db_entered, color: 'bg-blue-200' },
              { label: '전화 상담', value: funnel_analysis.phone_consulted, color: 'bg-yellow-200' },
              { label: '방문 상담', value: funnel_analysis.visit_consulted, color: 'bg-purple-200' },
              { label: '등록 완료', value: funnel_analysis.converted, color: 'bg-green-200' }
            ].map((stage) => {
              const percentage = funnel_analysis.total_leads > 0 
                ? Math.round((stage.value / funnel_analysis.total_leads) * 100) 
                : 0;
              return (
                <div key={stage.label} className="relative">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-700">{stage.label}</span>
                    <span className="text-sm text-gray-600">{stage.value}명 ({percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-8">
                    <div
                      className={`${stage.color} h-8 rounded-full flex items-center justify-center transition-all`}
                      style={{ width: `${percentage}%` }}
                    >
                      {percentage > 10 && (
                        <span className="text-xs font-medium text-gray-700">{percentage}%</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 채널별 성과 */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">채널별 성과</h2>
            <div className="space-y-3">
              {channel_performance.map((channel) => (
                <div key={channel.channel} className="border-b pb-3 last:border-0">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium text-gray-700">{channel.channel || '미분류'}</span>
                    <span className="text-sm text-gray-600">{channel.leads}명</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">전환율:</span>
                      <span className="ml-2 font-medium text-indigo-600">{channel.conversion_rate}%</span>
                    </div>
                    <div>
                      <span className="text-gray-500">평균 소요일:</span>
                      <span className="ml-2 font-medium">{channel.avg_days_to_convert}일</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 지역별 통계 */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">지역별 분포</h2>
            <div className="space-y-3">
              {regional_stats.slice(0, 10).map((region) => (
                <div key={region.region} className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">{region.region || '미분류'}</span>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-600">{region.leads}명</span>
                    <span className="text-sm font-medium text-indigo-600">{region.conversion_rate}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 월별 트렌드 */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">월별 트렌드</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    월
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    유입
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    전환
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    전환율
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    전월 대비
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {monthly_trends.map((trend, index) => {
                  const prevTrend = monthly_trends[index - 1];
                  const rateChange = prevTrend 
                    ? trend.conversion_rate - prevTrend.conversion_rate 
                    : 0;
                  
                  return (
                    <tr key={trend.month}>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {trend.month}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-900">
                        {trend.leads}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-900">
                        {trend.conversions}
                      </td>
                      <td className="px-4 py-3 text-sm text-right font-medium text-indigo-600">
                        {trend.conversion_rate}%
                      </td>
                      <td className="px-4 py-3 text-sm text-right">
                        {index > 0 && (
                          <span className={`font-medium ${rateChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {rateChange >= 0 ? '+' : ''}{rateChange.toFixed(1)}%
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}