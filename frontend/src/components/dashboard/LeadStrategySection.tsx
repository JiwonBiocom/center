import React, { useState } from 'react';
import { Target, Megaphone, Users, Video, Gift, Brain, Cpu, BarChart, Globe } from 'lucide-react';

const LeadStrategySection: React.FC = () => {
  const [strategies, setStrategies] = useState([
    {
      id: 1,
      title: '당근마켓 광고 소재 최적화',
      icon: Target,
      description: '지역 기반 타겟팅과 매력적인 소재로 전환율 향상',
      status: 'planning', // planning, in_progress, completed
      priority: 'high'
    },
    {
      id: 2,
      title: '페이스북 상세페이지 개선',
      icon: Megaphone,
      description: '사용자 경험 개선과 전환 최적화',
      status: 'planning',
      priority: 'high'
    },
    {
      id: 3,
      title: '바이오해킹 웨비나 진행',
      icon: Video,
      description: '전문성 어필과 신뢰도 구축을 통한 리드 확보',
      status: 'planning',
      priority: 'medium'
    },
    {
      id: 4,
      title: '기존 고객 추천 프로그램',
      icon: Gift,
      description: '만족 고객을 통한 자연스러운 신규 고객 유입',
      status: 'planning',
      priority: 'medium'
    }
  ]);

  const [developmentPrograms, setDevelopmentPrograms] = useState([
    {
      id: 5,
      title: 'AI 기반 세션 추천 프로그램',
      icon: Brain,
      description: '개인별 데이터 분석을 통한 맞춤형 세션 추천',
      status: 'planning',
      priority: 'high'
    },
    {
      id: 6,
      title: 'AI 기반 식단, 영양 추천 알고리즘',
      icon: Cpu,
      description: '건강 데이터 기반 개인화된 식단 및 영양 가이드',
      status: 'planning',
      priority: 'high'
    },
    {
      id: 7,
      title: 'AI 고객 데이터 예측 프로그램',
      icon: BarChart,
      description: '고객 패턴 분석 및 예측을 통한 서비스 최적화',
      status: 'planning',
      priority: 'medium'
    },
    {
      id: 8,
      title: '통합 바이오해킹 플랫폼',
      icon: Globe,
      description: '모든 바이오해킹 서비스를 통합한 원스톱 플랫폼',
      status: 'planning',
      priority: 'medium'
    }
  ]);

  const updateStatus = (id: number, isStrategy: boolean) => {
    const currentList = isStrategy ? strategies : developmentPrograms;
    const setList = isStrategy ? setStrategies : setDevelopmentPrograms;
    
    setList(currentList.map(item => {
      if (item.id === id) {
        let newStatus = item.status;
        switch (item.status) {
          case 'planning':
            newStatus = 'in_progress';
            break;
          case 'in_progress':
            newStatus = 'completed';
            break;
          case 'completed':
            newStatus = 'planning';
            break;
        }
        return { ...item, status: newStatus };
      }
      return item;
    }));
  };

  const getStatusBadge = (status: string, id: number, isStrategy: boolean) => {
    const handleClick = () => updateStatus(id, isStrategy);
    
    switch (status) {
      case 'planning':
        return (
          <button 
            onClick={handleClick}
            className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full hover:bg-gray-200 cursor-pointer transition-colors"
          >
            계획중
          </button>
        );
      case 'in_progress':
        return (
          <button 
            onClick={handleClick}
            className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full hover:bg-blue-200 cursor-pointer transition-colors"
          >
            진행중
          </button>
        );
      case 'completed':
        return (
          <button 
            onClick={handleClick}
            className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full hover:bg-green-200 cursor-pointer transition-colors"
          >
            완료
          </button>
        );
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full">미정</span>;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-l-red-500';
      case 'medium':
        return 'border-l-yellow-500';
      case 'low':
        return 'border-l-green-500';
      default:
        return 'border-l-gray-500';
    }
  };

  const getAllItems = () => [...strategies, ...developmentPrograms];
  const getCompletedCount = () => getAllItems().filter(item => item.status === 'completed').length;
  const getTotalCount = () => getAllItems().length;
  const getHighPriorityCount = () => getAllItems().filter(item => item.priority === 'high').length;
  const getProgressPercentage = () => Math.round((getCompletedCount() / getTotalCount()) * 100);

  const renderStrategyCard = (item: any, isStrategy: boolean) => {
    const IconComponent = item.icon;
    return (
      <div
        key={item.id}
        className={`p-4 bg-gray-50 rounded-lg border-l-4 ${getPriorityColor(item.priority)} hover:bg-gray-100 transition-colors`}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-white rounded-lg">
              <IconComponent className="h-5 w-5 text-indigo-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-medium text-gray-900 text-sm">
                {item.title}
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                {item.description}
              </p>
            </div>
          </div>
          <div className="ml-2">
            {getStatusBadge(item.status, item.id, isStrategy)}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <Users className="h-6 w-6 text-indigo-500" />
          추진할 유입 전략
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          신규 고객 유입을 위한 마케팅 전략 로드맵
        </p>
      </div>
      
      <div className="p-6">
        {/* 마케팅 전략 */}
        <div className="mb-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">마케팅 전략</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {strategies.map((strategy) => renderStrategyCard(strategy, true))}
          </div>
        </div>

        {/* 개발 예정 프로그램 */}
        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">개발 예정 프로그램</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {developmentPrograms.map((program) => renderStrategyCard(program, false))}
          </div>
        </div>
        
        {/* 전체 진행 상황 요약 */}
        <div className="mt-6 p-4 bg-indigo-50 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <div className="text-indigo-700">
              <span className="font-medium">전체 진행률:</span> {getCompletedCount()}/{getTotalCount()} 완료
            </div>
            <div className="text-indigo-600">
              <span className="font-medium">우선순위 높음:</span> {getHighPriorityCount()}개 항목
            </div>
          </div>
          <div className="mt-2 w-full bg-indigo-200 rounded-full h-2">
            <div className="bg-indigo-600 h-2 rounded-full transition-all duration-300" style={{ width: `${getProgressPercentage()}%` }}></div>
          </div>
          <div className="mt-1 text-xs text-indigo-600 text-right">
            {getProgressPercentage()}% 완료
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeadStrategySection;