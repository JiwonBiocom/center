import { Plus, Download } from 'lucide-react';

interface ServiceHeaderProps {
  onExcelExport: () => void;
  onAddService: () => void;
}

export default function ServiceHeader({ onExcelExport, onAddService }: ServiceHeaderProps) {
  return (
    <div className="sm:flex sm:items-center">
      <div className="sm:flex-auto">
        <h1 className="text-3xl font-bold text-gray-900">서비스 이용 관리</h1>
        <p className="mt-2 text-sm text-gray-700">
          고객의 서비스 이용 내역을 관리합니다.
        </p>
      </div>
      <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none flex gap-2">
        <button
          onClick={onExcelExport}
          className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
        >
          <Download className="w-4 h-4 mr-2" />
          엑셀 내보내기
        </button>
        <button
          onClick={onAddService}
          className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          서비스 등록
        </button>
      </div>
    </div>
  );
}