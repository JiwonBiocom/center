import React, { useState } from 'react';
import { Plus, Activity, Clock, Users, Settings, BarChart3, RefreshCw } from 'lucide-react';
import { useEnhancedServices, useServiceSessions } from '../hooks/useEnhancedServices';
import SessionStartModal from '../components/enhanced-services/SessionStartModal';
import ServiceTypeModal from '../components/enhanced-services/ServiceTypeModal';

const EnhancedServices: React.FC = () => {
  const { 
    serviceTypes, 
    activeSessions, 
    stats, 
    loading, 
    error, 
    refreshData 
  } = useEnhancedServices();
  
  const { endSession, loading: sessionLoading } = useServiceSessions();
  const [activeTab, setActiveTab] = useState<'dashboard' | 'sessions' | 'types'>('dashboard');
  const [showSessionModal, setShowSessionModal] = useState(false);
  const [showServiceTypeModal, setShowServiceTypeModal] = useState(false);

  const handleRefresh = async () => {
    await refreshData();
  };

  const handleEndSession = async (sessionId: number) => {
    try {
      await endSession(sessionId);
      await refreshData(); // Refresh data after ending session
    } catch (error) {
      console.error('Failed to end session:', error);
    }
  };

  const handleSessionStart = () => {
    setShowSessionModal(false);
    refreshData(); // Refresh data after starting session
  };

  const handleServiceTypeUpdate = () => {
    setShowServiceTypeModal(false);
    refreshData(); // Refresh data after updating service types
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress': return 'text-green-600 bg-green-100';
      case 'completed': return 'text-blue-600 bg-blue-100';
      case 'cancelled': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const StatsCard = ({ title, value, icon: Icon, color }: {
    title: string;
    value: string | number;
    icon: any;
    color: string;
  }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-md ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <p className="text-red-600 mb-4">데이터를 불러오는 중 오류가 발생했습니다.</p>
          <button 
            onClick={handleRefresh}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">확장 서비스 관리</h1>
            <p className="text-gray-600">실시간 세션 모니터링 및 서비스 관리</p>
          </div>
          <div className="flex space-x-3">
            <button 
              onClick={handleRefresh}
              disabled={loading}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 flex items-center disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              새로고침
            </button>
            <button 
              onClick={() => setShowSessionModal(true)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 flex items-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              새 세션 시작
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'dashboard', name: '대시보드', icon: BarChart3 },
              { id: 'sessions', name: '활성 세션', icon: Activity },
              { id: 'types', name: '서비스 타입', icon: Settings }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-4 w-4 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatsCard
                title="오늘 총 세션"
                value={stats.total_sessions_today}
                icon={Activity}
                color="bg-blue-500"
              />
              <StatsCard
                title="현재 활성 세션"
                value={stats.active_sessions}
                icon={Users}
                color="bg-green-500"
              />
              <StatsCard
                title="오늘 매출"
                value={`₩${stats.total_revenue_today.toLocaleString()}`}
                icon={BarChart3}
                color="bg-purple-500"
              />
              <StatsCard
                title="장비 사용률"
                value={`${stats.equipment_utilization}%`}
                icon={Settings}
                color="bg-orange-500"
              />
            </div>

            {/* Active Sessions Overview */}
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">현재 진행 중인 세션</h3>
              </div>
              <div className="p-6">
                {activeSessions.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">현재 진행 중인 세션이 없습니다.</p>
                ) : (
                  <div className="space-y-4">
                    {activeSessions.slice(0, 5).map((session, index) => (
                      <div key={`dashboard-session-${session.id || index}`} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="flex-shrink-0">
                            <div className="h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center">
                              <Activity className="h-5 w-5 text-indigo-600" />
                            </div>
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{session.customer_name}</p>
                            <p className="text-sm text-gray-500">{session.service_type_name}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(session.status)}`}>
                            진행중
                          </span>
                          <div className="text-right">
                            <p className="text-sm text-gray-900">{formatTime(session.start_time)} ~</p>
                            <p className="text-sm text-gray-500">{formatTime(session.expected_end_time)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Active Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">활성 세션 관리</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      고객명
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      서비스
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      시작 시간
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      예상 종료
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      상태
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      액션
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {activeSessions.map((session, index) => (
                    <tr key={`active-session-${session.id || index}`}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {session.customer_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {session.service_type_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatTime(session.start_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatTime(session.expected_end_time)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(session.status)}`}>
                          {session.status === 'in_progress' ? '진행중' : session.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                          onClick={() => handleEndSession(session.id)}
                          disabled={sessionLoading}
                          className="text-indigo-600 hover:text-indigo-900 mr-4 disabled:opacity-50"
                        >
                          세션 종료
                        </button>
                        <button className="text-gray-600 hover:text-gray-900">
                          상세보기
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Service Types Tab */}
        {activeTab === 'types' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">서비스 타입 관리</h3>
              <button className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 text-sm">
                새 서비스 타입 추가
              </button>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {serviceTypes.map((type, index) => (
                  <div key={`service-type-${type.service_type_id || index}`} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-lg font-medium text-gray-900">{type.name}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        type.is_active ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
                      }`}>
                        {type.is_active ? '활성' : '비활성'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{type.description}</p>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{type.default_duration || 30}분</span>
                      </div>
                      <div className="flex items-center">
                        <Users className="h-4 w-4 text-gray-400 mr-2" />
                        <span>기본 가격: {Number(type.default_price).toLocaleString()}원</span>
                      </div>
                      <div className="flex items-center">
                        <Settings className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{type.code}</span>
                      </div>
                    </div>
                    <div className="mt-4 flex space-x-2">
                      <button 
                        onClick={() => setShowServiceTypeModal(true)}
                        className="flex-1 bg-indigo-600 text-white px-3 py-2 rounded text-sm hover:bg-indigo-700"
                      >
                        관리
                      </button>
                      <button className="flex-1 bg-gray-200 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-300">
                        설정
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Session Start Modal */}
      <SessionStartModal
        isOpen={showSessionModal}
        onClose={() => setShowSessionModal(false)}
        onSuccess={handleSessionStart}
        serviceTypes={serviceTypes}
      />

      {/* Service Type Management Modal */}
      <ServiceTypeModal
        isOpen={showServiceTypeModal}
        onClose={() => setShowServiceTypeModal(false)}
        onSuccess={handleServiceTypeUpdate}
        serviceTypes={serviceTypes}
      />
    </>
  );
};

export default EnhancedServices;