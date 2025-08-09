import { Users, TrendingUp, UserCheck, BarChart3 } from 'lucide-react';

interface CustomerLeadStatsProps {
  stats: {
    total_count: number;
    converted_count: number;
    conversion_rate: number;
    channel_stats: Array<{
      channel: string;
      count: number;
      converted_count: number;
      conversion_rate: number;
    }>;
    status_stats: Array<{
      status: string;
      count: number;
    }>;
  };
}

const statusLabels: Record<string, string> = {
  'new': '신규',
  'db_entered': 'DB입력',
  'phone_consulted': '전화상담',
  'visit_consulted': '방문상담',
  'converted': '등록완료'
};

const statusColors: Record<string, string> = {
  'new': 'bg-gray-100 text-gray-800',
  'db_entered': 'bg-blue-100 text-blue-800',
  'phone_consulted': 'bg-yellow-100 text-yellow-800',
  'visit_consulted': 'bg-purple-100 text-purple-800',
  'converted': 'bg-green-100 text-green-800'
};

export default function CustomerLeadStats({ stats }: CustomerLeadStatsProps) {
  return (
    <div className="mb-6">
      {/* 주요 지표 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">총 유입고객</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_count}</p>
            </div>
            <Users className="w-8 h-8 text-gray-400" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전환 고객</p>
              <p className="text-2xl font-bold text-green-600">{stats.converted_count}</p>
            </div>
            <UserCheck className="w-8 h-8 text-green-400" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전환율</p>
              <p className="text-2xl font-bold text-indigo-600">{stats.conversion_rate}%</p>
            </div>
            <TrendingUp className="w-8 h-8 text-indigo-400" />
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">평균 전환 기간</p>
              <p className="text-2xl font-bold text-gray-900">-일</p>
            </div>
            <BarChart3 className="w-8 h-8 text-gray-400" />
          </div>
        </div>
      </div>
      
      {/* 상태별 분포 */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">상태별 분포</h3>
        <div className="flex flex-wrap gap-2">
          {stats.status_stats.map((stat) => (
            <div
              key={stat.status}
              className={`px-4 py-2 rounded-full text-sm font-medium ${
                statusColors[stat.status] || 'bg-gray-100 text-gray-800'
              }`}
            >
              {statusLabels[stat.status] || stat.status}: {stat.count}명
            </div>
          ))}
        </div>
      </div>
      
      {/* 채널별 통계 */}
      {stats.channel_stats.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mt-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">채널별 전환율</h3>
          <div className="space-y-3">
            {stats.channel_stats.slice(0, 5).map((channel) => (
              <div key={channel.channel}>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">{channel.channel}</span>
                  <span className="text-sm text-gray-500">
                    {channel.converted_count}/{channel.count} ({channel.conversion_rate}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full"
                    style={{ width: `${channel.conversion_rate}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}