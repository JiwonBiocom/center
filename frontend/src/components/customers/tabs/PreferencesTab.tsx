import { useState } from 'react';
import { Heart, Clock, Calendar, AlertCircle, Save } from 'lucide-react';

interface PreferencesTabProps {
  customerId: number;
  preferences: any;
  onUpdate?: (preferences: any) => void;
}

export default function PreferencesTab({ preferences, onUpdate }: PreferencesTabProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPreferences, setEditedPreferences] = useState(preferences || {
    preferred_services: [],
    preferred_time: '',
    preferred_days: [],
    preferred_staff: '',
    health_goals: '',
    health_concerns: '',
    exercise_frequency: '',
    stress_level: '',
    sleep_quality: '',
    dietary_restrictions: '',
    medical_conditions: '',
    medications: '',
    notes: ''
  });

  const services = ['브레인', '펄스', '림프', '레드', 'AI바이크'];
  const weekDays = ['월', '화', '수', '목', '금', '토', '일'];
  const timeSlots = ['오전', '오후', '저녁'];

  const handleServiceToggle = (service: string) => {
    const currentServices = editedPreferences.preferred_services || [];
    const newServices = currentServices.includes(service)
      ? currentServices.filter((s: string) => s !== service)
      : [...currentServices, service];
    
    setEditedPreferences({
      ...editedPreferences,
      preferred_services: newServices
    });
  };

  const handleDayToggle = (day: string) => {
    const currentDays = editedPreferences.preferred_days || [];
    const newDays = currentDays.includes(day)
      ? currentDays.filter((d: string) => d !== day)
      : [...currentDays, day];
    
    setEditedPreferences({
      ...editedPreferences,
      preferred_days: newDays
    });
  };

  const handleSave = () => {
    // API 호출 로직 추가
    if (onUpdate) {
      onUpdate(editedPreferences);
    }
    setIsEditing(false);
  };

  return (
    <div className="space-y-6">
      {/* 편집 버튼 */}
      <div className="flex justify-end">
        {!isEditing ? (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
          >
            수정
          </button>
        ) : (
          <div className="space-x-2">
            <button
              onClick={() => {
                setEditedPreferences(preferences);
                setIsEditing(false);
              }}
              className="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-md"
            >
              취소
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
            >
              <Save className="h-4 w-4" />
              저장
            </button>
          </div>
        )}
      </div>

      {/* 서비스 선호도 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Heart className="h-5 w-5 text-red-500" />
          선호 서비스
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {services.map((service) => (
            <label
              key={service}
              className={`
                flex items-center justify-center p-3 rounded-lg border cursor-pointer transition-all
                ${isEditing ? 'hover:border-blue-400' : 'cursor-default'}
                ${editedPreferences.preferred_services?.includes(service)
                  ? 'bg-blue-50 border-blue-400 text-blue-700'
                  : 'bg-gray-50 border-gray-200'
                }
              `}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={editedPreferences.preferred_services?.includes(service)}
                onChange={() => isEditing && handleServiceToggle(service)}
                disabled={!isEditing}
              />
              <span className="font-medium">{service}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 시간 선호도 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="h-5 w-5 text-blue-500" />
          선호 시간대
        </h4>
        <div className="grid grid-cols-3 gap-3 mb-4">
          {timeSlots.map((time) => (
            <label
              key={time}
              className={`
                flex items-center justify-center p-3 rounded-lg border cursor-pointer transition-all
                ${isEditing ? 'hover:border-blue-400' : 'cursor-default'}
                ${editedPreferences.preferred_time === time
                  ? 'bg-blue-50 border-blue-400 text-blue-700'
                  : 'bg-gray-50 border-gray-200'
                }
              `}
            >
              <input
                type="radio"
                name="preferred_time"
                className="sr-only"
                checked={editedPreferences.preferred_time === time}
                onChange={() => isEditing && setEditedPreferences({ ...editedPreferences, preferred_time: time })}
                disabled={!isEditing}
              />
              <span className="font-medium">{time}</span>
            </label>
          ))}
        </div>

        <h5 className="font-medium mb-2 flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          선호 요일
        </h5>
        <div className="grid grid-cols-7 gap-2">
          {weekDays.map((day) => (
            <label
              key={day}
              className={`
                flex items-center justify-center p-2 rounded-lg border cursor-pointer transition-all text-sm
                ${isEditing ? 'hover:border-blue-400' : 'cursor-default'}
                ${editedPreferences.preferred_days?.includes(day)
                  ? 'bg-blue-50 border-blue-400 text-blue-700'
                  : 'bg-gray-50 border-gray-200'
                }
              `}
            >
              <input
                type="checkbox"
                className="sr-only"
                checked={editedPreferences.preferred_days?.includes(day)}
                onChange={() => isEditing && handleDayToggle(day)}
                disabled={!isEditing}
              />
              <span className="font-medium">{day}</span>
            </label>
          ))}
        </div>
      </div>

      {/* 건강 정보 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-yellow-500" />
          건강 정보
        </h4>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">건강 목표</label>
            <textarea
              className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
              rows={2}
              value={editedPreferences.health_goals || ''}
              onChange={(e) => setEditedPreferences({ ...editedPreferences, health_goals: e.target.value })}
              disabled={!isEditing}
              placeholder="예: 체중 감량, 스트레스 관리, 수면 개선"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">건강 우려사항</label>
            <textarea
              className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
              rows={2}
              value={editedPreferences.health_concerns || ''}
              onChange={(e) => setEditedPreferences({ ...editedPreferences, health_concerns: e.target.value })}
              disabled={!isEditing}
              placeholder="예: 허리 통증, 불면증, 만성 피로"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">운동 빈도</label>
              <select
                className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                value={editedPreferences.exercise_frequency || ''}
                onChange={(e) => setEditedPreferences({ ...editedPreferences, exercise_frequency: e.target.value })}
                disabled={!isEditing}
              >
                <option value="">선택하세요</option>
                <option value="none">운동 안함</option>
                <option value="1-2">주 1-2회</option>
                <option value="3-4">주 3-4회</option>
                <option value="5+">주 5회 이상</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">스트레스 수준</label>
              <select
                className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                value={editedPreferences.stress_level || ''}
                onChange={(e) => setEditedPreferences({ ...editedPreferences, stress_level: e.target.value })}
                disabled={!isEditing}
              >
                <option value="">선택하세요</option>
                <option value="low">낮음</option>
                <option value="medium">보통</option>
                <option value="high">높음</option>
                <option value="very_high">매우 높음</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">복용 중인 약물</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={editedPreferences.medications || ''}
              onChange={(e) => setEditedPreferences({ ...editedPreferences, medications: e.target.value })}
              disabled={!isEditing}
              placeholder="복용 중인 약물이 있다면 입력하세요"
            />
          </div>
        </div>
      </div>

      {/* 추가 메모 */}
      <div className="bg-white rounded-lg border p-6">
        <h4 className="text-lg font-semibold mb-4">추가 메모</h4>
        <textarea
          className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
          rows={4}
          value={editedPreferences.notes || ''}
          onChange={(e) => setEditedPreferences({ ...editedPreferences, notes: e.target.value })}
          disabled={!isEditing}
          placeholder="고객의 특별한 요청사항이나 주의사항을 입력하세요"
        />
      </div>
    </div>
  );
}