import { Package, Activity, AlertCircle } from 'lucide-react';

interface PackageStatsProps {
  active_purchases: number;
  total_remaining_sessions: number;
  expiring_this_month: number;
}

interface PackageStatusSectionProps {
  packageStats: PackageStatsProps;
}

export default function PackageStatusSection({ packageStats }: PackageStatusSectionProps) {
  const statusItems = [
    {
      title: '활성 패키지',
      value: `${packageStats.active_purchases}개`,
      icon: Package,
      iconColor: 'text-blue-500',
    },
    {
      title: '총 잔여 세션',
      value: `${packageStats.total_remaining_sessions}회`,
      icon: Activity,
      iconColor: 'text-green-500',
    },
    {
      title: '이번달 만료',
      value: `${packageStats.expiring_this_month}개`,
      icon: AlertCircle,
      iconColor: 'text-orange-500',
    },
  ];

  return (
    <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">패키지 잔여 현황</h2>
        <Package className="w-5 h-5 text-gray-400" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {statusItems.map((item, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{item.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{item.value}</p>
              </div>
              <item.icon className={`w-8 h-8 ${item.iconColor}`} />
            </div>
          </div>
        ))}
      </div>
      <p className="mt-4 text-xs text-gray-500">
        * 패키지 구매 시 자동으로 잔여 세션이 추가되며, 서비스 이용 시 자동으로 차감됩니다.
      </p>
    </div>
  );
}