export const NotificationType = {
  PACKAGE: 'package',
  KIT: 'kit',
  APPOINTMENT: 'appointment',
  SYSTEM: 'system',
  PAYMENT: 'payment',
  CUSTOMER: 'customer',
} as const

export const NotificationPriority = {
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
} as const

export type NotificationTypeValue = typeof NotificationType[keyof typeof NotificationType]
export type NotificationPriorityValue = typeof NotificationPriority[keyof typeof NotificationPriority]

export interface Notification {
  notification_id: number
  user_id?: number
  type: NotificationTypeValue
  title: string
  message: string
  is_read: boolean
  is_sent: boolean
  priority: NotificationPriorityValue
  action_url?: string
  related_id?: number
  created_at: string
  read_at?: string
  scheduled_for?: string
}

export interface NotificationStats {
  total: number
  unread: number
  by_type: Record<NotificationTypeValue, number>
  by_priority: Record<NotificationPriorityValue, number>
}

export interface NotificationSettings {
  user_id: number
  email_enabled: boolean
  sms_enabled: boolean
  push_enabled: boolean
  package_alerts: boolean
  appointment_reminders: boolean
  payment_notifications: boolean
  system_notifications: boolean
  marketing_notifications: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start?: string
  quiet_hours_end?: string
  created_at: string
  updated_at: string
}