import { useState } from 'react'
import { User, Phone, Mail, Calendar, MapPin, Briefcase, AlertCircle } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../../lib/api'

interface CustomerDetail {
  customer: {
    customer_id: number
    name: string
    phone: string | null
    email: string | null
    first_visit_date: string | null
    region: string | null
    referral_source: string | null
    health_concerns: string | null
    notes: string | null
    assigned_staff: string | null
    birth_year: number | null
    gender: string | null
    address: string | null
    emergency_contact: string | null
    occupation: string | null
    membership_level: string
    customer_status: string
    preferred_time_slots: string[] | null
    health_goals: string | null
    last_visit_date: string | null
    total_visits: number
    average_visit_interval: number | null
    total_revenue: number
    average_satisfaction: number | null
    risk_level: string
    created_at: string
    updated_at: string
  }
}

interface BasicInfoTabProps {
  customerDetail: CustomerDetail
  customerId: number
}

export default function BasicInfoTab({ customerDetail, customerId }: BasicInfoTabProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedData, setEditedData] = useState(customerDetail.customer)
  const queryClient = useQueryClient()

  const updateMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.put(`/customers/${customerId}/detail`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customer-detail', customerId] })
      setIsEditing(false)
      alert('고객 정보가 업데이트되었습니다.')
    },
    onError: (error) => {
      console.error('Update error:', error)
      alert('업데이트 중 오류가 발생했습니다.')
    }
  })

  const handleSave = () => {
    updateMutation.mutate(editedData)
  }

  const handleCancel = () => {
    setEditedData(customerDetail.customer)
    setIsEditing(false)
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('ko-KR')
  }

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'dormant': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getRiskBadgeClass = (risk: string) => {
    switch (risk) {
      case 'stable': return 'bg-green-100 text-green-800'
      case 'warning': return 'bg-yellow-100 text-yellow-800'
      case 'danger': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const { customer } = customerDetail

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">기본 정보</h3>
        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
          >
            수정
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleSave}
              disabled={updateMutation.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors disabled:opacity-50"
            >
              {updateMutation.isPending ? '저장 중...' : '저장'}
            </button>
          </div>
        )}
      </div>

      {/* 상태 배지 */}
      <div className="flex gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">회원 상태:</span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadgeClass(customer.customer_status)}`}>
            {customer.customer_status === 'active' ? '활성' :
             customer.customer_status === 'inactive' ? '비활성' : '휴면'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">회원 등급:</span>
          <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
            {customer.membership_level === 'basic' ? '일반' :
             customer.membership_level === 'premium' ? '프리미엄' : 'VIP'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">위험도:</span>
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskBadgeClass(customer.risk_level)}`}>
            {customer.risk_level === 'stable' ? '안정' :
             customer.risk_level === 'warning' ? '주의' : '위험'}
          </span>
        </div>
      </div>

      {/* 기본 정보 그리드 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 개인 정보 */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700 border-b pb-2">개인 정보</h4>

          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <User className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">고객번호</label>
                <p className="text-sm font-medium">{customer.customer_id}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <User className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">이름</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedData.name}
                    onChange={(e) => setEditedData({ ...editedData, name: e.target.value })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  />
                ) : (
                  <p className="text-sm font-medium">{customer.name}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Phone className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">연락처</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedData.phone || ''}
                    onChange={(e) => setEditedData({ ...editedData, phone: e.target.value })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  />
                ) : (
                  <p className="text-sm">{customer.phone || '-'}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Mail className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">이메일</label>
                {isEditing ? (
                  <input
                    type="email"
                    value={editedData.email || ''}
                    onChange={(e) => setEditedData({ ...editedData, email: e.target.value })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  />
                ) : (
                  <p className="text-sm">{customer.email || '-'}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Calendar className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">생년</label>
                {isEditing ? (
                  <input
                    type="number"
                    value={editedData.birth_year || ''}
                    onChange={(e) => setEditedData({ ...editedData, birth_year: parseInt(e.target.value) || null })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  />
                ) : (
                  <p className="text-sm">{customer.birth_year || '-'}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <User className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">성별</label>
                {isEditing ? (
                  <select
                    value={editedData.gender || ''}
                    onChange={(e) => setEditedData({ ...editedData, gender: e.target.value })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  >
                    <option value="">선택</option>
                    <option value="male">남성</option>
                    <option value="female">여성</option>
                  </select>
                ) : (
                  <p className="text-sm">
                    {customer.gender === 'male' ? '남성' :
                     customer.gender === 'female' ? '여성' : '-'}
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <MapPin className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">주소</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedData.address || ''}
                    onChange={(e) => setEditedData({ ...editedData, address: e.target.value })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  />
                ) : (
                  <p className="text-sm">{customer.address || '-'}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Briefcase className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">직업</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedData.occupation || ''}
                    onChange={(e) => setEditedData({ ...editedData, occupation: e.target.value })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  />
                ) : (
                  <p className="text-sm">{customer.occupation || '-'}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <AlertCircle className="w-4 h-4 text-gray-400" />
              <div className="flex-1">
                <label className="text-xs text-gray-500">비상연락처</label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editedData.emergency_contact || ''}
                    onChange={(e) => setEditedData({ ...editedData, emergency_contact: e.target.value })}
                    className="w-full px-2 py-1 text-sm border rounded"
                  />
                ) : (
                  <p className="text-sm">{customer.emergency_contact || '-'}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 이용 정보 */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700 border-b pb-2">이용 정보</h4>

          <div className="space-y-3">
            <div>
              <label className="text-xs text-gray-500">첫 방문일</label>
              <p className="text-sm">{formatDate(customer.first_visit_date)}</p>
            </div>

            <div>
              <label className="text-xs text-gray-500">마지막 방문일</label>
              <p className="text-sm">{formatDate(customer.last_visit_date)}</p>
            </div>

            <div>
              <label className="text-xs text-gray-500">총 방문 횟수</label>
              <p className="text-sm font-medium">{customer.total_visits}회</p>
            </div>

            <div>
              <label className="text-xs text-gray-500">평균 방문 주기</label>
              <p className="text-sm">{customer.average_visit_interval ? `${customer.average_visit_interval}일` : '-'}</p>
            </div>

            <div>
              <label className="text-xs text-gray-500">총 이용 금액</label>
              <p className="text-sm font-medium">{customer.total_revenue.toLocaleString()}원</p>
            </div>

            <div>
              <label className="text-xs text-gray-500">담당자</label>
              <p className="text-sm">{customer.assigned_staff || '-'}</p>
            </div>

            <div>
              <label className="text-xs text-gray-500">유입 경로</label>
              <p className="text-sm">{customer.referral_source || '-'}</p>
            </div>

            <div>
              <label className="text-xs text-gray-500">거주 지역</label>
              <p className="text-sm">{customer.region || '-'}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 건강 정보 */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-700 border-b pb-2">건강 정보</h4>

        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-500">건강 관심사</label>
            {isEditing ? (
              <textarea
                value={editedData.health_concerns || ''}
                onChange={(e) => setEditedData({ ...editedData, health_concerns: e.target.value })}
                className="w-full px-2 py-1 text-sm border rounded"
                rows={2}
              />
            ) : (
              <p className="text-sm">{customer.health_concerns || '-'}</p>
            )}
          </div>

          <div>
            <label className="text-xs text-gray-500">건강 목표</label>
            {isEditing ? (
              <textarea
                value={editedData.health_goals || ''}
                onChange={(e) => setEditedData({ ...editedData, health_goals: e.target.value })}
                className="w-full px-2 py-1 text-sm border rounded"
                rows={2}
              />
            ) : (
              <p className="text-sm">{customer.health_goals || '-'}</p>
            )}
          </div>

          <div>
            <label className="text-xs text-gray-500">비고</label>
            {isEditing ? (
              <textarea
                value={editedData.notes || ''}
                onChange={(e) => setEditedData({ ...editedData, notes: e.target.value })}
                className="w-full px-2 py-1 text-sm border rounded"
                rows={3}
              />
            ) : (
              <p className="text-sm">{customer.notes || '-'}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
