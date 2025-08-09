import { useState } from 'react';
import { Calendar, Clock, Phone, ChevronRight } from 'lucide-react';
import { useReservations } from '../../hooks/useReservations';
import { formatPhoneNumber } from '../../lib/utils/format';

interface ReservationItemProps {
  reservation: any;
  onTap: () => void;
}

function ReservationItem({ reservation, onTap }: ReservationItemProps) {
  const statusColors = {
    confirmed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    cancelled: 'bg-red-100 text-red-800',
    completed: 'bg-gray-100 text-gray-600',
  };

  const statusLabels = {
    confirmed: '확정',
    pending: '대기',
    cancelled: '취소',
    completed: '완료',
  };

  return (
    <div 
      onClick={onTap}
      className="bg-white rounded-lg shadow-sm p-4 mb-3 active:bg-gray-50 transition-colors"
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-semibold text-lg">{reservation.customer_name}</span>
            <span className={`text-xs px-2 py-1 rounded-full ${statusColors[reservation.status] || 'bg-gray-100 text-gray-600'}`}>
              {statusLabels[reservation.status] || reservation.status}
            </span>
          </div>
          <p className="text-sm text-gray-600">{reservation.service_name}</p>
        </div>
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="flex items-center gap-4 text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <Clock className="w-4 h-4" />
          <span>{reservation.reservation_time}</span>
        </div>
        <div className="flex items-center gap-1">
          <Phone className="w-4 h-4" />
          <span>{formatPhoneNumber(reservation.customer_phone)}</span>
        </div>
      </div>
      
      {(reservation.customer_request || reservation.internal_memo) && (
        <p className="mt-2 text-sm text-gray-600 line-clamp-2">
          {reservation.customer_request || reservation.internal_memo}
        </p>
      )}
    </div>
  );
}

export default function MobileReservations() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedReservation, setSelectedReservation] = useState<any>(null);
  
  const { reservations, loading } = useReservations();
  
  // 날짜 탭 생성 (오늘 기준 ±3일)
  const dateTabs = [];
  for (let i = -3; i <= 3; i++) {
    const date = new Date();
    date.setDate(date.getDate() + i);
    dateTabs.push({
      date: date.toISOString().split('T')[0],
      label: i === 0 ? '오늘' : i === 1 ? '내일' : i === -1 ? '어제' : date.getDate() + '일',
      weekday: date.toLocaleDateString('ko-KR', { weekday: 'short' }),
    });
  }
  
  // 선택된 날짜의 예약만 필터링
  const filteredReservations = reservations.filter(r => 
    r.reservation_date === selectedDate
  );
  
  const handleReservationTap = (reservation: any) => {
    setSelectedReservation(reservation);
    // 상세 정보 표시를 위해 선택된 예약 저장
  };

  return (
    <div className="bg-gray-50 min-h-screen pb-20">
      {/* 헤더 */}
      <div className="bg-white shadow-sm px-4 py-3">
        <h1 className="text-lg font-semibold">예약 조회</h1>
      </div>
      
      {/* 날짜 선택 탭 */}
      <div className="bg-white border-b border-gray-200">
        <div className="flex overflow-x-auto py-2 px-2 gap-2">
          {dateTabs.map(tab => (
            <button
              key={tab.date}
              onClick={() => setSelectedDate(tab.date)}
              className={`flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedDate === tab.date
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <div className="text-center">
                <div>{tab.label}</div>
                <div className="text-xs opacity-80">{tab.weekday}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
      
      {/* 예약 목록 */}
      <div className="p-4">
        {loading ? (
          <div className="text-center py-8">
            <p className="text-gray-500">로딩 중...</p>
          </div>
        ) : filteredReservations.length === 0 ? (
          <div className="text-center py-12">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">예약이 없습니다</p>
          </div>
        ) : (
          <div>
            <p className="text-sm text-gray-600 mb-3">
              총 {filteredReservations.length}건의 예약
            </p>
            {filteredReservations.map(reservation => (
              <ReservationItem
                key={reservation.id}
                reservation={reservation}
                onTap={() => handleReservationTap(reservation)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}