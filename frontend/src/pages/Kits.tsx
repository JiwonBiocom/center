import { useState, useEffect } from 'react';
import { Plus, Info, Download, Upload } from 'lucide-react';
import { api } from '../lib/api';
import KitModal from '../components/KitModal';
import KitStats from '../components/kits/KitStats';
import KitFilters from '../components/kits/KitFilters';
import KitTable from '../components/kits/KitTable';

interface KitType {
  kit_type_id: number;
  name: string;
  code: string;
  description: string;
  price: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Customer {
  customer_id: number;
  name: string;
  phone: string;
}

interface Kit {
  kit_id: number;
  customer_id: number;
  kit_type: string;
  kit_type_id: number;
  serial_number: string | null;
  received_date: string | null;
  result_received_date: string | null;
  result_delivered_date: string | null;
  created_at: string;
  customer?: Customer;
  kit_type_ref?: KitType;
}

export default function Kits() {
  const [kits, setKits] = useState<Kit[]>([]);
  const [kitTypes, setKitTypes] = useState<KitType[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingKit, setEditingKit] = useState<Kit | null>(null);
  const [stats, setStats] = useState({
    total_kits: 0,
    pending_kits: 0,
    in_progress_kits: 0,
    completed_kits: 0
  });

  // 페이지네이션
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    const loadData = async () => {
      try {
        await Promise.all([
          fetchKits(),
          fetchKitTypes(),
          fetchStats()
        ]);
      } catch (error) {
        console.error('Failed to load kit data:', error);
      }
    };
    loadData();
  }, [currentPage, statusFilter]);

  const fetchKits = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: ((currentPage - 1) * pageSize).toString(),
        limit: pageSize.toString()
      });
      
      if (statusFilter !== 'all') {
        params.append('status', statusFilter);
      }

      const response = await api.get(`/api/v1/kits/?${params}`);
      if (response.data) {
        setKits(response.data.kits || []);
        setTotalPages(Math.ceil((response.data.total || 0) / pageSize));
      }
    } catch (error: any) {
      console.error('Failed to fetch kits:', error.response?.data || error.message);
      setKits([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchKitTypes = async () => {
    try {
      const response = await api.get('/api/v1/kits/kit-types');
      if (response.data && response.data.kit_types) {
        setKitTypes(response.data.kit_types.filter((kt: KitType) => kt.is_active));
      }
    } catch (error: any) {
      console.error('Failed to fetch kit types:', error.response?.data || error.message);
      setKitTypes([]);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/v1/kits/stats/summary');
      if (response.data) {
        setStats(response.data);
      }
    } catch (error: any) {
      console.error('Failed to fetch stats:', error.response?.data || error.message);
    }
  };

  const handleCreateOrUpdate = async (data: any) => {
    try {
      let response;
      if (editingKit) {
        response = await api.patch(`/api/v1/kits/${editingKit.kit_id}`, data);
        console.log('PATCH response:', response.data);
        
        // 응답 데이터로 로컬 상태 직접 업데이트하여 불필요한 API 호출 방지
        if (response.data && response.data.customer) {
          setKits(prevKits => 
            prevKits.map(kit => 
              kit.kit_id === editingKit.kit_id 
                ? { ...response.data, customer: response.data.customer }
                : kit
            )
          );
          
          // 통계만 새로고침 (키트 목록은 로컬 업데이트)
          fetchStats();
        } else {
          // customer 정보가 없는 경우에만 전체 새로고침
          console.warn('PATCH response missing customer info, refetching all kits');
          fetchKits();
          fetchStats();
        }
      } else {
        response = await api.post('/api/v1/kits/', data);
        // 새 키트 생성 시에만 전체 새로고침
        fetchKits();
        fetchStats();
      }
      
      setIsModalOpen(false);
      setEditingKit(null);
    } catch (error) {
      console.error('Failed to save kit:', error);
    }
  };

  const handleEdit = (kit: Kit) => {
    setEditingKit(kit);
    setIsModalOpen(true);
  };

  const handleDelete = async (kit: Kit) => {
    if (window.confirm('정말로 이 검사키트를 삭제하시겠습니까?')) {
      try {
        await api.delete(`/api/v1/kits/${kit.kit_id}`);
        fetchKits();
        fetchStats();
      } catch (error) {
        console.error('Failed to delete kit:', error);
      }
    }
  };

  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value);
    setCurrentPage(1);
  };

  const filteredKits = kits.filter(kit => {
    const customer = kit.customer;
    const searchLower = searchTerm.toLowerCase();
    return (
      customer?.name.toLowerCase().includes(searchLower) ||
      customer?.phone.includes(searchTerm) ||
      kit.serial_number?.toLowerCase().includes(searchLower) ||
      kit.kit_type.toLowerCase().includes(searchLower)
    );
  });

  const handleExportExcel = async () => {
    try {
      const response = await api.get('/api/v1/kits/export/excel', {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `검사키트목록_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export excel:', error);
      alert('엑셀 다운로드에 실패했습니다.');
    }
  };

  const handleImportExcel = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/api/v1/kits/import/excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      alert(response.data.message);
      fetchKits();
      fetchStats();
    } catch (error: any) {
      console.error('Failed to import excel:', error);
      alert(error.response?.data?.detail || '엑셀 업로드에 실패했습니다.');
    } finally {
      // 파일 입력 초기화
      event.target.value = '';
    }
  };

  return (
    <div>
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">검사키트 관리</h1>
          <p className="mt-2 text-sm text-gray-700">
            고객의 검사키트 주문 및 진행 상태를 관리합니다.
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none flex space-x-3">
          <button
            type="button"
            onClick={handleExportExcel}
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <Download className="h-4 w-4 mr-2" />
            엑셀 다운로드
          </button>
          
          <label className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 cursor-pointer">
            <Upload className="h-4 w-4 mr-2" />
            엑셀 업로드
            <input
              type="file"
              accept=".xlsx,.xls"
              onChange={handleImportExcel}
              className="hidden"
            />
          </label>
          
          <button
            type="button"
            onClick={() => {
              setEditingKit(null);
              setIsModalOpen(true);
            }}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <Plus className="h-4 w-4 mr-2" />
            새 검사키트
          </button>
        </div>
      </div>

      {/* 안내 메시지 */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Info className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-800">
              <span className="font-medium">안내:</span> 현재는 검사키트 정보를 매뉴얼로 기입해주세요. 추후 본사 DB와 연동 예정입니다.
            </p>
          </div>
        </div>
      </div>

      {/* 통계 카드 */}
      <KitStats stats={stats} />

      {/* 검색 및 필터 */}
      <KitFilters 
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        statusFilter={statusFilter}
        onStatusChange={handleStatusFilterChange}
      />

      {/* 테이블 */}
      <KitTable 
        kits={filteredKits}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {/* 페이지네이션 */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-700">
              <span className="font-medium">{(currentPage - 1) * pageSize + 1}</span>
              {' - '}
              <span className="font-medium">
                {Math.min(currentPage * pageSize, stats.total_kits)}
              </span>
              {' / '}
              <span className="font-medium">{stats.total_kits}</span>건
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              이전
            </button>
            <button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              다음
            </button>
          </div>
        </div>
      )}

      {/* 모달 */}
      {isModalOpen && (
        <KitModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setEditingKit(null);
          }}
          onSubmit={handleCreateOrUpdate}
          kit={editingKit}
          kitTypes={kitTypes}
        />
      )}
    </div>
  );
}