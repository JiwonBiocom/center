import { DollarSign, TrendingUp, Users, Package } from 'lucide-react'

interface SummaryData {
  monthly_revenue: number
  ytd_revenue: number
  total_customers: number
  new_customers_month: number
  active_customers: number
  services_month: number
}

interface SummaryCardsProps {
  summary: SummaryData | null
}

export default function SummaryCards({ summary }: SummaryCardsProps) {
  if (!summary) return null

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0
    }).format(value)
  }

  const cards = [
    {
      title: '월 매출',
      value: formatCurrency(summary.monthly_revenue),
      icon: DollarSign,
    },
    {
      title: '연간 매출',
      value: formatCurrency(summary.ytd_revenue),
      icon: TrendingUp,
    },
    {
      title: '총 고객수',
      value: `${summary.total_customers}명`,
      icon: Users,
    },
    {
      title: '월 서비스 이용',
      value: `${summary.services_month}건`,
      icon: Package,
    },
  ]

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      {cards.map((card, index) => {
        const Icon = card.icon
        return (
          <div key={index} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Icon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      {card.title}
                    </dt>
                    <dd className="text-lg font-semibold text-gray-900">
                      {card.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}