import { Search, X } from 'lucide-react';

interface CustomerLeadFiltersProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  onSearch: () => void;
  selectedStatus: string[];
  onStatusChange: (values: string[]) => void;
  selectedChannels: string[];
  onChannelsChange: (values: string[]) => void;
  selectedRegions: string[];
  onRegionsChange: (values: string[]) => void;
  dateRange: { from?: string; to?: string };
  onDateRangeChange: (range: { from?: string; to?: string }) => void;
}

const statusOptions = [
  { value: 'new', label: '신규' },
  { value: 'db_entered', label: 'DB입력' },
  { value: 'phone_consulted', label: '전화상담' },
  { value: 'visit_consulted', label: '방문상담' },
  { value: 'converted', label: '등록완료' }
];

const channelOptions = [
  '인스타그램', '네이버', '카카오', '페이스북', 
  '구글', '당근마켓', '지인소개', '기타'
];

const regionOptions = [
  '서울', '경기', '인천', '부산', '대구', 
  '광주', '대전', '울산', '세종', '강원'
];

export default function CustomerLeadFilters({
  searchTerm,
  onSearchChange,
  onSearch,
  selectedStatus,
  onStatusChange,
  selectedChannels,
  onChannelsChange,
  selectedRegions,
  onRegionsChange,
  dateRange,
  onDateRangeChange
}: CustomerLeadFiltersProps) {
  const handleStatusToggle = (value: string) => {
    if (selectedStatus.includes(value)) {
      onStatusChange(selectedStatus.filter(s => s !== value));
    } else {
      onStatusChange([...selectedStatus, value]);
    }
  };

  const handleChannelToggle = (value: string) => {
    if (selectedChannels.includes(value)) {
      onChannelsChange(selectedChannels.filter(c => c !== value));
    } else {
      onChannelsChange([...selectedChannels, value]);
    }
  };

  const handleRegionToggle = (value: string) => {
    if (selectedRegions.includes(value)) {
      onRegionsChange(selectedRegions.filter(r => r !== value));
    } else {
      onRegionsChange([...selectedRegions, value]);
    }
  };

  const clearAllFilters = () => {
    onSearchChange('');
    onStatusChange([]);
    onChannelsChange([]);
    onRegionsChange([]);
    onDateRangeChange({});
  };

  const hasActiveFilters = searchTerm || selectedStatus.length > 0 || 
    selectedChannels.length > 0 || selectedRegions.length > 0 || 
    dateRange.from || dateRange.to;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
      {/* 검색 */}
      <div className="mb-4">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && onSearch()}
              placeholder="이름, 전화번호, 당근ID, 비고로 검색"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={onSearch}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            검색
          </button>
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              필터 초기화
            </button>
          )}
        </div>
      </div>

      {/* 필터들 */}
      <div className="space-y-4">
        {/* 날짜 범위 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">DB 입력일</label>
          <div className="flex gap-2 items-center">
            <input
              type="date"
              value={dateRange.from || ''}
              onChange={(e) => onDateRangeChange({ ...dateRange, from: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
            <span className="text-gray-500">~</span>
            <input
              type="date"
              value={dateRange.to || ''}
              onChange={(e) => onDateRangeChange({ ...dateRange, to: e.target.value })}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        {/* 상태 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">상태</label>
          <div className="flex flex-wrap gap-2">
            {statusOptions.map(option => (
              <button
                key={option.value}
                onClick={() => handleStatusToggle(option.value)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  selectedStatus.includes(option.value)
                    ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-500'
                    : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* 채널 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">유입경로</label>
          <div className="flex flex-wrap gap-2">
            {channelOptions.map(channel => (
              <button
                key={channel}
                onClick={() => handleChannelToggle(channel)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  selectedChannels.includes(channel)
                    ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-500'
                    : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
                }`}
              >
                {channel}
              </button>
            ))}
          </div>
        </div>

        {/* 지역 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">거주지역</label>
          <div className="flex flex-wrap gap-2">
            {regionOptions.map(region => (
              <button
                key={region}
                onClick={() => handleRegionToggle(region)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  selectedRegions.includes(region)
                    ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-500'
                    : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:bg-gray-200'
                }`}
              >
                {region}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}