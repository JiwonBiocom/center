import { FileText, Download } from 'lucide-react'

interface ReportGenerationProps {
  startDate: string
  endDate: string
  onGeneratePDF: (reportType: string, params: any) => void
}

export default function ReportGeneration({ startDate, endDate, onGeneratePDF }: ReportGenerationProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">보고서 생성</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Monthly Revenue Report */}
        <div className="border rounded-lg p-4">
          <div className="flex items-center mb-3">
            <FileText className="h-5 w-5 text-indigo-600 mr-2" />
            <h3 className="font-medium text-gray-900">월간 매출 보고서</h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            선택한 월의 매출 분석, 일별 추이, 서비스별 매출, 결제 방법별 통계를 포함한 상세 보고서
          </p>
          <div className="flex items-center space-x-2 mb-4">
            <select
              id="revenue-year"
              className="block w-24 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              defaultValue={new Date().getFullYear()}
            >
              <option value="2024">2024</option>
              <option value="2025">2025</option>
            </select>
            <span className="text-gray-500">년</span>
            <select
              id="revenue-month"
              className="block w-20 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              defaultValue={new Date().getMonth() + 1}
            >
              {[...Array(12)].map((_, i) => (
                <option key={i + 1} value={i + 1}>{i + 1}</option>
              ))}
            </select>
            <span className="text-gray-500">월</span>
          </div>
          <button
            onClick={() => {
              const year = (document.getElementById('revenue-year') as HTMLSelectElement).value
              const month = (document.getElementById('revenue-month') as HTMLSelectElement).value
              onGeneratePDF('monthly-revenue', { year, month })
            }}
            className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Download className="h-4 w-4 mr-2" />
            PDF 생성
          </button>
        </div>

        {/* Customer Analysis Report */}
        <div className="border rounded-lg p-4">
          <div className="flex items-center mb-3">
            <FileText className="h-5 w-5 text-indigo-600 mr-2" />
            <h3 className="font-medium text-gray-900">고객 분석 보고서</h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            기간별 고객 통계, 지역별 분포, 유입 경로 분석, 상위 고객 리스트를 포함한 종합 보고서
          </p>
          <div className="flex items-center space-x-2 mb-4">
            <input
              type="date"
              id="customer-start-date"
              defaultValue={startDate}
              className="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <span className="text-gray-500">~</span>
            <input
              type="date"
              id="customer-end-date"
              defaultValue={endDate}
              className="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <button
            onClick={() => {
              const start = (document.getElementById('customer-start-date') as HTMLInputElement).value
              const end = (document.getElementById('customer-end-date') as HTMLInputElement).value
              onGeneratePDF('customer-analysis', { startDate: start, endDate: end })
            }}
            className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Download className="h-4 w-4 mr-2" />
            PDF 생성
          </button>
        </div>
      </div>
    </div>
  )
}