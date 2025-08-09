import { Filter, Calendar, Users, Activity, DollarSign, AlertTriangle } from 'lucide-react';
import { type AdvancedFilters } from '../../hooks/useCustomers';
import { useReferralSources } from '../../hooks/useReferralSources';
import RegionAutocomplete from '../RegionAutocomplete';

interface CustomerAdvancedFiltersProps {
  isOpen: boolean;
  onToggle: () => void;
  filters: AdvancedFilters;
  onFiltersChange: (filters: AdvancedFilters) => void;
  onClearFilters: () => void;
  filteredCount?: number;
  totalCount?: number;
}

export default function CustomerAdvancedFilters({
  isOpen,
  onToggle,
  filters,
  onFiltersChange,
  onClearFilters,
  filteredCount,
  totalCount
}: CustomerAdvancedFiltersProps) {
  const { referralSources, loading: referralSourcesLoading } = useReferralSources();

  const updateFilter = (key: keyof AdvancedFilters, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const activeFiltersCount = Object.values(filters).filter(value => {
    if (typeof value === 'object' && value !== null) {
      return Object.values(value).some(v => v !== undefined && v !== '');
    }
    return value !== undefined && value !== '';
  }).length;

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      {/* Filter Toggle Button */}
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between text-left hover:bg-gray-50 rounded-t-lg"
      >
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700">고급 필터</span>
          {activeFiltersCount > 0 && (
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {activeFiltersCount}
            </span>
          )}
          {/* 필터 결과 실시간 표시 */}
          {filteredCount !== undefined && totalCount !== undefined && (
            <span className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded-full">
              {activeFiltersCount > 0 ? (
                <>📊 {filteredCount}/{totalCount}명 검색됨</>
              ) : (
                <>👥 전체 {totalCount}명</>
              )}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {activeFiltersCount > 0 && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onClearFilters();
              }}
              className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-100"
            >
              초기화
            </button>
          )}
          <div className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}>
            ▼
          </div>
        </div>
      </button>

      {/* Filter Content */}
      {isOpen && (
        <div className="border-t border-gray-200 p-4 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* 고객 상태 */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Users className="h-4 w-4" />
                고객 상태
              </label>
              <select
                value={filters.customerStatus || ''}
                onChange={(e) => updateFilter('customerStatus', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">전체</option>
                <option value="active">활성</option>
                <option value="inactive">비활성</option>
                <option value="dormant">휴면</option>
              </select>
            </div>

            {/* 멤버십 레벨 */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Activity className="h-4 w-4" />
                멤버십 레벨
              </label>
              <select
                value={filters.membershipLevel || ''}
                onChange={(e) => updateFilter('membershipLevel', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">전체</option>
                <option value="basic">베이직</option>
                <option value="premium">프리미엄</option>
                <option value="vip">VIP</option>
              </select>
            </div>

            {/* 위험도 */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <AlertTriangle className="h-4 w-4" />
                위험도
              </label>
              <select
                value={filters.riskLevel || ''}
                onChange={(e) => updateFilter('riskLevel', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">전체</option>
                <option value="stable">안정</option>
                <option value="warning">주의</option>
                <option value="danger">위험</option>
              </select>
            </div>

            {/* 지역 */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">지역</label>
              <RegionAutocomplete
                value={filters.regionFilter || ''}
                onChange={(value) => updateFilter('regionFilter', value || undefined)}
                placeholder="예: 서울, 부산, 대구..."
              />
            </div>

            {/* 유입 경로 */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">유입 경로</label>
              <select
                value={filters.referralSource || ''}
                onChange={(e) => updateFilter('referralSource', e.target.value || undefined)}
                disabled={referralSourcesLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50"
              >
                <option value="">전체</option>
                {referralSourcesLoading ? (
                  <option disabled>로딩 중...</option>
                ) : (
                  referralSources.map(source => (
                    <option key={source} value={source}>
                      {source}
                    </option>
                  ))
                )}
              </select>
            </div>
          </div>

          {/* 숫자 범위 필터들 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* 나이 범위 */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">나이 범위</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={filters.ageRange?.min || ''}
                  onChange={(e) => updateFilter('ageRange', {
                    ...filters.ageRange,
                    min: e.target.value ? parseInt(e.target.value) : undefined
                  })}
                  placeholder="최소"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <span className="self-center text-gray-500">~</span>
                <input
                  type="number"
                  value={filters.ageRange?.max || ''}
                  onChange={(e) => updateFilter('ageRange', {
                    ...filters.ageRange,
                    max: e.target.value ? parseInt(e.target.value) : undefined
                  })}
                  placeholder="최대"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* 총 매출 범위 */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <DollarSign className="h-4 w-4" />
                총 매출 범위 (만원)
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={filters.totalRevenueRange?.min || ''}
                  onChange={(e) => updateFilter('totalRevenueRange', {
                    ...filters.totalRevenueRange,
                    min: e.target.value ? parseInt(e.target.value) : undefined
                  })}
                  placeholder="최소"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <span className="self-center text-gray-500">~</span>
                <input
                  type="number"
                  value={filters.totalRevenueRange?.max || ''}
                  onChange={(e) => updateFilter('totalRevenueRange', {
                    ...filters.totalRevenueRange,
                    max: e.target.value ? parseInt(e.target.value) : undefined
                  })}
                  placeholder="최대"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* 총 방문 횟수 범위 */}
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">총 방문 횟수</label>
              <div className="flex gap-2">
                <input
                  type="number"
                  value={filters.totalVisitsRange?.min || ''}
                  onChange={(e) => updateFilter('totalVisitsRange', {
                    ...filters.totalVisitsRange,
                    min: e.target.value ? parseInt(e.target.value) : undefined
                  })}
                  placeholder="최소"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <span className="self-center text-gray-500">~</span>
                <input
                  type="number"
                  value={filters.totalVisitsRange?.max || ''}
                  onChange={(e) => updateFilter('totalVisitsRange', {
                    ...filters.totalVisitsRange,
                    max: e.target.value ? parseInt(e.target.value) : undefined
                  })}
                  placeholder="최대"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* 날짜 범위 필터들 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 첫 방문일 범위 */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4" />
                첫 방문일 범위
              </label>
              <div className="flex gap-2">
                <input
                  type="date"
                  value={filters.firstVisitDateRange?.from || ''}
                  onChange={(e) => updateFilter('firstVisitDateRange', {
                    ...filters.firstVisitDateRange,
                    from: e.target.value || undefined
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <span className="self-center text-gray-500">~</span>
                <input
                  type="date"
                  value={filters.firstVisitDateRange?.to || ''}
                  onChange={(e) => updateFilter('firstVisitDateRange', {
                    ...filters.firstVisitDateRange,
                    to: e.target.value || undefined
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* 마지막 방문일 범위 */}
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <Calendar className="h-4 w-4" />
                마지막 방문일 범위
              </label>
              <div className="flex gap-2">
                <input
                  type="date"
                  value={filters.lastVisitDateRange?.from || ''}
                  onChange={(e) => updateFilter('lastVisitDateRange', {
                    ...filters.lastVisitDateRange,
                    from: e.target.value || undefined
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <span className="self-center text-gray-500">~</span>
                <input
                  type="date"
                  value={filters.lastVisitDateRange?.to || ''}
                  onChange={(e) => updateFilter('lastVisitDateRange', {
                    ...filters.lastVisitDateRange,
                    to: e.target.value || undefined
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          {/* 적용된 필터 요약 */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600">
                  {activeFiltersCount > 0 ? (
                    <>총 {activeFiltersCount}개의 필터가 적용되었습니다.</>
                  ) : (
                    <>모든 고객을 표시하고 있습니다.</>
                  )}
                </span>
                {filteredCount !== undefined && totalCount !== undefined && (
                  <div className="flex items-center gap-1">
                    <span className="text-lg">📊</span>
                    <span className="text-sm font-medium text-blue-600">
                      {filteredCount.toLocaleString()}명 / {totalCount.toLocaleString()}명
                    </span>
                    {activeFiltersCount > 0 && (
                      <span className="text-xs text-gray-500">
                        ({((filteredCount / totalCount) * 100).toFixed(1)}%)
                      </span>
                    )}
                  </div>
                )}
              </div>
              {activeFiltersCount > 0 && (
                <button
                  onClick={onClearFilters}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  모든 필터 초기화
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
