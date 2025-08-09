import { useState, useRef, useEffect } from 'react'
import { Bell, Check, Trash2, CheckCheck, ExternalLink } from 'lucide-react'
import { useNotifications } from '../contexts/NotificationContext'
import { NotificationType, NotificationPriority } from '../types/notification'
import type { NotificationTypeValue, NotificationPriorityValue, Notification as NotificationInterface } from '../types/notification'
import { formatDistanceToNow } from 'date-fns'
import { ko } from 'date-fns/locale'
import { Link } from 'react-router-dom'

export default function NotificationBell() {
  const { notifications, stats, markAsRead, markAllAsRead, deleteNotification } = useNotifications()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // 클릭 외부 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const getNotificationIcon = (type: NotificationTypeValue) => {
    switch (type) {
      case NotificationType.PACKAGE:
        return '📦'
      case NotificationType.KIT:
        return '🧪'
      case NotificationType.APPOINTMENT:
        return '📅'
      case NotificationType.SYSTEM:
        return '🔔'
      case NotificationType.PAYMENT:
        return '💰'
      case NotificationType.CUSTOMER:
        return '👤'
      default:
        return '📢'
    }
  }

  const getPriorityColor = (priority: NotificationPriorityValue) => {
    switch (priority) {
      case NotificationPriority.HIGH:
        return 'text-red-600'
      case NotificationPriority.MEDIUM:
        return 'text-yellow-600'
      case NotificationPriority.LOW:
        return 'text-gray-600'
      default:
        return 'text-gray-600'
    }
  }

  const handleNotificationClick = async (notification: NotificationInterface) => {
    if (!notification.is_read) {
      await markAsRead(notification.notification_id)
    }
    if (notification.action_url) {
      setIsOpen(false)
    }
  }

  const unreadNotifications = notifications.filter(n => !n.is_read)

  return (
    <div className="relative" ref={dropdownRef}>
      {/* 알림 벨 아이콘 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg"
      >
        <Bell className="w-6 h-6" />
        {stats && stats.unread > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
            {stats.unread > 99 ? '99+' : stats.unread}
          </span>
        )}
      </button>

      {/* 알림 드롭다운 */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {/* 헤더 */}
          <div className="px-4 py-3 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                알림 {stats && stats.unread > 0 && (
                  <span className="ml-2 text-sm text-gray-500">
                    ({stats.unread}개의 새 알림)
                  </span>
                )}
              </h3>
              {unreadNotifications.length > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
                >
                  <CheckCheck className="w-4 h-4" />
                  모두 읽음
                </button>
              )}
            </div>
          </div>

          {/* 알림 목록 */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <Bell className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>새로운 알림이 없습니다</p>
              </div>
            ) : (
              notifications.slice(0, 10).map((notification) => (
                <div
                  key={notification.notification_id}
                  className={`px-4 py-3 hover:bg-gray-50 transition-colors border-b border-gray-100 last:border-0 ${
                    !notification.is_read ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* 아이콘 */}
                    <span className="text-2xl flex-shrink-0">
                      {getNotificationIcon(notification.type)}
                    </span>

                    {/* 내용 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h4 className={`text-sm font-medium text-gray-900 ${
                            getPriorityColor(notification.priority)
                          }`}>
                            {notification.title}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-1">
                            {formatDistanceToNow(new Date(notification.created_at), {
                              addSuffix: true,
                              locale: ko
                            })}
                          </p>
                        </div>

                        {/* 액션 버튼 */}
                        <div className="flex items-center gap-1">
                          {notification.action_url && (
                            <Link
                              to={notification.action_url}
                              onClick={() => handleNotificationClick(notification)}
                              className="p-1 text-gray-400 hover:text-indigo-600"
                              title="바로가기"
                            >
                              <ExternalLink className="w-4 h-4" />
                            </Link>
                          )}
                          {!notification.is_read && (
                            <button
                              onClick={() => markAsRead(notification.notification_id)}
                              className="p-1 text-gray-400 hover:text-green-600"
                              title="읽음 표시"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => {
                              if (window.confirm('이 알림을 삭제하시겠습니까?')) {
                                deleteNotification(notification.notification_id)
                              }
                            }}
                            className="p-1 text-gray-400 hover:text-red-600"
                            title="삭제"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* 푸터 */}
          {notifications.length > 0 && (
            <div className="px-4 py-3 border-t border-gray-200">
              <Link
                to="/notifications"
                onClick={() => setIsOpen(false)}
                className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
              >
                모든 알림 보기
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}