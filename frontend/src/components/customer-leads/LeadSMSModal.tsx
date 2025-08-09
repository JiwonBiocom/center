import React, { useState } from 'react';
import { X, Send, Users, MessageSquare, AlertCircle } from 'lucide-react';
import { api } from '../../lib/api';

interface CustomerLead {
  lead_id: number;
  name: string;
  phone?: string;
  lead_channel?: string;
  status: string;
  db_entry_date?: string;
}

interface LeadSMSModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedLeads: CustomerLead[];
  onSuccess?: () => void;
}

const LEAD_SMS_TEMPLATES = {
  initial_contact: {
    name: '초기 상담 안내',
    description: '신규 유입고객에게 첫 연락 메시지를 보냅니다.',
    variables: []
  },
  visit_invitation: {
    name: '방문 상담 권유',
    description: '전화 상담 후 방문 상담을 권유합니다.',
    variables: []
  },
  follow_up: {
    name: '후속 연락',
    description: '상담 후 추가 연락을 위한 메시지입니다.',
    variables: []
  },
  promotion: {
    name: '프로모션 안내',
    description: '신규 고객 대상 특별 혜택을 안내합니다.',
    variables: ['title', 'content']
  },
  custom: {
    name: '직접 입력',
    description: '메시지를 직접 작성합니다.',
    variables: []
  }
};

