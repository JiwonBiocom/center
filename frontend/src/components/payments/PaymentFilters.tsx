import { Search, Plus, Download, Upload } from 'lucide-react';

interface PaymentFiltersProps {
  searchTerm: string;
  dateFrom: string;
  dateTo: string;
  paymentMethod: string;
  paymentStatus?: string;
  onSearchChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onPaymentMethodChange: (value: string) => void;
  onPaymentStatusChange?: (value: string) => void;
  onExcelExport: () => void;
  onExcelImport?: () => void;
  onAddPayment: () => void;
}

export default function PaymentFilters({
  searchTerm,
  dateFrom,
  dateTo,
  paymentMethod,
  paymentStatus,
  onSearchChange,
  onDateFromChange,
  onDateToChange,
  onPaymentMethodChange,
  onPaymentStatusChange,
  onExcelExport,
  onExcelImport,
  onAddPayment
}: PaymentFiltersProps) {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">검색</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="고객명, 전화번호, 승인번호..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">시작일</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => onDateFromChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">종료일</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => onDateToChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">결제 방법</label>
          <select
            value={paymentMethod}
            onChange={(e) => onPaymentMethodChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">전체</option>
            <option value="card">카드</option>
            <option value="transfer">계좌이체</option>
            <option value="cash">현금</option>
            <option value="other">기타</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">결제 상태</label>
          <select
            value={paymentStatus || ''}
            onChange={(e) => onPaymentStatusChange?.(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">전체</option>
            <option value="completed">완료</option>
            <option value="cancelled">취소</option>
            <option value="refunded">환불</option>
            <option value="pending">대기</option>
          </select>
        </div>
      </div>

      <div className="mt-4 flex justify-between">
        <div className="flex gap-2">
          <button
            onClick={onExcelExport}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 bg-white text-gray-700 rounded-md hover:bg-gray-50"
          >
            <Download className="w-4 h-4" />
            엑셀 내보내기
          </button>
          {onExcelImport && (
            <button
              onClick={onExcelImport}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 bg-white text-gray-700 rounded-md hover:bg-gray-50"
            >
              <Upload className="w-4 h-4" />
              엑셀 업로드
            </button>
          )}
        </div>
        <button
          onClick={onAddPayment}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          <Plus className="w-4 h-4" />
          결제 등록
        </button>
      </div>
    </div>
  );
}
