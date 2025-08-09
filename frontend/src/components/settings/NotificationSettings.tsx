import { useState, useEffect } from 'react'
import { api } from '../../lib/api'
import { Save } from 'lucide-react'

export default function NotificationSettings() {
  const [preferences, setPreferences] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const notificationTypes = [
    { type: 'package_expiry', label: '패키지 만료 알림', description: '패키지 만료일이 다가올 때 알림' },
    { type: 'payment_received', label: '결제 완료 알림', description: '고객 결제가 완료되었을 때 알림' },
    { type: 'new_customer', label: '신규 고객 알림', description: '새로운 고객이 등록되었을 때 알림' },
    { type: 'service_completed', label: '서비스 완료 알림', description: '서비스 이용이 완료되었을 때 알림' }
  ]

  useEffect(() => {
    fetchPreferences()
  }, [])

  const fetchPreferences = async () => {
    try {
      const response = await api.get('/api/v1/settings/notifications/preferences')
      const data = response.data
      
      // 기본 설정과 병합
      const merged = notificationTypes.map(nt => {
        const existing = data.find((p: any) => p.notification_type === nt.type)
        return existing || {
          notification_type: nt.type,
          in_app: true,
          email: false,
          sms: false
        }
      })
      
      setPreferences(merged)
    } catch (error) {
      console.error('Failed to fetch preferences:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = (type: string, channel: 'in_app' | 'email' | 'sms') => {
    setPreferences(prev => prev.map(p => 
      p.notification_type === type 
        ? { ...p, [channel]: !p[channel] }
        : p
    ))
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage('')
    
    try {
      await api.put('/api/v1/settings/notifications/preferences', preferences)
      setMessage('알림 설정이 저장되었습니다.')
    } catch (error) {
      setMessage('알림 설정 저장에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">알림 설정</h2>
      
      <div className="space-y-6">
        {notificationTypes.map(nt => {
          const pref = preferences.find(p => p.notification_type === nt.type)
          
          return (
            <div key={nt.type} className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="mb-3">
                <h3 className="font-medium text-gray-900">{nt.label}</h3>
                <p className="text-sm text-gray-500">{nt.description}</p>
              </div>
              
              <div className="flex gap-6">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={pref?.in_app || false}
                    onChange={() => handleToggle(nt.type, 'in_app')}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm">인앱 알림</span>
                </label>
                
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={pref?.email || false}
                    onChange={() => handleToggle(nt.type, 'email')}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm">이메일</span>
                </label>
                
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={pref?.sms || false}
                    onChange={() => handleToggle(nt.type, 'sms')}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <span className="text-sm">SMS</span>
                </label>
              </div>
            </div>
          )
        })}
      </div>

      {message && (
        <div className={`mt-4 p-3 rounded-md ${message.includes('실패') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {message}
        </div>
      )}

      <button
        onClick={handleSave}
        disabled={saving}
        className="mt-6 flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
      >
        <Save className="w-4 h-4" />
        {saving ? '저장 중...' : '저장'}
      </button>
    </div>
  )
}