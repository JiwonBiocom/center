import { formatCurrency, formatDate } from '../../lib/utils';
import { MessageSquare, Edit } from 'lucide-react';

interface Payment {
  payment_id: number;
  payment_number?: string;
  customer_id: number;
  customer_name: string;
  customer_phone: string;
  payment_date: string;
  amount: number;
  payment_method: string;
  payment_type?: string;
  payment_status?: string;
  card_holder_name?: string;
  approval_number?: string;
  payment_staff?: string;
  purchase_type?: string;
  purchase_order?: number;
  notes?: string;
  created_at: string;
}

interface PaymentTableProps {
  payments: Payment[];
  loading: boolean;
  onEdit?: (payment: Payment) => void;
  onDelete: (paymentId: number) => void;
}

export default function PaymentTable({ payments, loading, onEdit, onDelete }: PaymentTableProps) {

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              결제번호
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              결제일
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              고객
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              결제 금액
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              결제 방법
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              구매 항목
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              상태
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              담당자
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              작업
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {loading ? (
            <tr>
              <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                로딩 중...
              </td>
            </tr>
          ) : payments.length === 0 ? (
            <tr>
              <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                결제 내역이 없습니다.
              </td>
            </tr>
          ) : (
            payments.map((payment) => (
              <tr key={payment.payment_id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {payment.payment_number || `#${payment.payment_id}`}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(payment.payment_date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{payment.customer_name}</div>
                    <div className="text-sm text-gray-500">{payment.customer_phone}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <span className={payment.amount < 0 ? 'text-red-600' : 'text-gray-900'}>
                    {formatCurrency(Math.abs(payment.amount))}
                    {payment.amount < 0 && ' (환불)'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div>
                    <div className="font-medium">{payment.payment_method}</div>
                    {payment.approval_number && (
                      <div className="text-xs text-gray-500">승인: {payment.approval_number}</div>
                    )}
                    {payment.card_holder_name && (
                      <div className="text-xs text-gray-500">명의자: {payment.card_holder_name}</div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  <div>
                    {payment.purchase_type && (
                      <div className="font-medium">{payment.purchase_type}</div>
                    )}
                    {payment.purchase_order && (
                      <div className="text-xs text-gray-500">주문번호: #{payment.purchase_order}</div>
                    )}
                    {!payment.purchase_type && !payment.purchase_order && '-'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    payment.payment_status === 'completed' ? 'bg-green-100 text-green-800' :
                    payment.payment_status === 'cancelled' ? 'bg-red-100 text-red-800' :
                    payment.payment_status === 'refunded' ? 'bg-orange-100 text-orange-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {payment.payment_status === 'completed' ? '완료' :
                     payment.payment_status === 'cancelled' ? '취소' :
                     payment.payment_status === 'refunded' ? '환불' :
                     payment.payment_status === 'pending' ? '대기' :
                     payment.payment_status || '완료'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div className="flex items-center gap-2">
                    <span>{payment.payment_staff || '-'}</span>
                    {payment.notes && (
                      <div className="group relative">
                        <MessageSquare className="h-4 w-4 text-blue-500 cursor-help" />
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity z-10 max-w-xs">
                          {payment.notes}
                        </div>
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    {onEdit && (
                      <button
                        onClick={() => onEdit(payment)}
                        className="text-blue-600 hover:text-blue-900"
                        title="결제 수정"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => onDelete(payment.payment_id)}
                      className="text-red-600 hover:text-red-900"
                      title="결제 취소"
                    >
                      취소
                    </button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
