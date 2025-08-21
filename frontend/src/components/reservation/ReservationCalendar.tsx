import { format, startOfMonth, endOfMonth, eachDayOfInterval, addMonths, subMonths, isSameMonth, isToday, isSameDay, getDay, startOfWeek, endOfWeek } from 'date-fns';
import { ko } from 'date-fns/locale';
import type { Reservation, ServiceType } from '../../types';

interface ReservationCalendarProps {
  currentMonth: Date;
  selectedDate: Date;
  reservations: Reservation[];
  serviceTypes: ServiceType[];
  onMonthChange: (month: Date) => void;
  onDateSelect: (date: Date) => void;
  onTodayClick: () => void;
}

export default function ReservationCalendar({
  currentMonth,
  selectedDate,
  reservations,
  serviceTypes,
  onMonthChange,
  onDateSelect,
  onTodayClick
}: ReservationCalendarProps) {
  const getDaysInMonth = () => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const startDate = startOfWeek(monthStart, { weekStartsOn: 0 }); // Start from Sunday
    const endDate = endOfWeek(monthEnd, { weekStartsOn: 0 }); // End on Saturday
    return eachDayOfInterval({ start: startDate, end: endDate });
  };

  const getReservationsForDate = (date: Date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return reservations.filter(r => r.reservation_date === dateStr);
  };

  const handlePrevMonth = () => {
    onMonthChange(subMonths(currentMonth, 1));
  };

  const handleNextMonth = () => {
    onMonthChange(addMonths(currentMonth, 1));
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {format(currentMonth, 'yyyy년 M월', { locale: ko })}
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={onTodayClick}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              오늘
            </button>
            <button
              onClick={handlePrevMonth}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={handleNextMonth}
              className="p-2 hover:bg-gray-100 rounded-full"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-2">
          {['일', '월', '화', '수', '목', '금', '토'].map(day => (
            <div key={day} className="text-center text-sm font-medium text-gray-700 py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {getDaysInMonth().map((date, index) => {
            const dateReservations = getReservationsForDate(date);
            const isSelected = isSameDay(date, selectedDate);
            const isCurrentMonth = isSameMonth(date, currentMonth);
            const isTodayDate = isToday(date);
            
            return (
              <div
                key={index}
                onClick={() => onDateSelect(date)}
                className={`
                  min-h-[80px] p-2 border rounded cursor-pointer transition-colors
                  ${isSelected ? 'bg-blue-50 border-blue-500' : 'border-gray-200 hover:bg-gray-50'}
                  ${!isCurrentMonth ? 'opacity-50' : ''}
                  ${isTodayDate ? 'border-blue-400' : ''}
                `}
              >
                <div className={`text-sm font-medium ${isTodayDate ? 'text-blue-600' : 'text-gray-900'}`}>
                  {format(date, 'd')}
                </div>
                <div className="mt-1 space-y-1">
                  {dateReservations.slice(0, 3).map((reservation, idx) => {
                    const serviceType = serviceTypes.find(s => s.service_type_id === reservation.service_type_id);
                    return (
                      <div
                        key={idx}
                        className="text-xs px-1 py-0.5 rounded truncate"
                        style={{
                          backgroundColor: (serviceType?.service_color || '#000') + '20',
                          color: serviceType?.service_color || '#000'
                        }}
                      >
                        {format(new Date(`2000-01-01T${reservation.reservation_time}`), 'HH:mm')} {reservation.customer_name}
                      </div>
                    );
                  })}
                  {dateReservations.length > 3 && (
                    <div className="text-xs text-gray-500">
                      +{dateReservations.length - 3}건
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
