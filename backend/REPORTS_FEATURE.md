# Reports and Analytics Feature

## Overview
The Reports feature provides comprehensive analytics and insights for the AIBIO Center management system. It includes various charts and visualizations to help track business performance.

## Features Implemented

### 1. Backend API Endpoints
- **Monthly Revenue**: `/api/v1/reports/revenue/monthly`
- **Quarterly Revenue**: `/api/v1/reports/revenue/quarterly`
- **Customer Acquisition**: `/api/v1/reports/customers/acquisition`
- **Service Usage Statistics**: `/api/v1/reports/services/usage`
- **Staff Performance**: `/api/v1/reports/staff/performance`
- **Summary Dashboard**: `/api/v1/reports/summary`
- **CSV Export**: `/api/v1/reports/export/csv`

### 2. Frontend Components
- **Reports Page**: Comprehensive dashboard with multiple charts
- **Interactive Charts**: Using Recharts library
  - Area chart for monthly revenue trends
  - Line chart for customer acquisition
  - Bar charts for service usage and staff performance
- **Date Range Filters**: Customizable date ranges for all reports
- **Export Functionality**: Download reports as CSV files
- **Mobile Responsive**: All charts adapt to different screen sizes

### 3. Chart Types
1. **Revenue Charts**
   - Monthly revenue trend (Area chart)
   - Transaction counts
   - Average transaction values

2. **Customer Analytics**
   - New customer acquisition trend
   - Cumulative customer growth
   - Customer distribution by region

3. **Service Usage**
   - Service type distribution
   - Usage trends over time
   - Unique customer counts per service

4. **Staff Performance**
   - Revenue per staff member
   - Transaction counts
   - Customer assignments
   - Performance table with detailed metrics

## Technical Stack
- **Backend**: FastAPI with SQLAlchemy
- **Frontend**: React with TypeScript
- **Charts**: Recharts
- **Styling**: Tailwind CSS
- **Date Handling**: date-fns
- **Icons**: lucide-react

## Usage

### Starting the Application
1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to the Reports page from the sidebar menu

### Testing with Sample Data
Run the sample data script to populate the database:
```bash
python scripts/add_sample_report_data.py
```

### API Testing
Test the API endpoints:
```bash
python test_reports_api.py
```

## Key Files
- **Backend**:
  - `/api/v1/reports.py` - All report API endpoints
  - `/scripts/add_sample_report_data.py` - Sample data generator
  - `/test_reports_api.py` - API endpoint tester

- **Frontend**:
  - `/src/pages/Reports.tsx` - Main reports page
  - `/src/components/Layout.tsx` - Navigation layout with Reports menu item

## Future Enhancements
1. PDF export functionality
2. Email scheduling for reports
3. More advanced filtering options
4. Comparison views (YoY, MoM)
5. Custom report builder
6. Real-time data updates
7. Predictive analytics