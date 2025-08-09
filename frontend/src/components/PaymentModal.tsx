import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { X } from 'lucide-react'
import { formatDateToISO } from '../lib/utils'

interface Payment {
  payment_id: number;
  customer_id: number;
  customer_name: string;
  customer_phone: string;
  payment_date: string;
  amount: number;
  payment_method: string;
  payment_type?: string;
  payment_status?: string;
  card_holder_name?: string;
  approval_number?: string;
  payment_staff?: string;
  purchase_type?: string;
  purchase_order?: number;
  notes?: string;
  created_at: string;
}

interface PaymentModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  payment?: Payment
}

interface Customer {
  customer_id: number
  name: string
  phone: string
}

interface Package {
  package_id: number
  package_name: string
  total_sessions: number
  price: number
}

export default function PaymentModal({ isOpen, onClose, onSuccess, payment }: PaymentModalProps) {
  const [formData, setFormData] = useState({
    customer_id: 0,
    payment_date: formatDateToISO(new Date()),
    amount: '' as number | '',
    payment_method: '카드',
    card_holder_name: '',
    approval_number: '',
    payment_staff: '',
    purchase_type: '',
    purchase_order: null as number | null,
    package_id: null as number | null,
    notes: ''
  })

  const [customers, setCustomers] = useState<Customer[]>([])
  const [packages, setPackages] = useState<Package[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<any>({})

  useEffect(() => {
    if (isOpen) {
      fetchCustomers()
      fetchPackages()

      // 수정 모드인 경우 기존 데이터로 초기화
      if (payment) {
        setFormData({
          customer_id: payment.customer_id,
          payment_date: payment.payment_date.split('T')[0], // 날짜 형식 맞추기
          amount: payment.amount,
          payment_method: payment.payment_method || '카드',
          card_holder_name: payment.card_holder_name || '',
          approval_number: payment.approval_number || '',
          payment_staff: payment.payment_staff || '',
          purchase_type: payment.purchase_type || '',
          purchase_order: payment.purchase_order || null,
          package_id: null, // 패키지 ID는 별도로 조회 필요
          notes: payment.notes || ''
        })
      } else {
        // 새로 추가하는 경우 초기화
        setFormData({
          customer_id: 0,
          payment_date: formatDateToISO(new Date()),
          amount: '',
          payment_method: '카드',
          card_holder_name: '',
          approval_number: '',
          payment_staff: '',
          purchase_type: '',
          purchase_order: null,
          package_id: null,
          notes: ''
        })
      }
    }
  }, [isOpen, payment])

  useEffect(() => {
    if (searchTerm) {
      fetchCustomers()
    }
  }, [searchTerm])

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers', {
        params: searchTerm ? { search: searchTerm } : {}
      })
      // response.data가 배열인지 확인
      if (Array.isArray(response.data)) {
        setCustomers(response.data)
      } else if (response.data?.data && Array.isArray(response.data.data)) {
        // ResponseFormatter 형식인 경우
        setCustomers(response.data.data)
      } else {
        console.error('Unexpected customers format:', response.data)
        setCustomers([])
      }
    } catch (error) {
      console.error('Failed to fetch customers:', error)
      setCustomers([])
    }
  }

  const fetchPackages = async () => {
    try {
      const response = await api.get('/packages/', {
        params: { is_active: true }
      })
      // response.data가 배열인지 확인
      if (Array.isArray(response.data)) {
        setPackages(response.data)
      } else if (response.data?.data && Array.isArray(response.data.data)) {
        // ResponseFormatter 형식인 경우
        setPackages(response.data.data)
      } else {
        console.error('Unexpected packages format:', response.data)
        setPackages([])
      }
    } catch (error) {
      console.error('Failed to fetch packages:', error)
      setPackages([])
    }
  }

  const handlePackageSelect = (packageId: string) => {
    const id = packageId ? parseInt(packageId) : null
    setFormData({ ...formData, package_id: id })

    if (id) {
      const selectedPackage = packages.find(p => p.package_id === id)
      if (selectedPackage) {
        setFormData(prev => ({
          ...prev,
          package_id: id,
          amount: selectedPackage.price || 0,  // null일 경우 0으로 설정
          purchase_type: '패키지'
        }))
      }
    } else {
      setFormData(prev => ({
        ...prev,
        package_id: null,
        purchase_type: ''
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setErrors({})

    try {
      const payload = {
        customer_id: formData.customer_id,
        payment_date: formData.payment_date,
        amount: formData.amount === '' ? 0 : formData.amount,
        payment_method: formData.payment_method === '카드' ? 'card' :
                        formData.payment_method === '계좌이체' ? 'transfer' :
                        formData.payment_method === '현금' ? 'cash' : 'other',
        payment_type: formData.package_id ? 'package' : 'single',
        payment_staff: formData.payment_staff || null,
        reference_type: formData.purchase_type || null,
        reference_id: formData.purchase_order || formData.package_id || null,
        notes: formData.notes || null
      }

      if (payment) {
        // 수정 모드
        await api.put(`/payments/${payment.payment_id}`, payload)
      } else {
        // 생성 모드
        await api.post('/payments', payload)
      }
      onSuccess()

      // Reset form
      setFormData({
        customer_id: 0,
        payment_date: formatDateToISO(new Date()),
        amount: '',
        payment_method: '카드',
        card_holder_name: '',
        approval_number: '',
        payment_staff: '',
        purchase_type: '',
        purchase_order: null,
        package_id: null,
        notes: ''
      })
      setSearchTerm('')
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
              {payment ? '결제 수정' : '결제 등록'}
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
                  onChange={(e) => setSearchTerm(e.target.value)}
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
                  {Array.isArray(customers) && customers.map((customer) => (
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
                  결제일 *
                </label>
                <input
                  type="date"
                  required
                  value={formData.payment_date}
                  onChange={(e) => setFormData({ ...formData, payment_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  결제 방법 *
                </label>
                <select
                  required
                  value={formData.payment_method}
                  onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="카드">카드</option>
                  <option value="계좌이체">계좌이체</option>
                  <option value="현금">현금</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                패키지 선택
              </label>
              <select
                value={formData.package_id || ''}
                onChange={(e) => handlePackageSelect(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">패키지 선택 안함</option>
                {packages.map((pkg) => (
                  <option key={pkg.package_id} value={pkg.package_id}>
                    {pkg.package_name} ({pkg.total_sessions}회){pkg.price ? ` - ${pkg.price.toLocaleString()}원` : ''}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  결제 금액 *
                </label>
                <input
                  type="number"
                  required
                  value={formData.amount || ''}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value === '' ? 0 : parseFloat(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  min="0"
                  step="1"
                  placeholder="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  구매 항목
                </label>
                <input
                  type="text"
                  value={formData.purchase_type}
                  onChange={(e) => setFormData({ ...formData, purchase_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="예: 패키지, 단일 서비스"
                />
              </div>
            </div>

            {formData.payment_method === '카드' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    카드 소유자명
                  </label>
                  <input
                    type="text"
                    value={formData.card_holder_name}
                    onChange={(e) => setFormData({ ...formData, card_holder_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    승인번호
                  </label>
                  <input
                    type="text"
                    value={formData.approval_number}
                    onChange={(e) => setFormData({ ...formData, approval_number: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  담당 직원
                </label>
                <input
                  type="text"
                  value={formData.payment_staff}
                  onChange={(e) => setFormData({ ...formData, payment_staff: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  구매 차수
                </label>
                <input
                  type="number"
                  value={formData.purchase_order || ''}
                  onChange={(e) => setFormData({ ...formData, purchase_order: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                메모 / 특이사항
              </label>
              <textarea
                rows={3}
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="분할결제, 특이사항 등을 입력하세요..."
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
