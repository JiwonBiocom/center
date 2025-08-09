import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

interface AdvancedFilters {
  membershipLevel?: string;
  customerStatus?: string;
  riskLevel?: string;
  regionFilter?: string;
  ageRange?: { min?: number; max?: number };
  totalRevenueRange?: { min?: number; max?: number };
  totalVisitsRange?: { min?: number; max?: number };
  lastVisitDateRange?: { from?: string; to?: string };
  firstVisitDateRange?: { from?: string; to?: string };
  referralSource?: string;
}

interface Customer {
  customer_id: number;
  name: string;
  phone: string;
  first_visit_date: string;
  region: string;
  referral_source: string;
  health_concerns?: string;
  notes?: string;
  assigned_staff?: string;
}

export function useCustomers(advancedFilters?: AdvancedFilters) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [totalCount, setTotalCount] = useState(0);
  const [allCustomersCount, setAllCustomersCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{
    status: 'idle' | 'uploading' | 'processing' | 'complete';
    message?: string;
    progress?: number;
  }>({ status: 'idle' });
  const [sortBy, setSortBy] = useState<string | null>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const pageSize = 20;

  const fetchCustomers = useCallback(async () => {
    try {
      const params: any = {
        ...(searchTerm ? { search: searchTerm } : {}),
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        ...(sortBy ? { sort_by: sortBy, sort_order: sortOrder } : {})
      };

      // 고급 필터 적용
      if (advancedFilters) {
        if (advancedFilters.membershipLevel) {
          params.membership_level = advancedFilters.membershipLevel;
        }
        if (advancedFilters.customerStatus) {
          params.customer_status = advancedFilters.customerStatus;
        }
        if (advancedFilters.riskLevel) {
          params.risk_level = advancedFilters.riskLevel;
        }
        if (advancedFilters.regionFilter) {
          params.region = advancedFilters.regionFilter;
        }
        if (advancedFilters.referralSource) {
          params.referral_source = advancedFilters.referralSource;
        }

        // 나이 범위
        if (advancedFilters.ageRange) {
          if (advancedFilters.ageRange.min !== undefined) {
            params.age_min = advancedFilters.ageRange.min;
          }
          if (advancedFilters.ageRange.max !== undefined) {
            params.age_max = advancedFilters.ageRange.max;
          }
        }

        // 매출 범위
        if (advancedFilters.totalRevenueRange) {
          if (advancedFilters.totalRevenueRange.min !== undefined) {
            params.revenue_min = advancedFilters.totalRevenueRange.min;
          }
          if (advancedFilters.totalRevenueRange.max !== undefined) {
            params.revenue_max = advancedFilters.totalRevenueRange.max;
          }
        }

        // 방문 횟수 범위
        if (advancedFilters.totalVisitsRange) {
          if (advancedFilters.totalVisitsRange.min !== undefined) {
            params.visits_min = advancedFilters.totalVisitsRange.min;
          }
          if (advancedFilters.totalVisitsRange.max !== undefined) {
            params.visits_max = advancedFilters.totalVisitsRange.max;
          }
        }

        // 첫 방문일 범위
        if (advancedFilters.firstVisitDateRange) {
          if (advancedFilters.firstVisitDateRange.from) {
            params.first_visit_from = advancedFilters.firstVisitDateRange.from;
          }
          if (advancedFilters.firstVisitDateRange.to) {
            params.first_visit_to = advancedFilters.firstVisitDateRange.to;
          }
        }

        // 마지막 방문일 범위
        if (advancedFilters.lastVisitDateRange) {
          if (advancedFilters.lastVisitDateRange.from) {
            params.last_visit_from = advancedFilters.lastVisitDateRange.from;
          }
          if (advancedFilters.lastVisitDateRange.to) {
            params.last_visit_to = advancedFilters.lastVisitDateRange.to;
          }
        }
      }

      const [customersResponse, countResponse, allCountResponse] = await Promise.all([
        api.get('/customers/', { params }),
        api.get('/customers/count', { params }),
        api.get('/customers/count') // 전체 고객 수 (필터 없음)
      ]);

      // 페이지네이션 응답 구조 처리
      if (customersResponse.data && customersResponse.data.data) {
        // 새로운 표준 응답 구조
        setCustomers(customersResponse.data.data);
        setTotalCount(customersResponse.data.total || countResponse.data.count);
      } else if (Array.isArray(customersResponse.data)) {
        // 기존 배열 응답 구조 (호환성)
        setCustomers(customersResponse.data);
        setTotalCount(countResponse.data.count);
      } else {
        console.error('Unexpected response structure:', customersResponse.data);
        setCustomers([]);
        setTotalCount(0);
      }

      // 전체 고객 수 설정
      setAllCustomersCount(allCountResponse.data.count);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoading(false);
    }
  }, [searchTerm, currentPage, advancedFilters, sortBy, sortOrder]);

  useEffect(() => {
    fetchCustomers();
  }, [fetchCustomers]);

  const handleDelete = async (customerId: number) => {
    if (!confirm('정말로 이 고객을 삭제하시겠습니까?')) return;

    try {
      await api.delete(`/api/v1/customers/${customerId}`);
      fetchCustomers();
    } catch (error) {
      console.error('Failed to delete customer:', error);
      alert('고객 삭제에 실패했습니다.');
    }
  };

  const handleExcelExport = async () => {
    try {
      const params: any = {
        ...(searchTerm ? { search: searchTerm } : {})
      };

      // 고급 필터 적용 (fetchCustomers와 동일하게)
      if (advancedFilters) {
        if (advancedFilters.membershipLevel) {
          params.membership_level = advancedFilters.membershipLevel;
        }
        if (advancedFilters.customerStatus) {
          params.customer_status = advancedFilters.customerStatus;
        }
        if (advancedFilters.riskLevel) {
          params.risk_level = advancedFilters.riskLevel;
        }
        if (advancedFilters.regionFilter) {
          params.region = advancedFilters.regionFilter;
        }
        if (advancedFilters.referralSource) {
          params.referral_source = advancedFilters.referralSource;
        }

        // 나이 범위
        if (advancedFilters.ageRange) {
          if (advancedFilters.ageRange.min !== undefined) {
            params.age_min = advancedFilters.ageRange.min;
          }
          if (advancedFilters.ageRange.max !== undefined) {
            params.age_max = advancedFilters.ageRange.max;
          }
        }

        // 매출 범위
        if (advancedFilters.totalRevenueRange) {
          if (advancedFilters.totalRevenueRange.min !== undefined) {
            params.revenue_min = advancedFilters.totalRevenueRange.min;
          }
          if (advancedFilters.totalRevenueRange.max !== undefined) {
            params.revenue_max = advancedFilters.totalRevenueRange.max;
          }
        }

        // 방문 횟수 범위
        if (advancedFilters.totalVisitsRange) {
          if (advancedFilters.totalVisitsRange.min !== undefined) {
            params.visits_min = advancedFilters.totalVisitsRange.min;
          }
          if (advancedFilters.totalVisitsRange.max !== undefined) {
            params.visits_max = advancedFilters.totalVisitsRange.max;
          }
        }

        // 첫 방문일 범위
        if (advancedFilters.firstVisitDateRange) {
          if (advancedFilters.firstVisitDateRange.from) {
            params.first_visit_from = advancedFilters.firstVisitDateRange.from;
          }
          if (advancedFilters.firstVisitDateRange.to) {
            params.first_visit_to = advancedFilters.firstVisitDateRange.to;
          }
        }

        // 마지막 방문일 범위
        if (advancedFilters.lastVisitDateRange) {
          if (advancedFilters.lastVisitDateRange.from) {
            params.last_visit_from = advancedFilters.lastVisitDateRange.from;
          }
          if (advancedFilters.lastVisitDateRange.to) {
            params.last_visit_to = advancedFilters.lastVisitDateRange.to;
          }
        }
      }

      const response = await api.get('/customers/export/excel', {
        params,
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `customers_${new Date().toISOString().slice(0, 10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export customers:', error);
      alert('엑셀 내보내기에 실패했습니다.');
    }
  };

  const handleExcelImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadProgress({
      status: 'uploading',
      message: '파일 읽는 중... (1/3)',
      progress: 0
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
      // 파일 크기 확인
      const fileSizeMB = file.size / (1024 * 1024);
      if (fileSizeMB > 10) {
        throw new Error('파일 크기가 10MB를 초과합니다.');
      }

      // 대략적인 처리 시간 예상
      const estimatedRows = fileSizeMB * 1000; // 대략적인 추정
      const estimatedTime = Math.ceil(estimatedRows / 100); // 초 단위

      setUploadProgress({
        status: 'processing',
        message: `고객 정보 검증 중... (2/3) 예상 시간: ${estimatedTime}초`,
        progress: 50
      });

      const response = await api.post('/api/v1/customers/import/excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(prev => ({
              ...prev,
              progress: Math.min(percentCompleted * 0.5, 50) // 업로드는 전체의 50%까지
            }));
          }
        }
      });

      // 서버 응답 후 데이터베이스 저장 중 표시
      setUploadProgress({
        status: 'processing',
        message: '데이터베이스 저장 중... (3/3)',
        progress: 90
      });

      // 잠시 후 완료 표시
      setTimeout(() => {
        setUploadProgress({
          status: 'complete',
          message: '✅ 업로드 완료!',
          progress: 100
        });
      }, 500);

      const result = response.data;
      let message = `가져오기 완료!\n성공: ${result.success_count}건`;

      if (result.error_count > 0) {
        message += `\n실패: ${result.error_count}건`;
        if (result.errors.length > 0) {
          message += '\n\n오류 내역:';
          result.errors.forEach((error: string) => {
            message += `\n- ${error}`;
          });
        }
      }

      // 첫방문일 관련 특별 안내
      if (result.first_visit_date_issues) {
        message += '\n\n⚠️ 첫방문일 입력 관련:';
        message += '\n지원되는 날짜 형식: YYYY-MM-DD, YYYY/MM/DD, DD/MM/YYYY 등';
        message += '\n엑셀에서 날짜 형식으로 설정되어 있는지 확인해주세요.';
      }

      if (result.warnings && result.warnings.length > 0) {
        message += '\n\n경고:';
        result.warnings.forEach((warning: string) => {
          message += `\n- ${warning}`;
        });
      }

      alert(message);
      fetchCustomers();
    } catch (error: any) {
      console.error('Failed to import customers:', error);
      setUploadProgress({
        status: 'idle',
        message: '오류 발생'
      });
      alert(error.response?.data?.detail || error.message || '엑셀 가져오기에 실패했습니다.');
    } finally {
      setUploading(false);
      setUploadProgress({ status: 'idle' });
      // Reset file input
      event.target.value = '';
    }
  };

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
    setCurrentPage(1);
  };

  return {
    customers,
    loading,
    searchTerm,
    totalCount,
    allCustomersCount,
    currentPage,
    uploading,
    uploadProgress,
    pageSize,
    sortBy,
    sortOrder,
    fetchCustomers,
    handleDelete,
    handleExcelExport,
    handleExcelImport,
    handleSearchChange,
    handlePageChange,
    handleSort
  };
}

export type { AdvancedFilters };
