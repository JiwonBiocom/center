import { useState } from 'react'
import { Save } from 'lucide-react'

export default function ReportSettings() {
  const [settings, setSettings] = useState({
    autoGenerate: false,
    generateDay: '1', // 매월 1일
    generateTime: '09:00',
    sendEmail: false,
    emailRecipients: '',
    reportTypes: {
      monthly_summary: true,
      revenue_analysis: true,
      customer_analysis: true,
      service_analysis: false
    }
  })
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const reportTypeLabels = {
    monthly_summary: '월간 요약 보고서',
    revenue_analysis: '매출 분석 보고서',
    customer_analysis: '고객 분석 보고서',
    service_analysis: '서비스 이용 분석'
  }

  const handleSave = async () => {
    setSaving(true)
    setMessage('')
    
    try {
      // TODO: API 구현 후 연결
      await new Promise(resolve => setTimeout(resolve, 1000))
      setMessage('보고서 설정이 저장되었습니다.')
    } catch (error) {
      setMessage('보고서 설정 저장에 실패했습니다.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">보고서 설정</h2>

      <div className="space-y-6">
        {/* 자동 생성 설정 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">자동 생성 설정</h3>
          
          <div className="space-y-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.autoGenerate}
                onChange={(e) => setSettings({ ...settings, autoGenerate: e.target.checked })}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm font-medium">월간 보고서 자동 생성</span>
            </label>

            {settings.autoGenerate && (
              <div className="ml-6 space-y-3">
                <div className="flex items-center gap-3">
                  <label className="text-sm">매월</label>
                  <select
                    value={settings.generateDay}
                    onChange={(e) => setSettings({ ...settings, generateDay: e.target.value })}
                    className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {[...Array(28)].map((_, i) => (
                      <option key={i + 1} value={i + 1}>{i + 1}일</option>
                    ))}
                  </select>
                  <input
                    type="time"
                    value={settings.generateTime}
                    onChange={(e) => setSettings({ ...settings, generateTime: e.target.value })}
                    className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <span className="text-sm text-gray-500">에 생성</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 보고서 유형 선택 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">보고서 유형</h3>
          
          <div className="space-y-3">
            {Object.entries(reportTypeLabels).map(([key, label]) => (
              <label key={key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={settings.reportTypes[key as keyof typeof settings.reportTypes]}
                  onChange={(e) => setSettings({
                    ...settings,
                    reportTypes: {
                      ...settings.reportTypes,
                      [key]: e.target.checked
                    }
                  })}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-sm">{label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* 이메일 발송 설정 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">이메일 발송</h3>
          
          <div className="space-y-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.sendEmail}
                onChange={(e) => setSettings({ ...settings, sendEmail: e.target.checked })}
                className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
              />
              <span className="text-sm font-medium">생성된 보고서 이메일로 발송</span>
            </label>

            {settings.sendEmail && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  수신자 이메일 (쉼표로 구분)
                </label>
                <input
                  type="text"
                  value={settings.emailRecipients}
                  onChange={(e) => setSettings({ ...settings, emailRecipients: e.target.value })}
                  placeholder="admin@aibio.com, manager@aibio.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            )}
          </div>
        </div>
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
        {saving ? '저장 중...' : '설정 저장'}
      </button>
    </div>
  )
}