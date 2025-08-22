import { useState } from 'react'
import { X, User, Calendar, Package, Heart, BarChart3, Sparkles, Activity, FileText, Brain, MessageSquare } from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../lib/api'
import BasicInfoTab from './tabs/BasicInfoTab'
import ServiceHistoryTab from './tabs/ServiceHistoryTab'
import PackageManagementTab from './tabs/PackageManagementTab'
import PreferencesTab from './tabs/PreferencesTab'
import AnalyticsTab from './tabs/AnalyticsTab'
import RecommendationsTab from './tabs/RecommendationsTab'
import InBodyTab from './tabs/InBodyTab'
import HealthSurveyTab from './tabs/HealthSurveyTab'
import AIHealthAnalysisTab from './tabs/AIHealthAnalysisTab'
import CounselingTab from './tabs/CounselingTab'

interface CustomerDetailModalProps {
  customerId: number
  customerName: string
  isOpen: boolean
  onClose: () => void
}

interface TabConfig {
  id: string
  label: string
  icon: React.ElementType
}

const tabs: TabConfig[] = [
  { id: 'basic', label: '기본정보', icon: User },
  { id: 'service-history', label: '서비스이력', icon: Calendar },
  { id: 'packages', label: '패키지관리', icon: Package },
  { id: 'inbody', label: '인바디정보', icon: Activity },
  { id: 'health-survey', label: '건강설문', icon: FileText },
  { id: 'counseling', label: '상담 내역', icon: MessageSquare },
  { id: 'preferences', label: '선호도', icon: Heart },
  { id: 'analytics', label: '분석', icon: BarChart3 },
  // 추천 탭과 AI 건강분석 탭은 추후 고도화 후 오픈 예정
  // { id: 'recommendations', label: '추천', icon: Sparkles },
  // { id: 'ai-health', label: 'AI 건강분석', icon: Brain },
]

export default function CustomerDetailModal({ 
  customerId, 
  customerName,
  isOpen, 
  onClose 
}: CustomerDetailModalProps) {
  const [activeTab, setActiveTab] = useState('basic')
  const queryClient = useQueryClient()

  // 고객 상세 정보 조회
  const { data: customerDetail, isLoading, error, refetch: fetchCustomerDetail } = useQuery({
    queryKey: ['customer-detail', customerId],
    queryFn: async () => {
      const response = await api.get(`/customers/${customerId}/detail`)
      return response.data
    },
    enabled: isOpen && !!customerId,
  })

  // 고객 패키지 정보 조회
  const { data: customerPackages } = useQuery({
    queryKey: ['customer-packages', customerId],
    queryFn: async () => {
      const response = await api.get(`/customers/${customerId}/packages`)
      return response.data
    },
    enabled: isOpen && !!customerId && activeTab === 'packages',
  })

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-[90%] max-w-6xl h-[85vh] flex flex-col">
        {/* 헤더 */}
        <div className="px-6 py-4 border-b flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {customerName} 고객 상세정보
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              고객번호: {customerId}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* 탭 네비게이션 */}
        <div className="border-b px-6">
          <nav className="flex space-x-6">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  data-tab-id={tab.id}
                  className={`
                    flex items-center gap-2 py-3 px-1 border-b-2 transition-colors
                    ${isActive 
                      ? 'border-indigo-600 text-indigo-600' 
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* 탭 컨텐츠 */}
        <div className="flex-1 overflow-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-red-600 mb-2">데이터를 불러오는 중 오류가 발생했습니다.</p>
                <p className="text-gray-500 text-sm">잠시 후 다시 시도해주세요.</p>
              </div>
            </div>
          ) : (
            <div className="h-full">
              {activeTab === 'basic' && customerDetail && (
                <BasicInfoTab 
                  customerDetail={customerDetail} 
                  customerId={customerId} 
                />
              )}
              
              {activeTab === 'service-history' && (
                <ServiceHistoryTab customerId={customerId} />
              )}
              
              {activeTab === 'packages' && customerDetail && (
                <PackageManagementTab 
                  customerId={customerId}
                  customerName={customerDetail.customer.name}
                  packages={customerPackages || []}
                  onRefresh={() => {
                    fetchCustomerDetail();
                    // 패키지 정보도 다시 조회
                    queryClient.invalidateQueries({ queryKey: ['customer-packages', customerId] });
                  }}
                />
              )}

              {activeTab === 'inbody' && customerDetail && (
                <InBodyTab 
                  customerId={customerId}
                  inbodyRecords={customerDetail.inbodyRecords || []}
                  onRefresh={() => {
                    // React Query를 사용해서 데이터 리프레시
                    queryClient.invalidateQueries({ queryKey: ['customer-detail', customerId] });
                    fetchCustomerDetail();
                  }}
                />
              )}

              {activeTab === 'health-survey' && (
                <HealthSurveyTab customerId={customerId} />
              )}

              {activeTab === 'counseling' && (
                <CounselingTab customerId={customerId} />
              )}
              
              {activeTab === 'preferences' && customerDetail && (
                <PreferencesTab 
                  customerId={customerId}
                  preferences={customerDetail.preferences}
                />
              )}
              
              {activeTab === 'analytics' && (
                <AnalyticsTab customerId={customerId} />
              )}
              
              {activeTab === 'recommendations' && (
                <RecommendationsTab customerId={customerId} />
              )}
              
              {activeTab === 'ai-health' && (
                <AIHealthAnalysisTab customerId={customerId} />
              )}
            </div>
          )}
        </div>

        {/* 푸터 - 필요시 액션 버튼 추가 */}
        <div className="px-6 py-4 border-t flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  )
}
