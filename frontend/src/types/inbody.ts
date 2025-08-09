export interface InBodyRecord {
  record_id: number;
  customer_id: number;
  measurement_date: string;
  weight?: number;
  body_fat_percentage?: number;
  skeletal_muscle_mass?: number;
  extracellular_water_ratio?: number;
  phase_angle?: number;
  visceral_fat_level?: number;
  notes?: string;
  measured_by?: string;
  created_at: string;
  updated_at?: string;
}

export interface InBodyRecordCreate {
  customer_id: number;
  measurement_date: string;
  weight?: number;
  body_fat_percentage?: number;
  skeletal_muscle_mass?: number;
  extracellular_water_ratio?: number;
  phase_angle?: number;
  visceral_fat_level?: number;
  notes?: string;
  measured_by?: string;
}

export interface InBodyRecordUpdate {
  measurement_date?: string;
  weight?: number;
  body_fat_percentage?: number;
  skeletal_muscle_mass?: number;
  extracellular_water_ratio?: number;
  phase_angle?: number;
  visceral_fat_level?: number;
  notes?: string;
  measured_by?: string;
}

export interface InBodyRecordSummary {
  total_records: number;
  latest_record?: InBodyRecord;
  weight_trend?: 'increasing' | 'decreasing' | 'stable';
  body_fat_trend?: 'increasing' | 'decreasing' | 'stable';
}