import { useState, useEffect } from 'react';
import { X, User, Users, Search, Check } from 'lucide-react';
import { api } from '../../lib/api';

interface Staff {
  user_id: number;
  username: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
}

interface StaffAssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAssign: (staffId: number) => void;
  selectedLeadsCount: number;
  currentStaffId?: number;
}

export default function StaffAssignmentModal({
  isOpen,
  onClose,
  onAssign,
  selectedLeadsCount,
  currentStaffId
}: StaffAssignmentModalProps) {
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStaffId, setSelectedStaffId] = useState<number | null>(currentStaffId || null);

  useEffect(() => {
    if (isOpen) {
      fetchStaffList();
    }
  }, [isOpen]);

  const fetchStaffList = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/users/', {
        params: { is_active: true }
      });
      setStaffList(response.data);
    } catch (error) {
      console.error('Failed to fetch staff list:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredStaff = staffList.filter(staff => 
    staff.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    staff.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    staff.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAssign = () => {
    if (selectedStaffId) {
      onAssign(selectedStaffId);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full max-h-[80vh] overflow-hidden flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">담당자 지정</h2>
              <p className="text-sm text-gray-600 mt-1">
                {selectedLeadsCount}명의 고객에게 담당자를 지정합니다
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-4 border-b">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="이름, 아이디, 이메일로 검색"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">직원 목록을 불러오는 중...</p>
            </div>
          ) : filteredStaff.length === 0 ? (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">검색 결과가 없습니다.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredStaff.map((staff) => (
                <div
                  key={staff.user_id}
                  onClick={() => setSelectedStaffId(staff.user_id)}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedStaffId === staff.user_id
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        selectedStaffId === staff.user_id ? 'bg-indigo-600' : 'bg-gray-200'
                      }`}>
                        <User className={`w-5 h-5 ${
                          selectedStaffId === staff.user_id ? 'text-white' : 'text-gray-600'
                        }`} />
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{staff.name}</div>
                        <div className="text-sm text-gray-500">
                          @{staff.username} · {staff.role === 'admin' ? '관리자' : '직원'}
                        </div>
                      </div>
                    </div>
                    {selectedStaffId === staff.user_id && (
                      <Check className="w-5 h-5 text-indigo-600" />
                    )}
                  </div>
                  {staff.user_id === currentStaffId && (
                    <div className="mt-2 text-xs text-indigo-600">현재 담당자</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-6 border-t border-gray-200">
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              취소
            </button>
            <button
              onClick={handleAssign}
              disabled={!selectedStaffId}
              className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              지정하기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}