import { useState, useEffect } from 'react';
import { Phone, MessageSquare, User, Package, Calendar } from 'lucide-react';
import { api } from '../lib/api';
import type { Customer } from '../types';

interface CustomerWithDetails extends Customer {
  activePackages?: number;
  lastVisit?: string;
}

function CustomerQuickCard({ customer }: { customer: CustomerWithDetails }) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-lg">{customer.name}</h4>
          <p className="text-sm text-gray-600">{customer.phone}</p>
        </div>
        <div className="flex gap-2">
          <a 
            href={`tel:${customer.phone}`}
            className="p-2 bg-blue-100 text-blue-600 rounded-lg hover:bg-blue-200 transition-colors"
          >
            <Phone className="w-4 h-4" />
          </a>
          <a 
            href={`sms:${customer.phone}`}
            className="p-2 bg-green-100 text-green-600 rounded-lg hover:bg-green-200 transition-colors"
          >
            <MessageSquare className="w-4 h-4" />
          </a>
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-2 text-sm">
        <div className="text-center p-2 bg-gray-50 rounded">
          <User className="w-4 h-4 mx-auto mb-1 text-gray-600" />
          <p className="text-xs text-gray-600">상태</p>
          <p className="font-medium">{customer.status === 'active' ? '활성' : '비활성'}</p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <Package className="w-4 h-4 mx-auto mb-1 text-gray-600" />
          <p className="text-xs text-gray-600">패키지</p>
          <p className="font-medium">{customer.activePackages || 0}개</p>
        </div>
        <div className="text-center p-2 bg-gray-50 rounded">
          <Calendar className="w-4 h-4 mx-auto mb-1 text-gray-600" />
          <p className="text-xs text-gray-600">최근방문</p>
          <p className="font-medium">{customer.lastVisit || '없음'}</p>
        </div>
      </div>
    </div>
  );
}

export default function QuickSearch() {
  const [phone, setPhone] = useState('');
  const [results, setResults] = useState<CustomerWithDetails[]>([]);
  const [loading, setLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  useEffect(() => {
    // 최근 검색 기록 로드
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  const handlePhoneInput = (value: string) => {
    // 숫자만 추출
    const cleaned = value.replace(/\D/g, '');
    
    // 11자리까지만 입력 가능
    if (cleaned.length > 11) return;
    
    // 하이픈 자동 추가
    let formatted = cleaned;
    if (cleaned.length >= 4 && cleaned.length <= 7) {
      formatted = `${cleaned.slice(0, 3)}-${cleaned.slice(3)}`;
    } else if (cleaned.length >= 8) {
      formatted = `${cleaned.slice(0, 3)}-${cleaned.slice(3, 7)}-${cleaned.slice(7)}`;
    }
    
    setPhone(formatted);
    
    // 4자리 이상 입력시 실시간 검색
    if (cleaned.length >= 4) {
      searchCustomers(cleaned);
    } else {
      setResults([]);
    }
  };

  const searchCustomers = async (phoneNumber: string) => {
    setLoading(true);
    try {
      const response = await api.get('/customers', {
        params: {
          search: phoneNumber,
          page: 1,
          page_size: 10
        }
      });
      
      if (response.data.success && response.data.data) {
        setResults(response.data.data.data || []);
      }
    } catch (error) {
      console.error('검색 실패:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const saveToRecent = (phoneNumber: string) => {
    const updated = [phoneNumber, ...recentSearches.filter(p => p !== phoneNumber)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('recentSearches', JSON.stringify(updated));
  };

  const handleRecentClick = (phoneNumber: string) => {
    setPhone(phoneNumber);
    handlePhoneInput(phoneNumber);
    saveToRecent(phoneNumber);
  };

  return (
    <div className="p-4 pb-20 bg-gray-50 min-h-screen">
      <h1 className="text-xl font-bold mb-4">빠른 고객 검색</h1>
      
      {/* 큰 전화번호 입력 필드 */}
      <div className="mb-6">
        <input
          type="tel"
          value={phone}
          onChange={(e) => handlePhoneInput(e.target.value)}
          placeholder="010-0000-0000"
          className="w-full text-2xl p-4 border-2 border-gray-300 rounded-lg text-center focus:border-indigo-500 focus:outline-none"
          autoFocus
        />
        {loading && (
          <p className="text-center text-sm text-gray-500 mt-2">검색 중...</p>
        )}
      </div>
      
      {/* 최근 검색 */}
      {phone === '' && recentSearches.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">최근 검색</h3>
          <div className="space-y-2">
            {recentSearches.map((recentPhone, index) => (
              <button
                key={index}
                onClick={() => handleRecentClick(recentPhone)}
                className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
              >
                <span className="text-gray-900">{recentPhone}</span>
              </button>
            ))}
          </div>
        </div>
      )}
      
      {/* 검색 결과 */}
      {results.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700">검색 결과</h3>
          {results.map(customer => (
            <CustomerQuickCard key={customer.id} customer={customer} />
          ))}
        </div>
      )}
      
      {/* 검색 결과 없음 */}
      {phone.length >= 4 && !loading && results.length === 0 && (
        <div className="text-center py-8">
          <User className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-500">검색 결과가 없습니다</p>
          <button className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
            신규 고객 등록
          </button>
        </div>
      )}
    </div>
  );
}