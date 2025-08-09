import { useState } from 'react';
import PaymentModal from '../components/PaymentModal';
import PaymentSummaryCards from '../components/payments/PaymentSummaryCards';
import PaymentFilters from '../components/payments/PaymentFilters';
import PaymentTable from '../components/payments/PaymentTable';
import PaymentExcelUpload from '../components/payments/PaymentExcelUpload';
import { usePayments } from '../hooks/usePayments';


interface Payment {
  payment_id: number;
  payment_number?: string;
  customer_id: number;
  customer_name: string;
  customer_phone: string;
  payment_date: string;
  amount: number;
  payment_method: string;
  payment_type?: string;
  payment_status?: string;
  card_holder_name?: string;
  approval_number?: string;
  payment_staff?: string;
  purchase_type?: string;
  purchase_order?: number;
  notes?: string;
  created_at: string;
}

export default function Payments() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedPayment, setSelectedPayment] = useState<Payment | undefined>();

  const {
    payments,
    summary,
    loading,
    searchTerm,
    dateFrom,
    dateTo,
    paymentMethod,
    paymentStatus,
    setSearchTerm,
    setDateFrom,
    setDateTo,
    setPaymentMethod,
    setPaymentStatus,
    fetchPayments,
    fetchSummary,
    handleDelete,
    handleExcelExport,
    loadMore,
    hasMore
  } = usePayments();

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">결제 관리</h1>

        <PaymentSummaryCards summary={summary} />

        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-800">
            <span className="font-semibold">📊 평균 결제액 계산 방법:</span>
            최근 3개월 기준 전체 결제 금액의 합계 ÷ 전체 결제 건수
          </p>
        </div>

        <PaymentFilters
          searchTerm={searchTerm}
          dateFrom={dateFrom}
          dateTo={dateTo}
          paymentMethod={paymentMethod}
          paymentStatus={paymentStatus}
          onSearchChange={setSearchTerm}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
          onPaymentMethodChange={setPaymentMethod}
          onPaymentStatusChange={setPaymentStatus}
          onExcelExport={handleExcelExport}
          onExcelImport={() => setIsUploadModalOpen(true)}
          onAddPayment={() => setIsModalOpen(true)}
        />

        <PaymentTable
          payments={payments}
          loading={loading}
          onEdit={(payment) => {
            setSelectedPayment(payment);
            setIsModalOpen(true);
          }}
          onDelete={handleDelete}
        />

        {hasMore && !loading && (
          <div className="mt-4 text-center">
            <button
              onClick={loadMore}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              더 보기
              <svg className="ml-2 -mr-0.5 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        )}
      </div>

      <PaymentModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedPayment(undefined);
        }}
        onSuccess={() => {
          setIsModalOpen(false);
          setSelectedPayment(undefined);
          fetchPayments();
          fetchSummary();
        }}
        payment={selectedPayment}
      />

      <PaymentExcelUpload
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={() => {
          setIsUploadModalOpen(false)
          fetchPayments()
          fetchSummary()
        }}
      />
    </div>
  )
}
