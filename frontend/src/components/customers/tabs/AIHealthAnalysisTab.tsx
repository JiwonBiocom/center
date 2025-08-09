import { useQuery } from '@tanstack/react-query';
import { api } from '../../../lib/api';
import { 
  Sparkles, Package, TrendingUp, Heart, 
  AlertCircle, CheckCircle, Clock, Gift,
  FileText, Activity, Pill, Apple,
  BarChart3, Target, Brain, Zap,
  Users, Calendar, Award, ChevronRight
} from 'lucide-react';
import { useState } from 'react';

interface AIHealthAnalysisTabProps {
  customerId: number;
}

interface HealthAnalysisData {
  has_health_data?: boolean;
  message?: string;
  service_recommendations: Array<{
    service_name: string;
    reason: string;
    expected_benefit: string;
    priority: 'high' | 'medium' | 'low';
    frequency?: string;
    duration?: number;
  }>;
  package_recommendations: Array<{
    package_name: string;
    services_included: string[];
    discount_rate: number;
    recommended_price: number;
    reason: string;
  }>;
  care_recommendations: Array<{
    category: string;
    suggestion: string;
    urgency: 'immediate' | 'soon' | 'long-term';
  }>;
  supplement_recommendations?: Array<{
    name: string;
    reason: string;
    dosage: string;
    price: number;
    category: string;
  }>;
  diet_recommendations?: Array<{
    meal_type: string;
    menu: string;
    calories: number;
    reason: string;
    nutrients: {
      protein: number;
      carbs: number;
      fat: number;
    };
  }>;
  health_analysis?: {
    cellular_age?: number;
    age_gap?: number;
    overall_score?: number;
    category_scores?: {
      body_composition: number;
      metabolic_health: number;
      stress_management: number;
      vitality: number;
      nutrition: number;
    };
    overall_status: string;
    main_concerns: string[];
    strengths: string[];
    improvement_areas: string[];
  };
}

