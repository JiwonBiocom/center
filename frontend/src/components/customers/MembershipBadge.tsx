import { Shield } from 'lucide-react';

interface MembershipBadgeProps {
  level: string;
  status: string;
  showTooltip?: boolean;
}

export default function MembershipBadge({ level, status, showTooltip = true }: MembershipBadgeProps) {
  const levelInfo: Record<string, { name: string; color: string }> = {
    bronze: { name: '브론즈', color: 'bg-amber-100 text-amber-800 border-amber-200' },
    silver: { name: '실버', color: 'bg-gray-100 text-gray-800 border-gray-200' },
    gold: { name: '골드', color: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
    platinum: { name: '플래티넘', color: 'bg-purple-100 text-purple-800 border-purple-200' }
  };

  const statusInfo: Record<string, { name: string; color: string; icon: string }> = {
    active: { name: '활성', color: 'text-green-600', icon: '🟢' },
    inactive: { name: '비활성', color: 'text-yellow-600', icon: '🟡' },
    dormant: { name: '휴면', color: 'text-red-600', icon: '🔴' }
  };

  const currentLevel = levelInfo[level] || levelInfo.bronze;
  const currentStatus = statusInfo[status] || statusInfo.active;

  return (
    <div className="flex items-center gap-2">
      {/* 회원 등급 */}
      <div className="relative group">
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${currentLevel.color}`}>
          <Shield className="w-3 h-3 mr-1" />
          {currentLevel.name}
        </div>
        {showTooltip && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 p-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
            <div className="font-semibold mb-1">회원 등급</div>
            <div className="text-gray-300">
              연매출과 누적 방문 횟수에 따라 자동으로 부여됩니다.
            </div>
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
              <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        )}
      </div>

      {/* 고객 상태 */}
      <div className="relative group">
        <div className={`inline-flex items-center text-sm font-medium ${currentStatus.color}`}>
          <span className="mr-1">{currentStatus.icon}</span>
          {currentStatus.name}
        </div>
        {showTooltip && (
          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 p-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
            <div className="font-semibold mb-1">고객 상태</div>
            <div className="text-gray-300">
              {status === 'active' && '최근 30일 이내 방문'}
              {status === 'inactive' && '31일~90일 사이 방문'}
              {status === 'dormant' && '90일 이상 미방문'}
            </div>
            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
              <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}