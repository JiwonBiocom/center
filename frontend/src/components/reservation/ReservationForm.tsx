import React from 'react';
import { Calendar, Clock } from 'lucide-react';
import CustomerSelector from './CustomerSelector';

interface Customer {
  customer_id: number;
  name: string;
  phone: string | null;
}

interface ServiceType {
  service_type_id: number;
  service_name: string;
  default_duration: number;
  price: number;
}

interface User {
  user_id: number;
  name: string;
  email: string;
}

interface FormData {
  customer_id: string;
  service_type_id: string;
  staff_id: string;
  reservation_date: string;
  reservation_time: string;
  duration_minutes: number;
  status: string;
  customer_request: string;
  internal_memo: string;
}

interface ReservationFormProps {
  formData: FormData;
  setFormData: React.Dispatch<React.SetStateAction<FormData>>;
  customers: Customer[];
  serviceTypes: ServiceType[];
  users: User[];
  isEdit: boolean;
  onSubmit: (e: React.FormEvent) => void;
  loading: boolean;
}

export default function ReservationForm({
  formData,
  setFormData,
  customers,
  serviceTypes,
  users,
  isEdit,
  onSubmit
}: ReservationFormProps) {
  const handleServiceChange = (serviceId: string) => {
    setFormData(prev => ({ ...prev, service_type_id: serviceId }));
    const service = serviceTypes.find(s => s.service_type_id.toString() === serviceId);
    if (service) {
      setFormData(prev => ({ ...prev, duration_minutes: service.default_duration }));
    }
  };

  const timeSlots = [];
  for (let hour = 9; hour <= 20; hour++) {
    for (let minute = 0; minute < 60; minute += 15) {
      const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      timeSlots.push(time);
    }
  }

  return (
    <form id="reservation-form" onSubmit={onSubmit} className="space-y-4">
      <CustomerSelector
        customers={customers}
        selectedCustomerId={formData.customer_id}
        onCustomerSelect={(customerId) => setFormData(prev => ({ ...prev, customer_id: customerId }))}
      />

      {/* 서비스 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          서비스 <span className="text-red-500">*</span>
        </label>
        <select
          value={formData.service_type_id}
          onChange={(e) => handleServiceChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          required
        >
          <option value="">서비스를 선택하세요</option>
          {serviceTypes.map(service => (
            <option key={service.service_type_id} value={service.service_type_id}>
              {service.service_name} ({service.default_duration}분)
            </option>
          ))}
        </select>
      </div>

      {/* 날짜 및 시간 */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            예약 날짜 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <input
              type="date"
              value={formData.reservation_date}
              onChange={(e) => setFormData(prev => ({ ...prev, reservation_date: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            />
            <Calendar className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 pointer-events-none" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            예약 시간 <span className="text-red-500">*</span>
          </label>
          <div className="relative">
            <select
              value={formData.reservation_time}
              onChange={(e) => setFormData(prev => ({ ...prev, reservation_time: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
              required
            >
              {timeSlots.map(time => (
                <option key={time} value={time}>{time}</option>
              ))}
            </select>
            <Clock className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 pointer-events-none" />
          </div>
        </div>
      </div>

      {/* 안내 메시지 */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <p className="text-sm text-blue-700 mb-2">
          ℹ️ 예약이 완료되면 고객님께 SMS가 자동으로 발송됩니다.
        </p>
        <div className="bg-white border border-blue-100 rounded p-3 text-xs text-gray-600">
          <p className="font-medium mb-1">SMS 발송 예시:</p>
          <p className="whitespace-pre-line">[AIBIO 센터] 예약 확인
홍길동님, 예약이 확정되었습니다.

▶ 일시: 2025-06-10 14:00
▶ 서비스: AI-BIKE
▶ 담당: 김직원

변경/취소: 02-2039-2783</p>
        </div>
      </div>

      {/* 소요 시간 및 담당자 */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            소요 시간 (분)
          </label>
          <input
            type="number"
            value={formData.duration_minutes}
            onChange={(e) => setFormData(prev => ({ ...prev, duration_minutes: parseInt(e.target.value) || 60 }))}
            min="15"
            step="15"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            담당자
          </label>
          <select
            value={formData.staff_id}
            onChange={(e) => setFormData(prev => ({ ...prev, staff_id: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">미정</option>
            {users.map(user => (
              <option key={user.user_id} value={user.user_id}>
                {user.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* 상태 (수정 시에만) */}
      {isEdit && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            예약 상태
          </label>
          <p className="text-xs text-blue-600 mb-2">
            ℹ️ 예약 대기 후 확정 상태로 바꿔주세요
          </p>
          <select
            value={formData.status}
            onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="pending">예약 대기</option>
            <option value="confirmed">예약 확정</option>
            <option value="cancelled">예약 취소</option>
            <option value="completed">서비스 완료</option>
            <option value="no_show">노쇼</option>
          </select>
        </div>
      )}

      {/* 고객 요청사항 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          고객 요청사항
        </label>
        <textarea
          value={formData.customer_request}
          onChange={(e) => setFormData(prev => ({ ...prev, customer_request: e.target.value }))}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="고객의 특별한 요청사항을 입력하세요"
        />
      </div>

      {/* 내부 메모 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          내부 메모
        </label>
        <textarea
          value={formData.internal_memo}
          onChange={(e) => setFormData(prev => ({ ...prev, internal_memo: e.target.value }))}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          placeholder="직원들만 볼 수 있는 메모를 입력하세요"
        />
      </div>
    </form>
  );
}