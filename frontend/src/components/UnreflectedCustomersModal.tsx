import React, { useState, useEffect } from 'react';
import { X, ArrowRight, Trash2, Search, Filter } from 'lucide-react';
import { api } from '../lib/api';
import { formatDate } from '../utils/formatters';

interface UnreflectedCustomer {
  id: number;
  original_customer_id?: number;
  name: string;
  phone?: string;
  email?: string;
  region?: string;
  referral_source?: string;
  data_source?: string;
  import_date?: string;
  status: string;
  created_at?: string;
}

interface UnreflectedCustomersModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function UnreflectedCustomersModal({ isOpen, onClose, onSuccess }: UnreflectedCustomersModalProps) {
  const [customers, setCustomers] = useState<UnreflectedCustomer[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [stats, setStats] = useState<any>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    if (isOpen) {
      fetchUnreflectedCustomers();
      fetchStats();
    }
  }, [isOpen, search, selectedSource, currentPage]);

  const fetchUnreflectedCustomers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: ((currentPage - 1) * 20).toString(),
        limit: '20'
      });

      if (search) params.append('search', search);
      if (selectedSource) params.append('data_source', selectedSource);

      const response = await api.get(`/unreflected-customers?${params}`);
      setCustomers(response.data.data);
      setTotalPages(Math.ceil(response.data.total / 20));
    } catch (error) {
      console.error('미반영 고객 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/unreflected-customers/stats/summary');
      setStats(response.data);
    } catch (error) {
      console.error('통계 조회 실패:', error);
    }
  };

  const handleMoveBack = async (customerId: number) => {
    if (!confirm('이 고객을 정식 고객으로 이동하시겠습니까?')) return;

    try {
      await api.post(`/unreflected-customers/${customerId}/move-back`);
      await fetchUnreflectedCustomers();
      await fetchStats();
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('고객 이동 실패:', error);
      alert('고객 이동에 실패했습니다.');
    }
  };

  const handleDelete = async (customerId: number) => {
    if (!confirm('이 고객을 거부 처리하시겠습니까?')) return;

    try {
      await api.delete(`/unreflected-customers/${customerId}`);
      await fetchUnreflectedCustomers();
      await fetchStats();
    } catch (error) {
      console.error('고객 삭제 실패:', error);
      alert('고객 삭제에 실패했습니다.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-800">미반영 고객 DB</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={24} />
          </button>
        </div>

        {/* Stats */}
        {stats && (
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-600">전체:</span>
                <span className="ml-2 font-semibold">{stats.total}명</span>
              </div>
              <div>
                <span className="text-gray-600">대기중:</span>
                <span className="ml-2 font-semibold text-yellow-600">
                  {stats.by_status?.pending || 0}명
                </span>
              </div>
              <div>
                <span className="text-gray-600">이동됨:</span>
                <span className="ml-2 font-semibold text-green-600">
                  {stats.by_status?.moved_back || 0}명
                </span>
              </div>
              <div>
                <span className="text-gray-600">거부됨:</span>
                <span className="ml-2 font-semibold text-red-600">
                  {stats.by_status?.rejected || 0}명
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="이름 또는 전화번호로 검색"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">모든 출처</option>
              <option value="초기 마이그레이션 (6/5)">초기 마이그레이션</option>
              <option value="월별 이용현황 import (6/25)">월별 이용현황</option>
              <option value="수동 입력 또는 테스트 데이터">수동 입력</option>
              <option value="Unknown">Unknown</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          <table className="w-full">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">전화번호</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">지역</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">유입경로</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">데이터 출처</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    로딩 중...
                  </td>
                </tr>
              ) : customers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    미반영 고객이 없습니다.
                  </td>
                </tr>
              ) : (
                customers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {customer.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {customer.phone || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {customer.region || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {customer.referral_source || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {customer.data_source || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        customer.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                        customer.status === 'moved_back' ? 'bg-green-100 text-green-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {customer.status === 'pending' ? '대기중' :
                         customer.status === 'moved_back' ? '이동됨' : '거부됨'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                      {customer.status === 'pending' && (
                        <div className="flex justify-center gap-2">
                          <button
                            onClick={() => handleMoveBack(customer.id)}
                            className="text-blue-600 hover:text-blue-900"
                            title="정식 고객으로 이동"
                          >
                            <ArrowRight size={18} />
                          </button>
                          <button
                            onClick={() => handleDelete(customer.id)}
                            className="text-red-600 hover:text-red-900"
                            title="거부 처리"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex justify-center">
            <nav className="flex gap-2">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
              >
                이전
              </button>
              <span className="px-3 py-1">
                {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
              >
                다음
              </button>
            </nav>
          </div>
        )}
      </div>
    </div>
  );
}
