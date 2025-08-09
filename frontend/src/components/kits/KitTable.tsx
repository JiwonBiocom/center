import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface KitType {
  kit_type_id: number;
  name: string;
  code: string;
  description: string;
  price: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Customer {
  customer_id: number;
  name: string;
  phone: string;
}

interface Kit {
  kit_id: number;
  customer_id: number;
  kit_type: string;
  kit_type_id: number;
  serial_number: string | null;
  received_date: string | null;
  result_received_date: string | null;
  result_delivered_date: string | null;
  created_at: string;
  customer?: Customer;
  kit_type_ref?: KitType;
}

interface KitTableProps {
  kits: Kit[];
  loading: boolean;
  onEdit: (kit: Kit) => void;
  onDelete: (kit: Kit) => void;
}

export default function KitTable({ kits, loading, onEdit, onDelete }: KitTableProps) {
  // 디버깅용 로그
  console.log('KitTable received kits:', kits);
  if (kits.length > 0) {
    console.log('First kit customer:', kits[0].customer);
  }
  const getStatusBadge = (kit: Kit) => {
    if (!kit.received_date) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          <Clock className="w-3 h-3 mr-1" />
          대기중
        </span>
      );
    } else if (!kit.result_delivered_date) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
          <AlertCircle className="w-3 h-3 mr-1" />
          진행중
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="w-3 h-3 mr-1" />
          완료
        </span>
      );
    }
  };

  return (
    <div className="mt-8 flex flex-col">
      <div className="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div className="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-gray-300">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    고객
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    검사 종류
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    시리얼번호
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    상태
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    접수일
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    결과 수령일
                  </th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    결과 전달일
                  </th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="text-center py-4">
                      <div className="flex justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                      </div>
                    </td>
                  </tr>
                ) : kits.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="text-center py-4 text-gray-500">
                      검사키트가 없습니다.
                    </td>
                  </tr>
                ) : (
                  kits.map((kit) => (
                    <tr key={kit.kit_id}>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                        <div>
                          <div className="font-medium">{kit.customer?.name}</div>
                          <div className="text-gray-500">{kit.customer?.phone}</div>
                        </div>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                        {kit.kit_type}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                        {kit.serial_number || '-'}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm">
                        {getStatusBadge(kit)}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                        {kit.received_date 
                          ? format(new Date(kit.received_date), 'yyyy-MM-dd', { locale: ko })
                          : '-'
                        }
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                        {kit.result_received_date 
                          ? format(new Date(kit.result_received_date), 'yyyy-MM-dd', { locale: ko })
                          : '-'
                        }
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-gray-900">
                        {kit.result_delivered_date 
                          ? format(new Date(kit.result_delivered_date), 'yyyy-MM-dd', { locale: ko })
                          : '-'
                        }
                      </td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                        <button
                          onClick={() => onEdit(kit)}
                          className="text-indigo-600 hover:text-indigo-900 mr-3"
                        >
                          수정
                        </button>
                        <button
                          onClick={() => onDelete(kit)}
                          className="text-red-600 hover:text-red-900"
                        >
                          삭제
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}