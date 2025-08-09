import { Package, Edit2, Trash2, ToggleLeft, ToggleRight } from 'lucide-react';

interface PackageType {
  package_id: number;
  package_name: string;
  total_sessions: number;
  price: number;
  valid_days: number;
  is_active: boolean;
  description?: string;
  created_at?: string;
}

interface PackageCardProps {
  pkg: PackageType;
  onEdit: (pkg: PackageType) => void;
  onToggleActive: (packageId: number) => void;
}

export default function PackageCard({ pkg, onEdit, onToggleActive }: PackageCardProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${!pkg.is_active ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between mb-4">
        <Package className="w-8 h-8 text-indigo-500" />
        <div className="flex items-center gap-2">
          <button
            onClick={() => onEdit(pkg)}
            className="text-gray-400 hover:text-gray-600"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          {pkg.is_active && (
            <button
              onClick={() => onToggleActive(pkg.package_id)}
              className="text-gray-400 hover:text-red-600"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {pkg.package_name}
      </h3>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">총 세션 수:</span>
          <span className="font-medium">{pkg.total_sessions}회</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">가격:</span>
          <span className="font-medium">{formatCurrency(pkg.price)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">유효기간:</span>
          <span className="font-medium">{pkg.valid_days}일</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">회당 가격:</span>
          <span className="font-medium">
            {formatCurrency(Math.round(pkg.price / pkg.total_sessions))}
          </span>
        </div>
      </div>
      
      {pkg.description && (
        <p className="mt-4 text-sm text-gray-600">
          {pkg.description}
        </p>
      )}
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">
            상태: {pkg.is_active ? '활성' : '비활성'}
          </span>
          {pkg.is_active ? (
            <ToggleRight className="w-5 h-5 text-green-500" />
          ) : (
            <ToggleLeft className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </div>
    </div>
  );
}