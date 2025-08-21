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
  onCustomerSelect: (customerId: string, customerName?: string, customerPhone?: string) => void;
}

export default function CustomerSelector({ 
  customers, 
  selectedCustomerId, 
  onCustomerSelect 
}: CustomerSelectorProps) {
  const [customerSearch, setCustomerSearch] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [showCustomerDropdown, setShowCustomerDropdown] = useState(false);
  const [isNewCustomer, setIsNewCustomer] = useState(false);

  // Set initial customer name when selectedCustomerId changes
  useEffect(() => {
    if (selectedCustomerId && customers) {
      const customer = customers.find(c => c.customer_id.toString() === selectedCustomerId);
      if (customer) {
        setCustomerSearch(customer.name);
        setIsNewCustomer(false);
      }
    } else if (!selectedCustomerId) {
      setCustomerSearch('');
    }
  }, [selectedCustomerId, customers]);

  const handleCustomerSearch = (value: string) => {
    setCustomerSearch(value);
    setShowCustomerDropdown(true);
    
    // Check if the entered value matches any existing customer
    const matchingCustomer = customers.find(c => 
      c.name.toLowerCase() === value.toLowerCase()
    );
    
    if (matchingCustomer) {
      onCustomerSelect(matchingCustomer.customer_id.toString());
      setIsNewCustomer(false);
    } else if (value) {
      // This is a new customer name
      onCustomerSelect('', value, customerPhone);
      setIsNewCustomer(true);
    } else {
      onCustomerSelect('');
      setIsNewCustomer(false);
    }
  };

  const handlePhoneChange = (value: string) => {
    setCustomerPhone(value);
    if (isNewCustomer) {
      onCustomerSelect('', customerSearch, value);
    }
  };

  const selectCustomer = (customer: Customer) => {
    setCustomerSearch(customer.name);
    setCustomerPhone(customer.phone || '');
    onCustomerSelect(customer.customer_id.toString());
    setShowCustomerDropdown(false);
    setIsNewCustomer(false);
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
            <div className="px-4 py-3 border-b bg-blue-50">
              <div className="text-sm text-blue-700 font-medium">새 고객으로 예약</div>
              <div className="text-xs text-gray-600 mt-1">"{customerSearch}"님으로 예약이 진행됩니다</div>
            </div>
          ) : (
            <>
              {filteredCustomers.map(customer => (
                <div
                  key={customer.customer_id}
                  onClick={() => selectCustomer(customer)}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                >
                  <div className="font-medium">{customer.name}</div>
                  <div className="text-sm text-gray-500">{customer.phone}</div>
                </div>
              ))}
              {customerSearch && !filteredCustomers.some(c => c.name.toLowerCase() === customerSearch.toLowerCase()) && (
                <div className="px-4 py-3 border-t bg-blue-50">
                  <div className="text-sm text-blue-700 font-medium">새 고객으로 예약</div>
                  <div className="text-xs text-gray-600 mt-1">"{customerSearch}"님으로 예약이 진행됩니다</div>
                </div>
              )}
            </>
          )}
        </div>
      )}
      
      {/* Show phone input for new customers */}
      {isNewCustomer && (
        <div className="mt-3">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            전화번호 (선택)
          </label>
          <input
            type="tel"
            value={customerPhone}
            onChange={(e) => handlePhoneChange(e.target.value)}
            placeholder="010-0000-0000"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <p className="mt-1 text-xs text-blue-600">
            ℹ️ 미등록 고객으로 예약이 진행됩니다. 전화번호를 입력하면 SMS 알림을 받을 수 있습니다.
          </p>
        </div>
      )}
    </div>
  );
}
