import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { formatPhoneNumber, formatDateToISO } from '../lib/utils'
import BaseModal from './common/BaseModal'
import { useReferralSources } from '../hooks/useReferralSources'

interface CustomerModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  customer?: any
}

export default function CustomerModal({ isOpen, onClose, onSuccess, customer }: CustomerModalProps) {
  const { referralSources, loading: referralSourcesLoading } = useReferralSources();

  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    first_visit_date: new Date().toISOString().split('T')[0],
    region: '',
    referral_source: '',
    health_concerns: '',
    notes: '',
    assigned_staff: ''
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<any>({})

  useEffect(() => {
    if (customer) {
      setFormData({
        name: customer.name || '',
        phone: customer.phone || '',
        first_visit_date: customer.first_visit_date || formatDateToISO(new Date()),
        region: customer.region || '',
        referral_source: customer.referral_source || '',
        health_concerns: customer.health_concerns || '',
        notes: customer.notes || '',
        assigned_staff: customer.assigned_staff || ''
      })
    }
  }, [customer])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setErrors({})

    console.log('CustomerModal: Submitting form data:', formData)

    try {
      let response;
      if (customer) {
        // 수정
        console.log(`CustomerModal: Updating customer ${customer.customer_id}`)
        response = await api.put(`/api/v1/customers/${customer.customer_id}`, formData)
      } else {
        // 신규 등록
        console.log('CustomerModal: Creating new customer')
        console.log('CustomerModal: API endpoint:', '/api/v1/customers')
        response = await api.post('/api/v1/customers', formData)
      }

      console.log('CustomerModal: API response:', response.data)

      onSuccess()
      onClose()

      // 폼 데이터 초기화
      setFormData({
        name: '',
        phone: '',
        first_visit_date: formatDateToISO(new Date()),
        region: '',
        referral_source: '',
        health_concerns: '',
        notes: '',
        assigned_staff: ''
      })
    } catch (error: any) {
      console.error('CustomerModal: Error submitting form:', error)
      console.error('CustomerModal: Error response:', error.response)

      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          setErrors({ general: error.response.data.detail })
        } else if (Array.isArray(error.response.data.detail)) {
          // FastAPI validation errors
          const errorMessages = error.response.data.detail.map((err: any) =>
            `${err.loc.join('.')}: ${err.msg}`
          ).join(', ')
          setErrors({ general: errorMessages })
        } else {
          setErrors(error.response.data.detail)
        }
      } else if (error.message) {
        setErrors({ general: error.message })
      } else {
        setErrors({ general: '고객 정보 저장 중 오류가 발생했습니다.' })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      title={customer ? '고객 정보 수정' : '신규 고객 등록'}
      onSubmit={handleSubmit}
      loading={loading}
    >
      {errors.general && (
        <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-md text-sm">
          {errors.general}
        </div>
      )}

      <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  이름 *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  연락처
                </label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => {
                    const formatted = formatPhoneNumber(e.target.value)
                    setFormData({ ...formData, phone: formatted })
                  }}
                  placeholder="010-0000-0000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  첫 방문일
                </label>
                <input
                  type="date"
                  value={formData.first_visit_date}
                  onChange={(e) => setFormData({ ...formData, first_visit_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  거주지역
                </label>
                <input
                  type="text"
                  value={formData.region}
                  onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                  placeholder="예: 서울 강서구"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  유입경로
                </label>
                <select
                  value={formData.referral_source}
                  onChange={(e) => setFormData({ ...formData, referral_source: e.target.value })}
                  disabled={referralSourcesLoading}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50"
                >
                  <option value="">선택하세요</option>
                  {referralSourcesLoading ? (
                    <option disabled>로딩 중...</option>
                  ) : (
                    referralSources.map(source => (
                      <option key={source} value={source}>
                        {source}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  담당자
                </label>
                <input
                  type="text"
                  value={formData.assigned_staff}
                  onChange={(e) => setFormData({ ...formData, assigned_staff: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                호소 문제
              </label>
              <textarea
                value={formData.health_concerns}
                onChange={(e) => setFormData({ ...formData, health_concerns: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                메모
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
      </div>
    </BaseModal>
  )
}
