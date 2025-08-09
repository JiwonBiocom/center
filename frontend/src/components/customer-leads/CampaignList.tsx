import { Edit, Trash2, Users, TrendingUp, Play, Pause, Target } from 'lucide-react';

interface Campaign {
  campaign_id: number;
  campaign_name: string;
  start_date: string;
  end_date?: string;
  target_criteria?: any;
  notes?: string;
  is_active: boolean;
  target_count: number;
  success_count: number;
  created_by?: number;
  created_by_name?: string;
  created_at: string;
  updated_at?: string;
}

interface CampaignListProps {
  campaigns: Campaign[];
  loading: boolean;
  onEdit: (campaign: Campaign) => void;
  onDelete: (id: number) => void;
  onViewTargets: (campaign: Campaign) => void;
}

export default function CampaignList({ campaigns, loading, onEdit, onDelete, onViewTargets }: CampaignListProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">캠페인을 불러오는 중...</p>
      </div>
    );
  }

  if (campaigns.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
        <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">아직 생성된 캠페인이 없습니다.</p>
        <p className="text-sm text-gray-500 mt-1">새 캠페인을 만들어 재등록을 유도해보세요.</p>
      </div>
    );
  }

  const getSuccessRate = (campaign: Campaign) => {
    if (campaign.target_count === 0) return 0;
    return Math.round((campaign.success_count / campaign.target_count) * 100);
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {campaigns.map((campaign) => (
        <div
          key={campaign.campaign_id}
          className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow"
        >
          <div className="p-6">
            {/* 헤더 */}
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900">{campaign.campaign_name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    campaign.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {campaign.is_active ? (
                      <>
                        <Play className="w-3 h-3 mr-1" />
                        진행중
                      </>
                    ) : (
                      <>
                        <Pause className="w-3 h-3 mr-1" />
                        일시정지
                      </>
                    )}
                  </span>
                </div>
              </div>
              <div className="flex gap-1">
                <button
                  onClick={() => onEdit(campaign)}
                  className="p-1 text-gray-400 hover:text-gray-600"
                  title="수정"
                >
                  <Edit className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onDelete(campaign.campaign_id)}
                  className="p-1 text-gray-400 hover:text-red-600"
                  title="삭제"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* 기간 */}
            <div className="text-sm text-gray-600 mb-4">
              {new Date(campaign.start_date).toLocaleDateString()} ~{' '}
              {campaign.end_date ? new Date(campaign.end_date).toLocaleDateString() : '진행중'}
            </div>

            {/* 통계 */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 rounded p-3">
                <div className="flex items-center justify-between">
                  <Users className="w-5 h-5 text-gray-400" />
                  <span className="text-lg font-semibold text-gray-900">{campaign.target_count}</span>
                </div>
                <p className="text-xs text-gray-600 mt-1">대상 인원</p>
              </div>
              <div className="bg-green-50 rounded p-3">
                <div className="flex items-center justify-between">
                  <TrendingUp className="w-5 h-5 text-green-400" />
                  <span className="text-lg font-semibold text-green-900">{campaign.success_count}</span>
                </div>
                <p className="text-xs text-green-600 mt-1">재등록 성공</p>
              </div>
            </div>

            {/* 성공률 */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">성공률</span>
                <span className="font-medium text-gray-900">{getSuccessRate(campaign)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full transition-all"
                  style={{ width: `${getSuccessRate(campaign)}%` }}
                />
              </div>
            </div>

            {/* 메모 */}
            {campaign.notes && (
              <div className="text-sm text-gray-600 mb-4 line-clamp-2">
                {campaign.notes}
              </div>
            )}

            {/* 액션 버튼 */}
            <button
              onClick={() => onViewTargets(campaign)}
              className="w-full px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
            >
              대상 고객 관리
            </button>

            {/* 생성 정보 */}
            <div className="mt-4 pt-4 border-t text-xs text-gray-500">
              {campaign.created_by_name && (
                <p>생성자: {campaign.created_by_name}</p>
              )}
              <p>생성일: {new Date(campaign.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}