import { Plus } from 'lucide-react';

interface PackageHeaderProps {
  showInactive: boolean;
  onShowInactiveChange: (show: boolean) => void;
  onAddPackage: () => void;
}

export default function PackageHeader({ 
  showInactive, 
  onShowInactiveChange, 
  onAddPackage 
}: PackageHeaderProps) {
  return (
    <div className="mb-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">패키지 관리</h1>
      
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(e) => onShowInactiveChange(e.target.checked)}
                className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
              />
              <span className="text-sm text-gray-700">비활성 패키지 포함</span>
            </label>
          </div>
          
          <button
            onClick={onAddPackage}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            <Plus className="w-4 h-4" />
            새 패키지 등록
          </button>
        </div>
      </div>
    </div>
  );
}