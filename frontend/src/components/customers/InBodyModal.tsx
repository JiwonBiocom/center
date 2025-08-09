import React, { useState, useEffect } from 'react';
import { X, Save, Activity, Calendar, FileText } from 'lucide-react';
import type { InBodyRecord, InBodyRecordCreate, InBodyRecordUpdate } from '../../types/inbody';

interface InBodyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: InBodyRecordCreate | InBodyRecordUpdate) => Promise<void>;
  customerId: number;
  record?: InBodyRecord;
  mode: 'create' | 'edit';
}

const InBodyModal: React.FC<InBodyModalProps> = ({
  isOpen,
  onClose,
  onSave,
  customerId,
  record,
  mode
}) => {
  const [formData, setFormData] = useState({
    measurement_date: '',
    weight: '',
    body_fat_percentage: '',
    skeletal_muscle_mass: '',
    extracellular_water_ratio: '',
    phase_angle: '',
    visceral_fat_level: '',
    notes: '',
    measured_by: ''
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (isOpen) {
      if (mode === 'edit' && record) {
        setFormData({
          measurement_date: record.measurement_date ? record.measurement_date.split('T')[0] : '',
          weight: record.weight?.toString() || '',
          body_fat_percentage: record.body_fat_percentage?.toString() || '',
          skeletal_muscle_mass: record.skeletal_muscle_mass?.toString() || '',
          extracellular_water_ratio: record.extracellular_water_ratio?.toString() || '',
          phase_angle: record.phase_angle?.toString() || '',
          visceral_fat_level: record.visceral_fat_level?.toString() || '',
          notes: record.notes || '',
          measured_by: record.measured_by || ''
        });
      } else {
        // 새 기록 생성 시 오늘 날짜로 초기화
        const today = new Date().toISOString().split('T')[0];
        setFormData({
          measurement_date: today,
          weight: '',
          body_fat_percentage: '',
          skeletal_muscle_mass: '',
          extracellular_water_ratio: '',
          phase_angle: '',
          visceral_fat_level: '',
          notes: '',
          measured_by: ''
        });
      }
      setErrors({});
    }
  }, [isOpen, mode, record]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // 에러 메시지 제거
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.measurement_date) {
      newErrors.measurement_date = '측정일을 선택해주세요.';
    }

    // 숫자 필드 유효성 검사
    const numericFields = [
      { key: 'weight', label: '체중', min: 0, max: 300 },
      { key: 'body_fat_percentage', label: '체지방률', min: 0, max: 100 },
      { key: 'skeletal_muscle_mass', label: '골격근량', min: 0, max: 100 },
      { key: 'extracellular_water_ratio', label: '세포외수분비', min: 0, max: 1 },
      { key: 'phase_angle', label: '위상각', min: 0, max: 20 },
      { key: 'visceral_fat_level', label: '내장지방 레벨', min: 1, max: 30 }
    ];

    numericFields.forEach(field => {
      const value = formData[field.key as keyof typeof formData];
      if (value && value.trim()) {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) {
          newErrors[field.key] = `${field.label}은 숫자로 입력해주세요.`;
        } else if (numValue < field.min || numValue > field.max) {
          newErrors[field.key] = `${field.label}은 ${field.min}~${field.max} 범위로 입력해주세요.`;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const submitData = {
        ...(mode === 'create' && { customer_id: customerId }),
        measurement_date: formData.measurement_date + 'T00:00:00',
        weight: formData.weight ? parseFloat(formData.weight) : undefined,
        body_fat_percentage: formData.body_fat_percentage ? parseFloat(formData.body_fat_percentage) : undefined,
        skeletal_muscle_mass: formData.skeletal_muscle_mass ? parseFloat(formData.skeletal_muscle_mass) : undefined,
        extracellular_water_ratio: formData.extracellular_water_ratio ? parseFloat(formData.extracellular_water_ratio) : undefined,
        phase_angle: formData.phase_angle ? parseFloat(formData.phase_angle) : undefined,
        visceral_fat_level: formData.visceral_fat_level ? parseInt(formData.visceral_fat_level) : undefined,
        notes: formData.notes || undefined,
        measured_by: formData.measured_by || undefined
      };

      await onSave(submitData);
      onClose();
    } catch (error) {
      console.error('Failed to save inbody record:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 text-indigo-500" />
            <h2 className="text-xl font-semibold text-gray-900">
              {mode === 'create' ? '인바디 기록 추가' : '인바디 기록 수정'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 측정 기본 정보 */}
            <div className="md:col-span-2">
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-indigo-500" />
                측정 정보
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    측정일 *
                  </label>
                  <input
                    type="date"
                    name="measurement_date"
                    value={formData.measurement_date}
                    onChange={handleInputChange}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                      errors.measurement_date ? 'border-red-300' : 'border-gray-300'
                    }`}
                    required
                  />
                  {errors.measurement_date && (
                    <p className="mt-1 text-sm text-red-600">{errors.measurement_date}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    측정자
                  </label>
                  <input
                    type="text"
                    name="measured_by"
                    value={formData.measured_by}
                    onChange={handleInputChange}
                    placeholder="측정자 이름"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>
            </div>

            {/* 체성분 정보 */}
            <div className="md:col-span-2">
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                <Activity className="h-5 w-5 text-indigo-500" />
                체성분 분석
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    체중 (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    name="weight"
                    value={formData.weight}
                    onChange={handleInputChange}
                    placeholder="예: 65.5"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                      errors.weight ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.weight && (
                    <p className="mt-1 text-sm text-red-600">{errors.weight}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    체지방률 (%)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    name="body_fat_percentage"
                    value={formData.body_fat_percentage}
                    onChange={handleInputChange}
                    placeholder="예: 18.5"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                      errors.body_fat_percentage ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.body_fat_percentage && (
                    <p className="mt-1 text-sm text-red-600">{errors.body_fat_percentage}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    골격근량 (kg)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    name="skeletal_muscle_mass"
                    value={formData.skeletal_muscle_mass}
                    onChange={handleInputChange}
                    placeholder="예: 28.2"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                      errors.skeletal_muscle_mass ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.skeletal_muscle_mass && (
                    <p className="mt-1 text-sm text-red-600">{errors.skeletal_muscle_mass}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    세포외수분비
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    name="extracellular_water_ratio"
                    value={formData.extracellular_water_ratio}
                    onChange={handleInputChange}
                    placeholder="예: 0.385"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                      errors.extracellular_water_ratio ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.extracellular_water_ratio && (
                    <p className="mt-1 text-sm text-red-600">{errors.extracellular_water_ratio}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    위상각 (°)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    name="phase_angle"
                    value={formData.phase_angle}
                    onChange={handleInputChange}
                    placeholder="예: 6.8"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                      errors.phase_angle ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.phase_angle && (
                    <p className="mt-1 text-sm text-red-600">{errors.phase_angle}</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    내장지방 레벨
                  </label>
                  <input
                    type="number"
                    name="visceral_fat_level"
                    value={formData.visceral_fat_level}
                    onChange={handleInputChange}
                    placeholder="예: 8"
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 ${
                      errors.visceral_fat_level ? 'border-red-300' : 'border-gray-300'
                    }`}
                  />
                  {errors.visceral_fat_level && (
                    <p className="mt-1 text-sm text-red-600">{errors.visceral_fat_level}</p>
                  )}
                </div>
              </div>
            </div>

            {/* 메모 */}
            <div className="md:col-span-2">
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                <FileText className="h-5 w-5 text-indigo-500" />
                추가 정보
              </h3>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  측정 메모
                </label>
                <textarea
                  name="notes"
                  value={formData.notes}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="측정과 관련된 특이사항이나 메모를 입력하세요."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* 버튼 */}
          <div className="flex justify-end gap-3 mt-8 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  저장 중...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  {mode === 'create' ? '저장' : '수정'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InBodyModal;