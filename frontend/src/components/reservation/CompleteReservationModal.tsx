import { useState, useEffect } from 'react';
import { X, AlertCircle, Package } from 'lucide-react';
import { api } from '../../lib/api';

interface Package {
  purchase_id: number;
  package_id: number;
  package_name: string;
  remaining_sessions: number;
  expiry_date: string;
}

interface CompleteReservationModalProps {
  isOpen: boolean;
  onClose: () => void;
  reservation: any;
  onComplete: () => void;
}

export default function CompleteReservationModal({
  isOpen,
  onClose,
  reservation,
  onComplete
}: CompleteReservationModalProps) {
  const [packages, setPackages] = useState<Package[]>([]);
  const [selectedPackageId, setSelectedPackageId] = useState<number | null>(null);
  const [sessionDetails, setSessionDetails] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && reservation) {
      fetchCustomerPackages();
    }
  }, [isOpen, reservation]);

  const fetchCustomerPackages = async () => {
    try {
      const response = await api.get(`/api/v1/packages/customer/${reservation.customer_id}/active`);
      setPackages(response.data);
    } catch (error) {
      console.error('Failed to fetch customer packages:', error);
    }
  };

  const handleComplete = async () => {
    setError('');
    setLoading(true);

    try {
      const requestData = {
        package_id: selectedPackageId,
        session_details: sessionDetails || undefined
      };

      await api.post(`/api/v1/reservations/${reservation.reservation_id}/complete`, requestData);
      onComplete();
      onClose();
    } catch (error: any) {
      let errorMessage = '서비스 완료 처리에 실패했습니다.';
      
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            서비스 완료 처리
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

        <div className="space-y-4">
          {/* 예약 정보 */}
          <div className="bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium text-gray-900 mb-2">예약 정보</h4>
            <p className="text-sm text-gray-600">고객: {reservation?.customer_name}</p>
            <p className="text-sm text-gray-600">서비스: {reservation?.service_name}</p>
            <p className="text-sm text-gray-600">
              일시: {reservation?.reservation_date} {reservation?.reservation_time}
            </p>
          </div>

          {/* 패키지 선택 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Package className="inline h-4 w-4 mr-1" />
              패키지 사용 (선택사항)
            </label>
            <select
              value={selectedPackageId || ''}
              onChange={(e) => setSelectedPackageId(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="">패키지 미사용</option>
              {packages.map(pkg => (
                <option key={pkg.purchase_id} value={pkg.purchase_id}>
                  {pkg.package_name} (잔여: {pkg.remaining_sessions}회)
                </option>
              ))}
            </select>
            {packages.length === 0 && (
              <p className="text-sm text-gray-500 mt-1">사용 가능한 패키지가 없습니다.</p>
            )}
          </div>

          {/* 세션 상세 내용 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              서비스 상세 내용
            </label>
            <textarea
              value={sessionDetails}
              onChange={(e) => setSessionDetails(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="서비스 진행 내용을 입력하세요 (선택사항)"
            />
          </div>
        </div>

        {/* 버튼 */}
        <div className="flex justify-end space-x-3 mt-6">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            취소
          </button>
          <button
            onClick={handleComplete}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {loading ? '처리 중...' : '서비스 완료'}
          </button>
        </div>
      </div>
    </div>
  );
}