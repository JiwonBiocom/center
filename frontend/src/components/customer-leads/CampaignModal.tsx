import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { api } from '../../lib/api';

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

interface CampaignModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  campaignData?: Campaign | null;
}

export default function CampaignModal({ isOpen, onClose, onSuccess, campaignData }: CampaignModalProps) {
  const [formData, setFormData] = useState({
    campaign_name: '',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    notes: '',
    is_active: true,
    target_criteria: {
      days_since_last_service: 90,
      include_no_registration: true,
      regions: [] as string[],
      channels: [] as string[]
    }
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (campaignData) {
      setFormData({
        campaign_name: campaignData.campaign_name || '',
        start_date: campaignData.start_date || new Date().toISOString().split('T')[0],
        end_date: campaignData.end_date || '',
        notes: campaignData.notes || '',
        is_active: campaignData.is_active ?? true,
        target_criteria: campaignData.target_criteria || {
          days_since_last_service: 90,
          include_no_registration: true,
          regions: [],
          channels: []
        }
      });
    }
  }, [campaignData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        end_date: formData.end_date || null
      };

      if (campaignData) {
        await api.put(`/api/v1/customer-leads/campaigns/${campaignData.campaign_id}`, submitData);
      } else {
        await api.post('/api/v1/customer-leads/campaigns', submitData);
      }
      
      onSuccess();
    } catch (error) {
      console.error('Failed to save campaign:', error);
      alert('캠페인 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {campaignData ? '캠페인 수정' : '새 캠페인 만들기'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* 기본 정보 */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">기본 정보</h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  캠페인명 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={formData.campaign_name}
                  onChange={(e) => setFormData({ ...formData, campaign_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    시작일 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    종료일
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                    min={formData.start_date}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* 대상 설정 */}
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-4">대상 설정</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  마지막 서비스 이용 후 경과일
                </label>
                <input
                  type="number"
                  value={formData.target_criteria.days_since_last_service}
                  onChange={(e) => setFormData({
                    ...formData,
                    target_criteria: {
                      ...formData.target_criteria,
                      days_since_last_service: parseInt(e.target.value) || 0
                    }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  min="0"
                />
                <p className="text-sm text-gray-500 mt-1">
                  지정한 일수 이상 서비스를 이용하지 않은 고객을 대상으로 합니다
                </p>
              </div>

              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.target_criteria.include_no_registration}
                    onChange={(e) => setFormData({
                      ...formData,
                      target_criteria: {
                        ...formData.target_criteria,
                        include_no_registration: e.target.checked
                      }
                    })}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    미등록 고객 포함
                  </span>
                </label>
                <p className="text-sm text-gray-500 ml-6">
                  등록하지 않은 상담 고객도 캠페인 대상에 포함합니다
                </p>
              </div>
            </div>
          </div>

          {/* 메모 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              메모
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={3}
            />
          </div>

          {/* 상태 */}
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
              />
              <span className="text-sm font-medium text-gray-700">
                캠페인 활성화
              </span>
            </label>
          </div>

          {/* 버튼 */}
          <div className="flex justify-end gap-2 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? '저장 중...' : (campaignData ? '수정' : '생성')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}