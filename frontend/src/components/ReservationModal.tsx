import React, { useState, useEffect } from 'react';
import { X, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';
import { api } from '../lib/api';
import type { User } from '../types';
import ReservationForm from './reservation/ReservationForm';
import CompleteReservationModal from './reservation/CompleteReservationModal';

interface ServiceType {
  service_type_id: number;
  service_name: string;
  default_duration: number;
  price: number;
}

interface ReservationModalProps {
  isOpen: boolean;
  onClose: () => void;
  reservation?: any;
  selectedDate: Date;
  customers: Array<{
    customer_id: number;
    name: string;
    phone: string | null;
    [key: string]: any;
  }>;
  onSave: () => void;
}

export default function ReservationModal({
  isOpen,
  onClose,
  reservation,
  selectedDate,
  customers,
  onSave
}: ReservationModalProps) {
  const [formData, setFormData] = useState<{
    customer_id: string;
    customer_name?: string;
    customer_phone?: string;
    service_type_id: string;
    staff_id: string;
    reservation_date: string;
    reservation_time: string;
    duration_minutes: number;
    status: string;
    customer_request: string;
    internal_memo: string;
  }>({
    customer_id: '',
    customer_name: '',
    customer_phone: '',
    service_type_id: '',
    staff_id: '',
    reservation_date: format(selectedDate, 'yyyy-MM-dd'),
    reservation_time: '09:00',
    duration_minutes: 60,
    status: 'pending',
    customer_request: '',
    internal_memo: ''
  });

  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCompleteModal, setShowCompleteModal] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchData();
      if (reservation) {
        setFormData({
          customer_id: reservation.customer_id.toString(),
          customer_name: '',
          customer_phone: '',
          service_type_id: reservation.service_type_id.toString(),
          staff_id: reservation.staff_id ? reservation.staff_id.toString() : '',
          reservation_date: reservation.reservation_date,
          reservation_time: reservation.reservation_time,
          duration_minutes: reservation.duration_minutes,
          status: reservation.status,
          customer_request: reservation.customer_request || '',
          internal_memo: reservation.internal_memo || ''
        });
      } else {
        // 새 예약 생성 시 초기화
        setFormData({
          customer_id: '',
          customer_name: '',
          customer_phone: '',
          service_type_id: '',
          staff_id: '',
          reservation_date: format(selectedDate, 'yyyy-MM-dd'),
          reservation_time: '09:00',
          duration_minutes: 60,
          status: 'pending',
          customer_request: '',
          internal_memo: ''
        });
      }
    }
  }, [isOpen, reservation, selectedDate]);

  const fetchData = async () => {
    try {
      const [servicesRes, usersRes] = await Promise.all([
        api.get('/api/v1/services/types'),
        api.get('/api/v1/settings/users')
      ]);
      
      setServiceTypes(Array.isArray(servicesRes.data) ? servicesRes.data : servicesRes.data.data || []);
      setUsers(Array.isArray(usersRes.data) ? usersRes.data : usersRes.data.data || []);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 데이터 타입 변환
      const requestData: any = {
        service_type_id: parseInt(formData.service_type_id),
        staff_id: formData.staff_id ? parseInt(formData.staff_id) : null,
        duration_minutes: parseInt(formData.duration_minutes.toString()),
        reservation_date: formData.reservation_date,
        reservation_time: formData.reservation_time,
        customer_request: formData.customer_request,
        internal_memo: formData.internal_memo,
        status: formData.status
      };

      // Handle customer creation for new customers first
      let finalCustomerId = formData.customer_id;
      
      if (!formData.customer_id || formData.customer_id === '') {
        // Create customer first if it's a new customer
        if (formData.customer_name && formData.customer_name !== '') {
          try {
            const customerData = {
              name: formData.customer_name,
              phone: formData.customer_phone || null,
              membership_level: 'basic',
              customer_status: 'active',
              memo: `예약 시 자동 생성 (${formData.reservation_date})`
            };
            
            const customerResponse = await api.post('/api/v1/customers', customerData);
            finalCustomerId = customerResponse.data.customer_id?.toString() || customerResponse.data.data?.customer_id?.toString();
            console.log('Created new customer with ID:', finalCustomerId);
          } catch (customerError: any) {
            console.error('Failed to create customer:', customerError);
            throw new Error('고객 정보 생성에 실패했습니다.');
          }
        }
      }
      
      // Now always send customer_id
      if (!finalCustomerId || finalCustomerId === '') {
        throw new Error('고객 정보가 없습니다. 고객을 선택하거나 새 고객 정보를 입력해주세요.');
      }
      
      requestData.customer_id = parseInt(finalCustomerId);
      
      console.log('Sending reservation data:', requestData);
      console.log('FormData state:', formData);
      
      if (reservation) {
        await api.put(`/api/v1/reservations/${reservation.reservation_id}`, requestData);
      } else {
        await api.post('/api/v1/reservations', requestData);
      }
      onSave();
      onClose();
    } catch (error: any) {
      console.log('Error response:', error.response?.data);
      let errorMessage = '예약 저장에 실패했습니다.';
      
      if (error.response?.data?.detail) {
        if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail.map((err: any) => err.msg || err).join(', ');
        } else {
          errorMessage = error.response.data.detail;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!reservation) return;
    
    const reason = prompt('취소 사유를 입력하세요:');
    if (!reason) return;

    try {
      await api.post(`/api/v1/reservations/${reservation.reservation_id}/cancel`, {
        reason
      });
      onSave();
      onClose();
    } catch (error: any) {
      setError(error.response?.data?.detail || '예약 취소에 실패했습니다.');
    }
  };

  const handleDelete = async () => {
    if (!reservation) return;
    
    if (!confirm('정말로 이 예약을 삭제하시겠습니까?\n삭제된 예약은 복구할 수 없습니다.')) {
      return;
    }

    setLoading(true);
    try {
      await api.delete(`/api/v1/reservations/${reservation.reservation_id}`);
      onSave();
      onClose();
    } catch (error: any) {
      setError(error.response?.data?.detail || '예약 삭제에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = () => {
    if (!reservation) return;
    setShowCompleteModal(true);
  };

  const handleCompleteSuccess = () => {
    setShowCompleteModal(false);
    onSave();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            {reservation ? '예약 수정' : '새 예약'}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-start">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2 flex-shrink-0 mt-0.5" />
            <span className="text-sm text-red-800">{error}</span>
          </div>
        )}

        <ReservationForm
          formData={formData}
          setFormData={setFormData}
          customers={customers}
          serviceTypes={serviceTypes}
          users={users}
          isEdit={!!reservation}
          onSubmit={handleSubmit}
          loading={loading}
        />

        {/* 버튼 */}
        <div className="flex justify-between pt-4">
          <div className="flex space-x-2">
            {reservation && (
              <>
                {reservation.status === 'confirmed' && (
                  <>
                    <button
                      type="button"
                      onClick={handleComplete}
                      className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      서비스 완료
                    </button>
                    <button
                      type="button"
                      onClick={handleCancel}
                      className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      예약 취소
                    </button>
                  </>
                )}
                {reservation.status === 'cancelled' && (
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={loading}
                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
                  >
                    {loading ? '삭제 중...' : '예약 삭제'}
                  </button>
                )}
              </>
            )}
          </div>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              취소
            </button>
            <button
              type="submit"
              form="reservation-form"
              disabled={loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? '저장 중...' : '저장'}
            </button>
          </div>
        </div>
      </div>

      {/* 서비스 완료 모달 */}
      <CompleteReservationModal
        isOpen={showCompleteModal}
        onClose={() => setShowCompleteModal(false)}
        reservation={reservation}
        onComplete={handleCompleteSuccess}
      />
    </div>
  );
}
