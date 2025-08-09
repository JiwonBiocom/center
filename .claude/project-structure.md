# Project Structure Guidelines - AIBIO Center

## Backend Structure (FastAPI)
```
backend/
├── api/
│   └── v1/                    # API endpoints (max 300 lines each)
│       ├── auth.py            # ~200 lines
│       ├── customers.py       # ~250 lines
│       ├── dashboard.py       # ~300 lines
│       ├── payments.py        # ~200 lines
│       └── services.py        # ~250 lines
├── core/                      # Core functionality
│   ├── auth.py               # Authentication logic ~150 lines
│   ├── config.py             # Settings ~50 lines
│   └── database.py           # DB connection ~100 lines
├── models/                   # SQLAlchemy models (max 150 lines each)
│   ├── customer.py           # ~100 lines
│   ├── payment.py            # ~120 lines
│   └── service.py            # ~100 lines
├── schemas/                  # Pydantic schemas (max 100 lines each)
│   ├── customer.py           # ~80 lines
│   └── payment.py            # ~80 lines
├── services/                 # Business logic (max 200 lines each)
│   ├── kakao_service.py      # ~150 lines
│   └── notification_service.py # ~180 lines
└── utils/                    # Utilities (max 150 lines each)
    ├── excel.py              # ~140 lines
    └── validators.py         # ~80 lines
```

## Frontend Structure (React + TypeScript)
```
frontend/src/
├── components/               # UI Components (max 250 lines each)
│   ├── Layout.tsx           # ~100 lines
│   ├── CustomerModal.tsx    # ~200 lines
│   └── ServiceModal.tsx     # ~180 lines
├── pages/                   # Page components (max 300 lines each)
│   ├── Dashboard.tsx        # ~250 lines
│   ├── Customers.tsx        # ~300 lines
│   └── Services.tsx         # ~280 lines
├── lib/                     # Core utilities
│   ├── api.ts              # API client ~100 lines
│   └── auth.ts             # Auth helpers ~80 lines
├── hooks/                   # Custom hooks (max 100 lines each)
│   └── useAuth.ts          # ~60 lines
└── types/                   # TypeScript types
    └── index.ts            # ~150 lines
```

## Import Rules

### Backend (Python)
1. Standard library imports first
2. Third-party imports second  
3. Local imports last
4. Use absolute imports from project root

### Frontend (TypeScript)
1. React imports first
2. Third-party libraries second
3. Local components third
4. Types/interfaces last
5. Use @ alias for src/ directory

## Naming Conventions

### Backend
- Files: snake_case (customer_service.py)
- Classes: PascalCase (CustomerModel)
- Functions: snake_case (get_customer_by_id)
- Constants: UPPER_SNAKE_CASE (MAX_RETRIES)

### Frontend
- Components: PascalCase (CustomerCard.tsx)
- Hooks: camelCase with 'use' prefix (useCustomer.ts)
- Utils: camelCase (formatDate.ts)
- Types: PascalCase with 'Type' suffix (CustomerType.ts)

## File Organization Rules

1. **Co-location**: Keep related files together
2. **Feature folders**: Group by feature, not file type
3. **Index files**: Use for clean imports
4. **Shared code**: Put in common/ or shared/