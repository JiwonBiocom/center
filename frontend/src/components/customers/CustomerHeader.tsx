import { Plus, Upload, Download, Database } from 'lucide-react';
import { useRef } from 'react';

interface CustomerHeaderProps {
  totalCount: number;
  onExcelExport: () => void;
  onExcelImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onServiceHistoryImport: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onAddCustomer: () => void;
  onSendSMS?: () => void;
  onUnreflectedCustomers?: () => void;
  uploading: boolean;
  uploadProgress?: {
    status: 'idle' | 'uploading' | 'processing' | 'complete';
    message?: string;
    progress?: number;
  };
}

export default function CustomerHeader({
  totalCount,
  onExcelExport,
  onExcelImport,
  onServiceHistoryImport,
  onAddCustomer,
  onUnreflectedCustomers,
  uploading,
  uploadProgress
}: CustomerHeaderProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const serviceHistoryInputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="sm:flex sm:items-center">
      <div className="sm:flex-auto">
        <h1 className="text-3xl font-bold text-gray-900">고객 관리</h1>
        <p className="mt-2 text-sm text-gray-700">
          전체 {totalCount}명의 고객을 관리합니다.
        </p>
        <div className="mt-3 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-700 font-medium">📋 서비스 이력 업데이트 안내</p>
          <p className="text-xs text-blue-600 mt-1">
            고객별 서비스 이용 내역과 패키지 정보를 업데이트합니다.
          </p>
          <ul className="text-xs text-blue-600 mt-1 space-y-0.5">
            <li>• 고객명으로 매칭하여 기록 추가</li>
            <li>• 기존 데이터는 유지되며 신규 내역만 추가</li>
          </ul>
        </div>
      </div>
      <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none flex gap-2 relative">
        <button
          onClick={onExcelExport}
          className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          <Download className="w-4 h-4 mr-2" />
          엑셀 내보내기
        </button>
        {onUnreflectedCustomers && (
          <button
            onClick={onUnreflectedCustomers}
            className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <Database className="w-4 h-4 mr-2" />
            미반영 고객DB
          </button>
        )}
        <label className="relative inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 cursor-pointer">
          {uploading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
              <span className="text-indigo-600 font-medium">{uploadProgress?.message || '업로드 중...'}</span>
            </>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2" />
              엑셀 가져오기
            </>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls,.xlsm"
            onChange={onExcelImport}
            disabled={uploading}
            className="hidden"
          />
          {uploading && uploadProgress?.progress !== undefined && (
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200 rounded-b-md overflow-hidden">
              <div
                className="h-full bg-indigo-600 transition-all duration-300"
                style={{ width: `${uploadProgress.progress}%` }}
              />
            </div>
          )}
        </label>
        <label className="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 cursor-pointer">
          <Upload className="w-4 h-4 mr-2" />
          서비스 이력 업데이트
          <input
            ref={serviceHistoryInputRef}
            type="file"
            accept=".xlsx,.xls,.xlsm"
            onChange={onServiceHistoryImport}
            disabled={uploading}
            className="hidden"
          />
        </label>
        <button
          onClick={onAddCustomer}
          className="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          <Plus className="w-4 h-4 mr-2" />
          고객 등록
        </button>
      </div>
    </div>
  );
}
