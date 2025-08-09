import { useNavigate } from 'react-router-dom'
import { Shield, Users, AlertTriangle, ChevronRight } from 'lucide-react'

export default function MasterSettings() {
  const navigate = useNavigate()

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">시스템 관리 (마스터)</h2>
        <p className="text-sm text-gray-600 mt-1">최고 권한으로 시스템을 관리합니다</p>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-yellow-800">주의사항</p>
            <p className="text-sm text-yellow-700 mt-1">
              마스터 권한은 시스템의 모든 기능에 접근할 수 있습니다.
              사용자 삭제, 비밀번호 초기화 등 중요한 작업을 수행할 때는 신중하게 진행하세요.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <button
          onClick={() => navigate('/master')}
          className="w-full flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-red-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">마스터 관리 페이지</p>
              <p className="text-sm text-gray-600">전체 사용자 관리, 시스템 통계 확인</p>
            </div>
          </div>
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </button>

        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900 mb-3">마스터 권한 기능</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-0.5">•</span>
              <span>전체 사용자 조회 및 삭제</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-0.5">•</span>
              <span>사용자 비밀번호 초기화</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-0.5">•</span>
              <span>사용자 권한 변경 (staff, manager, admin, master)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-500 mt-0.5">•</span>
              <span>시스템 전체 통계 조회</span>
            </li>
          </ul>
        </div>

        <div className="p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Users className="w-5 h-5 text-blue-600" />
            <h3 className="font-medium text-blue-900">권한 계층 구조</h3>
          </div>
          <div className="space-y-1 text-sm">
            <div className="flex items-center gap-2">
              <span className="font-mono bg-red-100 text-red-700 px-2 py-0.5 rounded">master</span>
              <span className="text-gray-600">시스템 관리자 (최고 권한)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono bg-purple-100 text-purple-700 px-2 py-0.5 rounded">admin</span>
              <span className="text-gray-600">관리자</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono bg-blue-100 text-blue-700 px-2 py-0.5 rounded">manager</span>
              <span className="text-gray-600">매니저</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono bg-gray-100 text-gray-700 px-2 py-0.5 rounded">staff</span>
              <span className="text-gray-600">직원</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
