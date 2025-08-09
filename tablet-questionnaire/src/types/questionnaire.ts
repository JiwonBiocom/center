export enum QuestionType {
  SINGLE_CHOICE = 'single_choice',
  MULTIPLE_CHOICE = 'multiple_choice',
  SCALE = 'scale',
  TEXT = 'text',
  NUMBER = 'number',
  DATE = 'date',
  BODY_MAP = 'body_map',
}

export enum QuestionnaireSection {
  BASIC = 'basic',
  HEALTH_STATUS = 'health_status',
  GOALS = 'goals',
  STRESS_MENTAL = 'stress_mental',
  DIGESTIVE = 'digestive',
  HORMONE_METABOLIC = 'hormone',
  MUSCULOSKELETAL = 'musculoskeletal',
}

export interface QuestionOption {
  value: string;
  label: string;
  score?: number;
  next_question?: string;
}

export interface ValidationRule {
  min?: number;
  max?: number;
  maxSelections?: number;
  pattern?: string;
}

export interface UIConfig {
  widget?: string;
  showLabels?: boolean;
  allowMultiple?: boolean;
}

export interface ConditionLogic {
  trigger_conditions?: {
    value?: {in?: string[]; gte?: number};
    score?: {gte?: number};
    activate_sections?: string[];
  };
}

export interface Question {
  question_id: number;
  template_id: number;
  section: QuestionnaireSection;
  question_type: QuestionType;
  question_code: string;
  question_text: string;
  question_subtext?: string;
  order_index: number;
  is_required: boolean;
  options?: QuestionOption[];
  validation_rules?: ValidationRule;
  ui_config?: UIConfig;
  condition_logic?: ConditionLogic;
  created_at: string;
  updated_at?: string;
}

export interface Answer {
  answer_id?: number;
  response_id: number;
  question_id: number;
  answer_value?: string;
  answer_number?: number;
  answer_json?: any;
  answer_date?: string;
  time_spent_seconds?: number;
  answered_at?: string;
}

export interface QuestionnaireTemplate {
  template_id: number;
  name: string;
  description?: string;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  questions: Question[];
}

export interface QuestionnaireResponse {
  response_id: number;
  customer_id: number;
  template_id: number;
  started_at: string;
  completed_at?: string;
  is_completed: boolean;
  completion_rate: number;
  device_id?: string;
  app_version?: string;
  answers: Answer[];
}

export interface QuestionnaireProgress {
  response_id: number;
  current_section: QuestionnaireSection;
  answered_questions: number;
  total_questions: number;
  completion_rate: number;
  next_question?: Question;
  estimated_time_remaining: number;
}

export interface StartQuestionnaireRequest {
  customer_id: number;
  template_id: number;
  device_id: string;
  app_version: string;
}

export interface SubmitAnswerRequest {
  question_id: number;
  answer: string | number | string[] | {[key: string]: any} | null;
  time_spent_seconds: number;
}