# Common Mistakes to Avoid - AIBIO Center

> Version: 1.1.0
> Last Updated: 2025-06-22
> Purpose: Document common coding mistakes and their solutions

## ❌ NEVER DO THESE

### 1. Giant Files
```typescript
// ❌ NEVER: 800-line component
export function Dashboard() {
  // 200 lines of state
  // 100 lines of effects
  // 150 lines of handlers
  // 350 lines of JSX
}
```

### 2. Multiple Responsibilities
```python
# ❌ NEVER: API route doing everything
@router.post("/customers")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Validation logic (should be in validator)
    if not re.match(r'^\d{3}-\d{4}-\d{4}$', customer.phone):
        # Format phone number
        # Complex formatting logic here...

    # Business logic (should be in service)
    # Check duplicates
    # Calculate loyalty points
    # Send notifications
    # Generate reports

    # Database operations
    # Multiple queries and updates

    # Response formatting
    # Complex response building

    return response  # 300+ lines later...
```

### 3. Inline Everything
```typescript
// ❌ NEVER: All logic inline
function BadComponent() {
  return (
    <div onClick={async () => {
      // 50 lines of async logic
      const response = await fetch('/api/customers');
      const data = await response.json();
      const filtered = data.filter(/* complex filter */);
      const sorted = filtered.sort(/* complex sort */);
      // More processing...
      setState(processed);
    }}>
      {customers.map(customer => (
        <div>
          {/* 200 lines of nested JSX */}
          <div>
            <div>
              <div>
                {/* Deep nesting... */}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### 4. Creating Fake Data Without Permission
```python
# ❌ NEVER: Create sample data without asking
def add_sample_data():
    fake_customers = [
        {"name": "테스트1", "phone": "010-1111-1111"},
        {"name": "테스트2", "phone": "010-2222-2222"},
        # More fake data...
    ]
    # Just add to database without permission
    for customer in fake_customers:
        db.add(Customer(**customer))
    db.commit()
```

### 5. Dangerous Database Operations
```python
# ❌ NEVER: Drop tables in regular scripts
Base.metadata.drop_all(bind=engine)  # NEVER!
db.execute("TRUNCATE TABLE customers")  # NEVER!
db.execute("DROP TABLE payments")  # NEVER!
```

## 🚨 If You're About to Write These, STOP!

- A function over 50 lines → Split it
- A component over 250 lines → Extract sub-components
- A file over 300 lines → Create new modules
- Nested JSX over 3 levels → Extract components
- useEffect over 15 lines → Extract to custom hook
- API route over 300 lines → Split into service layer
- Inline styles over 5 properties → Extract to CSS module

## 🎯 When Users Ask for "Everything in One File"

Response template:
```
"I understand you want everything together, but this would create a {estimated_lines}-line file. Our project limit is 300 lines for maintainability.

Let me implement this properly split:
- Main component (~100 lines)
- Sub-components (~150 lines each)
- Hooks (~80 lines)
- Services (~150 lines)

This structure will be:
✅ Easier to understand
✅ Faster to debug
✅ Simpler to modify
✅ Better for team collaboration

Shall I proceed with the proper structure?"
```

## 🔴 Red Flags in Code Review

1. **File size**: Over 300 lines
2. **Function size**: Over 50 lines
3. **Nesting depth**: Over 3 levels
4. **Import count**: Over 20 imports
5. **Component props**: Over 10 props
6. **State variables**: Over 10 in one component
7. **Inline functions**: In render/return
8. **Magic numbers**: Hardcoded values
9. **No error handling**: try/catch missing
10. **No loading states**: Async without loading

## 📋 Checklist Before Committing

- [ ] All files under 300 lines?
- [ ] All functions under 50 lines?
- [ ] Single responsibility per file?
- [ ] No fake data without permission?
- [ ] No dangerous DB operations?
- [ ] Proper error handling?
- [ ] Loading states implemented?
- [ ] Code follows project patterns?

## 🆕 Recent Production Mistakes (2025-06)

### 6. POST Trailing Slash Missing → 404 Error
```python
# ❌ WRONG: Single route definition when frontend adds trailing slash
@router.post("/users")
def create_user(...):
    pass

# ✅ CORRECT: Both versions when redirect_slashes=False
@router.post("/users")
@router.post("/users/")  # Must add this!
def create_user(...):
    pass
```
**Impact**: All POST/PUT/PATCH requests returned 404 in production
**Lesson**: Always define both route versions for mutation endpoints

### 7. Enum Case Mismatch → 500 Error
```python
# ❌ WRONG: Database has 'pending', code uses 'PENDING'
class ReservationStatus(str, Enum):
    PENDING = "PENDING"    # Database expects lowercase!
    CONFIRMED = "CONFIRMED"

# ✅ CORRECT: Match database exactly
class ReservationStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
```
**Impact**: All reservation saves failed with enum validation error
**Lesson**: Always verify enum values match database exactly

### 8. Schema Drift Without Migration → 500 Error
```python
# ❌ WRONG: Change model without database migration
class Notification(Base):
    user_id = Column(Integer)  # Changed from customer_id

# But database still has 'customer_id' column!

# ✅ CORRECT: Always create migration first
# 1. Create migration: supabase migration new change_customer_to_user
# 2. Update model after migration applied
```
**Impact**: Complete API failure on notification endpoints
**Lesson**: Never change models without corresponding migrations

### 9. Console Check on Wrong Page
```python
# ❌ WRONG: Check console on login page for customer page errors
async def check_console():
    await page.goto("/login")  # Wrong page!
    errors = console_messages  # These are login page errors

# ✅ CORRECT: Navigate to specific page after login
async def check_console():
    await login()
    console_messages.clear()  # Clear login messages
    await page.goto("/customers")  # Check actual page
    errors = console_messages  # Now these are customer page errors
```
**Impact**: Missed critical errors on authenticated pages
**Lesson**: Always test the exact page with proper authentication
