import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import type { Reservation } from '../types';

export function useReservations() {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReservations = async (params?: {
    start_date?: string;
    end_date?: string;
    status?: string;
    customer_id?: number;
  }) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/reservations', { params });
      
      if (response.data.success && response.data.data) {
        // 페이지네이션된 응답 처리
        if (Array.isArray(response.data.data)) {
          setReservations(response.data.data);
        } else if (response.data.data.data && Array.isArray(response.data.data.data)) {
          setReservations(response.data.data.data);
        } else {
          setReservations([]);
        }
      } else {
        setReservations([]);
      }
    } catch (err) {
      console.error('예약 조회 실패:', err);
      setError('예약 정보를 불러오는데 실패했습니다.');
      setReservations([]);
    } finally {
      setLoading(false);
    }
  };

  const createReservation = async (data: any) => {
    try {
      const response = await api.post('/reservations', data);
      if (response.data.success) {
        await fetchReservations();
        return response.data.data;
      }
    } catch (err) {
      console.error('예약 생성 실패:', err);
      throw err;
    }
  };

  const updateReservation = async (id: number, data: any) => {
    try {
      const response = await api.put(`/reservations/${id}`, data);
      if (response.data.success) {
        await fetchReservations();
        return response.data.data;
      }
    } catch (err) {
      console.error('예약 수정 실패:', err);
      throw err;
    }
  };

  const deleteReservation = async (id: number) => {
    try {
      const response = await api.delete(`/reservations/${id}`);
      if (response.data.success) {
        await fetchReservations();
      }
    } catch (err) {
      console.error('예약 삭제 실패:', err);
      throw err;
    }
  };

  useEffect(() => {
    fetchReservations();
  }, []);

  return {
    reservations,
    loading,
    error,
    fetchReservations,
    createReservation,
    updateReservation,
    deleteReservation
  };
}