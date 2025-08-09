import React, { useEffect, useState } from 'react';
import { Calendar, Package, AlertCircle, Edit2, X, Check } from 'lucide-react';
import { api } from '../../lib/api';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

interface ServiceUsage {
  total: number;
  used: number;
  remaining: number;
}

interface PackageUsage {
  purchase_id: number;
  package_name: string;
  purchase_date: string;
  expiry_date: string | null;
  total_sessions: number;
  used_sessions: number;
  remaining_sessions: number;
  is_active: boolean;
  service_usage: {
    [key: string]: ServiceUsage;
  };
}

interface CustomerPackageUsageProps {
  customerId: number;
}

export default function CustomerPackageUsage({ customerId }: CustomerPackageUsageProps) {
  const [packages, setPackages] = useState<PackageUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingPackageId, setEditingPackageId] = useState<number | null>(null);
  const [editValues, setEditValues] = useState<{ used: number; remaining: number }>({ used: 0, remaining: 0 });
  const [editingServiceAllocations, setEditingServiceAllocations] = useState<{ [key: string]: { used: number; total: number } }>({});

  useEffect(() => {
    fetchPackages();
  }, [customerId]);

  const fetchPackages = async () => {
    try {
      const response = await api.get(`/customers/${customerId}/packages/`);
      setPackages(response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch packages:', error);
      alert('패키지 정보를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleUseSession = async (purchaseId: number, serviceType: string) => {
    try {
      await api.post(`/customers/${customerId}/packages/${purchaseId}/use/`, null, {
        params: { service_type: serviceType }
      });

      alert(`${serviceType} 세션이 사용 처리되었습니다.`);

      // 데이터 새로고침
      fetchPackages();
    } catch (error) {
      console.error('Failed to use session:', error);
      alert('세션 사용 처리에 실패했습니다.');
    }
  };

  const handleEditClick = (pkg: PackageUsage) => {
    setEditingPackageId(pkg.purchase_id);
    setEditValues({ used: pkg.used_sessions, remaining: pkg.remaining_sessions });

    // 서비스별 할당량 초기화
    const allocations: { [key: string]: { used: number; total: number } } = {};
    Object.entries(pkg.service_usage).forEach(([service, usage]) => {
      allocations[service] = {
        used: usage.used,
        total: usage.total
      };
    });
    setEditingServiceAllocations(allocations);
  };

  const handleCancelEdit = () => {
    setEditingPackageId(null);
    setEditValues({ used: 0, remaining: 0 });
    setEditingServiceAllocations({});
  };

  const handleSaveEdit = async (purchaseId: number) => {
    try {
      await api.put(`/customers/${customerId}/packages/${purchaseId}/services/`, {
        service_allocations: editingServiceAllocations
      });

      alert('서비스별 할당량이 수정되었습니다.');
      setEditingPackageId(null);
      setEditingServiceAllocations({});
      fetchPackages();
    } catch (error) {
      console.error('Failed to update package:', error);
      alert('패키지 수정에 실패했습니다.');
    }
  };

  const updateServiceAllocation = (service: string, field: 'used' | 'total', value: number) => {
    setEditingServiceAllocations(prev => ({
      ...prev,
      [service]: {
        ...prev[service],
        [field]: value
      }
    }));
  };

  if (loading) {
    return <div className="p-4">로딩 중...</div>;
  }

  if (packages.length === 0) {
    return (
      <div className="bg-white rounded-lg border p-6">
        <div className="text-center text-gray-500">
          <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
          <p>구매한 패키지가 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {packages.map((pkg) => (
        <div key={pkg.purchase_id} className="bg-white rounded-lg border p-6">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold">
                {/* 서비스명만 표시 */}
                {Object.keys(pkg.service_usage).join(', ')}
              </h3>
              <div className="flex items-center gap-2">
                {editingPackageId === pkg.purchase_id ? (
                  <>
                    <button
                      onClick={() => handleSaveEdit(pkg.purchase_id)}
                      className="p-1.5 text-green-600 hover:bg-green-50 rounded"
                      title="저장"
                    >
                      <Check className="h-4 w-4" />
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      className="p-1.5 text-red-600 hover:bg-red-50 rounded"
                      title="취소"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleEditClick(pkg)}
                    className="p-1.5 text-gray-600 hover:bg-gray-100 rounded"
                    title="수정"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                )}
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  pkg.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {pkg.is_active ? '사용 가능' : '만료됨'}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                <span>구매일: {format(new Date(pkg.purchase_date), 'yyyy.MM.dd', { locale: ko })}</span>
              </div>
              {pkg.expiry_date && (
                <div className="flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  <span>만료일: {format(new Date(pkg.expiry_date), 'yyyy.MM.dd', { locale: ko })}</span>
                </div>
              )}
            </div>
          </div>
            {/* 전체 진행률 */}
            {editingPackageId !== pkg.purchase_id && (
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span>전체 이용률</span>
                  <span>{pkg.used_sessions} / {pkg.total_sessions} 회</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(pkg.used_sessions / pkg.total_sessions) * 100}%` }}
                  />
                </div>
              </div>
            )}

            {/* 서비스별 이용 현황 */}
            <div className="space-y-3">
              {Object.entries(pkg.service_usage).map(([serviceType, usage]) => (
                <div key={serviceType} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{serviceType}</h4>
                    {editingPackageId !== pkg.purchase_id && (
                      <button
                        className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                          !pkg.is_active || usage.remaining === 0
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                        }`}
                        onClick={() => handleUseSession(pkg.purchase_id, serviceType)}
                        disabled={!pkg.is_active || usage.remaining === 0}
                      >
                        사용
                      </button>
                    )}
                  </div>

                  {editingPackageId === pkg.purchase_id ? (
                    <div className="space-y-2">
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            사용
                          </label>
                          <input
                            type="number"
                            min="0"
                            value={editingServiceAllocations[serviceType]?.used || 0}
                            onChange={(e) => updateServiceAllocation(serviceType, 'used', parseInt(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-600 mb-1">
                            전체
                          </label>
                          <input
                            type="number"
                            min="0"
                            value={editingServiceAllocations[serviceType]?.total || 0}
                            onChange={(e) => updateServiceAllocation(serviceType, 'total', parseInt(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        잔여: {(editingServiceAllocations[serviceType]?.total || 0) - (editingServiceAllocations[serviceType]?.used || 0)}회
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>사용: {usage.used}회</span>
                        <span>잔여: {usage.remaining}회</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="relative h-2 flex">
                          {/* 사용 부분 */}
                          <div
                            className="bg-blue-600 h-2 rounded-l-full transition-all duration-300"
                            style={{ width: `${usage.remaining >= 0 ? (usage.used / (usage.used + usage.remaining)) * 100 : 100}%` }}
                          />
                          {/* 잔여 부분 (음수가 아닐 때만 표시) */}
                          {usage.remaining > 0 && (
                            <div
                              className="bg-green-500 h-2 rounded-r-full transition-all duration-300"
                              style={{ width: `${(usage.remaining / (usage.used + usage.remaining)) * 100}%` }}
                            />
                          )}
                        </div>
                      </div>
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>사용 {usage.remaining >= 0 ? ((usage.used / (usage.used + usage.remaining)) * 100).toFixed(0) : '100'}%</span>
                        <span>잔여 {usage.remaining >= 0 ? ((usage.remaining / (usage.used + usage.remaining)) * 100).toFixed(0) : '0'}%</span>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
        </div>
      ))}
    </div>
  );
}
