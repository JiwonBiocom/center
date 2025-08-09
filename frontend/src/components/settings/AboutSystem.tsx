import React from 'react';
import { Info, Zap, AlertCircle, Rocket, Heart } from 'lucide-react';

const AboutSystem: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">시스템 소개</h2>
        <p className="mt-1 text-sm text-gray-500">
          AIBIO 센터 관리 시스템에 대한 안내
        </p>
      </div>

      {/* 소개 메시지 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start">
          <Info className="h-6 w-6 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="text-gray-700">
            <p className="mb-3">
              본 프로그램은 AIBIO 센터의 목표를 달성하고, 구성원들이 더 효율적으로 일할 수 있도록 개발되고 있습니다.
            </p>
            <p>
              현재는 고객관리대장과 예약 시스템을 옮겨놓는 것에서부터 시작하였으며, 앞으로는 차세대 AI 기반 헬스케어 CRM으로 발전시킬 예정입니다. 
              고객 생애주기 전반에 걸친 개인화된 경험 제공과 데이터 기반 의사결정을 목표로 합니다.
            </p>
          </div>
        </div>
      </div>

      {/* 현재 시스템 분석 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 강점 */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center mb-4">
            <Zap className="h-6 w-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">강점</h3>
          </div>
          <ul className="space-y-2">
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✅</span>
              <span className="text-sm text-gray-700">통합된 예약-서비스-결제 워크플로우</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✅</span>
              <span className="text-sm text-gray-700">실시간 대시보드 및 분석 기능</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✅</span>
              <span className="text-sm text-gray-700">패키지 관리 및 자동 차감 시스템</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✅</span>
              <span className="text-sm text-gray-700">알림문자 연동</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-500 mr-2">✅</span>
              <span className="text-sm text-gray-700">고급 필터링 및 검색 기능</span>
            </li>
          </ul>
        </div>

        {/* 개선 기회 */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="flex items-center mb-4">
            <Rocket className="h-6 w-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">개선 기회 (개발 예정)</h3>
          </div>
          <ul className="space-y-2">
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">🔄</span>
              <span className="text-sm text-gray-700">AI 기반 고객 행동 예측</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">🔄</span>
              <span className="text-sm text-gray-700">자동화된 마케팅 캠페인 기능</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">🔄</span>
              <span className="text-sm text-gray-700">고객 건강 데이터 통합 관리</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">🔄</span>
              <span className="text-sm text-gray-700">멀티채널 커뮤니케이션</span>
            </li>
            <li className="flex items-start">
              <span className="text-blue-500 mr-2">🔄</span>
              <span className="text-sm text-gray-700">고객 여정 맵핑 및 추적</span>
            </li>
          </ul>
        </div>
      </div>

      {/* 협조 요청 */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <div className="flex items-start">
          <AlertCircle className="h-6 w-6 text-amber-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="text-gray-700">
            <p className="mb-3 font-semibold">시스템 개선을 위한 협조 요청</p>
            <p className="mb-3">
              시스템을 업그레이드 하기 위해서는, 본 시스템에 보다 많은 정보들이 입력되어야 합니다. 
              고객 데이터, 예약 내역, 방문 내역, 문진 사항, 인바디 데이터 등 본 시스템의 다양한 메뉴를 최대한 이용 부탁 드립니다.
            </p>
            <p>
              개발 초기에는 오류들이 있을 수 있습니다. 사소한 것들이라도 발견되면 바로 전달해주세요. 
              또한 이런 기능들이 있으면 좋겠다, 하는 아이디어가 있으면 언제든 편하게 제시해주세요.
            </p>
          </div>
        </div>
      </div>

      {/* 마무리 인사 */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6 text-center">
        <Heart className="h-8 w-8 text-purple-600 mx-auto mb-3" />
        <p className="text-lg font-semibold text-gray-800 mb-2">
          모두의 성공과 행복을 기원합니다.
        </p>
        <p className="text-gray-600">
          - 바이오컴 운영진 -
        </p>
      </div>

      {/* 시스템 정보 */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">시스템 정보</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-gray-500">버전</p>
            <p className="font-medium">1.0.0</p>
          </div>
          <div>
            <p className="text-gray-500">개발 시작일</p>
            <p className="font-medium">2025년 6월 5일</p>
          </div>
          <div>
            <p className="text-gray-500">기술 스택</p>
            <p className="font-medium">React + FastAPI</p>
          </div>
          <div>
            <p className="text-gray-500">데이터베이스</p>
            <p className="font-medium">PostgreSQL</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutSystem;