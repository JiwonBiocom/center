import React from 'react';
import { TrendingUp, Users, CreditCard, Calculator } from 'lucide-react';

interface WeeklyStatusProps {
  weeklyData?: {
    new_consultation_visits: number;
    conversion_rate: number;
    paying_customers: number;
    average_payment: number;
    weekly_revenue: number;
  };
}

const WeeklyStatusSection: React.FC<WeeklyStatusProps> = ({ weeklyData }) => {
  // 기본 데이터 (실제 데이터가 없을 때)
  const data = weeklyData || {
    new_consultation_visits: 24,
    conversion_rate: 0.42, // 42%
    paying_customers: 10,
    average_payment: 850000,
    weekly_revenue: 8500000
  };

  const conversionRatePercent = Math.round(data.conversion_rate * 100);

  return (
    <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-blue-500" />
          지난 일주일 현황
        </h2>
      </div>
      
      <div className="p-6">
        {/* 계산 공식 표시 */}
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-center space-x-4 text-sm">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-blue-600" />
              <span className="font-medium text-blue-800">신규 방문상담 수</span>
            </div>
            <span className="text-blue-600">×</span>
            <div className="flex items-center gap-2">
              <Calculator className="h-4 w-4 text-blue-600" />
              <span className="font-medium text-blue-800">전환율</span>
            </div>
            <span className="text-blue-600">=</span>
            <div className="flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-blue-600" />
              <span className="font-medium text-blue-800">결제 고객 수</span>
            </div>
          </div>
        </div>

        {/* 첫 번째 계산: 신규 방문상담 → 결제 고객 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <Users className="h-8 w-8 text-blue-500 mx-auto mb-2" />
            <p className="text-sm text-gray-600 mb-1">신규 방문상담 수</p>
            <p className="text-2xl font-bold text-gray-900">{data.new_consultation_visits}명</p>
          </div>
          
          <div className="flex items-center justify-center">
            <div className="bg-blue-100 rounded-full p-2">
              <span className="text-blue-600 font-bold">×</span>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <Calculator className="h-8 w-8 text-green-500 mx-auto mb-2" />
            <p className="text-sm text-gray-600 mb-1">전환율</p>
            <p className="text-2xl font-bold text-gray-900">{conversionRatePercent}%</p>
          </div>
          
          <div className="bg-green-50 rounded-lg p-4 text-center border-2 border-green-200">
            <CreditCard className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-sm text-green-700 mb-1">결제 고객 수</p>
            <p className="text-2xl font-bold text-green-800">{data.paying_customers}명</p>
          </div>
        </div>

        {/* 구분선 */}
        <div className="border-t border-gray-200 my-6"></div>

        {/* 두 번째 계산 공식 */}
        <div className="bg-green-50 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-center space-x-4 text-sm">
            <div className="flex items-center gap-2">
              <CreditCard className="h-4 w-4 text-green-600" />
              <span className="font-medium text-green-800">결제 고객 수</span>
            </div>
            <span className="text-green-600">×</span>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="font-medium text-green-800">평균 결제 객단가</span>
            </div>
            <span className="text-green-600">=</span>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="font-medium text-green-800">주간 매출액</span>
            </div>
          </div>
        </div>

        {/* 두 번째 계산: 결제 고객 → 주간 매출 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-green-50 rounded-lg p-4 text-center border-2 border-green-200">
            <CreditCard className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <p className="text-sm text-green-700 mb-1">결제 고객 수</p>
            <p className="text-2xl font-bold text-green-800">{data.paying_customers}명</p>
          </div>
          
          <div className="flex items-center justify-center">
            <div className="bg-green-100 rounded-full p-2">
              <span className="text-green-600 font-bold">×</span>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <TrendingUp className="h-8 w-8 text-orange-500 mx-auto mb-2" />
            <p className="text-sm text-gray-600 mb-1">평균 객단가</p>
            <p className="text-xl font-bold text-gray-900">₩{data.average_payment.toLocaleString()}</p>
          </div>
          
          <div className="bg-blue-50 rounded-lg p-4 text-center border-2 border-blue-200">
            <TrendingUp className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <p className="text-sm text-blue-700 mb-1">주간 매출액</p>
            <p className="text-xl font-bold text-blue-800">₩{data.weekly_revenue.toLocaleString()}</p>
          </div>
        </div>

        {/* 요약 정보 */}
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-4">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">지난 일주일 성과 요약</p>
            <div className="flex items-center justify-center gap-6 text-sm">
              <div>
                <span className="text-gray-600">전환율: </span>
                <span className="font-semibold text-blue-600">{conversionRatePercent}%</span>
              </div>
              <div>
                <span className="text-gray-600">고객당 평균: </span>
                <span className="font-semibold text-green-600">₩{data.average_payment.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WeeklyStatusSection;