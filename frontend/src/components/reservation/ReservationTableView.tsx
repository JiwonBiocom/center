import { format } from 'date-fns';
import type { Reservation } from '../../types';

interface ReservationTableViewProps {
  reservations: Reservation[];
  selectedDate: Date;
  onReservationClick: (reservation: Reservation) => void;
}

export default function ReservationTableView({
  reservations,
  selectedDate,
  onReservationClick
}: ReservationTableViewProps) {
  // 시간 슬롯 생성 (10:00 ~ 16:30, 30분 간격)
  const timeSlots = [];
  for (let hour = 10; hour <= 16; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      if (hour === 16 && minute > 30) break; // 16:30까지만
      const time = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      timeSlots.push(time);
    }
  }

  // 서비스/스태프 컬럼 정의 
  const serviceColumns = [
    { key: 'brain', label: '브레인' },
    { key: 'pulse', label: '펄스' },
    { key: 'red', label: '레드' },
    { key: 'lymph', label: '림프' },
    { key: 'consultation', label: '상담' },
    { key: 'aibike_red', label: 'AI바이크&레드엔바이브' }
  ];

  // 서비스명으로 컬럼 매핑
  const getColumnKey = (serviceName: string) => {
    const name = serviceName?.toLowerCase() || '';
    if (name.includes('브레인') || name.includes('brain')) return 'brain';
    if (name.includes('펄스') || name.includes('pulse')) return 'pulse';
    if (name.includes('레드') || name.includes('red')) return 'red';
    if (name.includes('림프') || name.includes('lymph')) return 'lymph';
    if (name.includes('상담') || name.includes('consultation')) return 'consultation';
    if (name.includes('바이크') || name.includes('bike')) return 'aibike_red';
    return 'consultation'; // 기본값
  };

  // 시간대별 예약 데이터 구성
  const getReservationForTimeAndService = (timeSlot: string, columnKey: string) => {
    return reservations.find(reservation => {
      const reservationTime = reservation.reservation_time.substring(0, 5); // HH:MM 형태로 변환
      const serviceColumnKey = getColumnKey(reservation.service_name);
      return reservationTime === timeSlot && serviceColumnKey === columnKey;
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">
          {format(selectedDate, 'yyyy년 MM월 dd일')} 예약 현황
        </h3>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="sticky left-0 z-10 bg-gray-50 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-r border-gray-200">
                시간대
              </th>
              {serviceColumns.map(column => (
                <th
                  key={column.key}
                  className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[150px]"
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {timeSlots.map(timeSlot => (
              <tr key={timeSlot} className="hover:bg-gray-50">
                <td className="sticky left-0 z-10 bg-white px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 border-r border-gray-200">
                  {timeSlot} - {(() => {
                    const [hour, minute] = timeSlot.split(':').map(Number);
                    const endMinute = minute + 30;
                    const endHour = endMinute >= 60 ? hour + 1 : hour;
                    const finalMinute = endMinute >= 60 ? endMinute - 60 : endMinute;
                    return `${endHour.toString().padStart(2, '0')}:${finalMinute.toString().padStart(2, '0')}`;
                  })()}
                </td>
                {serviceColumns.map(column => {
                  const reservation = getReservationForTimeAndService(timeSlot, column.key);
                  return (
                    <td
                      key={`${timeSlot}-${column.key}`}
                      className="px-4 py-4 text-center text-sm"
                    >
                      {reservation ? (
                        <div
                          onClick={() => onReservationClick(reservation)}
                          className={`inline-block px-3 py-2 rounded-md text-xs font-medium cursor-pointer hover:shadow-md transition-shadow border ${getStatusColor(reservation.status)}`}
                        >
                          <div className="font-semibold">{reservation.customer_name}</div>
                          {reservation.staff_name && (
                            <div className="text-xs opacity-75 mt-1">
                              ({reservation.staff_name})
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="text-gray-400 text-xs">-</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}