import React, { useState } from 'react';
import { X, Send, User, MessageSquare, AlertCircle } from 'lucide-react';
import { api } from '../../lib/api';

interface CustomerLead {
  lead_id: number;
  name: string;
  phone?: string;
  lead_channel?: string;
  status: string;
  db_entry_date?: string;
}

interface IndividualLeadSMSModalProps {
  isOpen: boolean;
  onClose: () => void;
  lead: CustomerLead;
  onSuccess?: () => void;
}

const INDIVIDUAL_SMS_TEMPLATES = {
  initial_contact: {
    name: '초기 상담 안내',
    description: '첫 연락 시 사용하는 메시지입니다.',
    message: `[AIBIO 센터] 안녕하세요!
{name}님, AIBIO 바이오해킹 센터입니다.

문의해 주셔서 감사합니다. 
개인 맞춤 건강관리 프로그램에 대해 
자세히 상담드리겠습니다.

상담 예약: 02-2039-2783
센터 위치: 강남구 테헤란로`
  },
  visit_invitation: {
    name: '방문 상담 권유',
    description: '전화 상담 후 방문을 권유할 때 사용합니다.',
    message: `[AIBIO 센터]
{name}님, 전화 상담 감사했습니다.

더 정확한 검사와 상담을 위해
센터 방문을 추천드립니다.

✓ 정밀 체성분 분석
✓ 1:1 맞춤 상담
✓ 시설 둘러보기

예약: 02-2039-2783`
  },
  follow_up: {
    name: '후속 연락',
    description: '상담 후 추가 연락이 필요할 때 사용합니다.',
    message: `[AIBIO 센터]
{name}님, 안녕하세요.

지난 상담 내용 검토해보셨나요?
추가 궁금한 점이 있으시면
언제든 연락주세요.

무료 체험 프로그램도 
준비되어 있습니다.

문의: 02-2039-2783`
  },
  reminder: {
    name: '예약 리마인더',
    description: '예약 일정을 상기시킬 때 사용합니다.',
    message: `[AIBIO 센터] 예약 안내
{name}님, 안녕하세요.

예약하신 상담 일정을 
다시 한 번 안내드립니다.

궁금한 점이 있으시면
언제든 연락주세요.

문의: 02-2039-2783`
  },
  custom: {
    name: '직접 입력',
    description: '메시지를 직접 작성합니다.',
    message: ''
  }
};

export default function IndividualLeadSMSModal({ isOpen, onClose, lead, onSuccess }: IndividualLeadSMSModalProps) {
  const [messageType, setMessageType] = useState<string>('initial_contact');
  const [customMessage, setCustomMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [remainingSMS, setRemainingSMS] = useState<any>(null);
  const [error, setError] = useState('');

  // SMS 잔여건수 조회
  React.useEffect(() => {
    if (isOpen) {
      fetchRemainingSMS();
      setError('');
      setMessageType('initial_contact');
      setCustomMessage('');
    }
  }, [isOpen]);

  const fetchRemainingSMS = async () => {
    try {
      const response = await api.get('/sms/remain');
      setRemainingSMS(response.data);
    } catch (error) {
      console.error('SMS 잔여건수 조회 실패:', error);
      setRemainingSMS(null);
    }
  };

  const getCurrentMessage = () => {
    if (messageType === 'custom') {
      return customMessage;
    } else {
      const template = INDIVIDUAL_SMS_TEMPLATES[messageType as keyof typeof INDIVIDUAL_SMS_TEMPLATES];
      return template.message.replace('{name}', lead.name);
    }
  };

  const handleSend = async () => {
    if (!lead.phone) {
      setError('전화번호가 등록되지 않은 고객입니다.');
      return;
    }

    const message = getCurrentMessage();
    if (!message.trim()) {
      setError('메시지를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (messageType === 'custom') {
        // 직접 입력한 메시지 발송
        await api.post('/sms/send-leads', {
          lead_ids: [lead.lead_id],
          message: message
        });
      } else {
        // 템플릿 메시지 발송
        await api.post('/sms/send-leads-template', {
          lead_ids: [lead.lead_id],
          template_type: messageType
        });
      }

      alert(`${lead.name}님에게 SMS가 성공적으로 발송되었습니다.`);
      onSuccess?.();
      onClose();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'SMS 발송에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">개별 SMS 발송</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* 잔여 SMS 표시 */}
        {remainingSMS && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center gap-2 text-blue-700">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">
                SMS 잔여: {remainingSMS.sms_count}건 | 
                LMS 잔여: {remainingSMS.lms_count}건
              </span>
            </div>
          </div>
        )}

        {/* 수신자 정보 */}
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2 text-gray-700">
            <User className="h-4 w-4" />
            <span className="text-sm font-medium">
              수신자: {lead.name}
            </span>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            전화번호: {lead.phone || '미등록'}
          </div>
          <div className="mt-1 text-xs text-gray-500">
            유입경로: {lead.lead_channel || '미분류'} | 상태: {lead.status}
          </div>
        </div>

        {/* 메시지 타입 선택 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            메시지 유형
          </label>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(INDIVIDUAL_SMS_TEMPLATES).map(([key, template]) => (
              <button
                key={key}
                onClick={() => setMessageType(key)}
                className={`p-3 rounded-lg border-2 text-left transition-colors ${
                  messageType === key
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium text-sm">{template.name}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {template.description}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* 메시지 입력/미리보기 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {messageType === 'custom' ? '메시지 내용' : '메시지 미리보기'}
          </label>
          {messageType === 'custom' ? (
            <textarea
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              rows={8}
              placeholder="메시지를 입력하세요. (90자 이상은 LMS로 발송됩니다)"
            />
          ) : (
            <div className="p-4 bg-gray-50 rounded-lg">
              <MessageSquare className="h-5 w-5 text-gray-400 mb-2" />
              <div className="text-sm text-gray-600 whitespace-pre-wrap">
                {getCurrentMessage()}
              </div>
            </div>
          )}
          <div className="mt-1 text-xs text-gray-500 text-right">
            {getCurrentMessage().length}자 / {getCurrentMessage().length > 90 ? 'LMS' : 'SMS'}
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* 버튼 */}
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            취소
          </button>
          <button
            onClick={handleSend}
            disabled={loading || !lead.phone || !getCurrentMessage().trim()}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                발송 중...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                {lead.name}님에게 발송
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}