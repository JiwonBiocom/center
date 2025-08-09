import React, { useState, useEffect } from 'react';
import { X, Clock, User, Settings, Calendar } from 'lucide-react';
import { useServiceSessions } from '../../hooks/useEnhancedServices';
import { api } from '../../lib/api';

interface Customer {
  customer_id: number;
  name: string;
  phone: string;
}

interface ServiceType {
  service_type_id: number;
  name: string;
  code: string;
  description: string;
  default_duration: number;
  default_price: string;
}

interface SessionStartModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  serviceTypes: ServiceType[];
}

export default function SessionStartModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  serviceTypes 
}: SessionStartModalProps) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [selectedServiceType, setSelectedServiceType] = useState<ServiceType | null>(null);
  const [sessionDate, setSessionDate] = useState(new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState(new Date().toTimeString().slice(0, 5));
  const [equipmentSettings, setEquipmentSettings] = useState('{}');
  const [notes, setNotes] = useState('');
  const [loadingCustomers, setLoadingCustomers] = useState(false);
  
  const { startSession, loading, error } = useServiceSessions();

  // 고객 검색 - 실제 API 호출
  const searchCustomers = async (term: string) => {
    if (term.length < 2) {
      setCustomers([]);
      return;
    }

    setLoadingCustomers(true);
    try {
      const params = {
        search: term,
        limit: 10
      };
      
      const response = await api.get('/api/v1/customers', { params });
      console.log('Customer search response:', response.data);
      setCustomers(Array.isArray(response.data) ? response.data : []);
    } catch (err: any) {
      console.error('Failed to search customers:', err);
      console.error('Error details:', err.response?.data);
      
      // API 실패 시 fallback 더미 데이터 제공
      const dummyCustomers = [
        { customer_id: 1, name: '김영희', phone: '010-1234-5678' },
        { customer_id: 2, name: '박철수', phone: '010-9876-5432' },
        { customer_id: 3, name: '이민수', phone: '010-5555-1234' },
        { customer_id: 4, name: '정미영', phone: '010-7777-8888' },
        { customer_id: 5, name: '최은진', phone: '010-3333-4444' }
      ];
      
      const filtered = dummyCustomers.filter(customer => 
        customer.name.includes(term) || customer.phone.includes(term)
      );
      
      setCustomers(filtered);
      console.log('Using fallback dummy data:', filtered);
    } finally {
      setLoadingCustomers(false);
    }
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      searchCustomers(searchTerm);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedCustomer || !selectedServiceType) {
      alert('고객과 서비스 타입을 선택해주세요.');
      return;
    }

    try {
      let equipmentData = {};
      try {
        equipmentData = JSON.parse(equipmentSettings);
      } catch (err) {
        // 기본값 사용
      }

      await startSession({
        customer_id: selectedCustomer.customer_id,
        service_type_id: selectedServiceType.service_type_id,
        session_date: sessionDate,
        start_time: startTime,
        equipment_settings: equipmentData,
        session_notes: notes
      });

      onSuccess();
      handleClose();
    } catch (err) {
      console.error('Failed to start session:', err);
    }
  };

  const handleClose = () => {
    setSearchTerm('');
    setSelectedCustomer(null);
    setSelectedServiceType(null);
    setSessionDate(new Date().toISOString().split('T')[0]);
    setStartTime(new Date().toTimeString().slice(0, 5));
    setEquipmentSettings('{}');
    setNotes('');
    setCustomers([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">새 세션 시작</h2>
          <button onClick={handleClose} className="text-gray-400 hover:text-gray-600">
            <X className="h-6 w-6" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Debug Info - 개발 중에만 표시 */}
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm">
          <div><strong>Debug:</strong></div>
          <div>고객 선택됨: {selectedCustomer ? selectedCustomer.name : '없음'}</div>
          <div>서비스 타입 선택됨: {selectedServiceType ? selectedServiceType.name : '없음'}</div>
          <div>버튼 활성화: {(!loading && selectedCustomer && selectedServiceType) ? '예' : '아니오'}</div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 고객 선택 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <User className="h-4 w-4 inline mr-1" />
              고객 선택
            </label>
            <div className="relative">
              <input
                type="text"
                value={selectedCustomer ? selectedCustomer.name : searchTerm}
                onChange={(e) => {
                  if (!selectedCustomer) {
                    setSearchTerm(e.target.value);
                  }
                }}
                placeholder="고객 이름 또는 전화번호로 검색..."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                disabled={!!selectedCustomer}
              />
              {selectedCustomer && (
                <button
                  type="button"
                  onClick={() => {
                    setSelectedCustomer(null);
                    setSearchTerm('');
                  }}
                  className="absolute right-2 top-2 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {/* 고객 검색 결과 */}
            {!selectedCustomer && customers.length > 0 && (
              <div className="mt-2 border border-gray-300 rounded-md bg-white shadow-lg max-h-40 overflow-y-auto">
                {customers.map((customer, index) => (
                  <button
                    key={`customer-${customer.customer_id || index}`}
                    type="button"
                    onClick={() => {
                      console.log('Customer selected:', customer);
                      setSelectedCustomer(customer);
                      setSearchTerm('');
                      setCustomers([]);
                    }}
                    className="w-full text-left px-3 py-2 hover:bg-gray-100 border-b border-gray-100 last:border-b-0"
                  >
                    <div className="font-medium">{customer.name}</div>
                    <div className="text-sm text-gray-600">{customer.phone}</div>
                  </button>
                ))}
              </div>
            )}
            
            {loadingCustomers && (
              <div className="mt-2 text-sm text-gray-500">검색 중...</div>
            )}
            
            {!selectedCustomer && !loadingCustomers && customers.length === 0 && searchTerm.length >= 2 && (
              <div className="mt-2 text-sm text-gray-500">검색 결과가 없습니다.</div>
            )}
          </div>

          {/* 서비스 타입 선택 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Settings className="h-4 w-4 inline mr-1" />
              서비스 타입
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {serviceTypes.map((type, index) => (
                <button
                  key={`modal-service-type-${type.service_type_id || index}`}
                  type="button"
                  onClick={() => {
                    console.log('Service type selected:', type);
                    setSelectedServiceType(type);
                  }}
                  className={`p-3 border rounded-lg text-left transition-colors ${
                    selectedServiceType?.service_type_id === type.service_type_id
                      ? 'border-indigo-500 bg-indigo-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <div className="font-medium">{type.name}</div>
                  <div className="text-sm text-gray-600">{type.default_duration}분</div>
                  <div className="text-sm text-gray-600">
                    {Number(type.default_price).toLocaleString()}원
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* 일정 설정 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4 inline mr-1" />
                세션 날짜
              </label>
              <input
                type="date"
                value={sessionDate}
                onChange={(e) => setSessionDate(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Clock className="h-4 w-4 inline mr-1" />
                시작 시간
              </label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
          </div>

          {/* 장비 설정 (선택사항) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              장비 설정 (JSON, 선택사항)
            </label>
            <textarea
              value={equipmentSettings}
              onChange={(e) => setEquipmentSettings(e.target.value)}
              rows={3}
              placeholder='{"intensity": "medium", "frequency": "10Hz"}'
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* 세션 노트 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              세션 노트 (선택사항)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              placeholder="세션에 대한 특별한 사항이나 고객 요청사항을 기록하세요..."
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* 버튼 */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300 transition-colors"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading || !selectedCustomer || !selectedServiceType}
              className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              onClick={() => {
                console.log('Button click debug:', {
                  loading,
                  selectedCustomer,
                  selectedServiceType,
                  disabled: loading || !selectedCustomer || !selectedServiceType
                });
              }}
            >
              {loading ? '시작 중...' : '세션 시작'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}