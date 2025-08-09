import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  color: string;
}

export default function StatCard({ title, value, icon: Icon, color }: StatCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 md:p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs md:text-sm font-medium text-gray-600 truncate">{title}</p>
          <p className="mt-1 md:mt-2 text-xl md:text-3xl font-bold text-gray-900 truncate">{value}</p>
        </div>
        <div className={`p-2 md:p-3 rounded-full ${color} bg-opacity-10 flex-shrink-0 ml-3`}>
          <Icon className={`w-5 h-5 md:w-6 md:h-6 ${color.replace('bg-', 'text-')}`} />
        </div>
      </div>
    </div>
  );
}