import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts'

interface ChartData {
  data: any[]
  summary?: any
  services?: string[]
  period?: {
    start_date: string
    end_date: string
  }
}

interface ReportChartsProps {
  revenueData: ChartData | null
  customerData: ChartData | null
  serviceData: ChartData | null
  staffData: ChartData | null
}

export default function ReportCharts({ 
  revenueData, 
  customerData, 
  serviceData, 
  staffData 
}: ReportChartsProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0
    }).format(value)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Revenue Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">월별 매출 추이</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={revenueData?.data || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis tickFormatter={(value) => `${value/1000000}M`} />
            <Tooltip formatter={(value: any) => formatCurrency(value)} />
            <Area type="monotone" dataKey="revenue" stroke="#8884d8" fill="#8884d8" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Customer Acquisition Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">고객 증가 추이</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={customerData?.data || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="new_customers" stroke="#8884d8" name="신규 고객" />
            <Line type="monotone" dataKey="total_customers" stroke="#82ca9d" name="누적 고객" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Service Usage Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">서비스별 이용 통계</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={serviceData?.data || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="service" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="usage_count" fill="#8884d8" name="이용 횟수" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Staff Performance Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">직원별 실적</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={staffData?.data || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="staff" />
            <YAxis />
            <Tooltip formatter={(value: any, name: string) => 
              name === 'revenue' ? formatCurrency(value) : value
            } />
            <Legend />
            <Bar dataKey="revenue" fill="#8884d8" name="매출" />
            <Bar dataKey="customers" fill="#82ca9d" name="고객수" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}