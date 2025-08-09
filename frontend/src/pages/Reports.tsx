import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import ReportHeader from '../components/reports/ReportHeader'
import SummaryCards from '../components/reports/SummaryCards'
import ReportGeneration from '../components/reports/ReportGeneration'
import ReportCharts from '../components/reports/ReportCharts'

interface SummaryData {
  monthly_revenue: number
  ytd_revenue: number
  total_customers: number
  new_customers_month: number
  active_customers: number
  services_month: number
}

interface ChartData {
  data: Array<Record<string, number | string>>
  summary?: Record<string, number | string>
  services?: string[]
  period?: {
    start_date: string
    end_date: string
  }
}


export default function Reports() {
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<SummaryData | null>(null)
  const [revenueData, setRevenueData] = useState<ChartData | null>(null)
  const [customerData, setCustomerData] = useState<ChartData | null>(null)
  const [serviceData, setServiceData] = useState<ChartData | null>(null)
  const [staffData, setStaffData] = useState<ChartData | null>(null)
  const [startDate, setStartDate] = useState(
    new Date(new Date().setMonth(new Date().getMonth() - 6)).toISOString().split('T')[0]
  )
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])

  useEffect(() => {
    fetchAllData()
  }, [startDate, endDate])

  const fetchAllData = async () => {
    setLoading(true)
    try {
      // Fetch summary
      const summaryRes = await api.get<SummaryData>('/api/v1/reports/summary')
      setSummary(summaryRes.data)

      // Fetch revenue data
      const revenueRes = await api.get<ChartData>('/api/v1/reports/revenue/monthly', {
        params: { start_date: startDate, end_date: endDate }
      })
      setRevenueData(revenueRes.data)

      // Fetch customer data
      const customerRes = await api.get<ChartData>('/api/v1/reports/customers/acquisition', {
        params: { start_date: startDate, end_date: endDate }
      })
      setCustomerData(customerRes.data)

      // Fetch service data
      const serviceRes = await api.get<ChartData>('/api/v1/reports/services/usage', {
        params: { start_date: startDate, end_date: endDate }
      })
      setServiceData(serviceRes.data)

      // Fetch staff performance
      const staffRes = await api.get<ChartData>('/api/v1/reports/staff/performance', {
        params: { start_date: startDate, end_date: endDate }
      })
      setStaffData(staffRes.data)

    } catch (error) {
      console.error('Failed to fetch report data:', error)
    } finally {
      setLoading(false)
    }
  }


  const handleExport = async (type: string) => {
    try {
      const response = await api.get(`/api/v1/reports/export/${type}`, {
        params: { start_date: startDate, end_date: endDate },
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${type}_report_${startDate}_${endDate}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to export report:', error)
    }
  }

  const handleGeneratePDF = async (reportType: string, params: Record<string, string | number> = {}) => {
    try {
      let endpoint = ''
      let filename = ''

      if (reportType === 'monthly-revenue') {
        const year = parseInt(String(params.year))
        const month = parseInt(String(params.month))
        endpoint = `/api/v1/reports/revenue/generate/monthly-revenue?year=${year}&month=${month}`
        filename = `monthly_revenue_${year}_${month}.pdf`
      } else if (reportType === 'customer-analysis') {
        endpoint = `/api/v1/reports/customers/generate/customer-analysis?start_date=${startDate}&end_date=${endDate}`
        filename = `customer_analysis_${startDate}_${endDate}.pdf`
      }

      const response = await api.get(endpoint, {
        responseType: 'blob'
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()

      alert('보고서가 생성되었습니다.')
    } catch (error) {
      console.error('Failed to generate PDF report:', error)
      alert('보고서 생성에 실패했습니다.')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ReportHeader
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onExport={handleExport}
        />

        <SummaryCards summary={summary} />

        <ReportGeneration
          startDate={startDate}
          endDate={endDate}
          onGeneratePDF={handleGeneratePDF}
        />

        <ReportCharts
          revenueData={revenueData}
          customerData={customerData}
          serviceData={serviceData}
          staffData={staffData}
        />
      </div>
    </div>
  )
}
