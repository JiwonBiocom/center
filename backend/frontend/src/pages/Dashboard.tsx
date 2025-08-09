import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalCustomers: 0,
    todayRevenue: 0,
    monthlyRevenue: 0,
    activePackages: 0
  })

  useEffect(() => {
    // TODO: Fetch dashboard stats from API
    // For now, using mock data
    setStats({
      totalCustomers: 950,
      todayRevenue: 1500000,
      monthlyRevenue: 45000000,
      activePackages: 320
    })
  }, [])

  return (
    <div>
      <div className="px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">대시보드</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-sm font-medium text-gray-500">전체 고객</h2>
            <p className="mt-2 text-3xl font-semibold text-gray-900">
              {stats.totalCustomers.toLocaleString()}명
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-sm font-medium text-gray-500">오늘 매출</h2>
            <p className="mt-2 text-3xl font-semibold text-gray-900">
              ₩{stats.todayRevenue.toLocaleString()}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-sm font-medium text-gray-500">월 매출</h2>
            <p className="mt-2 text-3xl font-semibold text-gray-900">
              ₩{stats.monthlyRevenue.toLocaleString()}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-sm font-medium text-gray-500">활성 패키지</h2>
            <p className="mt-2 text-3xl font-semibold text-gray-900">
              {stats.activePackages.toLocaleString()}개
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
