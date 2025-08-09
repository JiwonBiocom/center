import { useState, useEffect } from 'react';
import { TrendingUp, Users, DollarSign, Calculator, CalendarIcon, BarChart3 } from 'lucide-react';
import { api } from '../../lib/api';
import { formatCurrency } from '../../lib/utils';

interface KeyMetrics {
  new_visit_consults: number;
  converted_customers: number;
  conversion_rate: number;
  total_payment_customers: number;
  total_revenue: number;
  avg_payment_amount: number;
}

interface Formula {
  description: string;
  calculation: string;
  values: {
    [key: string]: number;
  };
}

interface TrendData {
  month?: string;
  week?: string;
  visit_consults: number;
  conversions: number;
  conversion_rate: number;
  payment_customers: number;
  revenue: number;
  avg_payment_amount?: number;
}

interface KeyMetricsData {
  target_month: string;
  key_metrics: KeyMetrics;
  formulas: {
    formula1: Formula;
    formula2: Formula;
  };
  monthly_trends: TrendData[];
  weekly_trends: TrendData[];
}

export default function KeyMetricsStats() {
  const [data, setData] = useState<KeyMetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'monthly' | 'weekly'>('monthly');
  const [selectedMonth, setSelectedMonth] = useState<string>('');

  useEffect(() => {
    fetchKeyMetrics();
  }, [selectedMonth]);

  const fetchKeyMetrics = async () => {
    try {
      const params = selectedMonth ? { target_month: selectedMonth } : {};
      const response = await api.get('/api/v1/customer-leads/key-metrics', { params });
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch key metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const { key_metrics, formulas, monthly_trends, weekly_trends, target_month } = data;

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white p-6 rounded-lg">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <TrendingUp className="w-6 h-6" />
              전월 핵심지표
            </h2>
            <p className="text-indigo-100 mt-1">{target_month} 기준</p>
          </div>
          <div className="flex items-center gap-2">
            <CalendarIcon className="w-5 h-5" />
            <input
              type="month"
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(e.target.value)}
              className="px-3 py-2 rounded text-gray-900"
            />
          </div>
        </div>
      </div>

      {/* 핵심 공식 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 유입 지표 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-l-4 border-l-blue-500">
          <div className="flex items-center gap-3 mb-4">
            <Calculator className="w-6 h-6 text-blue-500" />
            <h3 className="text-lg font-semibold text-gray-900">유입 지표</h3>
          </div>
          <p className="text-sm text-gray-600 mb-3">{formulas.formula1.description}</p>
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-lg font-mono text-blue-800">{formulas.formula1.calculation}</p>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">{formulas.formula1.values.visit_consults}</p>
              <p className="text-xs text-gray-500">방문상담</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">{formulas.formula1.values.conversion_rate}%</p>
              <p className="text-xs text-gray-500">전환율</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{formulas.formula1.values.result}명</p>
              <p className="text-xs text-gray-500">결제고객</p>
            </div>
          </div>
        </div>

        {/* 결제 지표 */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-l-4 border-l-green-500">
          <div className="flex items-center gap-3 mb-4">
            <DollarSign className="w-6 h-6 text-green-500" />
            <h3 className="text-lg font-semibold text-gray-900">결제 지표</h3>
          </div>
          <p className="text-sm text-gray-600 mb-3">{formulas.formula2.description}</p>
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-lg font-mono text-green-800">{formulas.formula2.calculation}</p>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-green-600">{formulas.formula2.values.payment_customers}명</p>
              <p className="text-xs text-gray-500">결제고객</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(formulas.formula2.values.avg_amount)}</p>
              <p className="text-xs text-gray-500">평균객단가</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(formulas.formula2.values.result)}</p>
              <p className="text-xs text-gray-500">매출액</p>
            </div>
          </div>
        </div>
      </div>

      {/* 상세 지표 */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border text-center">
          <div className="text-2xl font-bold text-blue-600">{key_metrics.new_visit_consults}</div>
          <div className="text-sm text-gray-600">신규 방문상담</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border text-center">
          <div className="text-2xl font-bold text-green-600">{key_metrics.converted_customers}</div>
          <div className="text-sm text-gray-600">전환 고객</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border text-center">
          <div className="text-2xl font-bold text-indigo-600">{key_metrics.conversion_rate}%</div>
          <div className="text-sm text-gray-600">전환율</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border text-center">
          <div className="text-2xl font-bold text-purple-600">{key_metrics.total_payment_customers}</div>
          <div className="text-sm text-gray-600">전체 결제고객</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border text-center">
          <div className="text-2xl font-bold text-green-600">{formatCurrency(key_metrics.avg_payment_amount)}</div>
          <div className="text-sm text-gray-600">평균 객단가</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border text-center">
          <div className="text-2xl font-bold text-green-600">{formatCurrency(key_metrics.total_revenue)}</div>
          <div className="text-sm text-gray-600">총 매출</div>
        </div>
      </div>

      {/* 추이 차트 */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            성과 추이
          </h3>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('monthly')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'monthly'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              월별
            </button>
            <button
              onClick={() => setViewMode('weekly')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'weekly'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              주별
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium text-gray-600">
                  {viewMode === 'monthly' ? '월' : '주'}
                </th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">방문상담</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">전환</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">전환율</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">결제고객</th>
                <th className="text-center py-3 px-4 font-medium text-gray-600">매출</th>
                {viewMode === 'monthly' && (
                  <th className="text-center py-3 px-4 font-medium text-gray-600">평균객단가</th>
                )}
              </tr>
            </thead>
            <tbody>
              {(viewMode === 'monthly' ? monthly_trends : weekly_trends).map((trend, index) => (
                <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-900">
                    {trend.month || trend.week}
                  </td>
                  <td className="text-center py-3 px-4">{trend.visit_consults}</td>
                  <td className="text-center py-3 px-4">{trend.conversions}</td>
                  <td className="text-center py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-sm ${
                      trend.conversion_rate >= 30 ? 'bg-green-100 text-green-800' :
                      trend.conversion_rate >= 20 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {trend.conversion_rate}%
                    </span>
                  </td>
                  <td className="text-center py-3 px-4">{trend.payment_customers}</td>
                  <td className="text-center py-3 px-4 font-medium">
                    {formatCurrency(trend.revenue)}
                  </td>
                  {viewMode === 'monthly' && trend.avg_payment_amount && (
                    <td className="text-center py-3 px-4">
                      {formatCurrency(trend.avg_payment_amount)}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
