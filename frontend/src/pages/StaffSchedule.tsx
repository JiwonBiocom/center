import { useState, useEffect } from 'react';
import { Save, Edit, Calendar, Users, Clock } from 'lucide-react';
import { api } from '../lib/api';

interface ScheduleData {
  staff_info: Record<string, Record<string, string>>;
  time_table: Record<string, Record<string, string>>;
}

interface StaffScheduleResponse {
  schedule_id: number;
  week_start_date: string;
  schedule_data: ScheduleData;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export default function StaffSchedule() {
  const [schedule, setSchedule] = useState<StaffScheduleResponse | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<ScheduleData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const days = ['월', '화', '수', '목', '금', '토', '일'];
  const timeSlots = ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21'];

  useEffect(() => {
    fetchCurrentSchedule();
  }, []);

  const fetchCurrentSchedule = async () => {
    try {
      setLoading(true);
      const response = await api.get<StaffScheduleResponse>('/staff-schedule/current');
      setSchedule(response.data);
      setEditData(response.data.schedule_data);
    } catch (error) {
      console.error('Error fetching schedule:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!schedule || !editData) return;

    try {
      setSaving(true);
      const response = await api.put<StaffScheduleResponse>(`/staff-schedule/${schedule.schedule_id}`, {
        schedule_data: editData,
        updated_by: 'admin'
      });

      setSchedule(response.data);
      setIsEditing(false);
      alert('근무표가 저장되었습니다.');
    } catch (error) {
      console.error('Error saving schedule:', error);
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setSaving(false);
    }
  };

  const handleCellChange = (section: 'staff_info' | 'time_table', staff: string, day: string, value: string) => {
    if (!editData) return;

    setEditData(prev => ({
      ...prev!,
      [section]: {
        ...prev![section],
        [staff]: {
          ...prev![section][staff],
          [day]: value
        }
      }
    }));
  };

  const formatWeekDate = (dateString: string) => {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${year}년 ${month}월 ${day}일 주`;
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!schedule || !editData) {
    return (
      <div className="p-8">
        <div className="text-center text-gray-500">
          <Calendar className="w-12 h-12 mx-auto mb-4" />
          <p>근무표를 불러올 수 없습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Users className="w-8 h-8" />
              직원 근무표
            </h1>
            <p className="text-gray-600 mt-2">
              {formatWeekDate(schedule.week_start_date)} 근무 일정
            </p>
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setEditData(schedule.schedule_data);
                  }}
                  className="px-4 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  disabled={saving}
                >
                  취소
                </button>
                <button
                  onClick={handleSave}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
                  disabled={saving}
                >
                  <Save className="w-4 h-4" />
                  {saving ? '저장 중...' : '저장'}
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center gap-2"
              >
                <Edit className="w-4 h-4" />
                수정
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-8">
        {/* 직원별 근무 정보 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">센터 근무</h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="border border-gray-300 p-3 bg-gray-50 text-left font-medium text-gray-900">
                      직원
                    </th>
                    {days.map(day => (
                      <th key={day} className="border border-gray-300 p-3 bg-gray-50 text-center font-medium text-gray-900 min-w-[120px]">
                        {day}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.keys(editData.staff_info).map(staff => (
                    <tr key={staff}>
                      <td className="border border-gray-300 p-3 font-medium text-gray-900 bg-gray-50">
                        {staff}
                      </td>
                      {days.map(day => (
                        <td key={`${staff}-${day}`} className="border border-gray-300 p-2">
                          {isEditing ? (
                            <textarea
                              value={editData.staff_info[staff]?.[day] || ''}
                              onChange={(e) => handleCellChange('staff_info', staff, day, e.target.value)}
                              className="w-full p-2 border border-gray-300 rounded resize-none text-sm"
                              rows={2}
                            />
                          ) : (
                            <div className="p-2 text-sm whitespace-pre-wrap min-h-[2.5rem]">
                              {editData.staff_info[staff]?.[day] || ''}
                            </div>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* 시간별 근무표 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Clock className="w-5 h-5" />
              타임 테이블
            </h2>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="border border-gray-300 p-3 bg-gray-50 text-left font-medium text-gray-900">
                      시간
                    </th>
                    {days.map(day => (
                      <th key={day} className="border border-gray-300 p-3 bg-gray-50 text-center font-medium text-gray-900 min-w-[120px]">
                        {day}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {timeSlots.map(time => (
                    <tr key={time}>
                      <td className="border border-gray-300 p-3 font-medium text-gray-900 bg-gray-50 text-center">
                        {time}:00
                      </td>
                      {days.map(day => (
                        <td key={`${time}-${day}`} className="border border-gray-300 p-2">
                          {isEditing ? (
                            <textarea
                              value={editData.time_table[time]?.[day] || ''}
                              onChange={(e) => handleCellChange('time_table', time, day, e.target.value)}
                              className="w-full p-2 border border-gray-300 rounded resize-none text-sm"
                              rows={2}
                            />
                          ) : (
                            <div className="p-2 text-sm whitespace-pre-wrap min-h-[2.5rem]">
                              {editData.time_table[time]?.[day] || ''}
                            </div>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* 업데이트 정보 */}
      <div className="mt-8 text-sm text-gray-500 text-center">
        <p>
          마지막 업데이트: {new Date(schedule.updated_at).toLocaleString('ko-KR')}
          {schedule.updated_by && ` (${schedule.updated_by})`}
        </p>
      </div>
    </div>
  );
}