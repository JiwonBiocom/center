import { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { api } from '../../lib/api';

interface ConsultationData {
  consultation_id?: number;
  lead_id: number;
  consultation_date: string;
  consultation_type: string;
  consulted_by: string;
  consultation_content: string;
  next_action?: string;
  next_action_date?: string;
}

interface ConsultationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  leadId: number;
  consultationData?: ConsultationData | null;
}

const consultationTypes = [
  { value: 'phone', label: '전화 상담' },
  { value: 'visit', label: '방문 상담' },
  { value: 'online', label: '온라인 상담' },
  { value: 'follow_up', label: '후속 상담' }
];

export default function ConsultationModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  leadId, 
  consultationData 
}: ConsultationModalProps) {
  const [formData, setFormData] = useState<ConsultationData>({
    lead_id: leadId,
    consultation_date: new Date().toISOString().slice(0, 16),
    consultation_type: 'phone',
    consulted_by: '',
    consultation_content: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (consultationData) {
      setFormData({
        ...consultationData,
        consultation_date: consultationData.consultation_date.slice(0, 16)
      });
    } else {
      setFormData({
        lead_id: leadId,
        consultation_date: new Date().toISOString().slice(0, 16),
        consultation_type: 'phone',
        consulted_by: '',
        consultation_content: ''
      });
    }
  }, [consultationData, leadId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const submitData = {
        ...formData,
        consultation_date: new Date(formData.consultation_date).toISOString()
      };

      if (consultationData?.consultation_id) {
        await api.put(
          `/api/v1/customer-leads/${leadId}/consultations/${consultationData.consultation_id}`,
          submitData
        );
      } else {
        await api.post(
          `/api/v1/customer-leads/${leadId}/consultations`,
          submitData
        );
      }
      onSuccess();
    } catch (error) {
      console.error('Failed to save consultation:', error);
      alert('상담 기록 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {consultationData ? '상담 기록 수정' : '신규 상담 기록'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상담 일시 <span className="text-red-500">*</span>
              </label>
              <input
                type="datetime-local"
                required
                value={formData.consultation_date}
                onChange={(e) => setFormData({ ...formData, consultation_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                상담 유형 <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.consultation_type}
                onChange={(e) => setFormData({ ...formData, consultation_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                {consultationTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              상담자 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={formData.consulted_by}
              onChange={(e) => setFormData({ ...formData, consulted_by: e.target.value })}
              placeholder="상담을 진행한 직원명"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              상담 내용 <span className="text-red-500">*</span>
            </label>
            <textarea
              required
              value={formData.consultation_content}
              onChange={(e) => setFormData({ ...formData, consultation_content: e.target.value })}
              rows={6}
              placeholder="상담 내용을 자세히 기록하세요..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div className="border-t pt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">후속 조치 (선택사항)</h3>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  다음 조치사항
                </label>
                <textarea
                  value={formData.next_action || ''}
                  onChange={(e) => setFormData({ ...formData, next_action: e.target.value })}
                  rows={3}
                  placeholder="필요한 후속 조치를 기록하세요..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  조치 예정일
                </label>
                <input
                  type="date"
                  value={formData.next_action_date || ''}
                  onChange={(e) => setFormData({ ...formData, next_action_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
              </div>
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