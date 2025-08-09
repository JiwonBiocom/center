import { useState } from 'react'
import { Calendar, Clock, User, Package, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../../lib/api'

interface ServiceHistoryTabProps {
  customerId: number
}

interface ServiceHistory {
  usage_id: number
  service_date: string
  service_name: string
  service_type_id: number
  duration_minutes: number
  session_number: number | null
  session_details: string | null
  package_name: string | null
  staff_name: string | null
}

interface ServiceHistoryResponse {
  total: number
  limit: number
  offset: number
  data: ServiceHistory[]
}

const serviceTypeColors: Record<number, { bg: string; text: string; label: string }> = {
  1: { bg: 'bg-purple-100', text: 'text-purple-800', label: '브레인' },
  2: { bg: 'bg-blue-100', text: 'text-blue-800', label: '펄스' },
  3: { bg: 'bg-green-100', text: 'text-green-800', label: '림프' },
  4: { bg: 'bg-red-100', text: 'text-red-800', label: '레드' },
  5: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'AI바이크' },
}

export default function ServiceHistoryTab({ customerId }: ServiceHistoryTabProps) {
  const [currentPage, setCurrentPage] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedServiceType, setSelectedServiceType] = useState<number | null>(null)
  const [dateRange, setDateRange] = useState({ start: '', end: '' })

  const pageSize = 10
  const offset = (currentPage - 1) * pageSize

  // 서비스 이력 조회
  const { data: historyResponse, isLoading } = useQuery({
    queryKey: ['service-history', customerId, currentPage, searchTerm, selectedServiceType, dateRange],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: pageSize.toString(),
        offset: offset.toString(),
      })

      // customer_id를 쿼리 파라미터로 전달
      params.append('customer_id', customerId.toString())

      const response = await api.get(`/services/usage?${params}`)
      return response.data
    },
  })

  // API 응답에서 실제 데이터 추출
  const historyData = historyResponse ? {
    data: Array.isArray(historyResponse) ? historyResponse : (historyResponse.data || []),
    total: historyResponse?.total || (Array.isArray(historyResponse) ? historyResponse.length : 0),
    page: historyResponse?.page || 1,
    page_size: historyResponse?.page_size || pageSize
  } : null

  const totalPages = historyData ? Math.ceil(historyData.total / pageSize) : 0

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      weekday: 'short',
    })
  }

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) {
      return `${hours}시간 ${mins > 0 ? `${mins}분` : ''}`
    }
    return `${mins}분`
  }

  const getServiceTypeInfo = (typeId: number) => {
    return serviceTypeColors[typeId] || {
      bg: 'bg-gray-100',
      text: 'text-gray-800',
      label: '기타'
    }
  }

  const filteredData = historyData?.data.filter(item => {
    // 검색어 필터
    if (searchTerm && !item.service_name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false
    }

    // 서비스 타입 필터
    if (selectedServiceType && item.service_type_id !== selectedServiceType) {
      return false
    }

    // 날짜 범위 필터
    if (dateRange.start && new Date(item.service_date) < new Date(dateRange.start)) {
      return false
    }
    if (dateRange.end && new Date(item.service_date) > new Date(dateRange.end)) {
      return false
    }

    return true
  }) || []

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          서비스 이용 이력
          {historyData && (
            <span className="ml-2 text-sm text-gray-500">
              (총 {historyData.total}건)
            </span>
          )}
        </h3>
      </div>

      {/* 필터 섹션 */}
      <div className="bg-gray-50 p-4 rounded-lg space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 검색 */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="서비스명 검색"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          {/* 서비스 타입 필터 */}
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <select
              value={selectedServiceType || ''}
              onChange={(e) => setSelectedServiceType(e.target.value ? Number(e.target.value) : null)}
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 appearance-none"
            >
              <option value="">전체 서비스</option>
              {Object.entries(serviceTypeColors).map(([id, info]) => (
                <option key={id} value={id}>{info.label}</option>
              ))}
            </select>
          </div>

          {/* 날짜 범위 */}
          <div className="flex gap-2">
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            <span className="self-center text-gray-500">~</span>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* 서비스 이력 테이블 */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : filteredData.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">서비스 이용 내역이 없습니다.</p>
        </div>
      ) : (
        <>
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    날짜
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    서비스
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    시간
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    회차
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    패키지
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    담당자
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    메모
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredData.map((history) => {
                  const typeInfo = getServiceTypeInfo(history.service_type_id)
                  return (
                    <tr key={history.usage_id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-900">{formatDate(history.service_date)}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${typeInfo.bg} ${typeInfo.text}`}>
                            {typeInfo.label}
                          </span>
                          <span className="text-gray-900">{history.service_name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{formatTime(history.duration_minutes)}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                        {history.session_number ? `${history.session_number}회차` : '-'}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {history.package_name ? (
                          <div className="flex items-center gap-1">
                            <Package className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-600">{history.package_name}</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {history.staff_name ? (
                          <div className="flex items-center gap-1">
                            <User className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-600">{history.staff_name}</span>
                          </div>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        <div className="max-w-xs truncate" title={history.session_details || ''}>
                          {history.session_details || '-'}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          {/* 페이지네이션 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                전체 {historyData?.total || 0}개 중 {offset + 1}-{Math.min(offset + pageSize, historyData?.total || 0)}개 표시
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="p-2 text-gray-500 hover:text-gray-700 disabled:text-gray-300 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>

                <div className="flex gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                    if (
                      page === 1 ||
                      page === totalPages ||
                      (page >= currentPage - 1 && page <= currentPage + 1)
                    ) {
                      return (
                        <button
                          key={page}
                          onClick={() => setCurrentPage(page)}
                          className={`px-3 py-1 text-sm rounded ${
                            page === currentPage
                              ? 'bg-indigo-600 text-white'
                              : 'text-gray-700 hover:bg-gray-100'
                          }`}
                        >
                          {page}
                        </button>
                      )
                    } else if (
                      page === currentPage - 2 ||
                      page === currentPage + 2
                    ) {
                      return <span key={page} className="px-1 text-gray-400">...</span>
                    }
                    return null
                  })}
                </div>

                <button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="p-2 text-gray-500 hover:text-gray-700 disabled:text-gray-300 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
