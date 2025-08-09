import { Calendar } from 'lucide-react';
import ServiceUsageCard from './ServiceUsageCard';

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

interface ServiceListProps {
  selectedDate: string;
  usages: ServiceUsage[];
}

export default function ServiceList({ selectedDate, usages }: ServiceListProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          {new Date(selectedDate).toLocaleDateString('ko-KR', { 
            month: 'long', 
            day: 'numeric',
            weekday: 'short'
          })}
        </h2>
        <Calendar className="w-5 h-5 text-gray-400" />
      </div>
      
      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {usages.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            서비스 이용 내역이 없습니다.
          </p>
        ) : (
          usages.map((usage) => (
            <ServiceUsageCard key={usage.usage_id} usage={usage} />
          ))
        )}
      </div>
    </div>
  );
}