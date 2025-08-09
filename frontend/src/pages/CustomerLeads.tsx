import { useState, useEffect, useRef } from 'react';
import { api } from '../lib/api';
import { Plus, Download, Upload, Users, Target, BarChart3, MessageSquare } from 'lucide-react';
import { Link } from 'react-router-dom';
import CustomerLeadModal from '../components/customer-leads/CustomerLeadModal';
import CustomerLeadTable from '../components/customer-leads/CustomerLeadTable';
import CustomerLeadFilters from '../components/customer-leads/CustomerLeadFilters';
import CustomerLeadStats from '../components/customer-leads/CustomerLeadStats';
import KeyMetricsStats from '../components/customer-leads/KeyMetricsStats';
import CustomerLeadDetailModal from '../components/customer-leads/CustomerLeadDetailModal';
import StaffAssignmentModal from '../components/customer-leads/StaffAssignmentModal';
import LeadSMSModal from '../components/customer-leads/LeadSMSModal';
import IndividualLeadSMSModal from '../components/customer-leads/IndividualLeadSMSModal';

// 타입 정의
interface CustomerLead {
  lead_id: number;
  name: string;
  phone?: string;
  lead_date: string;
  age?: number;
  region?: string;
  lead_channel?: string;
  db_channel?: string;
  carrot_id?: string;
  ad_watched?: string;
  price_informed: boolean;
  ab_test_group?: string;

  // 날짜 필드들
  db_entry_date?: string;
  phone_consult_date?: string;
  visit_consult_date?: string;
  registration_date?: string;

  // 추가 필드들
  phone_consult_result?: string;
  remind_date?: string;
  visit_cancelled: boolean;
  visit_cancel_reason?: string;

  // 재등록 관련
  is_reregistration_target: boolean;
  last_service_date?: string;
  reregistration_proposal_date?: string;

  // 구매 정보
  purchased_product?: string;
  no_registration_reason?: string;
  notes?: string;
  revenue?: number;

  // 상태 및 담당자
  status: string;
  assigned_staff_id?: number;
  assigned_staff_name?: string;
  converted_customer_id?: number;
  converted_customer_name?: string;

  created_at: string;
  updated_at?: string;
}

interface CustomerLeadStats {
  total_count: number;
  converted_count: number;
  conversion_rate: number;
  channel_stats: Array<{
    channel: string;
    count: number;
    converted_count: number;
    conversion_rate: number;
  }>;
  status_stats: Array<{
    status: string;
    count: number;
  }>;
  monthly_trend: Array<{
    month: string;
    count: number;
    converted_count: number;
  }>;
}

