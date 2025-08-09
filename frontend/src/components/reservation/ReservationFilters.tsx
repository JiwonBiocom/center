import { Search, Filter } from 'lucide-react';

interface ReservationFiltersProps {
  searchTerm: string;
  statusFilter: string;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
}

export default function ReservationFilters({
  searchTerm,
  statusFilter,
  onSearchChange,
  onStatusChange
}: ReservationFiltersProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              placeholder="고객명, 전화번호, 서비스명으로 검색"
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => onStatusChange(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="all">전체 상태</option>
            <option value="pending">예약 대기</option>
            <option value="confirmed">예약 확정</option>
            <option value="completed">서비스 완료</option>
            <option value="cancelled">예약 취소</option>
            <option value="no_show">노쇼</option>
          </select>
        </div>
      </div>
    </div>
  );
}