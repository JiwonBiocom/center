import { useState } from 'react';
import CustomerModal from '../components/CustomerModal';
import CustomerDetailModal from '../components/customers/CustomerDetailModal';
import CustomerHeader from '../components/customers/CustomerHeader';
import CustomerSearch from '../components/customers/CustomerSearch';
import CustomerAdvancedFilters from '../components/customers/CustomerAdvancedFilters';
import CustomerTable from '../components/customers/CustomerTable';
import CustomerPagination from '../components/customers/CustomerPagination';
import SMSModal from '../components/SMSModal';
import UnreflectedCustomersModal from '../components/UnreflectedCustomersModal';
import { useCustomers, type AdvancedFilters } from '../hooks/useCustomers';
import { api } from '../lib/api';


interface Customer {
  customer_id: number;
  name: string;
  phone: string;
  first_visit_date: string;
  region: string;
  referral_source: string;
  health_concerns?: string;
  notes?: string;
  assigned_staff?: string;
}

export default function Customers() {
  const [modalOpen, setModalOpen] = useState(false);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | undefined>();
  const [smsModalOpen, setSmsModalOpen] = useState(false);
  const [selectedCustomersForSMS, setSelectedCustomersForSMS] = useState<Customer[]>([]);
  const [unreflectedModalOpen, setUnreflectedModalOpen] = useState(false);

  // 고급 필터 상태
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [advancedFilters, setAdvancedFilters] = useState<AdvancedFilters>({});

  const {
    customers,
    loading,
    searchTerm,
    totalCount,
    allCustomersCount,
    currentPage,
    uploading,
    uploadProgress,
    pageSize,
    sortBy,
    sortOrder,
    fetchCustomers,
    handleDelete,
    handleExcelExport,
    handleExcelImport,
    handleSearchChange,
    handlePageChange,
    handleSort
  } = useCustomers(advancedFilters);

  const handleEdit = (customer: Customer) => {
    setSelectedCustomer(customer);
    setModalOpen(true);
  };

  const handleModalClose = () => {
    setModalOpen(false);
    setSelectedCustomer(undefined);
  };

  const handleModalSuccess = () => {
    fetchCustomers();
    handleModalClose();
  };

  const handleAddCustomer = () => {
    setSelectedCustomer(undefined);
    setModalOpen(true);
  };

  const handleView = (customer: Customer) => {
    setSelectedCustomer(customer);
    setDetailModalOpen(true);
  };

  // SMS 발송 핸들러
  const handleSendSMS = (customer?: Customer) => {
    if (customer) {
      setSelectedCustomersForSMS([customer]);
    } else {
      // 전체 고객에게 발송하는 경우
      setSelectedCustomersForSMS(customers);
    }
    setSmsModalOpen(true);
  };

  // 고급 필터 핸들러
  const handleFiltersToggle = () => {
    setFiltersOpen(!filtersOpen);
  };

  const handleFiltersChange = (filters: AdvancedFilters) => {
    setAdvancedFilters(filters);
    handlePageChange(1); // 필터 변경 시 첫 페이지로 이동
  };

  const handleClearFilters = () => {
    setAdvancedFilters({});
    handlePageChange(1); // 필터 초기화 시 첫 페이지로 이동
  };

  const handleServiceHistoryImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/api/v1/customers/import/service-history/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      const result = response.data;
      let message = `서비스 이력 업데이트 완료!\n`;

      if (result.customers_updated > 0) {
        message += `업데이트된 고객: ${result.customers_updated}명\n`;
      }
      if (result.service_records_added > 0) {
        message += `추가된 서비스 기록: ${result.service_records_added}건\n`;
      }
      if (result.package_records_added > 0) {
        message += `추가된 패키지 기록: ${result.package_records_added}건`;
      }

      if (result.errors && result.errors.length > 0) {
        message += '\n\n오류 내역:';
        result.errors.forEach((error: string) => {
          message += `\n- ${error}`;
        });
      }

      alert(message);
      fetchCustomers(); // 고객 목록 새로고침
    } catch (error: any) {
      console.error('Failed to import service history:', error);
      alert(error.response?.data?.detail || '서비스 이력 가져오기에 실패했습니다.');
    } finally {
      // Reset file input
      event.target.value = '';
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <p className="text-gray-500">로딩 중...</p>
      </div>
    )
  }

  return (
    <div className="p-8">
      <CustomerHeader
        totalCount={totalCount}
        onExcelExport={handleExcelExport}
        onExcelImport={handleExcelImport}
        onServiceHistoryImport={handleServiceHistoryImport}
        onAddCustomer={handleAddCustomer}
        onUnreflectedCustomers={() => setUnreflectedModalOpen(true)}
        uploading={uploading}
        uploadProgress={uploadProgress}
      />

      <CustomerSearch
        searchTerm={searchTerm}
        onSearchChange={handleSearchChange}
      />

      <CustomerAdvancedFilters
        isOpen={filtersOpen}
        onToggle={handleFiltersToggle}
        filters={advancedFilters}
        onFiltersChange={handleFiltersChange}
        onClearFilters={handleClearFilters}
        filteredCount={totalCount}
        totalCount={allCustomersCount}
      />

      <CustomerTable
        customers={customers}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onView={handleView}
        onSendSMS={handleSendSMS}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSort={handleSort}
      />

      <CustomerPagination
        totalCount={totalCount}
        currentPage={currentPage}
        pageSize={pageSize}
        onPageChange={handlePageChange}
      />

      <CustomerModal
        isOpen={modalOpen}
        onClose={handleModalClose}
        onSuccess={handleModalSuccess}
        customer={selectedCustomer}
      />

      {selectedCustomer && (
        <CustomerDetailModal
          isOpen={detailModalOpen}
          onClose={() => setDetailModalOpen(false)}
          customerId={selectedCustomer.customer_id}
          customerName={selectedCustomer.name}
        />
      )}

      <SMSModal
        isOpen={smsModalOpen}
        onClose={() => setSmsModalOpen(false)}
        selectedCustomers={selectedCustomersForSMS}
        onSuccess={() => {
          setSmsModalOpen(false);
          setSelectedCustomersForSMS([]);
        }}
      />

      <UnreflectedCustomersModal
        isOpen={unreflectedModalOpen}
        onClose={() => setUnreflectedModalOpen(false)}
        onSuccess={fetchCustomers}
      />

      {/* 회원 등급 및 고객 상태 설명 */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">회원 등급 안내</h3>
          <div className="space-y-3">
            <div className="flex items-start">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 mr-3">
                Bronze
              </span>
              <div className="text-sm text-gray-600">
                <p className="font-medium">기본 회원</p>
                <p>연 매출 500만원 미만 또는 누적 방문 10회 이하</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mr-3">
                Silver
              </span>
              <div className="text-sm text-gray-600">
                <p className="font-medium">실버 회원</p>
                <p>연 매출 500만원 이상 또는 누적 방문 11-30회</p>
                <p className="text-xs mt-1">혜택: 5% 할인</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 mr-3">
                Gold
              </span>
              <div className="text-sm text-gray-600">
                <p className="font-medium">골드 회원</p>
                <p>연 매출 1,000만원 이상 또는 누적 방문 31-50회</p>
                <p className="text-xs mt-1">혜택: 10% 할인, 생일 쿠폰</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800 mr-3">
                Platinum
              </span>
              <div className="text-sm text-gray-600">
                <p className="font-medium">플래티넘 회원</p>
                <p>연 매출 2,000만원 이상 또는 누적 방문 51회 이상</p>
                <p className="text-xs mt-1">혜택: 15% 할인, 우선 예약, VIP 이벤트</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">고객 상태 안내</h3>
          <div className="space-y-3">
            <div className="flex items-start">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mr-3">
                활성
              </span>
              <div className="text-sm text-gray-600">
                <p className="font-medium">활성 고객</p>
                <p>최근 30일 이내 방문한 고객</p>
                <p className="text-xs mt-1 text-green-600">정기적으로 센터를 이용하고 있습니다</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 mr-3">
                비활성
              </span>
              <div className="text-sm text-gray-600">
                <p className="font-medium">비활성 고객</p>
                <p>31-90일 전에 마지막으로 방문한 고객</p>
                <p className="text-xs mt-1 text-yellow-600">재방문 유도가 필요합니다</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mr-3">
                휴면
              </span>
              <div className="text-sm text-gray-600">
                <p className="font-medium">휴면 고객</p>
                <p>90일 이상 방문하지 않은 고객</p>
                <p className="text-xs mt-1 text-gray-600">재등록 캠페인 대상입니다</p>
              </div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-700">
              <span className="font-medium">참고:</span> 고객 상태는 예약 완료 시 자동으로 업데이트되며,
              매일 자정에 전체 고객 상태가 재계산됩니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
