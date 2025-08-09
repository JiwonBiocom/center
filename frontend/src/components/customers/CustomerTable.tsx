import React, { useState } from 'react';
import { Edit2, Trash2, Eye, ChevronDown, ChevronUp, Phone, Mail, MapPin, Users, MessageSquare, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { format } from 'date-fns';
import MembershipBadge from './MembershipBadge';
// import { formatDate } from '../../lib/utils';

interface Customer {
  customer_id: number;
  name: string;
  phone: string;
  email?: string;
  birth_year?: number;
  gender?: string;
  first_visit_date: string;
  region: string;
  referral_source: string;
  health_concerns?: string;
  notes?: string;
  assigned_staff?: string;
  membership_level?: string;
  customer_status?: string;
  risk_level?: string;
  last_visit_date?: string;
  visit_count?: number;
  total_spent?: number;
}

interface CustomerTableProps {
  customers: Customer[];
  onEdit: (customer: Customer) => void;
  onDelete: (customerId: number) => void;
  onView?: (customer: Customer) => void;
  onSendSMS?: (customer: Customer) => void;
  sortBy?: string | null;
  sortOrder?: 'asc' | 'desc';
  onSort?: (field: string) => void;
}

export default function CustomerTable({ customers, onEdit, onDelete, onView, onSendSMS, sortBy, sortOrder, onSort }: CustomerTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  const toggleRow = (customerId: number) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(customerId)) {
      newExpanded.delete(customerId);
    } else {
      newExpanded.add(customerId);
    }
    setExpandedRows(newExpanded);
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortBy === field) {
      return sortOrder === 'asc' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />;
    }
    return <ArrowUpDown className="w-4 h-4 text-gray-400" />;
  };


  return (
    <div className="mt-8 flex flex-col">
      <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th className="w-8 px-3 py-3.5"></th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    <button
                      onClick={() => onSort && onSort('name')}
                      className="flex items-center gap-1 hover:text-gray-700"
                    >
                      고객정보
                      <SortIcon field="name" />
                    </button>
                  </th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    연락처
                  </th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    <button
                      onClick={() => onSort && onSort('membership_level')}
                      className="flex items-center gap-1 hover:text-gray-700"
                    >
                      회원 등급 및 상태
                      <SortIcon field="membership_level" />
                    </button>
                  </th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    <button
                      onClick={() => onSort && onSort('last_visit_date')}
                      className="flex items-center gap-1 hover:text-gray-700"
                    >
                      방문정보
                      <SortIcon field="last_visit_date" />
                    </button>
                  </th>
                  <th className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    <button
                      onClick={() => onSort && onSort('assigned_staff')}
                      className="flex items-center gap-1 hover:text-gray-700"
                    >
                      담당자
                      <SortIcon field="assigned_staff" />
                    </button>
                  </th>
                  <th className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {customers.map((customer) => {
                  const isExpanded = expandedRows.has(customer.customer_id);
                  return (
                    <React.Fragment key={customer.customer_id}>
                      <tr className="hover:bg-gray-50">
                        <td className="px-3 py-4">
                          <button
                            onClick={() => toggleRow(customer.customer_id)}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </button>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <div>
                            <div className="font-medium text-gray-900">{customer.name}({customer.customer_id})</div>
                            {customer.birth_year && (
                              <div className="text-gray-500">
                                {new Date().getFullYear() - customer.birth_year}세
                                {customer.gender && ` · ${customer.gender}`}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <div className="space-y-1">
                            {customer.phone && (
                              <div className="flex items-center gap-1 text-gray-500">
                                <Phone className="w-3 h-3" />
                                {customer.phone}
                              </div>
                            )}
                            {customer.email && (
                              <div className="flex items-center gap-1 text-gray-500">
                                <Mail className="w-3 h-3" />
                                {customer.email}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm">
                          <MembershipBadge
                            level={customer.membership_level || 'bronze'}
                            status={customer.customer_status || 'active'}
                            showTooltip={true}
                          />
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          <div className="space-y-1">
                            <div>첫방문: {customer.first_visit_date ? format(new Date(customer.first_visit_date), 'yyyy.MM.dd') : '-'}</div>
                            {customer.last_visit_date && (
                              <div>최근: {format(new Date(customer.last_visit_date), 'yyyy.MM.dd')}</div>
                            )}
                            {customer.visit_count && (
                              <div className="font-medium text-gray-700">{customer.visit_count}회 방문</div>
                            )}
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                          {customer.assigned_staff || '-'}
                        </td>
                        <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                          <div className="flex items-center justify-end gap-2">
                            {onView && (
                              <button
                                onClick={() => onView(customer)}
                                className="text-gray-600 hover:text-gray-900"
                                title="상세보기"
                              >
                                <Eye className="w-4 h-4" />
                              </button>
                            )}
                            {onSendSMS && customer.phone && (
                              <button
                                onClick={() => onSendSMS(customer)}
                                className="text-green-600 hover:text-green-900"
                                title="SMS 발송"
                              >
                                <MessageSquare className="w-4 h-4" />
                              </button>
                            )}
                            <button
                              onClick={() => onEdit(customer)}
                              className="text-indigo-600 hover:text-indigo-900"
                              title="수정"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => onDelete(customer.customer_id)}
                              className="text-red-600 hover:text-red-900"
                              title="삭제"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>

                      {/* 확장 행 */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={7} className="bg-gray-50 px-6 py-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                              <div>
                                <h4 className="font-medium text-gray-900 mb-2">지역 및 유입</h4>
                                <div className="space-y-1 text-gray-600">
                                  <div className="flex items-center gap-2">
                                    <MapPin className="w-4 h-4" />
                                    {customer.region || '미지정'}
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Users className="w-4 h-4" />
                                    {customer.referral_source || '미지정'}
                                  </div>
                                </div>
                              </div>

                              {customer.total_spent !== undefined && (
                                <div>
                                  <h4 className="font-medium text-gray-900 mb-2">구매 정보</h4>
                                  <div className="text-gray-600">
                                    총 구매액: {customer.total_spent.toLocaleString()}원
                                  </div>
                                </div>
                              )}

                              {(customer.health_concerns || customer.notes) && (
                                <div>
                                  <h4 className="font-medium text-gray-900 mb-2">특이사항</h4>
                                  <div className="text-gray-600 space-y-1">
                                    {customer.health_concerns && (
                                      <div>건강: {customer.health_concerns}</div>
                                    )}
                                    {customer.notes && (
                                      <div>메모: {customer.notes}</div>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>

            {customers.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-500">고객이 없습니다.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
