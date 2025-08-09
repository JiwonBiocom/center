import { Download } from 'lucide-react'

interface ReportHeaderProps {
  startDate: string
  endDate: string
  onStartDateChange: (date: string) => void
  onEndDateChange: (date: string) => void
  onExport: (type: string) => void
}

export default function ReportHeader({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onExport
}: ReportHeaderProps) {
  return (
    <div className="md:flex md:items-center md:justify-between mb-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">리포트 (개발중)</h1>
        <p className="mt-2 text-sm text-gray-700">
          비즈니스 인사이트와 성과 분석
        </p>
      </div>
      <div className="mt-4 md:mt-0 md:ml-4 flex items-center space-x-3">
        <input
          type="date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
        <span className="text-gray-500">~</span>
        <input
          type="date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        />
        <div className="relative">
          <button
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            onClick={() => document.getElementById('export-menu')?.classList.toggle('hidden')}
          >
            <Download className="h-4 w-4 mr-2" />
            내보내기
          </button>
          <div id="export-menu" className="hidden absolute right-0 z-10 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
            <div className="py-1">
              <button
                onClick={() => onExport('revenue')}
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
              >
                매출 리포트
              </button>
              <button
                onClick={() => onExport('customers')}
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
              >
                고객 리포트
              </button>
              <button
                onClick={() => onExport('staff')}
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
              >
                직원 실적
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
