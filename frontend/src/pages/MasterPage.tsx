import { useState } from 'react'
import { Shield, Users, Key, AlertTriangle, Trash2, RefreshCw, UserCog } from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../lib/api'
import toast from 'react-hot-toast'
import BaseModal from '../components/common/BaseModal'

interface User {
  user_id: number
  email: string
  name: string
  role: string
  is_active: boolean
}

interface SystemStats {
  users: {
    total: number
    active: number
    by_role: {
      master: number
      admin: number
      manager: number
      staff: number
    }
  }
  customers: {
    total: number
  }
  services: {
    total: number
  }
  payments: {
    total: number
  }
}

export default function MasterPage() {
  const queryClient = useQueryClient()
  const [selectedUsers, setSelectedUsers] = useState<number[]>([])
  const [passwordResetModal, setPasswordResetModal] = useState<{ isOpen: boolean; user?: User }>({ isOpen: false })
  const [newPassword, setNewPassword] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [roleChangeModal, setRoleChangeModal] = useState<{ isOpen: boolean; user?: User; newRole?: string }>({ isOpen: false })

  // 시스템 통계 조회
  const { data: stats } = useQuery<SystemStats>({
    queryKey: ['system-stats'],
    queryFn: async () => {
      const response = await api.get('/master/system-stats')
      return response.data
    }
  })

  // 사용자 목록 조회
  const { data: users = [], isLoading } = useQuery<User[]>({
    queryKey: ['master-users'],
    queryFn: async () => {
      const response = await api.get('/master/users')
      return response.data
    }
  })

  // 비밀번호 초기화
  const resetPasswordMutation = useMutation({
    mutationFn: async ({ userId, password }: { userId: number; password: string }) => {
      await api.post('/master/reset-password', {
        user_id: userId,
        new_password: password
      })
    },
    onSuccess: () => {
      toast.success('비밀번호가 초기화되었습니다')
      setPasswordResetModal({ isOpen: false })
      setNewPassword('')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '비밀번호 초기화 실패')
    }
  })

  // 사용자 삭제
  const deleteUsersMutation = useMutation({
    mutationFn: async (userIds: number[]) => {
      await api.delete('/master/users', {
        data: { user_ids: userIds }
      })
    },
    onSuccess: () => {
      toast.success('사용자가 삭제되었습니다')
      setSelectedUsers([])
      setConfirmDelete(false)
      queryClient.invalidateQueries({ queryKey: ['master-users'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '사용자 삭제 실패')
    }
  })

  // 권한 변경
  const changeRoleMutation = useMutation({
    mutationFn: async ({ userId, newRole }: { userId: number; newRole: string }) => {
      await api.put(`/master/users/${userId}/role`, null, {
        params: { new_role: newRole }
      })
    },
    onSuccess: () => {
      toast.success('권한이 변경되었습니다')
      setRoleChangeModal({ isOpen: false })
      queryClient.invalidateQueries({ queryKey: ['master-users'] })
      queryClient.invalidateQueries({ queryKey: ['system-stats'] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '권한 변경 실패')
    }
  })

  const handlePasswordReset = () => {
    if (!passwordResetModal.user || !newPassword) return

    if (newPassword.length < 6) {
      toast.error('비밀번호는 최소 6자 이상이어야 합니다')
      return
    }

    resetPasswordMutation.mutate({
      userId: passwordResetModal.user.user_id,
      password: newPassword
    })
  }

  const handleDeleteUsers = () => {
    if (selectedUsers.length === 0) {
      toast.error('삭제할 사용자를 선택하세요')
      return
    }

    deleteUsersMutation.mutate(selectedUsers)
  }

  const handleRoleChange = () => {
    if (!roleChangeModal.user || !roleChangeModal.newRole) return

    changeRoleMutation.mutate({
      userId: roleChangeModal.user.user_id,
      newRole: roleChangeModal.newRole
    })
  }

  const roleColors = {
    master: 'bg-red-100 text-red-800',
    admin: 'bg-purple-100 text-purple-800',
    manager: 'bg-blue-100 text-blue-800',
    staff: 'bg-gray-100 text-gray-800'
  }

  const roleLabels = {
    master: '마스터',
    admin: '관리자',
    manager: '매니저',
    staff: '직원'
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Shield className="w-7 h-7 text-red-600" />
          시스템 관리 (마스터)
        </h1>
        <p className="text-sm text-gray-600 mt-1">시스템 전체를 관리하는 최고 권한 페이지입니다</p>
      </div>

      {/* 시스템 통계 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전체 사용자</p>
              <p className="text-2xl font-bold">{stats?.users.total || 0}</p>
              <p className="text-xs text-gray-500 mt-1">활성: {stats?.users.active || 0}</p>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전체 고객</p>
              <p className="text-2xl font-bold">{stats?.customers.total || 0}</p>
            </div>
            <Users className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">서비스 이용</p>
              <p className="text-2xl font-bold">{stats?.services.total || 0}</p>
            </div>
            <Shield className="w-8 h-8 text-purple-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전체 결제</p>
              <p className="text-2xl font-bold">{stats?.payments.total || 0}</p>
            </div>
            <Shield className="w-8 h-8 text-yellow-500" />
          </div>
        </div>
      </div>

      {/* 권한별 사용자 수 */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-lg font-semibold mb-4">권한별 사용자</h2>
        <div className="grid grid-cols-4 gap-4">
          {Object.entries(stats?.users.by_role || {}).map(([role, count]) => (
            <div key={role} className="text-center">
              <p className="text-sm text-gray-600">{roleLabels[role as keyof typeof roleLabels]}</p>
              <p className="text-xl font-bold">{count}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 사용자 관리 */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">사용자 관리</h2>
            {selectedUsers.length > 0 && (
              <button
                onClick={() => setConfirmDelete(true)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                선택 삭제 ({selectedUsers.length})
              </button>
            )}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  <input
                    type="checkbox"
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedUsers(users.map(u => u.user_id))
                      } else {
                        setSelectedUsers([])
                      }
                    }}
                    checked={selectedUsers.length === users.length && users.length > 0}
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이름</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">이메일</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">권한</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">상태</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">작업</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(user.user_id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedUsers([...selectedUsers, user.user_id])
                        } else {
                          setSelectedUsers(selectedUsers.filter(id => id !== user.user_id))
                        }
                      }}
                    />
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{user.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${roleColors[user.role as keyof typeof roleColors]}`}>
                      {roleLabels[user.role as keyof typeof roleLabels]}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? '활성' : '비활성'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setPasswordResetModal({ isOpen: true, user })}
                        className="text-blue-600 hover:text-blue-800"
                        title="비밀번호 초기화"
                      >
                        <Key className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setRoleChangeModal({ isOpen: true, user, newRole: user.role })}
                        className="text-purple-600 hover:text-purple-800"
                        title="권한 변경"
                      >
                        <UserCog className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 비밀번호 초기화 모달 */}
      <BaseModal
        isOpen={passwordResetModal.isOpen}
        onClose={() => {
          setPasswordResetModal({ isOpen: false })
          setNewPassword('')
        }}
        title="비밀번호 초기화"
      >
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600">
              <span className="font-semibold">{passwordResetModal.user?.name}</span>님의 비밀번호를 초기화합니다.
            </p>
            <p className="text-xs text-gray-500 mt-1">{passwordResetModal.user?.email}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              새 비밀번호
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="6자 이상 입력"
            />
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={() => {
                setPasswordResetModal({ isOpen: false })
                setNewPassword('')
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              취소
            </button>
            <button
              onClick={handlePasswordReset}
              disabled={!newPassword || resetPasswordMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {resetPasswordMutation.isPending ? '처리 중...' : '초기화'}
            </button>
          </div>
        </div>
      </BaseModal>

      {/* 권한 변경 모달 */}
      <BaseModal
        isOpen={roleChangeModal.isOpen}
        onClose={() => setRoleChangeModal({ isOpen: false })}
        title="권한 변경"
      >
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600">
              <span className="font-semibold">{roleChangeModal.user?.name}</span>님의 권한을 변경합니다.
            </p>
            <p className="text-xs text-gray-500 mt-1">{roleChangeModal.user?.email}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              새 권한
            </label>
            <select
              value={roleChangeModal.newRole}
              onChange={(e) => setRoleChangeModal({ ...roleChangeModal, newRole: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="staff">직원</option>
              <option value="manager">매니저</option>
              <option value="admin">관리자</option>
              <option value="master">마스터</option>
            </select>
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={() => setRoleChangeModal({ isOpen: false })}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              취소
            </button>
            <button
              onClick={handleRoleChange}
              disabled={changeRoleMutation.isPending}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
            >
              {changeRoleMutation.isPending ? '처리 중...' : '변경'}
            </button>
          </div>
        </div>
      </BaseModal>

      {/* 삭제 확인 모달 */}
      <BaseModal
        isOpen={confirmDelete}
        onClose={() => setConfirmDelete(false)}
        title="사용자 삭제 확인"
      >
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
            <div>
              <p className="text-sm text-gray-700">
                선택한 {selectedUsers.length}명의 사용자를 삭제하시겠습니까?
              </p>
              <p className="text-xs text-gray-500 mt-1">
                삭제된 사용자는 시스템에 접근할 수 없게 됩니다.
              </p>
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={() => setConfirmDelete(false)}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              취소
            </button>
            <button
              onClick={handleDeleteUsers}
              disabled={deleteUsersMutation.isPending}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {deleteUsersMutation.isPending ? '삭제 중...' : '삭제'}
            </button>
          </div>
        </div>
      </BaseModal>
    </div>
  )
}
