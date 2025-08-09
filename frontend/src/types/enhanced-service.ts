/**
 * Enhanced Service Management Types
 * 확장된 서비스 관리 시스템 타입 정의
 */

export interface EnhancedServiceType {
  service_type_id: number;
  name: string;
  code: string;
  description?: string;
  default_duration: number;
  default_price: number;
  equipment_required?: Record<string, any>;
  protocols?: Record<string, any>;
  intensity_levels?: Record<string, any>;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface ServiceSession {
  session_id: number;
  customer_id: number;
  service_type_id: number;
  package_usage_id?: number;
  session_date: string;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  equipment_settings?: Record<string, any>;
  protocol_used?: string;
  intensity_level?: string;
  session_notes?: string;
  customer_condition?: string;
  staff_notes?: string;
  customer_feedback?: string;
  is_completed: boolean;
  is_partial: boolean;
  completion_rate: number;
  conducted_by?: number;
  reservation_id?: number;
  created_at: string;
  updated_at: string;
}

export interface ServiceSessionWithDetails extends ServiceSession {
  customer_name?: string;
  service_name?: string;
  conducted_by_name?: string;
}

export interface EnhancedPackageUsage {
  usage_id: number;
  customer_id: number;
  package_id: number;
  purchase_date: string;
  valid_until: string;
  total_amount: number;
  
  // 서비스별 할당량
  brain_total: number;
  brain_used: number;
  brain_remaining: number;
  
  pulse_total: number;
  pulse_used: number;
  pulse_remaining: number;
  
  lymph_total: number;
  lymph_used: number;
  lymph_remaining: number;
  
  red_total: number;
  red_used: number;
  red_remaining: number;
  
  ai_bike_total: number;
  ai_bike_used: number;
  ai_bike_remaining: number;
  
  status: string;
  auto_renewal: boolean;
  low_session_alert_sent: boolean;
  expiry_alert_sent: boolean;
  created_at: string;
  updated_at: string;
}

export interface EnhancedPackageUsageWithDetails extends EnhancedPackageUsage {
  customer_name?: string;
  package_name?: string;
}

export interface Equipment {
  equipment_id: number;
  equipment_name: string;
  equipment_code: string;
  equipment_type: string;
  supported_services?: Record<string, any>;
  is_available: boolean;
  is_maintenance: boolean;
  current_session_id?: number;
  total_usage_hours: number;
  maintenance_due_date?: string;
  last_maintenance_date?: string;
  created_at: string;
  updated_at: string;
}

export interface ServiceUsageStats {
  service_name: string;
  total_sessions: number;
  total_duration: number;
  average_duration: number;
  usage_rate: number;
}

export interface CustomerSessionSummary {
  customer_id: number;
  customer_name: string;
  total_sessions: number;
  remaining_sessions: Record<string, number>;
  last_visit_date?: string;
  next_recommended_visit?: string;
}

export interface RealtimeSessionDashboard {
  current_sessions: ServiceSessionWithDetails[];
  available_equipment: Equipment[];
  upcoming_reservations: Record<string, any>[];
  session_alerts: {
    type: string;
    customer_name: string;
    message: string;
    priority: string;
  }[];
}

export interface EquipmentAvailability {
  total_equipment: number;
  available: number;
  in_use: number;
  maintenance: number;
  by_service: Record<string, {
    total: number;
    available: number;
    in_use: number;
    maintenance: number;
  }>;
  equipment_details: {
    equipment_id: number;
    equipment_name: string;
    equipment_code: string;
    equipment_type: string;
    status: string;
    current_session_id?: number;
    supported_services?: Record<string, any>;
  }[];
}

export interface EquipmentUsageStats {
  total_equipment: number;
  equipment_stats: {
    equipment_id: number;
    equipment_name: string;
    equipment_code: string;
    equipment_type: string;
    total_usage_hours: number;
    is_available: boolean;
    is_maintenance: boolean;
    last_maintenance_date?: string;
    maintenance_due_date?: string;
    session_count: number;
  }[];
  by_type: Record<string, {
    count: number;
    available: number;
    maintenance: number;
    total_usage_hours: number;
  }>;
  maintenance_due: {
    equipment_id: number;
    equipment_name: string;
    maintenance_due_date: string;
    days_until_due: number;
  }[];
}

// API Response Types
export interface EnhancedServiceTypeListResponse {
  service_types: EnhancedServiceType[];
  total: number;
}

export interface ServiceSessionListResponse {
  sessions: ServiceSessionWithDetails[];
  total: number;
  page: number;
  page_size: number;
}

export interface EnhancedPackageUsageListResponse {
  package_usages: EnhancedPackageUsageWithDetails[];
  total: number;
  page: number;
  page_size: number;
}

// Create/Update Types
export interface ServiceSessionCreate {
  customer_id: number;
  service_type_id: number;
  package_usage_id?: number;
  session_date: string;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  equipment_settings?: Record<string, any>;
  protocol_used?: string;
  intensity_level?: string;
  session_notes?: string;
  customer_condition?: string;
  staff_notes?: string;
  customer_feedback?: string;
  is_completed?: boolean;
  is_partial?: boolean;
  completion_rate?: number;
  conducted_by?: number;
  reservation_id?: number;
}

export interface ServiceSessionUpdate {
  end_time?: string;
  equipment_settings?: Record<string, any>;
  protocol_used?: string;
  intensity_level?: string;
  session_notes?: string;
  customer_condition?: string;
  staff_notes?: string;
  customer_feedback?: string;
  is_completed?: boolean;
  is_partial?: boolean;
  completion_rate?: number;
}

export interface EnhancedPackageUsageCreate {
  customer_id: number;
  package_id: number;
  purchase_date: string;
  valid_until: string;
  total_amount: number;
  brain_total?: number;
  pulse_total?: number;
  lymph_total?: number;
  red_total?: number;
  ai_bike_total?: number;
  status?: string;
  auto_renewal?: boolean;
}

// Service Type Color Mapping
export const SERVICE_TYPE_COLORS: Record<string, string> = {
  BRAIN: 'bg-purple-100 text-purple-800',
  PULSE: 'bg-blue-100 text-blue-800',
  LYMPH: 'bg-green-100 text-green-800',
  RED: 'bg-red-100 text-red-800',
  AI_BIKE: 'bg-yellow-100 text-yellow-800'
};

// Service Type Icons
export const SERVICE_TYPE_ICONS: Record<string, string> = {
  BRAIN: '🧠',
  PULSE: '💓',
  LYMPH: '🌿',
  RED: '🔴',
  AI_BIKE: '🚴'
};

// Intensity Level Colors
export const INTENSITY_COLORS: Record<string, string> = {
  weak: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  strong: 'bg-red-100 text-red-800'
};

// Session Status Colors
export const SESSION_STATUS_COLORS: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  in_progress: 'bg-blue-100 text-blue-800',
  partial: 'bg-yellow-100 text-yellow-800',
  cancelled: 'bg-red-100 text-red-800'
};