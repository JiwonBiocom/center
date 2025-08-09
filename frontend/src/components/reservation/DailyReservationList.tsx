import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Clock, User, Phone } from 'lucide-react';
import { getStatusColor, getStatusText } from '../../lib/utils/reservationStatus';
import type { Reservation, ServiceType } from '../../types';


interface DailyReservationListProps {
  selectedDate: Date;
  reservations: Reservation[];
  serviceTypes: ServiceType[];
  onReservationClick: (reservation: Reservation) => void;
}

export default function DailyReservationList({
  selectedDate,
  reservations,
  serviceTypes,
  onReservationClick
}: DailyReservationListProps) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {format(selectedDate, 'M월 d일', { locale: ko })} 예약
          </h3>
          <span className="text-sm text-gray-500">
            총 {reservations.length}건
          </span>
        </div>

        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {reservations.length === 0 ? (
            <p className="text-gray-500 text-center py-8">예약이 없습니다</p>
          ) : (
            reservations.map(reservation => (
              <div
                key={reservation.reservation_id}
                onClick={() => onReservationClick(reservation)}
                className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="font-medium">
                        {format(new Date(`2000-01-01T${reservation.reservation_time}`), 'HH:mm')}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(reservation.status)}`}>
                        {getStatusText(reservation.status)}
                      </span>
                    </div>
                    <div className="mt-2">
                      <div className="flex items-center space-x-2 text-sm">
                        <User className="h-3 w-3 text-gray-400" />
                        <span className="font-medium">{reservation.customer_name}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-gray-600 mt-1">
                        <Phone className="h-3 w-3 text-gray-400" />
                        <span>{reservation.customer_phone}</span>
                      </div>
                    </div>
                    <div className="mt-2">
                      <span
                        className="text-sm px-2 py-1 rounded"
                        style={{
                          backgroundColor: (serviceTypes.find(s => s.service_type_id === reservation.service_type_id)?.service_color || '#000') + '20',
                          color: serviceTypes.find(s => s.service_type_id === reservation.service_type_id)?.service_color || '#000'
                        }}
                      >
                        {reservation.service_name}
                      </span>
                    </div>
                    {reservation.customer_request && (
                      <p className="text-sm text-gray-600 mt-2 italic">"{reservation.customer_request}"</p>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}