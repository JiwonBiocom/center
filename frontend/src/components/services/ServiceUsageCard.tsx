import { User, Clock, Package } from 'lucide-react';
import { getServiceColor } from '../../lib/utils/serviceColors';

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

interface ServiceUsageCardProps {
  usage: ServiceUsage;
}

export default function ServiceUsageCard({ usage }: ServiceUsageCardProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <User className="w-4 h-4 text-gray-400" />
            <span className="font-medium text-gray-900">
              {usage.customer_name}
            </span>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getServiceColor(usage.service_name)}`}>
              {usage.service_name}
            </span>
            {usage.session_number && (
              <span className="flex items-center gap-1">
                <Package className="w-3 h-3" />
                {usage.session_number}회차
              </span>
            )}
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {usage.created_by}
            </span>
          </div>
          
          {usage.session_details && (
            <p className="mt-2 text-sm text-gray-600">
              {usage.session_details}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}