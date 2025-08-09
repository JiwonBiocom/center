import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts'
import { Calendar, Download, TrendingUp, Users, DollarSign, Activity } from 'lucide-react'
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns'
import { api } from '../lib/api'

// Chart colors
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

interface DateRange {
  startDate: Date
  endDate: Date
}

export default function Reports() {
  const [showExportMenu, setShowExportMenu] = useState(false)
  const [dateRange, setDateRange] = useState<DateRange>({
    startDate: subDays(new Date(), 365),
    endDate: new Date()
  })
  
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<any>(null)
  const [monthlyRevenue, setMonthlyRevenue] = useState<any[]>([])
  const [customerAcquisition, setCustomerAcquisition] = useState<any[]>([])
  const [serviceUsage, setServiceUsage] = useState<any>({ summary: [], trend: [] })
  const [staffPerformance, setStaffPerformance] = useState<any[]>([])

  // Fetch all report data
  useEffect(() => {
    const fetchReportData = async () => {
      setLoading(true)
      try {
        // Fetch summary
        const summaryRes = await api.get('/reports/summary')
        setSummary(summaryRes.data)

        // Fetch monthly revenue
        const revenueRes = await api.get('/reports/revenue/monthly', {
          params: {
            start_date: format(dateRange.startDate, 'yyyy-MM-dd'),
            end_date: format(dateRange.endDate, 'yyyy-MM-dd')
          }
        })
        setMonthlyRevenue(revenueRes.data.data)

        // Fetch customer acquisition
        const customerRes = await api.get('/reports/customers/acquisition', {
          params: {
            start_date: format(dateRange.startDate, 'yyyy-MM-dd'),
            end_date: format(dateRange.endDate, 'yyyy-MM-dd')
          }
        })
        setCustomerAcquisition(customerRes.data.data)

        // Fetch service usage
        const serviceRes = await api.get('/reports/services/usage', {
          params: {
            start_date: format(subDays(dateRange.endDate, 90), 'yyyy-MM-dd'),
            end_date: format(dateRange.endDate, 'yyyy-MM-dd')
          }
        })
        setServiceUsage(serviceRes.data)

        // Fetch staff performance
        const staffRes = await api.get('/reports/staff/performance', {
          params: {
            start_date: format(startOfMonth(dateRange.endDate), 'yyyy-MM-dd'),
            end_date: format(endOfMonth(dateRange.endDate), 'yyyy-MM-dd')
          }
        })
        setStaffPerformance(staffRes.data.data)

      } catch (error) {
        console.error('Failed to fetch report data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchReportData()
  }, [dateRange])

  // Custom tooltip formatter for currency
  const formatCurrency = (value: number) => {
    return `₩${value.toLocaleString()}`
  }

  // Download report handler
  const handleDownloadReport = async (reportType: string = 'revenue') => {
    try {
      const response = await api.get('/reports/export/csv', {
        params: {
          report_type: reportType,
          start_date: format(dateRange.startDate, 'yyyy-MM-dd'),
          end_date: format(dateRange.endDate, 'yyyy-MM-dd')
        },
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${reportType}_report_${format(new Date(), 'yyyy-MM-dd')}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download report:', error)
      alert('리포트 다운로드 중 오류가 발생했습니다.')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">리포트를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">리포트 & 분석</h1>
          <div className="flex gap-4">
            <div className="relative">
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <Download className="h-4 w-4" />
                리포트 다운로드
              </button>
              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
                  <button
                    onClick={() => {
                      handleDownloadReport('revenue')
                      setShowExportMenu(false)
                    }}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    매출 리포트
                  </button>
                  <button
                    onClick={() => {
                      handleDownloadReport('customers')
                      setShowExportMenu(false)
                    }}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    고객 리포트
                  </button>
                  <button
                    onClick={() => {
                      handleDownloadReport('staff')
                      setShowExportMenu(false)
                    }}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    직원 실적 리포트
                  </button>
                </div>
              )}
            </div>
            <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-md border border-gray-300">
              <Calendar className="h-4 w-4 text-gray-500" />
              <input
                type="date"
                value={format(dateRange.startDate, 'yyyy-MM-dd')}
                onChange={(e) => setDateRange({ ...dateRange, startDate: new Date(e.target.value) })}
                className="outline-none"
              />
              <span className="text-gray-500">~</span>
              <input
                type="date"
                value={format(dateRange.endDate, 'yyyy-MM-dd')}
                onChange={(e) => setDateRange({ ...dateRange, endDate: new Date(e.target.value) })}
                className="outline-none"
              />
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">이번 달 매출</p>
                  <p className="mt-2 text-2xl font-semibold text-gray-900">
                    {formatCurrency(summary.current_month_revenue)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-green-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">올해 총 매출</p>
                  <p className="mt-2 text-2xl font-semibold text-gray-900">
                    {formatCurrency(summary.ytd_revenue)}
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-blue-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">전체 고객</p>
                  <p className="mt-2 text-2xl font-semibold text-gray-900">
                    {summary.total_customers.toLocaleString()}명
                  </p>
                </div>
                <Users className="h-8 w-8 text-purple-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">신규 고객 (이번달)</p>
                  <p className="mt-2 text-2xl font-semibold text-gray-900">
                    {summary.new_customers_month}명
                  </p>
                </div>
                <Users className="h-8 w-8 text-orange-500" />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">이번달 서비스</p>
                  <p className="mt-2 text-2xl font-semibold text-gray-900">
                    {summary.services_month}건
                  </p>
                </div>
                <Activity className="h-8 w-8 text-indigo-500" />
              </div>
            </div>
          </div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Monthly Revenue Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">월별 매출 추이</h2>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={monthlyRevenue}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={formatCurrency} />
                <Tooltip formatter={(value: any) => formatCurrency(value)} />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#0088FE" 
                  fill="#0088FE" 
                  fillOpacity={0.6}
                  name="매출"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Customer Acquisition Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">고객 증가 추이</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={customerAcquisition}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="newCustomers" 
                  stroke="#00C49F" 
                  name="신규 고객"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="totalCustomers" 
                  stroke="#8884D8" 
                  name="누적 고객"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Service Usage Statistics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">서비스별 이용 현황</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={serviceUsage.summary}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="service" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="usageCount" fill="#FFBB28" name="이용 횟수" />
                <Bar dataKey="uniqueCustomers" fill="#FF8042" name="고객 수" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Staff Performance Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">직원별 실적</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={staffPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="staff" />
                <YAxis tickFormatter={formatCurrency} />
                <Tooltip formatter={(value: any) => formatCurrency(value)} />
                <Legend />
                <Bar dataKey="revenue" fill="#8884D8" name="매출" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Service Usage Trend */}
        {serviceUsage.trend.length > 0 && (
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">서비스 이용 트렌드</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={serviceUsage.trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Legend />
                {Object.keys(serviceUsage.trend[0] || {})
                  .filter(key => key !== 'month')
                  .map((service, index) => (
                    <Line
                      key={service}
                      type="monotone"
                      dataKey={service}
                      stroke={COLORS[index % COLORS.length]}
                      name={service}
                      strokeWidth={2}
                    />
                  ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Staff Performance Details */}
        <div className="mt-6 bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">직원 실적 상세</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    직원
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    매출
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    거래 수
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    평균 거래액
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    담당 고객
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {staffPerformance.map((staff, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {staff.staff}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(staff.revenue)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {staff.transactions}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(staff.avgTransaction)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {staff.customers}명
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}