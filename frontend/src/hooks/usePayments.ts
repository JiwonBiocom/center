import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

interface Payment {
  payment_id: number;
  payment_number?: string;
  customer_id: number;
  customer_name: string;
  customer_phone: string;
  payment_date: string;
  amount: number;
  payment_method: string;
  payment_type?: string;
  payment_status?: string;
  card_holder_name?: string;
  approval_number?: string;
  payment_staff?: string;
  purchase_type?: string;
  purchase_order?: number;
  notes?: string;
  created_at: string;
}

interface PaymentSummary {
  total_count: number;
  total_revenue: number;
  current_month_revenue?: number;
  customer_count: number;
  average_amount: number;
  previous_month?: string;
  current_month?: string;
}

export function usePayments() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [summary, setSummary] = useState<PaymentSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const itemsPerPage = 20;

  const fetchPayments = useCallback(async (page: number = 1) => {
    try {
      const params: any = {
        limit: itemsPerPage,
        skip: (page - 1) * itemsPerPage
      };
      if (searchTerm) params.search = searchTerm;
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      if (paymentMethod) params.payment_method = paymentMethod;
      if (paymentStatus) params.payment_status = paymentStatus;

      const response = await api.get('/payments/', { params });

      if (page === 1) {
        setPayments(response.data);
      } else {
        setPayments(prev => [...prev, ...response.data]);
      }

      setHasMore(response.data.length === itemsPerPage);
      setCurrentPage(page);
    } catch (error) {
      console.error('Failed to fetch payments:', error);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, dateFrom, dateTo, paymentMethod, paymentStatus]);

  const fetchSummary = useCallback(async () => {
    try {
      const params: any = {};
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;

      const response = await api.get('/payments/stats/summary', { params });
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    }
  }, [dateFrom, dateTo]);

  useEffect(() => {
    setCurrentPage(1);
    fetchPayments(1);
    fetchSummary();
  }, [fetchPayments, fetchSummary]);

  const handleDelete = async (paymentId: number) => {
    if (!window.confirm('정말로 이 결제를 취소하시겠습니까?')) return;

    try {
      await api.delete(`/payments/${paymentId}`);
      fetchPayments(1);
      fetchSummary();
    } catch (error) {
      console.error('Failed to delete payment:', error);
      alert('결제 취소에 실패했습니다.');
    }
  };

  const handleExcelExport = async () => {
    try {
      const params: any = {};
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      if (paymentMethod) params.payment_method = paymentMethod;

      const response = await api.get('/payments/export/excel', {
        params,
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payments_${new Date().toISOString().slice(0, 10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export payments:', error);
      alert('엑셀 내보내기에 실패했습니다.');
    }
  };

  const filteredPayments = payments.filter(payment => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      payment.customer_name.toLowerCase().includes(search) ||
      payment.customer_phone?.includes(search) ||
      payment.approval_number?.toLowerCase().includes(search) ||
      payment.payment_number?.toLowerCase().includes(search)
    );
  });

  const loadMore = () => {
    if (hasMore && !loading) {
      fetchPayments(currentPage + 1);
    }
  };

  return {
    payments: filteredPayments,
    summary,
    loading,
    searchTerm,
    dateFrom,
    dateTo,
    paymentMethod,
    paymentStatus,
    setSearchTerm,
    setDateFrom,
    setDateTo,
    setPaymentMethod,
    setPaymentStatus,
    fetchPayments,
    fetchSummary,
    handleDelete,
    handleExcelExport,
    loadMore,
    hasMore
  };
}
