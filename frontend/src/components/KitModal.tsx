import { useState, useEffect, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { X } from 'lucide-react';
import { api } from '../lib/api';

interface KitType {
  kit_type_id: number;
  name: string;
  code: string;
  description: string;
  price: number;
}

interface Customer {
  customer_id: number;
  name: string;
  phone: string;
}

interface Kit {
  kit_id: number;
  customer_id: number;
  kit_type_id: number;
  serial_number: string | null;
  received_date: string | null;
  result_received_date: string | null;
  result_delivered_date: string | null;
  customer?: Customer;
}

interface KitModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  kit?: Kit | null;
  kitTypes: KitType[];
}

export default function KitModal({ isOpen, onClose, onSubmit, kit, kitTypes }: KitModalProps) {
  const [formData, setFormData] = useState({
    customer_id: '',
    kit_type_id: '',
    serial_number: '',
    received_date: '',
    result_received_date: '',
    result_delivered_date: ''
  });
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [creatingCustomer, setCreatingCustomer] = useState(false);

  useEffect(() => {
    if (kit) {
      console.log('KitModal received kit:', kit);
      console.log('Kit customer:', kit.customer);
      
      setFormData({
        customer_id: kit.customer_id.toString(),
        kit_type_id: kit.kit_type_id.toString(),
        serial_number: kit.serial_number || '',
        received_date: kit.received_date || '',
        result_received_date: kit.result_received_date || '',
        result_delivered_date: kit.result_delivered_date || ''
      });
      
      // 고객 정보가 있으면 검색어와 고객 목록 설정
      if (kit.customer) {
        setSearchTerm(kit.customer.name);
        setCustomers([kit.customer]);
      }
    } else {
      setFormData({
        customer_id: '',
        kit_type_id: '',
        serial_number: '',
        received_date: '',
        result_received_date: '',
        result_delivered_date: ''
      });
      setSearchTerm('');
      setCustomers([]);
    }
  }, [kit]);

  useEffect(() => {
    // 디바운싱을 통해 과도한 API 호출 방지
    const timeoutId = setTimeout(() => {
      if (searchTerm.length > 1) {
        searchCustomers();
      } else {
        setCustomers([]);
        // 검색어를 지우면 customer_id도 초기화 (기존 키트 수정이 아닌 경우)
        if (!kit) {
          setFormData(prev => ({ ...prev, customer_id: '' }));
        }
      }
    }, 300); // 300ms 디바운싱
    
    return () => clearTimeout(timeoutId);
  }, [searchTerm, kit]);

  const searchCustomers = async () => {
    try {
      // 기존 키트를 수정하고 있고, 이름이 변경된 경우
      if (kit && kit.customer && searchTerm.trim() !== kit.customer.name) {
        console.log('Customer name changed from', kit.customer.name, 'to', searchTerm);
        setCreatingCustomer(true);
        
        try {
          // 백슬래시와 특수문자 제거
          const cleanName = searchTerm.trim().replace(/[\\\/\n\r\t]/g, '');
          
          // 기존 고객의 정보 업데이트 (이름만 변경)
          const updateCustomerResponse = await api.patch(`/api/v1/customers/${kit.customer.customer_id}`, {
            name: cleanName
          });
          
          if (updateCustomerResponse.data) {
            const updatedCustomer = updateCustomerResponse.data;
            console.log('Customer name updated:', updatedCustomer);
            
            // 업데이트된 고객 정보로 상태 설정
            setCustomers([updatedCustomer]);
            setFormData(prev => ({ ...prev, customer_id: updatedCustomer.customer_id.toString() }));
          }
        } catch (customerError) {
          console.error('Failed to update customer name:', customerError);
          
          // 업데이트 실패 시 기존 고객 정보 유지
          setCustomers([kit.customer]);
          setFormData(prev => ({ ...prev, customer_id: kit.customer!.customer_id.toString() }));
        } finally {
          setCreatingCustomer(false);
        }
        return; // 이름 변경의 경우 여기서 종료
      }
      
      // 일반적인 고객 검색
      const response = await api.get(`/api/v1/customers/?search=${searchTerm}`);
      const customerData = response.data.data || response.data.customers || [];
      
      // 정확히 일치하는 고객 찾기
      const exactMatch = customerData.find(c => c.name.toLowerCase() === searchTerm.toLowerCase());
      
      if (exactMatch) {
        // 정확히 일치하는 고객이 있으면 선택
        console.log('Exact match found:', exactMatch);
        setCustomers([exactMatch]);
        setFormData(prev => ({ ...prev, customer_id: exactMatch.customer_id.toString() }));
      } else if (searchTerm.trim().length >= 2 && !creatingCustomer && !kit) {
        // 새 키트 생성 시에만 새 고객 생성
        console.log('No exact match, creating new customer:', searchTerm);
        setCreatingCustomer(true);
        
        try {
          const cleanName = searchTerm.trim().replace(/[\\\/\n\r\t]/g, '');
          
          const newCustomerResponse = await api.post('/api/v1/customers/', {
            name: cleanName,
            phone: '',
            first_visit_date: new Date().toISOString().split('T')[0]
          });
          
          if (newCustomerResponse.data && newCustomerResponse.data.customer_id) {
            const newCustomer = newCustomerResponse.data;
            console.log('New customer created:', newCustomer);
            
            setCustomers([newCustomer]);
            setFormData(prev => ({ ...prev, customer_id: newCustomer.customer_id.toString() }));
          }
        } catch (customerError) {
          console.error('Failed to create customer:', customerError);
          setCustomers(customerData);
          if (customerData.length > 0) {
            setFormData(prev => ({ ...prev, customer_id: customerData[0].customer_id.toString() }));
          } else {
            setFormData(prev => ({ ...prev, customer_id: '' }));
          }
        } finally {
          setCreatingCustomer(false);
        }
      } else {
        // 검색 결과 표시
        setCustomers(customerData);
        if (customerData.length === 1) {
          setFormData(prev => ({ ...prev, customer_id: customerData[0].customer_id.toString() }));
        } else if (customerData.length === 0) {
          setFormData(prev => ({ ...prev, customer_id: '' }));
        }
      }
    } catch (error) {
      console.error('Failed to search customers:', error);
      setCustomers([]);
      setFormData(prev => ({ ...prev, customer_id: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const data = {
        customer_id: parseInt(formData.customer_id),
        kit_type_id: parseInt(formData.kit_type_id),
        serial_number: formData.serial_number || null,
        received_date: formData.received_date || null,
        result_received_date: formData.result_received_date || null,
        result_delivered_date: formData.result_delivered_date || null
      };

      console.log('Submitting kit data:', data);

      await onSubmit(data);
      onClose();
    } catch (error) {
      console.error('Failed to save kit:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Transition.Root show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div className="absolute top-0 right-0 pt-4 pr-4">
                  <button
                    type="button"
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    onClick={onClose}
                  >
                    <span className="sr-only">Close</span>
                    <X className="h-6 w-6" />
                  </button>
                </div>
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                    <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                      {kit ? '검사키트 수정' : '새 검사키트 등록'}
                    </Dialog.Title>
                    <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                      {/* 고객 선택 */}
                      <div>
                        <label htmlFor="customer" className="block text-sm font-medium text-gray-700">
                          고객 <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          placeholder="고객명 또는 전화번호로 검색..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          disabled={creatingCustomer}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm disabled:opacity-50"
                        />
                        {creatingCustomer && (
                          <p className="mt-1 text-sm text-blue-600">
                            새 고객 '{searchTerm}' 생성 중...
                          </p>
                        )}
                        {customers.length > 0 && (
                          <select
                            value={formData.customer_id}
                            onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            required
                          >
                            <option value="">고객을 선택하세요</option>
                            {customers.map((customer) => (
                              <option key={customer.customer_id} value={customer.customer_id}>
                                {customer.name} - {customer.phone}
                              </option>
                            ))}
                          </select>
                        )}
                      </div>

                      {/* 검사 종류 */}
                      <div>
                        <label htmlFor="kit_type" className="block text-sm font-medium text-gray-700">
                          검사 종류 <span className="text-red-500">*</span>
                        </label>
                        <select
                          value={formData.kit_type_id}
                          onChange={(e) => setFormData({ ...formData, kit_type_id: e.target.value })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          required
                        >
                          <option value="">검사 종류를 선택하세요</option>
                          {kitTypes.map((kitType) => (
                            <option key={kitType.kit_type_id} value={kitType.kit_type_id}>
                              {kitType.name} - {kitType.price.toLocaleString()}원
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* 시리얼 번호 */}
                      <div>
                        <label htmlFor="serial_number" className="block text-sm font-medium text-gray-700">
                          시리얼 번호
                        </label>
                        <input
                          type="text"
                          value={formData.serial_number}
                          onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          placeholder="키트 시리얼 번호"
                        />
                      </div>

                      {/* 날짜 필드들 */}
                      <div className="grid grid-cols-1 gap-4">
                        <div>
                          <label htmlFor="received_date" className="block text-sm font-medium text-gray-700">
                            접수일
                          </label>
                          <input
                            type="date"
                            value={formData.received_date}
                            onChange={(e) => setFormData({ ...formData, received_date: e.target.value })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </div>

                        <div>
                          <label htmlFor="result_received_date" className="block text-sm font-medium text-gray-700">
                            결과 수령일
                          </label>
                          <input
                            type="date"
                            value={formData.result_received_date}
                            onChange={(e) => setFormData({ ...formData, result_received_date: e.target.value })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </div>

                        <div>
                          <label htmlFor="result_delivered_date" className="block text-sm font-medium text-gray-700">
                            결과 전달일
                          </label>
                          <input
                            type="date"
                            value={formData.result_delivered_date}
                            onChange={(e) => setFormData({ ...formData, result_delivered_date: e.target.value })}
                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          />
                        </div>
                      </div>

                      <div className="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                        <button
                          type="submit"
                          disabled={loading || creatingCustomer || (!formData.customer_id && !searchTerm.trim()) || !formData.kit_type_id}
                          className="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {loading ? '저장 중...' : (kit ? '수정' : '등록')}
                        </button>
                        <button
                          type="button"
                          onClick={onClose}
                          className="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:w-auto sm:text-sm"
                        >
                          취소
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}