import { useState, useEffect } from 'react';
import { Plus, Calendar, Table } from 'lucide-react';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { api } from '../lib/api';
import type { Reservation, ServiceType } from '../types';
import { useIsMobile } from '../hooks/useMediaQuery';
import MobileReservations from '../components/mobile/MobileReservations';
import ReservationModal from '../components/ReservationModal';
import ReservationCalendar from '../components/reservation/ReservationCalendar';
import DailyReservationList from '../components/reservation/DailyReservationList';
import ReservationTableView from '../components/reservation/ReservationTableView';
import ReservationFilters from '../components/reservation/ReservationFilters';


export default function Reservations() {
  const isMobile = useIsMobile();
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [serviceTypes, setServiceTypes] = useState<ServiceType[]>([]);
  const [customers, setCustomers] = useState<Array<{
    customer_id: number;
    name: string;
    phone: string | null;
    [key: string]: any;
  }>>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showModal, setShowModal] = useState(false);
  const [selectedReservation, setSelectedReservation] = useState<Reservation | null>(null);
  const [viewMode, setViewMode] = useState<'calendar' | 'table'>('calendar');

  useEffect(() => {
    fetchReservations();
    fetchServiceTypes();
    fetchCustomers();
  }, [currentMonth, statusFilter]);

  const fetchReservations = async () => {
    try {
      const startDate = format(startOfMonth(currentMonth), 'yyyy-MM-dd');
      const endDate = format(endOfMonth(currentMonth), 'yyyy-MM-dd');
      
      const params: any = {
        start_date: startDate,
        end_date: endDate
      };
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      const response = await api.get('/api/v1/reservations/', { params });
      setReservations(response.data);
    } catch (error) {
      console.error('Failed to fetch reservations:', error);
    }
  };

  const fetchServiceTypes = async () => {
    try {
      const response = await api.get('/api/v1/services/types');
      setServiceTypes(response.data);
    } catch (error) {
      console.error('Failed to fetch service types:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/api/v1/customers/', { params: { limit: 1000 } });
      // 디버깅 로그 제거
      
      // 페이지네이션 응답 구조 처리
      if (response.data && typeof response.data === 'object' && 'data' in response.data && Array.isArray(response.data.data)) {
        // Using paginated data
        setCustomers(response.data.data);
      } else if (Array.isArray(response.data)) {
        // Using array data
        setCustomers(response.data);
      } else {
        console.error('Unexpected customers response structure:', response.data);
        setCustomers([]);
      }
    } catch (error) {
      console.error('Failed to fetch customers:', error);
      setCustomers([]);
    }
  };

  const handleTodayClick = () => {
    setCurrentMonth(new Date());
    setSelectedDate(new Date());
  };

  const handleAddReservation = () => {
    setSelectedReservation(null);
    setShowModal(true);
  };

  const handleEditReservation = (reservation: Reservation) => {
    setSelectedReservation(reservation);
    setShowModal(true);
  };

  const filteredReservations = reservations.filter(reservation => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      reservation.customer_name.toLowerCase().includes(searchLower) ||
      reservation.customer_phone.includes(searchTerm) ||
      reservation.service_name.toLowerCase().includes(searchLower)
    );
  });

  const selectedDateReservations = filteredReservations.filter(r => 
    r.reservation_date === format(selectedDate, 'yyyy-MM-dd')
  );

  // 모바일 화면 비활성화
  // if (isMobile) {
  //   return <MobileReservations />;
  // }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">예약 관리</h1>
        <div className="flex items-center space-x-4">
          {/* 뷰 모드 토글 */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('calendar')}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'calendar'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Calendar className="h-4 w-4 mr-2" />
              캘린더
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                viewMode === 'table'
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Table className="h-4 w-4 mr-2" />
              표 형태
            </button>
          </div>
          <button
            onClick={handleAddReservation}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Plus className="h-4 w-4 mr-2" />
            새 예약
          </button>
        </div>
      </div>

      {viewMode === 'calendar' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 캘린더 */}
          <div className="lg:col-span-2">
            <ReservationCalendar
              currentMonth={currentMonth}
              selectedDate={selectedDate}
              reservations={filteredReservations}
              serviceTypes={serviceTypes}
              onMonthChange={setCurrentMonth}
              onDateSelect={setSelectedDate}
              onTodayClick={handleTodayClick}
            />
          </div>

          {/* 선택된 날짜의 예약 목록 */}
          <DailyReservationList
            selectedDate={selectedDate}
            reservations={selectedDateReservations}
            serviceTypes={serviceTypes}
            onReservationClick={handleEditReservation}
          />
        </div>
      ) : (
        /* 테이블 뷰 */
        <ReservationTableView
          reservations={selectedDateReservations}
          selectedDate={selectedDate}
          onReservationClick={handleEditReservation}
        />
      )}

      {/* 필터 및 검색 */}
      <ReservationFilters
        searchTerm={searchTerm}
        statusFilter={statusFilter}
        onSearchChange={setSearchTerm}
        onStatusChange={setStatusFilter}
      />

      {/* 예약 모달 */}
      <ReservationModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        reservation={selectedReservation}
        selectedDate={selectedDate}
        customers={customers}
        onSave={fetchReservations}
      />
    </div>
  );
}