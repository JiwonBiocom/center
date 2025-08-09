import { useState, useEffect } from 'react';
import { X, User, Phone, Calendar, MapPin, Tag, DollarSign } from 'lucide-react';
import { api } from '../../lib/api';
import ConsultationHistory from './ConsultationHistory';

interface CustomerLead {
  lead_id: number;
  name: string;
  phone?: string;
  lead_date: string;
  age?: number;
  region?: string;
  lead_channel?: string;
  db_channel?: string;
  carrot_id?: string;
  ad_watched?: string;
  price_informed: boolean;
  ab_test_group?: string;
  
  db_entry_date?: string;
  phone_consult_date?: string;
  phone_consult_result?: string;
  visit_consult_date?: string;
  registration_date?: string;
  
  visit_cancelled: boolean;
  visit_cancel_reason?: string;
  remind_date?: string;
  
  is_reregistration_target: boolean;
  last_service_date?: string;
  
  purchased_product?: string;
  no_registration_reason?: string;
  notes?: string;
  revenue?: number;
  
  status: string;
  assigned_staff_id?: number;
  assigned_staff_name?: string;
  converted_customer_id?: number;
  converted_customer_name?: string;
}

interface CustomerLeadDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  leadId: number;
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

export default function CustomerLeadDetailModal({ isOpen, onClose, leadId }: CustomerLeadDetailModalProps) {
  const [leadData, setLeadData] = useState<CustomerLead | null>(null);
  const [activeTab, setActiveTab] = useState<'info' | 'consultation'>('info');

  useEffect(() => {
    if (isOpen && leadId) {
      fetchLeadData();
    }
  }, [isOpen, leadId]);

  const fetchLeadData = async () => {
    try {
      const response = await api.get(`/api/v1/customer-leads/${leadId}`);
      setLeadData(response.data);
    } catch (error) {
      console.error('Failed to fetch lead data:', error);
    }
  };

  if (!isOpen || !leadData) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold text-gray-900">
              {leadData.name}님의 상세 정보
            </h2>
            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
              statusColors[leadData.status] || 'bg-gray-100 text-gray-800'
            }`}>
              {statusLabels[leadData.status] || leadData.status}
            </span>
            {leadData.is_reregistration_target && (
              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">
                재등록 대상
              </span>
            )}
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* 탭 */}
        <div className="border-b">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('info')}
              className={`py-3 px-6 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'info'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              기본 정보
            </button>
            <button
              onClick={() => setActiveTab('consultation')}
              className={`py-3 px-6 text-sm font-medium border-b-2 transition-colors ${
                activeTab === 'consultation'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              상담 이력
            </button>
          </nav>
        </div>

        <div className="overflow-y-auto max-h-[calc(90vh-180px)]">
          {activeTab === 'info' ? (
            <div className="p-6">
              {/* 기본 정보 */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">기본 정보</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <User className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-600">이름</p>
                      <p className="text-sm font-medium text-gray-900">{leadData.name}</p>
                    </div>
                  </div>
                  
                  {leadData.phone && (
                    <div className="flex items-start gap-3">
                      <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">연락처</p>
                        <p className="text-sm font-medium text-gray-900">{leadData.phone}</p>
                      </div>
                    </div>
                  )}
                  
                  {leadData.age && (
                    <div className="flex items-start gap-3">
                      <User className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">나이</p>
                        <p className="text-sm font-medium text-gray-900">{leadData.age}세</p>
                      </div>
                    </div>
                  )}
                  
                  {leadData.region && (
                    <div className="flex items-start gap-3">
                      <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">거주지역</p>
                        <p className="text-sm font-medium text-gray-900">{leadData.region}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 유입 정보 */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">유입 정보</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-600">리드 날짜</p>
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(leadData.lead_date).toLocaleDateString('ko-KR')}
                      </p>
                    </div>
                  </div>
                  
                  {leadData.lead_channel && (
                    <div className="flex items-start gap-3">
                      <Tag className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">유입경로</p>
                        <p className="text-sm font-medium text-gray-900">{leadData.lead_channel}</p>
                      </div>
                    </div>
                  )}
                  
                  {leadData.db_channel && (
                    <div className="flex items-start gap-3">
                      <Tag className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">DB작성 채널</p>
                        <p className="text-sm font-medium text-gray-900">{leadData.db_channel}</p>
                      </div>
                    </div>
                  )}
                  
                  {leadData.carrot_id && (
                    <div className="flex items-start gap-3">
                      <User className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">당근 아이디</p>
                        <p className="text-sm font-medium text-gray-900">{leadData.carrot_id}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 상담 일정 */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">상담 일정</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {leadData.phone_consult_date && (
                    <div className="flex items-start gap-3">
                      <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">전화상담일</p>
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(leadData.phone_consult_date).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {leadData.visit_consult_date && (
                    <div className="flex items-start gap-3">
                      <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">방문상담일</p>
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(leadData.visit_consult_date).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {leadData.registration_date && (
                    <div className="flex items-start gap-3">
                      <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">등록일</p>
                        <p className="text-sm font-medium text-gray-900">
                          {new Date(leadData.registration_date).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* 구매 정보 */}
              {(leadData.purchased_product || leadData.revenue) && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">구매 정보</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {leadData.purchased_product && (
                      <div className="flex items-start gap-3">
                        <Tag className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">구매 상품</p>
                          <p className="text-sm font-medium text-gray-900">{leadData.purchased_product}</p>
                        </div>
                      </div>
                    )}
                    
                    {leadData.revenue && (
                      <div className="flex items-start gap-3">
                        <DollarSign className="w-5 h-5 text-gray-400 mt-0.5" />
                        <div>
                          <p className="text-sm text-gray-600">매출액</p>
                          <p className="text-sm font-medium text-gray-900">
                            {leadData.revenue.toLocaleString()}원
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 비고 */}
              {leadData.notes && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">비고</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{leadData.notes}</p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <ConsultationHistory leadId={leadId} leadName={leadData.name} />
          )}
        </div>
      </div>
    </div>
  );
}