export default function LeadSMSModal({ isOpen, onClose, selectedLeads, onSuccess }: LeadSMSModalProps) {
  const [messageType, setMessageType] = useState<string>('custom');
  const [customMessage, setCustomMessage] = useState('');
  const [templateData, setTemplateData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [remainingSMS, setRemainingSMS] = useState<any>(null);
  const [error, setError] = useState('');

  // SMS 잔여건수 조회
  React.useEffect(() => {
    if (isOpen) {
      fetchRemainingSMS();
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

  // 전화번호가 있는 리드만 필터링
  const validLeads = selectedLeads.filter(lead => lead.phone && lead.phone.trim());

  const handleSend = async () => {
    if (validLeads.length === 0) {
      setError('전화번호가 있는 유입고객이 없습니다.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (messageType === 'custom') {
        // 직접 입력한 메시지 발송
        await api.post('/sms/send-leads', {
          lead_ids: validLeads.map(l => l.lead_id),
          message: customMessage
        });
      } else {
        // 템플릿 메시지 발송
        await api.post('/sms/send-leads-template', {
          lead_ids: validLeads.map(l => l.lead_id),
          template_type: messageType,
          template_data: templateData
        });
      }

      alert(`SMS가 성공적으로 발송되었습니다. (발송 대상: ${validLeads.length}명)`);
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
          <h2 className="text-xl font-semibold">유입고객 SMS 발송</h2>
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
            <Users className="h-4 w-4" />
            <span className="text-sm font-medium">
              선택된 유입고객: {selectedLeads.length}명
            </span>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            {selectedLeads.slice(0, 3).map(l => l.name).join(', ')}
            {selectedLeads.length > 3 && ` 외 ${selectedLeads.length - 3}명`}
          </div>
          
          {/* 전화번호 없는 고객 경고 */}
          {validLeads.length !== selectedLeads.length && (
            <div className="mt-2 p-2 bg-yellow-50 rounded border-l-4 border-yellow-400">
              <p className="text-xs text-yellow-700">
                ⚠️ 전화번호가 없는 {selectedLeads.length - validLeads.length}명은 발송에서 제외됩니다.
                (실제 발송 대상: {validLeads.length}명)
              </p>
            </div>
          )}
        </div>

        {/* 메시지 타입 선택 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            메시지 유형
          </label>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(LEAD_SMS_TEMPLATES).map(([key, template]) => (
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

        {/* 메시지 입력 */}
        {messageType === 'custom' ? (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              메시지 내용
            </label>
            <textarea
              value={customMessage}
              onChange={(e) => setCustomMessage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              rows={6}
              placeholder="메시지를 입력하세요. (90자 이상은 LMS로 발송됩니다)"
            />
            <div className="mt-1 text-xs text-gray-500 text-right">
              {customMessage.length}자 / {customMessage.length > 90 ? 'LMS' : 'SMS'}
            </div>
          </div>
        ) : messageType === 'promotion' ? (
          <div className="mb-4 space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                프로모션 제목
              </label>
              <input
                type="text"
                value={templateData.title || ''}
                onChange={(e) => setTemplateData({ ...templateData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="예: 신규 고객 특별 할인"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                프로모션 내용
              </label>
              <textarea
                value={templateData.content || ''}
                onChange={(e) => setTemplateData({ ...templateData, content: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                rows={3}
                placeholder="프로모션 상세 내용을 입력하세요"
              />
            </div>
          </div>
        ) : (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              메시지 미리보기
            </label>
            <div className="p-4 bg-gray-50 rounded-lg">
              <MessageSquare className="h-5 w-5 text-gray-400 mb-2" />
              {messageType === 'initial_contact' ? (
                <div className="text-sm text-gray-600 whitespace-pre-wrap">
                  {validLeads.length === 1 ? 
                    `[AIBIO 센터] 안녕하세요!
${validLeads[0].name}님, AIBIO 바이오해킹 센터입니다.

문의해 주셔서 감사합니다. 
개인 맞춤 건강관리 프로그램에 대해 
자세히 상담드리겠습니다.

상담 예약: 02-2039-2783
센터 위치: 강남구 테헤란로` :
                    `[AIBIO 센터] 안녕하세요!
{고객명}님, AIBIO 바이오해킹 센터입니다.

문의해 주셔서 감사합니다. 
개인 맞춤 건강관리 프로그램에 대해 
자세히 상담드리겠습니다.

상담 예약: 02-2039-2783
센터 위치: 강남구 테헤란로`}
                </div>
              ) : messageType === 'visit_invitation' ? (
                <div className="text-sm text-gray-600 whitespace-pre-wrap">
                  {validLeads.length === 1 ? 
                    `[AIBIO 센터]
${validLeads[0].name}님, 전화 상담 감사했습니다.

더 정확한 검사와 상담을 위해
센터 방문을 추천드립니다.

✓ 정밀 체성분 분석
✓ 1:1 맞춤 상담
✓ 시설 둘러보기

예약: 02-2039-2783` :
                    `[AIBIO 센터]
{고객명}님, 전화 상담 감사했습니다.

더 정확한 검사와 상담을 위해
센터 방문을 추천드립니다.

✓ 정밀 체성분 분석
✓ 1:1 맞춤 상담
✓ 시설 둘러보기

예약: 02-2039-2783`}
                </div>
              ) : messageType === 'follow_up' ? (
                <div className="text-sm text-gray-600 whitespace-pre-wrap">
                  {validLeads.length === 1 ? 
                    `[AIBIO 센터]
${validLeads[0].name}님, 안녕하세요.

지난 상담 내용 검토해보셨나요?
추가 궁금한 점이 있으시면
언제든 연락주세요.

무료 체험 프로그램도 
준비되어 있습니다.

문의: 02-2039-2783` :
                    `[AIBIO 센터]
{고객명}님, 안녕하세요.

지난 상담 내용 검토해보셨나요?
추가 궁금한 점이 있으시면
언제든 연락주세요.

무료 체험 프로그램도 
준비되어 있습니다.

문의: 02-2039-2783`}
                </div>
              ) : (
                <p className="text-sm text-gray-600">
                  선택한 템플릿으로 자동 생성된 메시지가 발송됩니다.
                </p>
              )}
              
              {/* 메시지 길이 표시 */}
              {(messageType === 'initial_contact' || messageType === 'visit_invitation' || messageType === 'follow_up') && (
                <div className="mt-2 text-xs text-gray-500 text-right">
                  약 {messageType === 'initial_contact' ? '100' : messageType === 'visit_invitation' ? '85' : '95'}자 / LMS
                </div>
              )}
              
              {validLeads.length > 1 && (
                <div className="mt-3 p-2 bg-blue-50 rounded">
                  <p className="text-xs text-blue-700">
                    <span className="font-medium">참고:</span> {"{고객명}"} 부분은 각 고객의 실제 이름으로 자동 치환됩니다.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

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
            disabled={loading || (messageType === 'custom' && !customMessage.trim()) || validLeads.length === 0}
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                발송 중...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                {validLeads.length}명에게 발송
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}