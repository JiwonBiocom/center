import { useState, useEffect } from 'react'
import { api } from '../../lib/api'
import { Database } from 'lucide-react'

export default function BackupSettings() {
  const [backups, setBackups] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    fetchBackups()
  }, [])

  const fetchBackups = async () => {
    try {
      const response = await api.get('/api/v1/settings/backup/list')
      setBackups(response.data)
    } catch (error) {
      console.error('Failed to fetch backups:', error)
    } finally {
      setLoading(false)
    }
  }

  const createBackup = async () => {
    if (!confirm('데이터베이스 백업을 생성하시겠습니까?')) return
    
    setCreating(true)
    try {
      const response = await api.post('/api/v1/settings/backup/create')
      alert(`백업이 생성되었습니다: ${response.data.filename}`)
      fetchBackups()
    } catch (error) {
      alert('백업 생성에 실패했습니다.')
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">백업 및 복원</h2>
        <button
          onClick={createBackup}
          disabled={creating}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
        >
          <Database className="w-4 h-4" />
          {creating ? '백업 생성 중...' : '새 백업 생성'}
        </button>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                백업 파일
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                크기
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                생성일시
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {backups.map((backup, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <Database className="w-4 h-4 text-gray-400 mr-2" />
                    <span className="text-sm font-medium text-gray-900">{backup.filename}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {backup.size}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(backup.created_at).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {backups.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            백업 파일이 없습니다.
          </div>
        )}
      </div>

      <div className="mt-4 p-4 bg-yellow-50 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>주의:</strong> 백업 파일은 서버에 저장되며, 실제 환경에서는 자동 백업 스케줄과 외부 저장소 연동이 필요합니다.
        </p>
      </div>
    </div>
  )
}