export default function AIHealthAnalysisTab({ customerId }: AIHealthAnalysisTabProps) {
  const [activeSection, setActiveSection] = useState<string>('overview');
  
  // AI 건강 분석 데이터 조회
  const { data: analysisData, isLoading, error } = useQuery<HealthAnalysisData>({
    queryKey: ['ai-health-analysis', customerId],
    queryFn: async () => {
      const response = await api.get(`/customers/${customerId}/recommendations`);
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-gray-600">AI 건강 분석을 불러오는데 실패했습니다.</p>
      </div>
    );
  }

  if (!analysisData) {
    return null;
  }

  // 건강 데이터가 없는 경우
  if (analysisData.has_health_data === false) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="h-6 w-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">AI 건강 분석</h3>
          </div>
          <p className="text-gray-600">
            고객님의 건강 상태를 종합적으로 분석하여 맞춤형 건강 관리 솔루션을 제공합니다.
          </p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <div className="max-w-md mx-auto">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">건강 정보를 입력해주세요</h4>
            <p className="text-gray-600 mb-6">
              건강설문과 인바디970 정보를 바탕으로 AI가 맞춤 분석을 제공합니다.
            </p>
            <div className="space-y-3">
              <button 
                onClick={() => window.location.href = '/tablet-questionnaire'}
                className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <FileText className="h-5 w-5" />
                건강설문 작성하기
              </button>
              <button 
                onClick={() => {
                  const inbodyTab = document.querySelector('[data-tab-id="inbody"]');
                  if (inbodyTab) {
                    (inbodyTab as HTMLElement).click();
                  }
                }}
                className="w-full py-3 px-4 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
              >
                <Activity className="h-5 w-5" />
                인바디 측정 결과 입력
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getUrgencyIcon = (urgency: string) => {
    switch (urgency) {
      case 'immediate':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'soon':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'overview':
        return <BarChart3 className="h-5 w-5" />;
      case 'services':
        return <Zap className="h-5 w-5" />;
      case 'supplements':
        return <Pill className="h-5 w-5" />;
      case 'diet':
        return <Apple className="h-5 w-5" />;
      case 'lifestyle':
        return <Heart className="h-5 w-5" />;
      case 'packages':
        return <Package className="h-5 w-5" />;
      default:
        return <Activity className="h-5 w-5" />;
    }
  };

  const sections = [
    { id: 'overview', label: '종합 분석', icon: 'overview' },
    { id: 'services', label: '서비스 추천', icon: 'services' },
    { id: 'supplements', label: '영양제 추천', icon: 'supplements' },
    { id: 'diet', label: '식단 가이드', icon: 'diet' },
    { id: 'lifestyle', label: '생활 습관', icon: 'lifestyle' },
    { id: 'packages', label: '패키지 추천', icon: 'packages' },
  ];

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="h-6 w-6 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">AI 건강 분석</h3>
        </div>
        <p className="text-gray-600">
          고객님의 건강 상태를 종합적으로 분석하여 맞춤형 건강 관리 솔루션을 제공합니다.
        </p>
      </div>

      {/* 섹션 탭 */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 whitespace-nowrap transition-colors ${
              activeSection === section.id
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            {getCategoryIcon(section.icon)}
            {section.label}
          </button>
        ))}
      </div>

      {/* 종합 분석 섹션 */}
      {activeSection === 'overview' && analysisData.health_analysis && (
        <div className="space-y-6">
          {/* 건강 점수 대시보드 */}
          {analysisData.health_analysis.overall_score && (
            <div className="bg-white rounded-lg border p-6">
              <h4 className="text-lg font-semibold mb-4">종합 건강 점수</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* 세포 나이 */}
                <div className="text-center">
                  <div className="relative inline-flex items-center justify-center w-32 h-32 mb-3">
                    <svg className="w-32 h-32 transform -rotate-90">
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-gray-200"
                      />
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 56}`}
                        strokeDashoffset={`${2 * Math.PI * 56 * (1 - 0.7)}`}
                        className="text-purple-600"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-bold">{analysisData.health_analysis.cellular_age}세</span>
                      <span className="text-sm text-gray-500">세포 나이</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">
                    실제 나이 대비 {analysisData.health_analysis.age_gap > 0 ? '+' : ''}{analysisData.health_analysis.age_gap}세
                  </p>
                </div>

                {/* 전체 건강 점수 */}
                <div className="text-center">
                  <div className="relative inline-flex items-center justify-center w-32 h-32 mb-3">
                    <svg className="w-32 h-32 transform -rotate-90">
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        className="text-gray-200"
                      />
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke="currentColor"
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 56}`}
                        strokeDashoffset={`${2 * Math.PI * 56 * (1 - analysisData.health_analysis.overall_score / 100)}`}
                        className="text-blue-600"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-3xl font-bold">{Math.round(analysisData.health_analysis.overall_score)}</span>
                      <span className="text-sm text-gray-500">종합 점수</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">100점 만점</p>
                </div>

                {/* 카테고리별 점수 */}
                <div className="space-y-3">
                  <h5 className="font-medium text-gray-900 mb-2">카테고리별 평가</h5>
                  {analysisData.health_analysis.category_scores && Object.entries(analysisData.health_analysis.category_scores).map(([key, value]) => {
                    const labels: {[key: string]: string} = {
                      body_composition: '신체 구성',
                      metabolic_health: '대사 건강',
                      stress_management: '스트레스 관리',
                      vitality: '체력/활력',
                      nutrition: '영양 상태'
                    };
                    return (
                      <div key={key} className="flex items-center gap-2">
                        <span className="text-sm text-gray-600 w-24">{labels[key]}</span>
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              value >= 80 ? 'bg-green-600' :
                              value >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                            }`}
                            style={{ width: `${value}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-12 text-right">{Math.round(value)}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* 주요 분석 결과 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 주요 우려사항 */}
            {analysisData.health_analysis.main_concerns && analysisData.health_analysis.main_concerns.length > 0 && (
              <div className="bg-red-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-red-600" />
                  주요 우려사항
                </h5>
                <ul className="space-y-2">
                  {analysisData.health_analysis.main_concerns.map((concern, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                      <ChevronRight className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                      {concern}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 강점 */}
            {analysisData.health_analysis.strengths && analysisData.health_analysis.strengths.length > 0 && (
              <div className="bg-green-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  건강 강점
                </h5>
                <ul className="space-y-2">
                  {analysisData.health_analysis.strengths.map((strength, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                      <ChevronRight className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 개선 필요 영역 */}
            {analysisData.health_analysis.improvement_areas && analysisData.health_analysis.improvement_areas.length > 0 && (
              <div className="bg-blue-50 rounded-lg p-4">
                <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Target className="h-5 w-5 text-blue-600" />
                  개선 필요 영역
                </h5>
                <ul className="space-y-2">
                  {analysisData.health_analysis.improvement_areas.map((area, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                      <ChevronRight className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                      {area}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 서비스 추천 섹션 */}
      {activeSection === 'services' && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-600" />
            맞춤 서비스 추천
          </h4>
          <div className="space-y-4">
            {analysisData.service_recommendations.length > 0 ? (
              analysisData.service_recommendations.map((service, index) => (
                <div
                  key={index}
                  className={`border rounded-lg p-4 ${getPriorityColor(service.priority)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h5 className="font-semibold text-lg">{service.service_name}</h5>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      service.priority === 'high' ? 'bg-red-200' : 
                      service.priority === 'medium' ? 'bg-yellow-200' : 'bg-green-200'
                    }`}>
                      {service.priority === 'high' ? '강력 추천' : 
                       service.priority === 'medium' ? '추천' : '선택'}
                    </span>
                  </div>
                  <p className="text-sm mb-3">{service.reason}</p>
                  <div className="flex items-center gap-2 text-sm">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="font-medium">기대 효과:</span>
                    <span>{service.expected_benefit}</span>
                  </div>
                  {service.frequency && (
                    <div className="flex items-center gap-2 text-sm mt-2">
                      <Calendar className="h-4 w-4 text-blue-600" />
                      <span className="font-medium">권장 빈도:</span>
                      <span>{service.frequency}</span>
                    </div>
                  )}
                  {service.duration && (
                    <div className="flex items-center gap-2 text-sm mt-2">
                      <Clock className="h-4 w-4 text-purple-600" />
                      <span className="font-medium">세션 시간:</span>
                      <span>{service.duration}분</span>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">추천할 서비스가 없습니다.</p>
            )}
          </div>
        </div>
      )}

      {/* 영양제 추천 섹션 */}
      {activeSection === 'supplements' && analysisData.supplement_recommendations && analysisData.supplement_recommendations.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Pill className="h-5 w-5 text-indigo-600" />
            맞춤 영양제 추천
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {analysisData.supplement_recommendations.map((supplement, index) => (
              <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h5 className="font-semibold text-lg">{supplement.name}</h5>
                    <span className="text-sm text-gray-500">{supplement.category}</span>
                  </div>
                  <span className="text-lg font-bold text-indigo-600">
                    {supplement.price.toLocaleString()}원
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{supplement.reason}</p>
                <div className="flex items-center gap-2 text-sm bg-gray-50 rounded p-2">
                  <span className="font-medium">복용법:</span>
                  <span>{supplement.dosage}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 식단 가이드 섹션 */}
      {activeSection === 'diet' && analysisData.diet_recommendations && analysisData.diet_recommendations.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Apple className="h-5 w-5 text-green-600" />
            맞춤 식단 가이드
          </h4>
          <div className="space-y-4">
            {analysisData.diet_recommendations.map((diet, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium mb-2">
                      {diet.meal_type}
                    </span>
                    <h5 className="font-semibold text-lg">{diet.menu}</h5>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-bold text-gray-900">{diet.calories}</span>
                    <span className="text-sm text-gray-500 block">kcal</span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-3">{diet.reason}</p>
                <div className="flex gap-4 text-sm bg-gray-50 rounded p-3">
                  <div className="flex items-center gap-1">
                    <span className="font-medium">단백질:</span>
                    <span className="text-blue-600 font-medium">{diet.nutrients.protein}g</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="font-medium">탄수화물:</span>
                    <span className="text-green-600 font-medium">{diet.nutrients.carbs}g</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="font-medium">지방:</span>
                    <span className="text-orange-600 font-medium">{diet.nutrients.fat}g</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 생활 습관 섹션 */}
      {activeSection === 'lifestyle' && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Heart className="h-5 w-5 text-red-600" />
            생활 습관 관리
          </h4>
          <div className="space-y-3">
            {analysisData.care_recommendations.length > 0 ? (
              analysisData.care_recommendations
                .sort((a, b) => {
                  const urgencyOrder = { immediate: 0, soon: 1, 'long-term': 2 };
                  return urgencyOrder[a.urgency] - urgencyOrder[b.urgency];
                })
                .map((care, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    {getUrgencyIcon(care.urgency)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium">{care.category}</span>
                        <span className="text-xs text-gray-500">
                          ({care.urgency === 'immediate' ? '즉시 필요' : 
                            care.urgency === 'soon' ? '조만간 필요' : '장기적 관리'})
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{care.suggestion}</p>
                    </div>
                  </div>
                ))
            ) : (
              <p className="text-gray-500 text-center py-4">추천할 관리사항이 없습니다.</p>
            )}
          </div>
        </div>
      )}

      {/* 패키지 추천 섹션 */}
      {activeSection === 'packages' && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Package className="h-5 w-5 text-green-600" />
            추천 패키지
          </h4>
          <div className="space-y-4">
            {analysisData.package_recommendations.length > 0 ? (
              analysisData.package_recommendations.map((pkg, index) => (
                <div key={index} className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h5 className="font-semibold text-xl mb-2">{pkg.package_name}</h5>
                      <p className="text-gray-600">{pkg.reason}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-3xl font-bold text-blue-600">
                        {pkg.recommended_price.toLocaleString()}원
                      </p>
                      {pkg.discount_rate > 0 && (
                        <span className="text-sm text-red-600 font-medium">
                          {pkg.discount_rate}% 할인
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">포함 서비스:</p>
                    <div className="flex flex-wrap gap-2">
                      {pkg.services_included.map((service, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
                    <Award className="h-5 w-5" />
                    이 패키지 추천하기
                  </button>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">추천할 패키지가 없습니다.</p>
            )}
          </div>
        </div>
      )}

      {/* 특별 혜택 */}
      <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-3">
          <Gift className="h-6 w-6 text-orange-600" />
          <h4 className="text-lg font-semibold">고객님을 위한 특별 혜택</h4>
        </div>
        <p className="text-gray-700 mb-4">
          AI 분석 결과, 고객님께 아래 특별 혜택을 제공해드립니다.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-4">
            <p className="font-medium text-orange-600 mb-1">재방문 할인</p>
            <p className="text-sm text-gray-600">다음 방문 시 10% 할인</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <p className="font-medium text-orange-600 mb-1">친구 추천 혜택</p>
            <p className="text-sm text-gray-600">추천 시 양쪽 모두 혜택</p>
          </div>
        </div>
      </div>
    </div>
  );
}