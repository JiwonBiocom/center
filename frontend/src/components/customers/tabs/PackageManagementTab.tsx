import { useState } from 'react';
import { Package, AlertCircle, Plus, Activity } from 'lucide-react';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import PackagePurchaseModal from '../PackagePurchaseModal';
import CustomerPackageUsage from '../CustomerPackageUsage';

interface PackageManagementTabProps {
  customerId: number;
  customerName: string;
  packages: any[];
  onRefresh: () => void;
}

export default function PackageManagementTab({ customerId, customerName, packages, onRefresh }: PackageManagementTabProps) {
  const [showAddPackage, setShowAddPackage] = useState(false);
  const [showServiceDetail, setShowServiceDetail] = useState(false);

  // 패키지 상태별 색상
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-gray-100 text-gray-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'suspended':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // 패키지 상태 한글 변환
  const getStatusText = (status: string) => {
    switch (status) {
      case 'active':
        return '이용중';
      case 'expired':
        return '만료';
      case 'completed':
        return '완료';
      case 'suspended':
        return '일시중지';
      default:
        return status;
    }
  };

  return (
    <div className="space-y-6">
      {/* 탭 네비게이션 */}
      <div className="border-b">
        <div className="flex space-x-8">
          <button
            onClick={() => setShowServiceDetail(false)}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              !showServiceDetail
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            패키지 구매 내역
          </button>
          <button
            onClick={() => setShowServiceDetail(true)}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              showServiceDetail
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            서비스별 이용 현황
          </button>
        </div>
      </div>

      {/* 서비스별 이용 현황 탭 */}
      {showServiceDetail ? (
        <CustomerPackageUsage customerId={customerId} />
      ) : (
        <>
          {/* 패키지 구매 버튼 */}
          <div className="flex justify-end">
            <button
              onClick={() => setShowAddPackage(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <Plus className="h-4 w-4" />
              패키지 구매
            </button>
          </div>

      {/* 패키지 목록 */}
      {packages && packages.length > 0 ? (
        <div className="space-y-4">
          {packages.map((pkg) => (
            <div key={pkg.purchase_id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-lg font-semibold flex items-center gap-2">
                    <Package className="h-5 w-5 text-blue-600" />
                    {pkg.package_name}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {format(new Date(pkg.purchase_date), 'yyyy년 MM월 dd일', { locale: ko })} 구매
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(pkg.status)}`}>
                  {getStatusText(pkg.status)}
                </span>
              </div>

              {/* 전체 세션 정보 */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-sm text-gray-600">전체 이용 현황</p>
                  <p className="text-2xl font-semibold">
                    {pkg.remaining_sessions}
                    <span className="text-sm text-gray-500 ml-1">/ {pkg.total_sessions}회</span>
                  </p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${(pkg.remaining_sessions / pkg.total_sessions) * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  사용: {pkg.used_sessions}회
                </p>
              </div>

              {/* 패키지 정보 */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">구매금액</p>
                  <p className="font-medium">{pkg.price?.toLocaleString()}원</p>
                </div>
                <div>
                  <p className="text-gray-600">구매일</p>
                  <p className="font-medium">
                    {format(new Date(pkg.purchase_date), 'yyyy.MM.dd')}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">만료일</p>
                  <p className="font-medium">
                    {format(new Date(pkg.expiry_date), 'yyyy.MM.dd')}
                  </p>
                </div>
              </div>

              {/* 만료 임박 경고 */}
              {pkg.status === 'active' && new Date(pkg.expiry_date) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) && (
                <div className="mt-4 flex items-center gap-2 text-yellow-600 bg-yellow-50 p-3 rounded-md">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm">
                    {Math.ceil((new Date(pkg.expiry_date).getTime() - Date.now()) / (24 * 60 * 60 * 1000))}일 후 만료 예정
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">구매한 패키지가 없습니다.</p>
          <button
            onClick={() => setShowAddPackage(true)}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            패키지 구매하기
          </button>
        </div>
      )}
        </>
      )}

      {/* 패키지 구매 모달 */}
      <PackagePurchaseModal
        isOpen={showAddPackage}
        onClose={() => setShowAddPackage(false)}
        customerId={customerId}
        customerName={customerName}
        onSuccess={() => {
          onRefresh();
          setShowAddPackage(false);
        }}
      />
    </div>
  );
}
