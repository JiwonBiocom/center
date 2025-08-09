import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { api } from '../../lib/api';

interface CustomerLead {
  lead_id?: number;
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
  
  // 추가 상담 정보 필드
  consultant_name?: string;
  current_weight?: number;
  target_weight?: number;
  exercise_plan?: string;
  diet_plan?: string;
  experience_services?: string;
  experience_result?: string;
  rejection_reason?: string;
  past_diet_experience?: string;
  main_concerns?: string;
  referral_detail?: string;
  visit_purpose?: string;
}

interface CustomerLeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  leadData?: CustomerLead | null;
}

const channelOptions = [
  '인스타그램', '네이버', '카카오', '페이스북', 
  '구글', '당근마켓', '지인소개', '기타'
];

const regionOptions = [
  '서울', '경기', '인천', '부산', '대구', 
  '광주', '대전', '울산', '세종', '강원', '기타'
];

export default function CustomerLeadModal({ isOpen, onClose, onSuccess, leadData }: CustomerLeadModalProps) {
  const [formData, setFormData] = useState<CustomerLead>({
    name: '',
    lead_date: new Date().toISOString().split('T')[0],
    price_informed: false,
    visit_cancelled: false,
    is_reregistration_target: false,
    status: 'new'
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (leadData) {
      setFormData(leadData);
    } else {
      setFormData({
        name: '',
        lead_date: new Date().toISOString().split('T')[0],
        price_informed: false,
        visit_cancelled: false,
        is_reregistration_target: false,
        status: 'new'
      });
    }
  }, [leadData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (leadData?.lead_id) {
        await api.put(`/api/v1/customer-leads/${leadData.lead_id}`, formData);
      } else {
        await api.post('/api/v1/customer-leads/', formData);
      }
      onSuccess();
    } catch (error) {
      console.error('Failed to save lead:', error);
      alert('저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {leadData ? '유입고객 수정' : '신규 유입고객 등록'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 기본 정보 */}
            <div className="col-span-2">
              <h3 className="text-lg font-medium text-gray-900 mb-4">기본 정보</h3>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                이름 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">연락처</label>
              <input
                type="tel"
                value={formData.phone || ''}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">나이</label>
              <input
                type="number"
                value={formData.age || ''}
                onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">거주지역</label>
              <select
                value={formData.region || ''}
                onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">선택하세요</option>
                {regionOptions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>

            {/* 유입 정보 */}
            <div className="col-span-2 mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">유입 정보</h3>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">유입경로</label>
              <select
                value={formData.lead_channel || ''}
                onChange={(e) => setFormData({ ...formData, lead_channel: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">선택하세요</option>
                {channelOptions.map(channel => (
                  <option key={channel} value={channel}>{channel}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DB작성 채널</label>
              <input
                type="text"
                value={formData.db_channel || ''}
                onChange={(e) => setFormData({ ...formData, db_channel: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">당근 아이디</label>
              <input
                type="text"
                value={formData.carrot_id || ''}
                onChange={(e) => setFormData({ ...formData, carrot_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">시청 광고</label>
              <input
                type="text"
                value={formData.ad_watched || ''}
                onChange={(e) => setFormData({ ...formData, ad_watched: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* 날짜 정보 */}
            <div className="col-span-2 mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">일정 정보</h3>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                리드 날짜 <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                required
                value={formData.lead_date}
                onChange={(e) => setFormData({ ...formData, lead_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">DB 입력일</label>
              <input
                type="date"
                value={formData.db_entry_date || ''}
                onChange={(e) => setFormData({ ...formData, db_entry_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">전화상담일</label>
              <input
                type="date"
                value={formData.phone_consult_date || ''}
                onChange={(e) => setFormData({ ...formData, phone_consult_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">방문상담일</label>
              <input
                type="date"
                value={formData.visit_consult_date || ''}
                onChange={(e) => setFormData({ ...formData, visit_consult_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* 체크박스 */}
            <div className="col-span-2 mt-6">
              <div className="flex flex-wrap gap-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.price_informed}
                    onChange={(e) => setFormData({ ...formData, price_informed: e.target.checked })}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                  />
                  <span className="text-sm text-gray-700">가격 안내 완료</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.visit_cancelled}
                    onChange={(e) => setFormData({ ...formData, visit_cancelled: e.target.checked })}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                  />
                  <span className="text-sm text-gray-700">방문 취소</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_reregistration_target}
                    onChange={(e) => setFormData({ ...formData, is_reregistration_target: e.target.checked })}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 mr-2"
                  />
                  <span className="text-sm text-gray-700">재등록 대상</span>
                </label>
              </div>
            </div>

            {/* 상담 정보 */}
            <div className="col-span-2 mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">상담 정보</h3>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">상담자</label>
              <input
                type="text"
                value={formData.consultant_name || ''}
                onChange={(e) => setFormData({ ...formData, consultant_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 김예림"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">방문 목적</label>
              <input
                type="text"
                value={formData.visit_purpose || ''}
                onChange={(e) => setFormData({ ...formData, visit_purpose: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 다이어트"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">주요 관심사/니즈</label>
              <textarea
                value={formData.main_concerns || ''}
                onChange={(e) => setFormData({ ...formData, main_concerns: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 다이어트, 기초대사량 증진"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">유입 경로 상세</label>
              <textarea
                value={formData.referral_detail || ''}
                onChange={(e) => setFormData({ ...formData, referral_detail: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 팀키토 유튜브 시청 → 플레이스 예약 → 방문"
              />
            </div>

            {/* 체중 정보 */}
            <div className="col-span-2 mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">체중 및 운동 정보</h3>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">현재 체중(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.current_weight || ''}
                onChange={(e) => setFormData({ ...formData, current_weight: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">목표 체중(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.target_weight || ''}
                onChange={(e) => setFormData({ ...formData, target_weight: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">과거 다이어트 경험</label>
              <textarea
                value={formData.past_diet_experience || ''}
                onChange={(e) => setFormData({ ...formData, past_diet_experience: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 3개월차, 한약+유산소+간헐단식으로 5kg 감량"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">운동 계획</label>
              <textarea
                value={formData.exercise_plan || ''}
                onChange={(e) => setFormData({ ...formData, exercise_plan: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 유산소 꾸준히 / 근력 운동 주 2~3회(1시간)"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">식단 계획</label>
              <input
                type="text"
                value={formData.diet_plan || ''}
                onChange={(e) => setFormData({ ...formData, diet_plan: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 저탄수"
              />
            </div>

            {/* 체험 정보 */}
            <div className="col-span-2 mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">체험 및 결과</h3>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 서비스</label>
              <input
                type="text"
                value={formData.experience_services || ''}
                onChange={(e) => setFormData({ ...formData, experience_services: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 레드+림프+펄스"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 결과</label>
              <textarea
                value={formData.experience_result || ''}
                onChange={(e) => setFormData({ ...formData, experience_result: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 체중 동일, 골격근량 ↑, 체지방량 ↓, 위상각 0.2 ↑"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">미등록 사유</label>
              <textarea
                value={formData.rejection_reason || ''}
                onChange={(e) => setFormData({ ...formData, rejection_reason: e.target.value })}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 예상했던 금액보다 비싸 차후에 연락 주신다고 하심"
              />
            </div>

            {/* 비고 */}
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">비고</label>
              <textarea
                value={formData.notes || ''}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        </form>

        <div className="flex justify-end gap-3 px-6 py-4 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            취소
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? '저장 중...' : '저장'}
          </button>
        </div>
      </div>
    </div>
  );
}