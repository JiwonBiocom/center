import { useState, useEffect } from 'react';
import { api } from '../lib/api';

export function useReferralSources() {
  const [referralSources, setReferralSources] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReferralSources = async () => {
    try {
      setLoading(true);
      const response = await api.get('/customers/referral-sources');
      setReferralSources(response.data.referral_sources || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch referral sources:', err);
      setError('유입경로 목록을 가져오는데 실패했습니다.');
      // 기본값 사용
      setReferralSources(['당근', '유튜브', '검색', '지인소개', '인스타그램', '기타']);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReferralSources();
  }, []);

  return {
    referralSources,
    loading,
    error,
    refetch: fetchReferralSources
  };
}
