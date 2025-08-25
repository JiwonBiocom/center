import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Calendar, FileText, Clock, CheckCircle, AlertCircle, Plus, Edit2, Trash2 } from 'lucide-react'
import { api } from '../../../lib/api'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'

interface CounselingRecord {
  history_id: number
  customer_id: number
  consultation_date: string
  consultation_type: string
  result?: string
  notes?: string
  next_action?: string
  created_by?: number
  created_at?: string
}

interface CounselingTabProps {
  customerId: number
}

export default function CounselingTab({ customerId }: CounselingTabProps) {
  const queryClient = useQueryClient()
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingRecord, setEditingRecord] = useState<CounselingRecord | null>(null)

  // 상담 내역 조회
  const { data: counselingRecords, isLoading, error } = useQuery({
    queryKey: ['counseling', customerId],
    queryFn: async () => {
      const response = await api.get(`/customers/${customerId}/counseling`)
      return response.data as CounselingRecord[]
    }
  })

  // 상담 유형별 아이콘 반환
  const getTypeIcon = (type: string) => {
    switch (type) {
      case '전화상담':
        return <Clock className="h-4 w-4" />
      case '방문상담':
        return <Calendar className="h-4 w-4" />
      case '온라인상담':
        return <FileText className="h-4 w-4" />
      default:
        return <AlertCircle className="h-4 w-4" />
    }
  }

  // 상담 유형별 색상 반환
  const getTypeColor = (type: string) => {
    switch (type) {
      case '전화상담':
        return 'bg-blue-100 text-blue-800'
      case '방문상담':
        return 'bg-green-100 text-green-800'
      case '온라인상담':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return (
      <div className="p-6 flex justify-center items-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">상담 내역을 불러오는데 실패했습니다.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">상담 내역</h3>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          상담 추가
        </button>
      </div>

      {!counselingRecords || counselingRecords.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">등록된 상담 내역이 없습니다.</p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            첫 상담 내역 추가하기
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {counselingRecords.map((record) => (
            <div
              key={record.history_id}
              className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-3">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${getTypeColor(record.consultation_type)}`}>
                    {getTypeIcon(record.consultation_type)}
                    {record.consultation_type}
                  </span>
                  <span className="text-sm text-gray-600">
                    {format(new Date(record.consultation_date), 'yyyy년 MM월 dd일', { locale: ko })}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setEditingRecord(record)}
                    className="p-1 text-gray-600 hover:text-blue-600 transition-colors"
                  >
                    <Edit2 className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {/* 삭제 핸들러 */}}
                    className="p-1 text-gray-600 hover:text-red-600 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {record.result && (
                <div className="mb-2">
                  <span className="text-sm font-medium text-gray-700">상담 결과: </span>
                  <span className="text-sm text-gray-600">{record.result}</span>
                </div>
              )}

              {record.notes && (
                <div className="mb-2">
                  <span className="text-sm font-medium text-gray-700">상담 내용: </span>
                  <p className="text-sm text-gray-600 mt-1">{record.notes}</p>
                </div>
              )}

              {record.next_action && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <span className="text-sm font-medium text-gray-700">다음 조치: </span>
                  <span className="text-sm text-blue-600">{record.next_action}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
