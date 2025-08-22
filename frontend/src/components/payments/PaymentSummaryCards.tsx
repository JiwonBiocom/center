import { CreditCard, DollarSign, Calendar, TrendingUp } from 'lucide-react';

interface PaymentSummary {
  total_count: number;
  total_revenue: number;
  current_month_revenue?: number;
  customer_count: number;
  average_amount: number;
  previous_month?: string;
  current_month?: string;
}

interface PaymentSummaryCardsProps {
  summary: PaymentSummary | null;
}

interface SummaryCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
}

function SummaryCard({ title, value, icon }: SummaryCardProps) {
  return (
    <div className="bg-white p-3 md:p-4 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0 mr-3">
          <p className="text-xs md:text-sm text-gray-500 truncate">{title}</p>
          <p className="text-lg md:text-2xl font-bold text-gray-900 truncate">{value}</p>
        </div>
        <div className="flex-shrink-0">
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function PaymentSummaryCards({ summary }: PaymentSummaryCardsProps) {
  if (!summary) return null;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const cards = [
    {
      title: '총 결제 건수',
      value: `${summary.total_count}건`,
      icon: <CreditCard className="w-6 h-6 md:w-8 md:h-8 text-blue-500" />
    },
    {
      title: `전월 매출${summary.previous_month ? ` (${summary.previous_month})` : ''}`,
      value: formatCurrency(summary.total_revenue),
      icon: <DollarSign className="w-6 h-6 md:w-8 md:h-8 text-green-500" />
    },
    {
      title: `이번 달 매출${summary.current_month ? ` (${summary.current_month})` : ''}`,
      value: formatCurrency(summary.current_month_revenue || 0),
      icon: <DollarSign className="w-6 h-6 md:w-8 md:h-8 text-blue-600" />
    },
    {
      title: '결제 고객수',
      value: `${summary.customer_count}명`,
      icon: <TrendingUp className="w-6 h-6 md:w-8 md:h-8 text-purple-500" />
    },
    {
      title: '평균 결제액 (최근 3개월)',
      value: formatCurrency(summary.average_amount),
      icon: <Calendar className="w-6 h-6 md:w-8 md:h-8 text-orange-500" />
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
      {cards.map((card, index) => (
        <SummaryCard key={index} {...card} />
      ))}
    </div>
  );
}
