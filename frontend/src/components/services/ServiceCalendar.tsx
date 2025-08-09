import { ChevronLeft, ChevronRight } from 'lucide-react';
import { getServiceColor, SERVICE_TYPES } from '../../lib/utils/serviceColors';

interface CalendarData {
  [date: string]: {
    total_services: number;
    unique_customers: number;
    services: {
      [serviceName: string]: number;
    };
  };
}

interface ServiceCalendarProps {
  currentYear: number;
  currentMonth: number;
  selectedDate: string;
  calendarData: CalendarData;
  onDateSelect: (date: string) => void;
  onMonthChange: (year: number, month: number) => void;
}

export default function ServiceCalendar({
  currentYear,
  currentMonth,
  selectedDate,
  calendarData,
  onDateSelect,
  onMonthChange
}: ServiceCalendarProps) {
  const generateCalendar = () => {
    const firstDay = new Date(currentYear, currentMonth - 1, 1);
    const lastDay = new Date(currentYear, currentMonth, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const calendar = [];
    let week = [];
    
    // 빈 칸 채우기
    for (let i = 0; i < startingDayOfWeek; i++) {
      week.push(null);
    }
    
    // 날짜 채우기
    for (let day = 1; day <= daysInMonth; day++) {
      const dateStr = `${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
      const dayData = calendarData[dateStr] || { total_services: 0, unique_customers: 0, services: {} };
      
      week.push({
        day,
        date: dateStr,
        ...dayData
      });
      
      if (week.length === 7) {
        calendar.push(week);
        week = [];
      }
    }
    
    // 마지막 주 채우기
    if (week.length > 0) {
      while (week.length < 7) {
        week.push(null);
      }
      calendar.push(week);
    }
    
    return calendar;
  };

  const handlePrevMonth = () => {
    if (currentMonth === 1) {
      onMonthChange(currentYear - 1, 12);
    } else {
      onMonthChange(currentYear, currentMonth - 1);
    }
  };

  const handleNextMonth = () => {
    if (currentMonth === 12) {
      onMonthChange(currentYear + 1, 1);
    } else {
      onMonthChange(currentYear, currentMonth + 1);
    }
  };

  const handleTodayClick = () => {
    const today = new Date();
    onMonthChange(today.getFullYear(), today.getMonth() + 1);
    onDateSelect(today.toISOString().split('T')[0]);
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">
          {currentYear}년 {currentMonth}월
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleTodayClick}
            className="px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 rounded-md"
          >
            오늘
          </button>
          <button
            onClick={handlePrevMonth}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            onClick={handleNextMonth}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <table className="w-full">
        <thead>
          <tr>
            {['일', '월', '화', '수', '목', '금', '토'].map(day => (
              <th key={day} className="py-2 text-sm font-medium text-gray-700">
                {day}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {generateCalendar().map((week, weekIndex) => (
            <tr key={weekIndex}>
              {week.map((day, dayIndex) => (
                <td
                  key={dayIndex}
                  className={`h-24 border border-gray-200 p-2 align-top cursor-pointer transition-colors ${
                    day?.date === selectedDate ? 'bg-indigo-50 border-indigo-300' : 'hover:bg-gray-50'
                  } ${
                    day?.date === today ? 'ring-2 ring-indigo-400 ring-inset' : ''
                  }`}
                  onClick={() => day && onDateSelect(day.date)}
                >
                  {day && (
                    <div className="h-full">
                      <div className="flex justify-between items-start mb-1">
                        <span className={`font-medium text-sm ${
                          day.date === today 
                            ? 'text-indigo-600 font-bold' 
                            : 'text-gray-900'
                        }`}>
                          {day.day}
                        </span>
                        {day.total_services > 0 && (
                          <span className="text-xs font-medium text-gray-600">
                            {day.total_services}건
                          </span>
                        )}
                      </div>
                      {day.services && Object.keys(day.services).length > 0 && (
                        <div className="space-y-1">
                          {Object.entries(day.services).map(([serviceName, count]) => (
                            <div
                              key={serviceName}
                              className={`text-xs px-1.5 py-0.5 rounded ${getServiceColor(serviceName)}`}
                            >
                              {serviceName} {count}건
                            </div>
                          ))}
                        </div>
                      )}
                      {day.unique_customers > 0 && (
                        <div className="text-xs text-gray-500 mt-1">
                          고객 {day.unique_customers}명
                        </div>
                      )}
                    </div>
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      
      {/* 서비스 범례 */}
      <div className="mt-4 flex flex-wrap gap-2">
        <span className="text-xs text-gray-600 mr-2">서비스 종류:</span>
        {SERVICE_TYPES.map(service => (
          <span key={service} className={`text-xs px-2 py-1 rounded ${getServiceColor(service)}`}>
            {service}
          </span>
        ))}
      </div>
    </div>
  );
}