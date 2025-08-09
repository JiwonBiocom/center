import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { api } from '../lib/api'

interface ServiceModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  selectedDate?: string
}

interface Customer {
  customer_id: number
  name: string
  phone: string
}

interface ServiceType {
  service_type_id: number
  service_name: string
}

interface Package {
  purchase_id: number
  package_id: number
  remaining_sessions: number
  expiry_date: string
}

export default function ServiceModal({ isOpen, onClose, onSuccess, selectedDate }: ServiceModalProps) {
  const [formData, setFormData] = useState({
    customer_id: 0,
    service_date: selectedDate || new Date().toISOString().split('T')[0],
    service_type_id: 0,
    package_id: null as number | null,
    session_details: '',
    session_number: null as number | null,
    created_by: '직원'
  })
  
  const [customers, setCustomers] = useState<Customer[]>([])
  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([])
  const [packages, setPackages] = useState<Package[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<any>({})

  useEffect(() => {
    if (isOpen) {
      fetchCustomers()
      fetchServiceTypes()
      setFormData(prev => ({
        ...prev,
        service_date: selectedDate || new Date().toISOString().split('T')[0]
      }))
    }
  }, [isOpen, selectedDate])

  useEffect(() => {
    if (formData.customer_id) {
      fetchCustomerPackages()
    }
  }, [formData.customer_id])

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/api/v1/customers', {
        params: searchTerm ? { search: searchTerm } : {}
      })
      setCustomers(response.data)
    } catch (error) {
      console.error('Failed to fetch customers:', error)
    }
  }

  const fetchServiceTypes = async () => {
    try {
      const response = await api.get('/api/v1/services/types')
      setServiceTypes(response.data)
    } catch (error) {
      console.error('Failed to fetch service types:', error)
    }
  }

  const fetchCustomerPackages = async () => {
    try {
      const response = await api.get(`/api/v1/services/customer/${formData.customer_id}/packages`)
      setPackages(response.data)
    } catch (error) {
      console.error('Failed to fetch packages:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setErrors({})

    try {
      await api.post('/api/v1/services/usage', formData)
      onSuccess()
    } catch (error: any) {
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          setErrors({ general: error.response.data.detail })
        } else {
          setErrors(error.response.data.detail)
        }
      }
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />
        
        <div className="relative bg-white rounded-lg max-w-2xl w-full p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              서비스 이용 등록
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {errors.general && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-md text-sm">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                고객 선택 *
              </label>
              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="고객 이름 또는 전화번호 검색..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value)
                    fetchCustomers()
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <select
                  required
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  size={5}
                >
                  <option value="">고객을 선택하세요</option>
                  {customers.map((customer) => (
                    <option key={customer.customer_id} value={customer.customer_id}>
                      {customer.name} ({customer.phone || '전화번호 없음'})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  서비스 날짜 *
                </label>
                <input
                  type="date"
                  required
                  value={formData.service_date}
                  onChange={(e) => setFormData({ ...formData, service_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  서비스 종류 *
                </label>
                <select
                  required
                  value={formData.service_type_id}
                  onChange={(e) => setFormData({ ...formData, service_type_id: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">선택하세요</option>
                  {serviceTypes.map((type) => (
                    <option key={type.service_type_id} value={type.service_type_id}>
                      {type.service_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  패키지 선택
                </label>
                <select
                  value={formData.package_id || ''}
                  onChange={(e) => setFormData({ ...formData, package_id: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  disabled={!formData.customer_id}
                >
                  <option value="">패키지 미사용</option>
                  {packages.map((pkg) => (
                    <option key={pkg.purchase_id} value={pkg.purchase_id}>
                      패키지 #{pkg.package_id} (잔여: {pkg.remaining_sessions}회)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  회차
                </label>
                <input
                  type="number"
                  value={formData.session_number || ''}
                  onChange={(e) => setFormData({ ...formData, session_number: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                서비스 상세 내용
              </label>
              <textarea
                value={formData.session_details}
                onChange={(e) => setFormData({ ...formData, session_details: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="서비스 진행 내용을 입력하세요..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                담당자
              </label>
              <input
                type="text"
                value={formData.created_by}
                onChange={(e) => setFormData({ ...formData, created_by: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                취소
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? '등록 중...' : '등록'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}