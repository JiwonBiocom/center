import { useState, useEffect } from 'react'
import { api } from '../../lib/api'
import { Save, Building2, Phone, Mail, Clock, Calendar } from 'lucide-react'

interface BusinessHours {
  [key: string]: {
    open: string
    close: string
    closed?: boolean
  }
}

interface CompanyInfo {
  company_name: string
  address: string
  phone: string
  email: string
  business_hours: BusinessHours
  holidays: string[]
}

const WEEKDAYS = [
  { key: 'mon', label: '월요일' },
  { key: 'tue', label: '화요일' },
  { key: 'wed', label: '수요일' },
  { key: 'thu', label: '목요일' },
  { key: 'fri', label: '금요일' },
  { key: 'sat', label: '토요일' },
  { key: 'sun', label: '일요일' },
]

export default function SystemSettings() {
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo>({
    company_name: '',
    address: '',
    phone: '',
    email: '',
    business_hours: {},
    holidays: []
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [newHoliday, setNewHoliday] = useState('')

  useEffect(() => {
    fetchCompanyInfo()
  }, [])

  const fetchCompanyInfo = async () => {
    try {
      const response = await api.get('/api/v1/settings/system/company')
      const data = response.data
      
      // 기본 영업시간 설정
      const defaultHours: BusinessHours = {}
      WEEKDAYS.forEach(day => {
        defaultHours[day.key] = data.business_hours?.[day.key] || {
          open: '09:00',
          close: '18:00',
          closed: day.key === 'sun'
        }
      })
      
      setCompanyInfo({
        ...data,
        business_hours: defaultHours,
        holidays: data.holidays || []
      })
    } catch (error) {
      console.error('Failed to fetch company info:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')

    try {
      await api.put('/api/v1/settings/system/company', companyInfo)
      setMessage('회사 정보가 성공적으로 업데이트되었습니다.')
    } catch (error) {
      setMessage('회사 정보 업데이트에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  const handleBusinessHoursChange = (day: string, field: 'open' | 'close' | 'closed', value: string | boolean) => {
    setCompanyInfo(prev => ({
      ...prev,
      business_hours: {
        ...prev.business_hours,
        [day]: {
          ...prev.business_hours[day],
          [field]: value
        }
      }
    }))
  }

  const addHoliday = () => {
    if (newHoliday && !companyInfo.holidays.includes(newHoliday)) {
      setCompanyInfo(prev => ({
        ...prev,
        holidays: [...prev.holidays, newHoliday].sort()
      }))
      setNewHoliday('')
    }
  }

  const removeHoliday = (holiday: string) => {
    setCompanyInfo(prev => ({
      ...prev,
      holidays: prev.holidays.filter(h => h !== holiday)
    }))
  }

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">시스템 설정</h2>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* 회사 정보 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-gray-500" />
            회사 정보
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                회사명
              </label>
              <input
                type="text"
                value={companyInfo.company_name}
                onChange={(e) => setCompanyInfo({ ...companyInfo, company_name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="w-4 h-4 inline mr-1" />
                전화번호
              </label>
              <input
                type="tel"
                value={companyInfo.phone}
                onChange={(e) => setCompanyInfo({ ...companyInfo, phone: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                이메일
              </label>
              <input
                type="email"
                value={companyInfo.email}
                onChange={(e) => setCompanyInfo({ ...companyInfo, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                주소
              </label>
              <input
                type="text"
                value={companyInfo.address}
                onChange={(e) => setCompanyInfo({ ...companyInfo, address: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* 영업 시간 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-500" />
            영업 시간
          </h3>

          <div className="space-y-3">
            {WEEKDAYS.map(day => (
              <div key={day.key} className="flex items-center gap-4">
                <div className="w-20 text-sm font-medium text-gray-700">
                  {day.label}
                </div>
                
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={!companyInfo.business_hours[day.key]?.closed}
                    onChange={(e) => handleBusinessHoursChange(day.key, 'closed', !e.target.checked)}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm">영업</span>
                </label>

                {!companyInfo.business_hours[day.key]?.closed && (
                  <>
                    <input
                      type="time"
                      value={companyInfo.business_hours[day.key]?.open || '09:00'}
                      onChange={(e) => handleBusinessHoursChange(day.key, 'open', e.target.value)}
                      className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                    <span className="text-gray-500">~</span>
                    <input
                      type="time"
                      value={companyInfo.business_hours[day.key]?.close || '18:00'}
                      onChange={(e) => handleBusinessHoursChange(day.key, 'close', e.target.value)}
                      className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </>
                )}
                
                {companyInfo.business_hours[day.key]?.closed && (
                  <span className="text-gray-500 text-sm">휴무</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 휴무일 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-500" />
            휴무일 관리
          </h3>

          <div className="mb-4">
            <div className="flex gap-2">
              <input
                type="date"
                value={newHoliday}
                onChange={(e) => setNewHoliday(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                type="button"
                onClick={addHoliday}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
              >
                추가
              </button>
            </div>
          </div>

          <div className="space-y-2">
            {companyInfo.holidays.length === 0 ? (
              <p className="text-sm text-gray-500">등록된 휴무일이 없습니다.</p>
            ) : (
              companyInfo.holidays.map(holiday => (
                <div key={holiday} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                  <span className="text-sm">{new Date(holiday).toLocaleDateString()}</span>
                  <button
                    type="button"
                    onClick={() => removeHoliday(holiday)}
                    className="text-red-600 hover:text-red-700 text-sm"
                  >
                    삭제
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {message && (
          <div className={`p-3 rounded-md ${message.includes('실패') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
            {message}
          </div>
        )}

        <button
          type="submit"
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
        >
          <Save className="w-4 h-4" />
          {saving ? '저장 중...' : '저장'}
        </button>
      </form>
    </div>
  )
}