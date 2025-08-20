import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

interface PackageType {
  package_id: number;
  package_name: string;
  total_sessions: number;
  price: number;
  valid_days: number;
  is_active: boolean;
  description?: string;
  created_at?: string;
}

export function usePackages() {
  const [packages, setPackages] = useState<PackageType[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInactive, setShowInactive] = useState(false);

  const fetchPackages = useCallback(async () => {
    try {
      const params: any = {};
      // showInactive가 true면 모든 패키지를 보여줘야 하므로 is_active 파라미터를 보내지 않음
      // showInactive가 false면 활성 패키지만 보여줘야 하므로 is_active=true
      if (!showInactive) {
        params.is_active = true;
      }
      
      const response = await api.get('/packages/', { params });
      setPackages(response.data);
    } catch (error) {
      console.error('Failed to fetch packages:', error);
    } finally {
      setLoading(false);
    }
  }, [showInactive]);

  useEffect(() => {
    fetchPackages();
  }, [fetchPackages]);

  const handleToggleActive = async (packageId: number) => {
    if (!window.confirm('정말로 이 패키지를 비활성화하시겠습니까?')) return;
    
    try {
      await api.delete(`/packages/${packageId}`);
      fetchPackages();
    } catch (error) {
      console.error('Failed to toggle package:', error);
      alert('패키지 상태 변경에 실패했습니다.');
    }
  };

  return {
    packages,
    loading,
    showInactive,
    setShowInactive,
    fetchPackages,
    handleToggleActive
  };
}
