import { useState, useEffect } from 'react'
import { api } from '../../lib/api'
import { Plus, Edit2, Trash2, Calendar } from 'lucide-react'

interface ServiceType {
  service_type_id: number
  service_name: string
  description: string | null
}

export default function ServiceTypeManagement() {
  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingService, setEditingService] = useState<ServiceType | null>(null)

  useEffect(() => {
    fetchServiceTypes()
  }, [])

  const fetchServiceTypes = async () => {
    try {
      const response = await api.get('/api/v1/settings/service-types')
      setServiceTypes(response.data)
    } catch (error) {
      console.error('Failed to fetch service types:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (serviceData: any) => {
    try {
      if (editingService) {
        await api.put(`/api/v1/settings/service-types/${editingService.service_type_id}`, serviceData)
      } else {
        await api.post('/api/v1/settings/service-types', serviceData)
      }
      fetchServiceTypes()
      setShowModal(false)
      setEditingService(null)
    } catch (error: any) {
      alert(error.response?.data?.detail || '저장에 실패했습니다.')
    }
  }

  const handleDelete = async (serviceTypeId: number) => {
    if (!confirm('정말 삭제하시겠습니까? 이 서비스를 사용한 기록이 있다면 삭제할 수 없습니다.')) {
      return
    }

    try {
      await api.delete(`/api/v1/settings/service-types/${serviceTypeId}`)
      fetchServiceTypes()
    } catch (error: any) {
      alert(error.response?.data?.detail || '삭제에 실패했습니다.')
    }
  }

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">서비스 타입 관리</h2>
        <button
          onClick={() => {
            setEditingService(null)
            setShowModal(true)
          }}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          서비스 타입 추가
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                서비스명
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                설명
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                작업
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {serviceTypes.map((service) => (
              <tr key={service.service_type_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">{service.service_name}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm text-gray-500">
                    {service.description || '-'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => {
                      setEditingService(service)
                      setShowModal(true)
                    }}
                    className="text-indigo-600 hover:text-indigo-900 mr-3"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(service.service_type_id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {serviceTypes.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            등록된 서비스 타입이 없습니다.
          </div>
        )}
      </div>

      {/* 서비스 타입 추가/수정 모달 */}
      {showModal && (
        <ServiceTypeModal
          service={editingService}
          onClose={() => {
            setShowModal(false)
            setEditingService(null)
          }}
          onSave={handleSave}
        />
      )}
    </div>
  )
}

// 서비스 타입 추가/수정 모달
function ServiceTypeModal({ service, onClose, onSave }: {
  service: ServiceType | null
  onClose: () => void
  onSave: (data: any) => void
}) {
  const [formData, setFormData] = useState({
    service_name: service?.service_name || '',
    description: service?.description || ''
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave(formData)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {service ? '서비스 타입 수정' : '새 서비스 타입 추가'}
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              서비스명 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.service_name}
              onChange={(e) => setFormData({ ...formData, service_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
              maxLength={20}
            />
            <p className="mt-1 text-sm text-gray-500">최대 20자</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              설명
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={3}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              취소
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              {service ? '수정' : '추가'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}