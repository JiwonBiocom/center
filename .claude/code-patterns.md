# Code Patterns and Examples - AIBIO Center

## React Component Pattern (Max 250 lines)

```typescript
// ✅ GOOD: CustomerCard.tsx (120 lines)
import React, { useState } from 'react';
import { Phone, User, Calendar } from 'lucide-react';
import { Customer } from '@/types';
import { formatPhoneNumber, formatDate } from '@/lib/utils';

interface CustomerCardProps {
  customer: Customer;
  onEdit: (customer: Customer) => void;
  onDelete: (id: number) => void;
}

export default function CustomerCard({ customer, onEdit, onDelete }: CustomerCardProps) {
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDelete = () => {
    if (showConfirm) {
      onDelete(customer.customer_id);
    } else {
      setShowConfirm(true);
      setTimeout(() => setShowConfirm(false), 3000);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-lg flex items-center gap-2">
            <User className="w-4 h-4" />
            {customer.name}
          </h3>
          {customer.phone && (
            <p className="text-gray-600 flex items-center gap-2 mt-1">
              <Phone className="w-4 h-4" />
              {formatPhoneNumber(customer.phone)}
            </p>
          )}
          <p className="text-sm text-gray-500 flex items-center gap-2 mt-1">
            <Calendar className="w-4 h-4" />
            첫 방문: {formatDate(customer.first_visit_date)}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onEdit(customer)}
            className="text-blue-600 hover:text-blue-800"
          >
            수정
          </button>
          <button
            onClick={handleDelete}
            className={showConfirm ? "text-red-600" : "text-gray-600 hover:text-gray-800"}
          >
            {showConfirm ? '확인' : '삭제'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

## FastAPI Route Pattern (Max 300 lines)

```python
# ✅ GOOD: customers.py (200 lines)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from core.database import get_db
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from utils.validators import validate_phone_number

router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = Query(20, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """고객 목록 조회"""
    query = db.query(Customer)
    
    if search:
        query = query.filter(
            (Customer.name.contains(search)) |
            (Customer.phone.contains(search))
        )
    
    customers = query.offset(skip).limit(limit).all()
    return customers

@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """고객 생성"""
    # 전화번호 유효성 검사
    if customer.phone:
        customer.phone = validate_phone_number(customer.phone)
    
    # 중복 체크
    existing = db.query(Customer).filter(
        Customer.phone == customer.phone
    ).first()
    if existing:
        raise HTTPException(400, "이미 등록된 전화번호입니다")
    
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    
    return db_customer
```

## Service/Business Logic Pattern (Max 200 lines)

```python
# ✅ GOOD: excel_service.py (150 lines)
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import re

class ExcelService:
    """Excel 파일 처리 서비스"""
    
    @staticmethod
    def read_customer_data(file_path: str) -> List[Dict[str, Any]]:
        """고객 데이터 읽기"""
        df = pd.read_excel(file_path, sheet_name='고객정보')
        
        # 데이터 정제
        df['phone'] = df['전화번호'].apply(ExcelService._clean_phone)
        df['name'] = df['이름'].str.strip()
        
        return df.to_dict('records')
    
    @staticmethod
    def _clean_phone(phone: str) -> str:
        """전화번호 정제"""
        if pd.isna(phone):
            return None
        
        # 숫자만 추출
        numbers = re.sub(r'[^0-9]', '', str(phone))
        
        # 11자리 휴대폰
        if len(numbers) == 11 and numbers.startswith('010'):
            return f"{numbers[:3]}-{numbers[3:7]}-{numbers[7:11]}"
        
        return phone
```

## When to Split Components

```typescript
// ❌ BAD: Everything in one file (500+ lines)
function CustomerPage() {
  // 100 lines of state and hooks
  // 50 lines of handlers
  // 350 lines of JSX with inline components
}

// ✅ GOOD: Split into logical parts
// CustomerPage/index.tsx (100 lines)
function CustomerPage() {
  const { customers, loading, error } = useCustomers();
  
  return (
    <div className="p-8">
      <CustomerHeader onAdd={handleAdd} />
      <CustomerFilters onFilter={handleFilter} />
      <CustomerList 
        customers={customers}
        loading={loading}
        error={error}
      />
    </div>
  );
}

// CustomerPage/CustomerList.tsx (150 lines)
function CustomerList({ customers, loading, error }) {
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="grid gap-4">
      {customers.map(customer => (
        <CustomerCard key={customer.id} customer={customer} />
      ))}
    </div>
  );
}
```

## Custom Hook Pattern (Max 100 lines)

```typescript
// ✅ GOOD: useCustomers.ts (80 lines)
import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { Customer } from '@/types';

interface UseCustomersOptions {
  page?: number;
  limit?: number;
  search?: string;
}

export function useCustomers(options: UseCustomersOptions = {}) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [total, setTotal] = useState(0);

  const fetchCustomers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get('/customers', { 
        params: options 
      });
      setCustomers(response.data.data);
      setTotal(response.data.total);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [options.page, options.limit, options.search]);

  useEffect(() => {
    fetchCustomers();
  }, [fetchCustomers]);

  return { customers, loading, error, total, refetch: fetchCustomers };
}
```