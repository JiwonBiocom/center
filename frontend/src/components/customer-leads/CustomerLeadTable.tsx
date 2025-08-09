import { ChevronLeft, ChevronRight, Edit, Trash2, Phone, Calendar, CheckCircle, Eye, MessageSquare } from 'lucide-react';
import IndividualStaffAssignment from './IndividualStaffAssignment';

interface CustomerLead {
  lead_id: number;
  name: string;
  phone?: string;
  lead_date: string;
  age?: number;
  region?: string;
  lead_channel?: string;
  db_channel?: string;
  status: string;
  phone_consult_date?: string;
  visit_consult_date?: string;
  registration_date?: string;
  assigned_staff_id?: number;
  assigned_staff_name?: string;
  is_reregistration_target: boolean;
  price_informed: boolean;
  visit_cancelled: boolean;
  created_at: string;
}

interface CustomerLeadTableProps {
  leads: CustomerLead[];
  loading: boolean;
  selectedLeads: number[];
  onSelectLeads: (ids: number[]) => void;
  onEdit: (lead: CustomerLead) => void;
  onDelete: (id: number) => void;
  onView: (lead: CustomerLead) => void;
  onSendSMS?: (lead: CustomerLead) => void;
  onRefresh?: () => void;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const statusLabels: Record<string, string> = {
  'new': '신규',
  'db_entered': 'DB입력',
  'phone_consulted': '전화상담',
  'visit_consulted': '방문상담',
  'converted': '등록완료'
};

const statusColors: Record<string, string> = {
  'new': 'bg-gray-100 text-gray-800',
  'db_entered': 'bg-blue-100 text-blue-800',
  'phone_consulted': 'bg-yellow-100 text-yellow-800',
  'visit_consulted': 'bg-purple-100 text-purple-800',
  'converted': 'bg-green-100 text-green-800'
};

export default function CustomerLeadTable({
  leads,
  loading,
  selectedLeads,
  onSelectLeads,
  onEdit,
  onDelete,
  onView,
  onSendSMS,
  onRefresh,
  currentPage,
  totalPages,
  onPageChange
}: CustomerLeadTableProps) {
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectLeads(leads.map(lead => lead.lead_id));
    } else {
      onSelectLeads([]);
    }
  };

  const handleSelectOne = (leadId: number, checked: boolean) => {
    if (checked) {
      onSelectLeads([...selectedLeads, leadId]);
    } else {
      onSelectLeads(selectedLeads.filter(id => id !== leadId));
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3">
                <input
                  type="checkbox"
                  checked={selectedLeads.length === leads.length && leads.length > 0}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                이름
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                연락처
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                유입정보
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                상태
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                상담일정
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                담당자
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {leads.map((lead) => (
              <tr key={lead.lead_id} className="hover:bg-gray-50">
                <td className="px-4 py-4">
                  <input
                    type="checkbox"
                    checked={selectedLeads.includes(lead.lead_id)}
                    onChange={(e) => handleSelectOne(lead.lead_id, e.target.checked)}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                    {lead.age && (
                      <div className="text-sm text-gray-500">{lead.age}세</div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{lead.phone || '-'}</div>
                  {lead.region && (
                    <div className="text-sm text-gray-500">{lead.region}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{lead.lead_channel || '-'}</div>
                  {lead.db_channel && (
                    <div className="text-sm text-gray-500">DB: {lead.db_channel}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    statusColors[lead.status] || 'bg-gray-100 text-gray-800'
                  }`}>
                    {statusLabels[lead.status] || lead.status}
                  </span>
                  {lead.is_reregistration_target && (
                    <span className="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">
                      재등록 대상
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-3 text-sm">
                    {lead.phone_consult_date && (
                      <div className="flex items-center gap-1 text-gray-600">
                        <Phone className="w-4 h-4" />
                        {new Date(lead.phone_consult_date).toLocaleDateString()}
                      </div>
                    )}
                    {lead.visit_consult_date && (
                      <div className="flex items-center gap-1 text-gray-600">
                        <Calendar className="w-4 h-4" />
                        {new Date(lead.visit_consult_date).toLocaleDateString()}
                      </div>
                    )}
                    {lead.registration_date && (
                      <div className="flex items-center gap-1 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        {new Date(lead.registration_date).toLocaleDateString()}
                      </div>
                    )}
                    {!lead.phone_consult_date && !lead.visit_consult_date && !lead.registration_date && (
                      <span className="text-gray-400">-</span>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <IndividualStaffAssignment
                    leadId={lead.lead_id}
                    currentStaffId={lead.assigned_staff_id}
                    currentStaffName={lead.assigned_staff_name}
                    onAssigned={() => onRefresh?.()}
                  />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => onView(lead)}
                    className="text-gray-600 hover:text-gray-900 mr-3"
                    title="상세보기"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  {lead.phone && onSendSMS && (
                    <button
                      onClick={() => onSendSMS(lead)}
                      className="text-green-600 hover:text-green-900 mr-3"
                      title="문자 보내기"
                    >
                      <MessageSquare className="w-4 h-4" />
                    </button>
                  )}
                  <button
                    onClick={() => onEdit(lead)}
                    className="text-indigo-600 hover:text-indigo-900 mr-3"
                    title="수정"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => onDelete(lead.lead_id)}
                    className="text-red-600 hover:text-red-900"
                    title="삭제"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* 페이지네이션 */}
      <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200">
        <div className="text-sm text-gray-700">
          {leads.length > 0 ? `${leads.length}개 표시 중` : '데이터가 없습니다'}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-1 rounded-md bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          
          <span className="text-sm text-gray-700">
            {currentPage} / {totalPages}
          </span>
          
          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-1 rounded-md bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}