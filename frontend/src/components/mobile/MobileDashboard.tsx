import { Calendar, TrendingUp, Users, Clock, AlertCircle } from 'lucide-react';
import { useDashboardData } from '../../hooks/useDashboardData';
import { formatCurrency } from '../../lib/utils/format';

interface QuickStatProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
}

function QuickStat({ icon, label, value, color }: QuickStatProps) {
  return (
    <div className={`${color} rounded-lg p-4 text-white flex-1 min-w-[140px]`}>
      <div className="flex items-center justify-between mb-2">
        {icon}
        <span className="text-xs opacity-80">{label}</span>
      </div>
      <p className="text-xl font-bold">{value}</p>
    </div>
  );
}

interface TodayScheduleItem {
  time: string;
  customerName: string;
  serviceName: string;
  status: 'confirmed' | 'pending' | 'completed';
}

function TodaySchedule({ items }: { items: TodayScheduleItem[] }) {
  const statusColors = {
    confirmed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-gray-100 text-gray-600',
  };

  const statusLabels = {
    confirmed: '확정',
    pending: '대기',
    completed: '완료',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4">
      <h3 className="font-semibold mb-3 flex items-center">
        <Calendar className="w-5 h-5 mr-2 text-indigo-600" />
        오늘의 예약
      </h3>
      <div className="space-y-3">
        {items.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-4">오늘 예약이 없습니다</p>
        ) : (
          items.map((item, index) => (
            <div key={index} className="flex items-center justify-between border-b pb-2 last:border-0">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{item.time}</span>
                  <span className="text-sm font-semibold">{item.customerName}</span>
                </div>
                <p className="text-xs text-gray-600">{item.serviceName}</p>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${statusColors[item.status]}`}>
                {statusLabels[item.status]}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function QuickAlerts({ alerts }: { alerts: Array<{ type: string; message: string }> }) {
  if (alerts.length === 0) return null;

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <h3 className="font-semibold mb-2 flex items-center text-red-800">
        <AlertCircle className="w-5 h-5 mr-2" />
        긴급 알림
      </h3>
      <div className="space-y-2">
        {alerts.map((alert, index) => (
          <p key={index} className="text-sm text-red-700">• {alert.message}</p>
        ))}
      </div>
    </div>
  );
}

export default function MobileDashboard() {
  const { stats, loading, error } = useDashboardData();
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-500">로딩 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  const today = new Date().toLocaleDateString('ko-KR', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });

  // 더미 데이터 - 실제로는 API에서 가져와야 함
  const todaySchedule: TodayScheduleItem[] = [
    { time: '09:00', customerName: '김미영', serviceName: '유전자 검사', status: 'completed' },
    { time: '10:30', customerName: '이정호', serviceName: '건강 상담', status: 'confirmed' },
    { time: '14:00', customerName: '박서연', serviceName: 'AI 바이크', status: 'confirmed' },
    { time: '16:00', customerName: '최준혁', serviceName: '종합 검진', status: 'pending' },
  ];

  const alerts = [
    { type: 'reservation', message: '14:00 박서연님 특별 요청사항 확인 필요' },
    { type: 'inventory', message: '유전자 검사 키트 재고 부족 (잔여: 3개)' },
  ];

  return (
    <div className="p-4 pb-20 bg-gray-50 min-h-screen">
      {/* 인사말 헤더 */}
      <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg p-4 text-white mb-4">
        <h2 className="text-lg font-bold mb-1">좋은 아침입니다! 👋</h2>
        <p className="text-sm opacity-90">{today}</p>
      </div>

      {/* 주요 지표 - 가로 스크롤 */}
      <div className="flex gap-3 overflow-x-auto pb-2 mb-4 -mx-4 px-4">
        <QuickStat
          icon={<Users className="w-5 h-5" />}
          label="오늘 예약"
          value={`${todaySchedule.filter(s => s.status !== 'completed').length}명`}
          color="bg-blue-500"
        />
        <QuickStat
          icon={<TrendingUp className="w-5 h-5" />}
          label="예상 매출"
          value={formatCurrency(5230000)}
          color="bg-green-500"
        />
        <QuickStat
          icon={<Clock className="w-5 h-5" />}
          label="대기 고객"
          value="3명"
          color="bg-orange-500"
        />
        <QuickStat
          icon={<Users className="w-5 h-5" />}
          label="전체 고객"
          value={stats.total_customers}
          color="bg-purple-500"
        />
      </div>

      {/* 긴급 알림 */}
      <div className="mb-4">
        <QuickAlerts alerts={alerts} />
      </div>

      {/* 오늘의 예약 */}
      <TodaySchedule items={todaySchedule} />

      {/* 빠른 액션 버튼 */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <button className="bg-white border border-gray-200 rounded-lg p-4 text-center hover:bg-gray-50 transition-colors">
          <Calendar className="w-6 h-6 mx-auto mb-2 text-indigo-600" />
          <span className="text-sm font-medium">예약 추가</span>
        </button>
        <button className="bg-white border border-gray-200 rounded-lg p-4 text-center hover:bg-gray-50 transition-colors">
          <Users className="w-6 h-6 mx-auto mb-2 text-indigo-600" />
          <span className="text-sm font-medium">고객 검색</span>
        </button>
      </div>
    </div>
  );
}