import { useState, useEffect } from 'react';
import api from '../lib/api';

interface ServiceType {
  service_type_id: number;
  name: string;
  code: string;
  description: string;
  default_duration: number;
  default_price: string;
  equipment_required?: Record<string, any>;
  protocols?: Record<string, any>;
  intensity_levels?: Record<string, any>;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

interface ServiceSession {
  id: number;
  customer_name: string;
  service_type_name: string;
  status: 'in_progress' | 'completed' | 'cancelled';
  start_time: string;
  expected_end_time: string;
  actual_end_time?: string;
  equipment_settings: Record<string, any>;
}

interface DailyStats {
  total_sessions_today: number;
  active_sessions: number;
  total_revenue_today: number;
  equipment_utilization: number;
}

interface UseEnhancedServicesReturn {
  serviceTypes: ServiceType[];
  activeSessions: ServiceSession[];
  stats: DailyStats;
  loading: boolean;
  error: string | null;
  refreshData: () => Promise<void>;
}

export const useEnhancedServices = (autoRefresh = true): UseEnhancedServicesReturn => {
  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([]);
  const [activeSessions, setActiveSessions] = useState<ServiceSession[]>([]);
  const [stats, setStats] = useState<DailyStats>({
    total_sessions_today: 0,
    active_sessions: 0,
    total_revenue_today: 0,
    equipment_utilization: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 각 API를 개별적으로 호출하여 일부 실패해도 다른 데이터는 표시
      try {
        const typesRes = await api.get('/test-enhanced/service-types');
        if (typesRes.data?.service_types) {
          setServiceTypes(typesRes.data.service_types);
        }
      } catch (err) {
        console.warn('Failed to fetch service types:', err);
      }

      try {
        const sessionsRes = await api.get('/test-enhanced/sessions/active');
        setActiveSessions(Array.isArray(sessionsRes.data) ? sessionsRes.data : []);
      } catch (err) {
        console.warn('Failed to fetch active sessions:', err);
        setActiveSessions([]);
      }

      try {
        const statsRes = await api.get('/test-enhanced/stats/today');
        setStats(statsRes.data);
      } catch (err) {
        console.warn('Failed to fetch stats:', err);
        // 기본값 유지
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch enhanced services data');
      console.error('Enhanced services fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();

    if (autoRefresh) {
      const interval = setInterval(refreshData, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  return {
    serviceTypes,
    activeSessions,
    stats,
    loading,
    error,
    refreshData
  };
};

// Hook for managing service sessions
export const useServiceSessions = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startSession = async (_sessionData: {
    customer_id: number;
    service_type_id: number;
    session_date: string;
    start_time: string;
    equipment_settings?: Record<string, any>;
    session_notes?: string;
  }) => {
    try {
      setLoading(true);
      setError(null);

      // 테스트용 엔드포인트로 일단 시뮬레이션
      // 실제로는 백엔드에 세션 생성 API를 호출해야 함
      await new Promise(resolve => setTimeout(resolve, 1000)); // 시뮬레이션
      
      return { success: true, session_id: Date.now() };
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to start session');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const endSession = async (sessionId: number) => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.post(`/enhanced/sessions/${sessionId}/end`);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to end session');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    startSession,
    endSession,
    loading,
    error
  };
};

// Hook for service type management
export const useServiceTypes = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createServiceType = async (serviceTypeData: any) => {
    try {
      setLoading(true);
      setError(null);

      // 시뮬레이션: 실제로는 API 호출 필요
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Creating service type:', serviceTypeData);
      
      return { success: true, service_type_id: Date.now() };
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create service type');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateServiceType = async (id: number, serviceTypeData: any) => {
    try {
      setLoading(true);
      setError(null);

      // 시뮬레이션: 실제로는 API 호출 필요
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Updating service type:', id, serviceTypeData);
      
      return { success: true };
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update service type');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    createServiceType,
    updateServiceType,
    loading,
    error
  };
};