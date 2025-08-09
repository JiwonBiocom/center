import React, { useState, useEffect } from 'react';
import { X, CreditCard, Package, Calendar, User, DollarSign } from 'lucide-react';
import { api } from '../../lib/api';

interface PackagePurchaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  customerId: number;
  customerName: string;
  onSuccess: () => void;
}

interface PackageOption {
  package_id: number;
  package_name: string;
  price: number;
  valid_days: number;
  total_sessions: number;
  description?: string;
}

export default function PackagePurchaseModal({
  isOpen,
  onClose,
  customerId,
  customerName,
  onSuccess
}: PackagePurchaseModalProps) {
  const [packages, setPackages] = useState<PackageOption[]>([]);
  const [selectedPackage, setSelectedPackage] = useState<PackageOption | null>(null);
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [paymentAmount, setPaymentAmount] = useState('');
  const [staffMemo, setStaffMemo] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadPackages();
    }
  }, [isOpen]);

  const loadPackages = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/packages/available');
      setPackages(response.data.data || []);
    } catch (error) {
      console.error('Failed to load packages:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePackageSelect = (pkg: PackageOption) => {
    setSelectedPackage(pkg);
    setPaymentAmount(pkg.price.toString());
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedPackage || !paymentAmount) {
      alert('패키지와 결제 금액을 확인해주세요.');
      return;
    }

    try {
      setIsSubmitting(true);
      
      // 패키지 구매 처리
      const purchaseData = {
        customer_id: customerId,
        package_id: selectedPackage.package_id,
        payment_amount: parseInt(paymentAmount),
        payment_method: paymentMethod,
        staff_memo: staffMemo,
        purchase_date: new Date().toISOString(),
        start_date: new Date().toISOString(),
        // 만료일 계산 (구매일 + 유효일수)
        end_date: new Date(Date.now() + selectedPackage.valid_days * 24 * 60 * 60 * 1000).toISOString()
      };

      await api.post('/packages/purchase', purchaseData);
      
      onSuccess();
      onClose();
      
      // 성공 메시지
      alert(`${selectedPackage.package_name} 패키지가 성공적으로 등록되었습니다.`);
      
    } catch (error: any) {
      console.error('Failed to purchase package:', error);
      alert('패키지 구매 처리 중 오류가 발생했습니다: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatPrice = (price: number) => {
    return price.toLocaleString() + '원';
  };

  const getSessionsSummary = (pkg: PackageOption) => {
    return `총 ${pkg.total_sessions}회`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Package className="h-6 w-6 text-blue-600" />
              패키지 구매
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              <User className="h-4 w-4 inline mr-1" />
              {customerName} 고객
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {/* 패키지 선택 */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-4">패키지 선택</h3>
            
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-600 mt-2">패키지 목록을 불러오는 중...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {packages.map((pkg) => (
                  <div
                    key={pkg.package_id}
                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedPackage?.package_id === pkg.package_id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handlePackageSelect(pkg)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-semibold text-lg">{pkg.package_name}</h4>
                      <span className="text-xl font-bold text-blue-600">
                        {formatPrice(pkg.price)}
                      </span>
                    </div>
                    
                    <div className="space-y-1 text-sm text-gray-600 mb-3">
                      <p className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        유효기간: {pkg.valid_days}일
                      </p>
                      <p>{getSessionsSummary(pkg)}</p>
                    </div>
                    
                    {pkg.description && (
                      <p className="text-sm text-gray-500">{pkg.description}</p>
                    )}
                    
                    {selectedPackage?.package_id === pkg.package_id && (
                      <div className="mt-3 p-2 bg-blue-100 rounded text-sm text-blue-800">
                        ✓ 선택됨
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedPackage && (
            <>
              {/* 결제 정보 */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-medium mb-4">결제 정보</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  {/* 결제 방법 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      결제 방법
                    </label>
                    <select
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="card">신용카드</option>
                      <option value="samsung_pay">삼성페이</option>
                      <option value="apple_pay">애플페이</option>
                      <option value="kakao_pay">카카오페이</option>
                      <option value="cash">현금</option>
                      <option value="bank_transfer">계좌이체</option>
                    </select>
                  </div>

                  {/* 결제 금액 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      결제 금액
                    </label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <input
                        type="number"
                        value={paymentAmount}
                        onChange={(e) => setPaymentAmount(e.target.value)}
                        className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="결제 금액"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* 직원 메모 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    직원 메모 (선택사항)
                  </label>
                  <textarea
                    value={staffMemo}
                    onChange={(e) => setStaffMemo(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="할인 사유, 특이사항 등을 입력하세요..."
                  />
                </div>
              </div>

              {/* 구매 요약 */}
              <div className="mb-6 p-4 border rounded-lg">
                <h3 className="text-lg font-medium mb-3">구매 요약</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>패키지명:</span>
                    <span className="font-medium">{selectedPackage.package_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>정가:</span>
                    <span>{formatPrice(selectedPackage.price)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>결제금액:</span>
                    <span className="font-medium text-blue-600">
                      {formatPrice(parseInt(paymentAmount) || 0)}
                    </span>
                  </div>
                  {parseInt(paymentAmount) !== selectedPackage.price && (
                    <div className="flex justify-between text-red-600">
                      <span>할인/할증:</span>
                      <span className="font-medium">
                        {formatPrice(parseInt(paymentAmount) - selectedPackage.price)}
                      </span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>유효기간:</span>
                    <span>{selectedPackage.valid_days}일</span>
                  </div>
                  <div className="flex justify-between">
                    <span>결제방법:</span>
                    <span>{paymentMethod === 'card' ? '신용카드' : 
                           paymentMethod === 'samsung_pay' ? '삼성페이' :
                           paymentMethod === 'apple_pay' ? '애플페이' :
                           paymentMethod === 'kakao_pay' ? '카카오페이' :
                           paymentMethod === 'cash' ? '현금' : '계좌이체'}</span>
                  </div>
                </div>
              </div>
            </>
          )}

          {/* 버튼 */}
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              disabled={isSubmitting}
            >
              취소
            </button>
            <button
              type="submit"
              disabled={!selectedPackage || !paymentAmount || isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  처리 중...
                </>
              ) : (
                <>
                  <CreditCard className="h-4 w-4" />
                  구매 완료
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}