# Claude Code Rules for This Project

## 🚨 CRITICAL RULES - NEVER BREAK THESE

1. **File Length Limit**: NO file should exceed 300 lines
   - If approaching 250 lines, suggest splitting
   - If over 300 lines, MUST split before proceeding

2. **Single Responsibility**: One file = One purpose
   - Component files: Only UI rendering
   - Hook files: Only logic
   - Utility files: Only pure functions
   - API files: Only endpoint definitions

3. **Change Scope**: Modify ONE file at a time
   - Never modify more than 2 files in a single response
   - Always show current code before modifying
   - Test after each change

4. **Data Integrity**: Never create fake/sample data
   - Use only real data from Excel files
   - Always ask permission before creating test data
   - Delete test data after use

## 📏 Code Length Guidelines

### Components (React)
- Maximum: 250 lines
- Ideal: 100-200 lines
- If larger: Split into smaller components

### Functions
- Maximum: 50 lines
- Ideal: 10-30 lines
- If larger: Extract helper functions

### API Routes (FastAPI)
- Maximum: 300 lines per file
- Ideal: 100-200 lines
- If larger: Split by feature

## 🛠 When You See Long Code

1. STOP and alert: "This file is {X} lines. Let me split it first."
2. Suggest splitting strategy
3. Wait for approval
4. Split step by step

## 📝 Example Response Format

```
"I see Dashboard.tsx is 450 lines. This exceeds our 300-line limit.

I suggest splitting it into:
- Dashboard/index.tsx (main container, ~100 lines)
- Dashboard/StatsSection.tsx (~150 lines)  
- Dashboard/ChartSection.tsx (~100 lines)
- Dashboard/TableSection.tsx (~100 lines)

Shall I proceed with this split?"
```

## 🔒 Database Safety Rules

1. NEVER use drop_all(), TRUNCATE, or DROP TABLE
2. Always backup before major changes
3. Use migrations for schema changes
4. Test queries on small datasets first