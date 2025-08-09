import PackageCard from './PackageCard';

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

interface PackageGridProps {
  packages: PackageType[];
  loading: boolean;
  onEdit: (pkg: PackageType) => void;
  onToggleActive: (packageId: number) => void;
}

export default function PackageGrid({ 
  packages, 
  loading, 
  onEdit, 
  onToggleActive 
}: PackageGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="col-span-full text-center py-8 text-gray-500">
          로딩 중...
        </div>
      </div>
    );
  }

  if (packages.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="col-span-full text-center py-8 text-gray-500">
          등록된 패키지가 없습니다.
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {packages.map((pkg) => (
        <PackageCard
          key={pkg.package_id}
          pkg={pkg}
          onEdit={onEdit}
          onToggleActive={onToggleActive}
        />
      ))}
    </div>
  );
}