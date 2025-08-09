import { useState, useEffect } from 'react';
import { X, Phone, CheckCircle, User, Calendar, MessageSquare } from 'lucide-react';
import { api } from '../../lib/api';

interface Campaign {
  campaign_id: number;
  campaign_name: string;
}

interface CampaignTarget {
  target_id: number;
  campaign_id: number;
  lead_id: number;
  contact_date?: string;
  contact_result?: string;
  converted: boolean;
  created_at: string;
  lead_name?: string;
  lead_phone?: string;
}

interface CampaignTargetsModalProps {
  isOpen: boolean;
  onClose: () => void;
  campaign: Campaign | null;
}

export default function CampaignTargetsModal({ isOpen, onClose, campaign }: CampaignTargetsModalProps) {
  const [targets, setTargets] = useState<CampaignTarget[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTargets, setSelectedTargets] = useState<number[]>([]);
  const [contactResult, setContactResult] = useState('');

  useEffect(() => {
    if (isOpen && campaign) {
      fetchTargets();
    }
  }, [isOpen, campaign]);

  const fetchTargets = async () => {
    if (!campaign) return;
    
    setLoading(true);
    try {
      const response = await api.get(`/api/v1/customer-leads/campaigns/${campaign.campaign_id}/targets`);
      setTargets(response.data);
    } catch (error) {
      console.error('Failed to fetch targets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateContact = async (targetId: number, result: string) => {
    try {
      await api.put(`/api/v1/customer-leads/campaigns/${campaign?.campaign_id}/targets/${targetId}`, {
        contact_date: new Date().toISOString().split('T')[0],
        contact_result: result
      });
      fetchTargets();
    } catch (error) {
      console.error('Failed to update contact:', error);
    }
  };

  const handleBulkUpdate = async () => {
    if (selectedTargets.length === 0 || !contactResult) {
      alert('대상 고객과 연락 결과를 선택해주세요.');
      return;
    }

    try {
      await Promise.all(
        selectedTargets.map(targetId =>
          api.put(`/api/v1/customer-leads/campaigns/${campaign?.campaign_id}/targets/${targetId}`, {
            contact_date: new Date().toISOString().split('T')[0],
            contact_result: contactResult
          })
        )
      );
      
      setSelectedTargets([]);
      setContactResult('');
      fetchTargets();
      alert(`${selectedTargets.length}명의 연락 결과가 업데이트되었습니다.`);
    } catch (error) {
      console.error('Failed to bulk update:', error);
      alert('일괄 업데이트에 실패했습니다.');
    }
  };

  const handleMarkConverted = async (targetId: number) => {
    try {
      await api.put(`/api/v1/customer-leads/campaigns/${campaign?.campaign_id}/targets/${targetId}`, {
        converted: true,
        contact_result: '재등록 완료'
      });
      fetchTargets();
    } catch (error) {
      console.error('Failed to mark as converted:', error);
    }
  };

  if (!isOpen || !campaign) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">캠페인 대상 고객 관리</h2>
              <p className="text-sm text-gray-600 mt-1">{campaign.campaign_name}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 일괄 작업 */}
        {selectedTargets.length > 0 && (
          <div className="p-4 bg-indigo-50 border-b border-indigo-200">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-indigo-900">
                {selectedTargets.length}명 선택됨
              </span>
              <select
                value={contactResult}
                onChange={(e) => setContactResult(e.target.value)}
                className="px-3 py-1 border border-indigo-300 rounded-md text-sm"
              >
                <option value="">연락 결과 선택</option>
                <option value="전화 연결">전화 연결</option>
                <option value="부재중">부재중</option>
                <option value="관심 없음">관심 없음</option>
                <option value="추후 연락 요청">추후 연락 요청</option>
                <option value="방문 예약">방문 예약</option>
              </select>
              <button
                onClick={handleBulkUpdate}
                className="px-4 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
              >
                일괄 업데이트
              </button>
            </div>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">대상 고객을 불러오는 중...</p>
            </div>
          ) : targets.length === 0 ? (
            <div className="text-center py-8">
              <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">캠페인 대상 고객이 없습니다.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {targets.map((target) => (
                <div
                  key={target.target_id}
                  className={`bg-white border rounded-lg p-4 ${
                    target.converted ? 'border-green-200 bg-green-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <input
                        type="checkbox"
                        checked={selectedTargets.includes(target.target_id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedTargets([...selectedTargets, target.target_id]);
                          } else {
                            setSelectedTargets(selectedTargets.filter(id => id !== target.target_id));
                          }
                        }}
                        className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                        disabled={target.converted}
                      />
                      
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium text-gray-900">{target.lead_name}</h4>
                          {target.converted && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              재등록 완료
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                          {target.lead_phone && (
                            <span className="flex items-center gap-1">
                              <Phone className="w-4 h-4" />
                              {target.lead_phone}
                            </span>
                          )}
                          {target.contact_date && (
                            <span className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {new Date(target.contact_date).toLocaleDateString()}
                            </span>
                          )}
                          {target.contact_result && (
                            <span className="flex items-center gap-1">
                              <MessageSquare className="w-4 h-4" />
                              {target.contact_result}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      {!target.converted && !target.contact_date && (
                        <>
                          <button
                            onClick={() => handleUpdateContact(target.target_id, '전화 연결')}
                            className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                          >
                            전화 연결
                          </button>
                          <button
                            onClick={() => handleUpdateContact(target.target_id, '부재중')}
                            className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                          >
                            부재중
                          </button>
                        </>
                      )}
                      
                      {target.contact_date && !target.converted && (
                        <button
                          onClick={() => handleMarkConverted(target.target_id)}
                          className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                        >
                          재등록 완료
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}