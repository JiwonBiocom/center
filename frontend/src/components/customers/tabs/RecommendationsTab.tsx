import { useQuery } from '@tanstack/react-query';
import { api } from '../../../lib/api';
import { 
  Sparkles, Package, TrendingUp, Heart, 
  AlertCircle, CheckCircle, Clock, Gift,
  FileText, Activity, Pill, Apple,
  BarChart3, Target
} from 'lucide-react';

interface RecommendationsTabProps {
  customerId: number;
}

interface Recommendation {
  has_health_data?: boolean;
  message?: string;
  service_recommendations: Array<{
    service_name: string;
    reason: string;
    expected_benefit: string;
    priority: 'high' | 'medium' | 'low';
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

export default function RecommendationsTab({ customerId }: RecommendationsTabProps) {
  // 추천 데이터 조회
  const { data: recommendations, isLoading, error } = useQuery<Recommendation>({
    queryKey: ['customer-recommendations', customerId],
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
        <p className="text-gray-600">추천 데이터를 불러오는데 실패했습니다.</p>
        {error && <p className="text-sm text-gray-500 mt-2">오류: {(error as any).message || '알 수 없는 오류'}</p>}
      </div>
    );
  }

  if (!recommendations) {
    return null;
  }

  // 건강 데이터가 없는 경우
  if (recommendations.has_health_data === false) {
    return (
      <div className="space-y-6">
        {/* AI 추천 헤더 */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="h-6 w-6 text-purple-600" />
            <h3 className="text-lg font-semibold text-gray-900">AI 맞춤 추천</h3>
          </div>
        </div>

        {/* 건강 데이터 필요 안내 */}
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <div className="max-w-md mx-auto">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">건강 정보를 입력해주세요</h4>
            <p className="text-gray-600 mb-6">
              {recommendations.message || "건강 설문과 인바디970 정보를 바탕으로 AI가 맞춤 관리해 드립니다. 정보를 채워주세요"}
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
                  // InBody 탭으로 이동하는 로직 추가 필요
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

  const getUrgencyText = (urgency: string) => {
    switch (urgency) {
      case 'immediate':
        return '즉시 필요';
      case 'soon':
        return '조만간 필요';
      default:
        return '장기적 관리';
    }
  };

  return (
    <div className="space-y-6">
      {/* AI 추천 헤더 */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-2">
          <Sparkles className="h-6 w-6 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">AI 맞춤 추천</h3>
        </div>
        <p className="text-gray-600">
          고객님의 이용 패턴과 건강 목표를 분석하여 최적의 서비스를 추천해드립니다.
        </p>
        {/* 건강설문이 없는 경우 안내 메시지 */}
        {recommendations.has_health_data === false && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <p className="text-sm text-yellow-800 font-medium">
                건강설문과 인바디를 통해 AI 추천을 받아보세요. 정보가 없습니다.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* 종합 건강 점수 대시보드 */}
      {recommendations.health_analysis && recommendations.health_analysis.overall_score && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-600" />
            종합 건강 점수
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 세포 나이 */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">세포 나이</p>
              <p className="text-2xl font-bold text-gray-900">{recommendations.health_analysis.cellular_age}세</p>
              <p className="text-sm text-gray-500 mt-1">
                실제 나이 대비 {recommendations.health_analysis.age_gap > 0 ? '+' : ''}{recommendations.health_analysis.age_gap}세
              </p>
            </div>
            
            {/* 전체 건강 점수 */}
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">전체 건강 점수</p>
              <p className="text-3xl font-bold text-blue-600">{Math.round(recommendations.health_analysis.overall_score)}점</p>
              <p className="text-sm text-gray-500 mt-1">100점 만점</p>
            </div>
            
            {/* 카테고리별 점수 */}
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-2">카테고리별 평가</p>
              <div className="space-y-1">
                {recommendations.health_analysis.category_scores && Object.entries(recommendations.health_analysis.category_scores).map(([key, value], index) => {
                  const labels: {[key: string]: string} = {
                    body_composition: '신체 구성',
                    metabolic_health: '대사 건강',
                    stress_management: '스트레스 관리',
                    vitality: '체력/활력',
                    nutrition: '영양 상태'
                  };
                  const getScoreColor = (score: number) => {
                    if (score >= 80) return 'text-green-600';
                    if (score >= 60) return 'text-yellow-600';
                    return 'text-red-600';
                  };
                  return (
                    <div key={key} className="flex justify-between items-center">
                      <span className="text-xs text-gray-600">{labels[key] || key}</span>
                      <span className={`text-xs font-medium ${getScoreColor(value)}`}>{Math.round(value)}점</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 서비스 추천 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-600" />
          추천 서비스
        </h4>
        <div className="space-y-4">
          {recommendations.service_recommendations.length > 0 ? (
            recommendations.service_recommendations.map((service, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 ${getPriorityColor(service.priority)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h5 className="font-semibold text-lg">{service.service_name}</h5>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    service.priority === 'high' ? 'bg-red-200' : 
                    service.priority === 'medium' ? 'bg-yellow-200' : 'bg-green-200'
                  }`}>
                    {service.priority === 'high' ? '높음' : 
                     service.priority === 'medium' ? '보통' : '낮음'}
                  </span>
                </div>
                <p className="text-sm mb-2">{service.reason}</p>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="font-medium">기대 효과:</span>
                  <span>{service.expected_benefit}</span>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">추천할 서비스가 없습니다.</p>
          )}
        </div>
      </div>

      {/* 패키지 추천 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Package className="h-5 w-5 text-green-600" />
          추천 패키지
        </h4>
        <div className="space-y-4">
          {recommendations.package_recommendations.length > 0 ? (
            recommendations.package_recommendations.map((pkg, index) => (
              <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h5 className="font-semibold text-lg">{pkg.package_name}</h5>
                    <p className="text-sm text-gray-600 mt-1">{pkg.reason}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-blue-600">
                      {pkg.recommended_price.toLocaleString()}원
                    </p>
                    {pkg.discount_rate > 0 && (
                      <span className="text-sm text-red-600 font-medium">
                        {pkg.discount_rate}% 할인
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mt-3">
                  {pkg.services_included.map((service, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                    >
                      {service}
                    </span>
                  ))}
                </div>
                <button className="mt-4 w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                  이 패키지 추천하기
                </button>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">추천할 패키지가 없습니다.</p>
          )}
        </div>
      </div>

      {/* 관리 추천 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Heart className="h-5 w-5 text-red-600" />
          관리 추천사항
        </h4>
        <div className="space-y-3">
          {recommendations.care_recommendations.length > 0 ? (
            recommendations.care_recommendations
              .sort((a, b) => {
                const urgencyOrder = { immediate: 0, soon: 1, 'long-term': 2 };
                return urgencyOrder[a.urgency] - urgencyOrder[b.urgency];
              })
              .map((care, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  {getUrgencyIcon(care.urgency)}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{care.category}</span>
                      <span className="text-xs text-gray-500">
                        ({getUrgencyText(care.urgency)})
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

      {/* 건강 분석 요약 */}
      {recommendations.health_analysis && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-purple-600" />
            건강 분석 요약
          </h4>
          <div className="space-y-4">
            {/* 주요 우려사항 */}
            {recommendations.health_analysis.main_concerns && recommendations.health_analysis.main_concerns.length > 0 && (
              <div>
                <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  주요 우려사항
                </h5>
                <div className="flex flex-wrap gap-2">
                  {recommendations.health_analysis.main_concerns.map((concern, index) => (
                    <span key={index} className="px-3 py-1 bg-red-50 text-red-700 rounded-full text-sm">
                      {concern}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* 강점 */}
            {recommendations.health_analysis.strengths && recommendations.health_analysis.strengths.length > 0 && (
              <div>
                <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  건강 강점
                </h5>
                <div className="flex flex-wrap gap-2">
                  {recommendations.health_analysis.strengths.map((strength, index) => (
                    <span key={index} className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm">
                      {strength}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* 개선 필요 영역 */}
            {recommendations.health_analysis.improvement_areas && recommendations.health_analysis.improvement_areas.length > 0 && (
              <div>
                <h5 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                  <Target className="h-4 w-4 text-blue-500" />
                  개선 필요 영역
                </h5>
                <div className="flex flex-wrap gap-2">
                  {recommendations.health_analysis.improvement_areas.map((area, index) => (
                    <span key={index} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">
                      {area}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 영양제 추천 */}
      {recommendations.supplement_recommendations && recommendations.supplement_recommendations.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Pill className="h-5 w-5 text-indigo-600" />
            맞춤 영양제 추천
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.supplement_recommendations.map((supplement, index) => (
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
                <div className="flex items-center gap-2 text-sm">
                  <span className="px-2 py-1 bg-gray-100 rounded">복용법: {supplement.dosage}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 식단 추천 */}
      {recommendations.diet_recommendations && recommendations.diet_recommendations.length > 0 && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Apple className="h-5 w-5 text-green-600" />
            맞춤 식단 추천
          </h4>
          <div className="space-y-4">
            {recommendations.diet_recommendations.map((diet, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium mb-2">
                      {diet.meal_type}
                    </span>
                    <h5 className="font-semibold">{diet.menu}</h5>
                  </div>
                  <span className="text-lg font-bold text-gray-900">{diet.calories}kcal</span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{diet.reason}</p>
                <div className="flex gap-4 text-sm">
                  <span className="flex items-center gap-1">
                    <span className="font-medium">단백질:</span> {diet.nutrients.protein}g
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="font-medium">탄수화물:</span> {diet.nutrients.carbs}g
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="font-medium">지방:</span> {diet.nutrients.fat}g
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 특별 프로모션 */}
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