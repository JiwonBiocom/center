import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api } from '../lib/api'
import type { Notification, NotificationStats } from '../types/notification'
import { useAuth } from './AuthContext'

interface NotificationContextType {
  notifications: Notification[]
  stats: NotificationStats | null
  loading: boolean
  fetchNotifications: () => Promise<void>
  markAsRead: (notificationId: number) => Promise<void>
  markAllAsRead: () => Promise<void>
  deleteNotification: (notificationId: number) => Promise<void>
  createTestNotification: () => Promise<void>
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const useNotifications = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider')
  }
  return context
}

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [stats, setStats] = useState<NotificationStats | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchNotifications = useCallback(async () => {
    // 알림 기능 임시 비활성화 (백엔드 500 에러 해결까지)
    console.log('📢 알림 기능이 임시 비활성화되었습니다.')
    setNotifications([])
    setStats({ total: 0, unread: 0, by_type: {}, by_priority: {} })
    setLoading(false)
    return
    
    if (!user) return

    setLoading(true)
    try {
      // 알림 목록 조회 - 에러 시 빈 배열 반환
      try {
        const notificationsRes = await api.get('/api/v1/notifications/', { params: { limit: 50 } })
        setNotifications(notificationsRes.data)
      } catch (error) {
        console.warn('Notifications API not available:', error)
        setNotifications([])
      }
      
      // 통계 조회 - 에러 시 null 유지
      try {
        const statsRes = await api.get('/api/v1/notifications/stats/')
        setStats(statsRes.data)
      } catch (error) {
        console.warn('Notification stats API not available:', error)
        setStats(null)
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
    } finally {
      setLoading(false)
    }
  }, [user])

  const markAsRead = async (notificationId: number) => {
    try {
      await api.patch(`/api/v1/notifications/${notificationId}`)
      
      // 로컬 상태 업데이트
      setNotifications(prev => 
        prev.map(n => 
          n.notification_id === notificationId 
            ? { ...n, is_read: true, read_at: new Date().toISOString() }
            : n
        )
      )
      
      // 통계 업데이트
      if (stats) {
        setStats({
          ...stats,
          unread: Math.max(0, stats.unread - 1)
        })
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await api.post('/api/v1/notifications/mark-all-read')
      
      // 로컬 상태 업데이트
      const now = new Date().toISOString()
      setNotifications(prev => 
        prev.map(n => ({ ...n, is_read: true, read_at: now }))
      )
      
      // 통계 업데이트
      if (stats) {
        setStats({
          ...stats,
          unread: 0
        })
      }
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
    }
  }

  const deleteNotification = async (notificationId: number) => {
    try {
      await api.delete(`/api/v1/notifications/${notificationId}`)
      
      // 로컬 상태 업데이트
      setNotifications(prev => prev.filter(n => n.notification_id !== notificationId))
      
      // 통계 업데이트
      await fetchNotifications()
    } catch (error) {
      console.error('Failed to delete notification:', error)
    }
  }

  const createTestNotification = async () => {
    try {
      await api.post('/api/v1/notifications/test')
      await fetchNotifications()
    } catch (error) {
      console.error('Failed to create test notification:', error)
    }
  }

  // 초기 로드 및 주기적 갱신
  useEffect(() => {
    if (user) {
      fetchNotifications()
      
      // 30초마다 새로운 알림 확인
      const interval = setInterval(fetchNotifications, 30000)
      
      return () => clearInterval(interval)
    }
  }, [user, fetchNotifications])

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        stats,
        loading,
        fetchNotifications,
        markAsRead,
        markAllAsRead,
        deleteNotification,
        createTestNotification
      }}
    >
      {children}
    </NotificationContext.Provider>
  )
}