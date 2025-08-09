import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import { api } from '../lib/api'

interface PackageModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  packageData?: PackageType | null
}

interface PackageType {
  package_id: number
  package_name: string
  total_sessions: number
  price: number
  valid_days: number
  is_active: boolean
  description?: string
}

export default function PackageModal({ isOpen, onClose, onSuccess, packageData }: PackageModalProps) {
  const [formData, setFormData] = useState({
    package_name: '',
    total_sessions: 0,
    price: 0,
    valid_days: 30,
    is_active: true,
    description: ''
  })

  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<any>({})

  useEffect(() => {
    if (packageData) {
      setFormData({
        package_name: packageData.package_name,
        total_sessions: packageData.total_sessions,
        price: packageData.price,
        valid_days: packageData.valid_days,
        is_active: packageData.is_active,
        description: packageData.description || ''
      })
    } else {
      setFormData({
        package_name: '',
        total_sessions: 0,
        price: 0,
        valid_days: 30,
        is_active: true,
        description: ''
      })
    }
  }, [packageData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setErrors({})

    try {
      const payload = {
        ...formData,
        description: formData.description || null
      }

      if (packageData) {
        await api.put(`/packages/${packageData.package_id}`, payload)
      } else {
        await api.post('/packages', payload)
      }

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

  const isEditing = !!packageData

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75" onClick={onClose} />

        <div className="relative bg-white rounded-lg max-w-md w-full p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              {isEditing ? '패키지 수정' : '새 패키지 등록'}
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
                패키지명 *
              </label>
              <input
                type="text"
                required
                value={formData.package_name}
                onChange={(e) => setFormData({ ...formData, package_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="예: 브레인 10회 패키지"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  총 세션 수 *
                </label>
                <input
                  type="number"
                  required
                  value={formData.total_sessions}
                  onChange={(e) => setFormData({ ...formData, total_sessions: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  min="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  유효기간 (일) *
                </label>
                <input
                  type="number"
                  required
                  value={formData.valid_days}
                  onChange={(e) => setFormData({ ...formData, valid_days: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                가격 (원) *
              </label>
              <input
                type="number"
                required
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                min="0"
                step="1000"
              />
              {formData.total_sessions > 0 && (
                <p className="mt-1 text-sm text-gray-500">
                  회당 가격: {(formData.price / formData.total_sessions).toLocaleString()}원
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                설명
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="패키지에 대한 추가 설명을 입력하세요..."
              />
            </div>

            <div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">활성 상태</span>
              </label>
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
                {loading ? '처리 중...' : isEditing ? '수정' : '등록'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