export default function CustomerLeads() {
  const [leads, setLeads] = useState<CustomerLead[]>([]);
  const [stats, setStats] = useState<CustomerLeadStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string[]>([]);
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [dateRange, setDateRange] = useState<{ from?: string; to?: string }>({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLead, setEditingLead] = useState<CustomerLead | null>(null);
  const [selectedLeads, setSelectedLeads] = useState<number[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [viewingLeadId, setViewingLeadId] = useState<number | null>(null);
  const [isStaffModalOpen, setIsStaffModalOpen] = useState(false);
  const [isSMSModalOpen, setIsSMSModalOpen] = useState(false);
  const [isIndividualSMSModalOpen, setIsIndividualSMSModalOpen] = useState(false);
  const [selectedLeadForSMS, setSelectedLeadForSMS] = useState<CustomerLead | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchLeads();
    fetchStats();
  }, [currentPage, selectedStatus, selectedChannels, selectedRegions, dateRange]);

  const fetchLeads = async () => {
    try {
      const params: any = {
        page: currentPage,
        page_size: 20,
        sort_by: 'created_at',
        sort_order: 'desc'
      };

      if (searchTerm) params.search = searchTerm;
      if (selectedStatus.length > 0) params.status = selectedStatus;
      if (selectedChannels.length > 0) params.lead_channel = selectedChannels;
      if (selectedRegions.length > 0) params.region = selectedRegions;
      if (dateRange.from) params.db_entry_date_from = dateRange.from;
      if (dateRange.to) params.db_entry_date_to = dateRange.to;

      const response = await api.get('/api/v1/customer-leads/', { params });
      setLeads(response.data.items);
      setTotalPages(response.data.total_pages);
      setTotalCount(response.data.total);
    } catch (error) {
      console.error('Failed to fetch leads:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const params: any = {};
      if (dateRange.from) params.db_entry_date_from = dateRange.from;
      if (dateRange.to) params.db_entry_date_to = dateRange.to;

      const response = await api.get('/api/v1/customer-leads/stats', { params });
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    fetchLeads();
  };

  const handleBulkAssignStaff = async (staffId: number) => {
    if (selectedLeads.length === 0) {
      alert('담당자를 지정할 고객을 선택해주세요.');
      return;
    }

    try {
      await api.post('/api/v1/customer-leads/assign-staff', {
        lead_ids: selectedLeads,
        staff_id: staffId
      });
      alert(`${selectedLeads.length}명의 고객에게 담당자가 지정되었습니다.`);
      setSelectedLeads([]);
      fetchLeads();
    } catch (error) {
      console.error('Failed to assign staff:', error);
      alert('담당자 지정에 실패했습니다.');
    }
  };

  const handleExcelExport = async () => {
    try {
      const params: any = { format: 'excel' };
      if (selectedStatus.length > 0) params.status = selectedStatus;
      if (selectedChannels.length > 0) params.lead_channel = selectedChannels;
      if (dateRange.from) params.db_entry_date_from = dateRange.from;
      if (dateRange.to) params.db_entry_date_to = dateRange.to;

      const response = await api.get('/api/v1/customer-leads/export', {
        params,
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `customer_leads_${new Date().toISOString().split('T')[0]}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export:', error);
      alert('엑셀 다운로드에 실패했습니다.');
    }
  };

  const handleExcelImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/api/v1/customer-leads/bulk-import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const result = response.data;
      alert(`업로드 완료! 성공: ${result.success_count}건, 실패: ${result.error_count}건`);

      if (result.errors && result.errors.length > 0) {
        console.error('Import errors:', result.errors);
      }

      fetchLeads();
      fetchStats();
    } catch (error) {
      console.error('Failed to import:', error);
      alert('엑셀 파일 업로드에 실패했습니다.');
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async (leadId: number) => {
    if (!window.confirm('정말로 이 유입고객을 삭제하시겠습니까?')) return;

    try {
      await api.delete(`/api/v1/customer-leads/${leadId}`);
      fetchLeads();
      fetchStats();
    } catch (error) {
      console.error('Failed to delete lead:', error);
      alert('유입고객 삭제에 실패했습니다.');
    }
  };

  const handleIndividualSMS = (lead: CustomerLead) => {
    setSelectedLeadForSMS(lead);
    setIsIndividualSMSModalOpen(true);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">유입고객 관리</h1>
            <p className="text-sm text-gray-600 mt-1">
              총 {totalCount}명의 유입고객이 등록되어 있습니다.
            </p>
          </div>

          <div className="flex gap-2">
            <Link
              to="/leads/analytics"
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <BarChart3 className="w-4 h-4" />
              분석 대시보드
            </Link>

            <Link
              to="/leads/campaigns"
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Target className="w-4 h-4" />
              캠페인 관리
            </Link>

            <button
              onClick={handleExcelExport}
              className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              엑셀 다운로드
            </button>

            <label className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2 cursor-pointer">
              <Upload className="w-4 h-4" />
              엑셀 업로드
              <input
                ref={fileInputRef}
                type="file"
                accept=".xlsx,.xls"
                onChange={handleExcelImport}
                className="hidden"
              />
            </label>

            <button
              onClick={() => {
                setEditingLead(null);
                setIsModalOpen(true);
              }}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              신규 등록
            </button>
          </div>
        </div>

        {/* 핵심 지표 */}
        <KeyMetricsStats />

        {/* 통계 */}
        {stats && <CustomerLeadStats stats={stats} />}

        {/* 필터 */}
        <CustomerLeadFilters
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          onSearch={handleSearch}
          selectedStatus={selectedStatus}
          onStatusChange={setSelectedStatus}
          selectedChannels={selectedChannels}
          onChannelsChange={setSelectedChannels}
          selectedRegions={selectedRegions}
          onRegionsChange={setSelectedRegions}
          dateRange={dateRange}
          onDateRangeChange={setDateRange}
        />

        {/* 테이블 */}
        <CustomerLeadTable
          leads={leads}
          loading={loading}
          selectedLeads={selectedLeads}
          onSelectLeads={setSelectedLeads}
          onEdit={(lead) => {
            setEditingLead(lead);
            setIsModalOpen(true);
          }}
          onDelete={handleDelete}
          onView={(lead) => {
            setViewingLeadId(lead.lead_id);
            setIsDetailModalOpen(true);
          }}
          onSendSMS={handleIndividualSMS}
          onRefresh={fetchLeads}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />

        {/* 일괄 작업 */}
        {selectedLeads.length > 0 && (
          <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 border">
            <p className="text-sm text-gray-600 mb-3">
              {selectedLeads.length}명 선택됨
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setIsStaffModalOpen(true)}
                className="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 text-sm flex items-center gap-1"
              >
                <Users className="w-4 h-4" />
                담당자 지정
              </button>
              <button
                onClick={() => setIsSMSModalOpen(true)}
                className="px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm flex items-center gap-1"
              >
                <MessageSquare className="w-4 h-4" />
                SMS 발송
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 모달 */}
      <CustomerLeadModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingLead(null);
        }}
        onSuccess={() => {
          setIsModalOpen(false);
          setEditingLead(null);
          fetchLeads();
          fetchStats();
        }}
        leadData={editingLead}
      />

      {/* 상세보기 모달 */}
      {viewingLeadId && (
        <CustomerLeadDetailModal
          isOpen={isDetailModalOpen}
          onClose={() => {
            setIsDetailModalOpen(false);
            setViewingLeadId(null);
          }}
          leadId={viewingLeadId}
        />
      )}

      {/* 담당자 지정 모달 */}
      <StaffAssignmentModal
        isOpen={isStaffModalOpen}
        onClose={() => setIsStaffModalOpen(false)}
        onAssign={(staffId) => {
          handleBulkAssignStaff(staffId);
          setIsStaffModalOpen(false);
        }}
        selectedLeadsCount={selectedLeads.length}
      />

      {/* SMS 발송 모달 */}
      <LeadSMSModal
        isOpen={isSMSModalOpen}
        onClose={() => setIsSMSModalOpen(false)}
        selectedLeads={leads.filter(lead => selectedLeads.includes(lead.lead_id))}
        onSuccess={() => {
          setIsSMSModalOpen(false);
          setSelectedLeads([]);
        }}
      />

      {/* 개별 SMS 발송 모달 */}
      {selectedLeadForSMS && (
        <IndividualLeadSMSModal
          isOpen={isIndividualSMSModalOpen}
          onClose={() => {
            setIsIndividualSMSModalOpen(false);
            setSelectedLeadForSMS(null);
          }}
          lead={selectedLeadForSMS}
          onSuccess={() => {
            setIsIndividualSMSModalOpen(false);
            setSelectedLeadForSMS(null);
          }}
        />
      )}
    </div>
  );
}
