import React, { useState, useEffect } from 'react';
import { X, Plus, Edit3, Trash2, Save, Clock, DollarSign, Settings, Package } from 'lucide-react';
import { useServiceTypes } from '../../hooks/useEnhancedServices';

interface ServiceType {
  service_type_id: number;
  name: string;
  code: string;
  description: string;
  default_duration: number;
  default_price: string;
  equipment_required?: any;
  protocols?: any;
  intensity_levels?: any;
  is_active: boolean;
  sort_order: number;
}

interface ServiceTypeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  serviceTypes: ServiceType[];
}

const defaultServiceType = {
  name: '',
  code: '',
  description: '',
  default_duration: 30,
  default_price: '50000',
  equipment_required: {},
  protocols: {},
  intensity_levels: {},
  is_active: true,
  sort_order: 0
};

export default function ServiceTypeModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  serviceTypes 
}: ServiceTypeModalProps) {
  const [mode, setMode] = useState<'list' | 'create' | 'edit'>('list');
  const [editingType, setEditingType] = useState<ServiceType | null>(null);
  const [formData, setFormData] = useState(defaultServiceType);
  const [equipmentJson, setEquipmentJson] = useState('{}');
  const [protocolsJson, setProtocolsJson] = useState('{}');
  const [intensityJson, setIntensityJson] = useState('{}');
  
  const { createServiceType, updateServiceType, loading, error } = useServiceTypes();

  useEffect(() => {
    if (editingType) {
      setFormData({
        name: editingType.name,
        code: editingType.code,
        description: editingType.description,
        default_duration: editingType.default_duration,
        default_price: editingType.default_price,
        equipment_required: editingType.equipment_required || {},
        protocols: editingType.protocols || {},
        intensity_levels: editingType.intensity_levels || {},
        is_active: editingType.is_active,
        sort_order: editingType.sort_order
      });
      setEquipmentJson(JSON.stringify(editingType.equipment_required || {}, null, 2));
      setProtocolsJson(JSON.stringify(editingType.protocols || {}, null, 2));
      setIntensityJson(JSON.stringify(editingType.intensity_levels || {}, null, 2));
    }
  }, [editingType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      // JSON 파싱
      let equipment = {};
      let protocols = {};
      let intensity = {};
      
      try {
        equipment = JSON.parse(equipmentJson);
        protocols = JSON.parse(protocolsJson);
        intensity = JSON.parse(intensityJson);
      } catch (err) {
        alert('JSON 형식이 올바르지 않습니다.');
        return;
      }

      const serviceTypeData = {
        ...formData,
        equipment_required: equipment,
        protocols,
        intensity_levels: intensity
      };

      if (mode === 'create') {
        await createServiceType(serviceTypeData);
      } else if (mode === 'edit' && editingType) {
        await updateServiceType(editingType.service_type_id, serviceTypeData);
      }

      onSuccess();
      handleClose();
    } catch (err) {
      console.error('Failed to save service type:', err);
    }
  };

  const handleClose = () => {
    setMode('list');
    setEditingType(null);
    setFormData(defaultServiceType);
    setEquipmentJson('{}');
    setProtocolsJson('{}');
    setIntensityJson('{}');
    onClose();
  };

  const handleEdit = (serviceType: ServiceType) => {
    setEditingType(serviceType);
    setMode('edit');
  };

  const handleCreate = () => {
    setEditingType(null);
    setFormData(defaultServiceType);
    setEquipmentJson('{}');
    setProtocolsJson('{}');
    setIntensityJson('{}');
    setMode('create');
  };

  const handleDelete = async (serviceType: ServiceType) => {
    if (!confirm(`"${serviceType.name}" 서비스 타입을 정말 삭제하시겠습니까?`)) {
      return;
    }

    try {
      // 실제로는 삭제 API 호출 필요
      alert('삭제 기능은 아직 구현되지 않았습니다.');
    } catch (err) {
      console.error('Failed to delete service type:', err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">
            {mode === 'list' && '서비스 타입 관리'}
            {mode === 'create' && '새 서비스 타입 추가'}
            {mode === 'edit' && '서비스 타입 편집'}
          </h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="overflow-y-auto" style={{ maxHeight: 'calc(90vh - 120px)' }}>
          {error && (
            <div className="m-6 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          {/* 목록 보기 */}
          {mode === 'list' && (
            <div className="p-6">
              <div className="mb-4 flex justify-between items-center">
                <h3 className="text-lg font-medium">현재 서비스 타입</h3>
                <button 
                  onClick={handleCreate}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  새 타입 추가
                </button>
              </div>
              
              <div className="grid gap-4">
                {serviceTypes.map((type, index) => (
                  <div key={`manage-service-type-${type.service_type_id || index}`} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="text-lg font-medium text-gray-900">{type.name}</h4>
                          <span className="px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-700">
                            {type.code}
                          </span>
                          <span className={`px-2 py-1 text-xs font-medium rounded ${
                            type.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                          }`}>
                            {type.is_active ? '활성' : '비활성'}
                          </span>
                        </div>
                        <p className="text-gray-600 mb-3">{type.description}</p>
                        <div className="flex items-center space-x-6 text-sm text-gray-500">
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {type.default_duration}분
                          </div>
                          <div className="flex items-center">
                            <DollarSign className="h-4 w-4 mr-1" />
                            {Number(type.default_price).toLocaleString()}원
                          </div>
                          <div className="flex items-center">
                            <Package className="h-4 w-4 mr-1" />
                            순서: {type.sort_order}
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2 ml-4">
                        <button
                          onClick={() => handleEdit(type)}
                          className="p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded"
                        >
                          <Edit3 className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(type)}
                          className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 생성/편집 폼 */}
          {(mode === 'create' || mode === 'edit') && (
            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      서비스명 *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      코드 *
                    </label>
                    <input
                      type="text"
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                      placeholder="BRAIN, PULSE, etc."
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    설명
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    rows={3}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Clock className="h-4 w-4 inline mr-1" />
                      기본 시간 (분) *
                    </label>
                    <input
                      type="number"
                      value={formData.default_duration}
                      onChange={(e) => setFormData({ ...formData, default_duration: parseInt(e.target.value) })}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                      min="1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <DollarSign className="h-4 w-4 inline mr-1" />
                      기본 가격 (원) *
                    </label>
                    <input
                      type="number"
                      value={formData.default_price}
                      onChange={(e) => setFormData({ ...formData, default_price: e.target.value })}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                      min="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      <Package className="h-4 w-4 inline mr-1" />
                      정렬 순서
                    </label>
                    <input
                      type="number"
                      value={formData.sort_order}
                      onChange={(e) => setFormData({ ...formData, sort_order: parseInt(e.target.value) })}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      min="0"
                    />
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                    활성 상태
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <Settings className="h-4 w-4 inline mr-1" />
                    장비 설정 (JSON)
                  </label>
                  <textarea
                    value={equipmentJson}
                    onChange={(e) => setEquipmentJson(e.target.value)}
                    rows={4}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
                    placeholder='{"device": "Brain Optimizer Pro", "channels": 8}'
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    프로토콜 설정 (JSON)
                  </label>
                  <textarea
                    value={protocolsJson}
                    onChange={(e) => setProtocolsJson(e.target.value)}
                    rows={4}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
                    placeholder='{"basic": {"frequency": "8-12Hz", "duration": 40}}'
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    강도 레벨 설정 (JSON)
                  </label>
                  <textarea
                    value={intensityJson}
                    onChange={(e) => setIntensityJson(e.target.value)}
                    rows={4}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
                    placeholder='{"weak": {"power": 30}, "medium": {"power": 60}, "strong": {"power": 90}}'
                  />
                </div>

                <div className="flex space-x-3">
                  <button
                    type="button"
                    onClick={() => setMode('list')}
                    className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors"
                  >
                    목록으로
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {loading ? '저장 중...' : '저장'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}