import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';

interface ServiceUsage {
  usage_id: number;
  customer_id: number;
  customer_name: string;
  service_date: string;
  service_type_id: number;
  service_name: string;
  package_id?: number;
  session_details?: string;
  session_number?: number;
  created_by: string;
  created_at: string;
}

interface CalendarData {
  [date: string]: {
    total_services: number;
    unique_customers: number;
    services: {
      [serviceName: string]: number;
    };
  };
}

export function useServiceData() {
  const [usages, setUsages] = useState<ServiceUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [calendarData, setCalendarData] = useState<CalendarData>({});
  
  const today = new Date();
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(today.getMonth() + 1);

  const fetchUsages = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/services/usage', {
        params: {
          date_from: selectedDate,
          date_to: selectedDate
        }
      });
      setUsages(response.data);
    } catch (error) {
      console.error('Failed to fetch service usage:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  const fetchCalendarData = useCallback(async () => {
    try {
      const response = await api.get('/api/v1/services/calendar', {
        params: {
          year: currentYear,
          month: currentMonth
        }
      });
      setCalendarData(response.data);
    } catch (error) {
      console.error('Failed to fetch calendar data:', error);
    }
  }, [currentYear, currentMonth]);

  useEffect(() => {
    fetchUsages();
    fetchCalendarData();
  }, [fetchUsages, fetchCalendarData]);

  const handleExcelExport = async () => {
    try {
      const params: any = {};
      if (selectedDate) {
        params.date_from = selectedDate;
        params.date_to = selectedDate;
      }
      
      const response = await api.get('/api/v1/services/usage/export/excel', {
        params,
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `service_usage_${new Date().toISOString().slice(0, 10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export service usage:', error);
      alert('엑셀 내보내기에 실패했습니다.');
    }
  };

  const handleMonthChange = (year: number, month: number) => {
    setCurrentYear(year);
    setCurrentMonth(month);
  };

  return {
    usages,
    loading,
    selectedDate,
    calendarData,
    currentYear,
    currentMonth,
    setSelectedDate,
    handleMonthChange,
    handleExcelExport,
    fetchUsages,
    fetchCalendarData
  };
}