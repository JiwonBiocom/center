import { useState, useEffect } from 'react';
import { User } from 'lucide-react';

interface Customer {
  customer_id: number;
  name: string;
  phone: string | null;
}

interface CustomerSelectorProps {
  customers: Customer[];
  selectedCustomerId: string;
  onCustomerSelect: (customerId: string) => void;
}

export default function CustomerSelector({ 
  customers, 
  selectedCustomerId, 
  onCustomerSelect 
}: CustomerSelectorProps) {
  const [customerSearch, setCustomerSearch] = useState('');
  const [showCustomerDropdown, setShowCustomerDropdown] = useState(false);

  // 디버깅 로그 제거됨

  // Set initial customer name when selectedCustomerId changes
  useEffect(() => {
    if (selectedCustomerId && customers) {
      const customer = customers.find(c => c.customer_id.toString() === selectedCustomerId);
      if (customer) {
        setCustomerSearch(customer.name);
      }
    } else if (!selectedCustomerId) {
      setCustomerSearch('');
    }
  }, [selectedCustomerId, customers]);

  const handleCustomerSearch = (value: string) => {
    setCustomerSearch(value);
    setShowCustomerDropdown(true);
    if (!value) {
      onCustomerSelect('');
    }
  };

  const selectCustomer = (customer: Customer) => {
    setCustomerSearch(customer.name);
    onCustomerSelect(customer.customer_id.toString());
    setShowCustomerDropdown(false);
  };

  const filteredCustomers = Array.isArray(customers) 
    ? customers.filter(customer =>
        customer.name?.toLowerCase().includes(customerSearch.toLowerCase()) ||
        customer.phone?.includes(customerSearch)
      )
    : [];

  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        고객 <span className="text-red-500">*</span>
      </label>
      <div className="relative">
        <input
          type="text"
          value={customerSearch}
          onChange={(e) => handleCustomerSearch(e.target.value)}
          onFocus={() => setShowCustomerDropdown(true)}
          onBlur={() => setTimeout(() => setShowCustomerDropdown(false), 200)}
          placeholder="고객명 또는 전화번호로 검색"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          required
        />
        <User className="absolute right-3 top-2.5 h-5 w-5 text-gray-400" />
      </div>
      {showCustomerDropdown && customerSearch && (
        <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md overflow-auto">
          {filteredCustomers.length === 0 ? (
            <div className="px-4 py-2 text-sm text-gray-500">검색 결과가 없습니다</div>
          ) : (
            filteredCustomers.map(customer => (
              <div
                key={customer.customer_id}
                onClick={() => selectCustomer(customer)}
                className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
              >
                <div className="font-medium">{customer.name}</div>
                <div className="text-sm text-gray-500">{customer.phone}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}