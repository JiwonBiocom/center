import { useState, useEffect } from 'react';
import { X, Weight, Activity } from 'lucide-react';
import { api } from '../../lib/api';

interface ExperienceService {
  experience_id?: number;
  lead_id: number;
  service_date: string;
  service_types: string;
  before_weight?: number;
  after_weight?: number;
  before_muscle_mass?: number;
  after_muscle_mass?: number;
  before_body_fat?: number;
  after_body_fat?: number;
  phase_angle_change?: number;
  result_summary?: string;
  staff_name?: string;
}

interface ExperienceServiceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  leadId: number;
  experienceData?: ExperienceService | null;
}

export default function ExperienceServiceModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  leadId,
  experienceData 
}: ExperienceServiceModalProps) {
  const [formData, setFormData] = useState<ExperienceService>({
    lead_id: leadId,
    service_date: new Date().toISOString().split('T')[0],
    service_types: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (experienceData) {
      setFormData(experienceData);
    } else {
      setFormData({
        lead_id: leadId,
        service_date: new Date().toISOString().split('T')[0],
        service_types: ''
      });
    }
  }, [experienceData, leadId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (experienceData?.experience_id) {
        await api.put(`/api/v1/customer-leads/experiences/${experienceData.experience_id}`, formData);
      } else {
        await api.post('/api/v1/customer-leads/experiences', formData);
      }
      onSuccess();
    } catch (error) {
      console.error('Failed to save experience:', error);
      alert('저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const calculateChanges = () => {
    const weightChange = formData.after_weight && formData.before_weight 
      ? (formData.after_weight - formData.before_weight).toFixed(1) 
      : null;
    
    const muscleChange = formData.after_muscle_mass && formData.before_muscle_mass
      ? (formData.after_muscle_mass - formData.before_muscle_mass).toFixed(1)
      : null;
    
    const fatChange = formData.after_body_fat && formData.before_body_fat
      ? (formData.after_body_fat - formData.before_body_fat).toFixed(1)
      : null;
    
    return { weightChange, muscleChange, fatChange };
  };

  if (!isOpen) return null;

  const { weightChange, muscleChange, fatChange } = calculateChanges();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {experienceData ? '체험 서비스 수정' : '체험 서비스 기록'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                체험 일자 <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                required
                value={formData.service_date}
                onChange={(e) => setFormData({ ...formData, service_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                체험 서비스 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.service_types}
                onChange={(e) => setFormData({ ...formData, service_types: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 레드+림프+펄스"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">담당 직원</label>
              <input
                type="text"
                value={formData.staff_name || ''}
                onChange={(e) => setFormData({ ...formData, staff_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* 체중 변화 */}
            <div className="col-span-2 mt-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <Weight className="w-5 h-5 mr-2 text-indigo-600" />
                체중 변화
              </h3>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 전 체중(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.before_weight || ''}
                onChange={(e) => setFormData({ ...formData, before_weight: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 후 체중(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.after_weight || ''}
                onChange={(e) => setFormData({ ...formData, after_weight: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {weightChange && (
              <div className="col-span-2 text-center py-2 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">체중 변화: </span>
                <span className={`font-medium ${parseFloat(weightChange) < 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {parseFloat(weightChange) > 0 ? '+' : ''}{weightChange}kg
                </span>
              </div>
            )}

            {/* 체성분 변화 */}
            <div className="col-span-2 mt-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-indigo-600" />
                체성분 변화
              </h3>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 전 골격근량(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.before_muscle_mass || ''}
                onChange={(e) => setFormData({ ...formData, before_muscle_mass: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 후 골격근량(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.after_muscle_mass || ''}
                onChange={(e) => setFormData({ ...formData, after_muscle_mass: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {muscleChange && (
              <div className="col-span-2 text-center py-2 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">골격근량 변화: </span>
                <span className={`font-medium ${parseFloat(muscleChange) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {parseFloat(muscleChange) > 0 ? '+' : ''}{muscleChange}kg
                </span>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 전 체지방량(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.before_body_fat || ''}
                onChange={(e) => setFormData({ ...formData, before_body_fat: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">체험 후 체지방량(kg)</label>
              <input
                type="number"
                step="0.1"
                value={formData.after_body_fat || ''}
                onChange={(e) => setFormData({ ...formData, after_body_fat: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {fatChange && (
              <div className="col-span-2 text-center py-2 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">체지방량 변화: </span>
                <span className={`font-medium ${parseFloat(fatChange) < 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {parseFloat(fatChange) > 0 ? '+' : ''}{fatChange}kg
                </span>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">위상각 변화</label>
              <input
                type="number"
                step="0.1"
                value={formData.phase_angle_change || ''}
                onChange={(e) => setFormData({ ...formData, phase_angle_change: parseFloat(e.target.value) || undefined })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 0.2"
              />
            </div>

            {/* 결과 요약 */}
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">결과 요약</label>
              <textarea
                value={formData.result_summary || ''}
                onChange={(e) => setFormData({ ...formData, result_summary: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                placeholder="체험 결과에 대한 요약을 작성하세요"
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