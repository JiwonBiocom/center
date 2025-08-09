import React, { useState } from 'react';
import { X, Send, Users, MessageSquare, AlertCircle } from 'lucide-react';
import { api } from '../lib/api';

interface SMSModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedCustomers: any[];
  onSuccess?: () => void;
}

const SMS_TEMPLATES = {
  birthday: {
    name: '생일 축하',
    description: '생일 고객에게 축하 메시지를 보냅니다.',
    variables: []
  },
  dormant: {
    name: '휴면 고객 재활성화',
    description: '오랫동안 방문하지 않은 고객에게 재방문을 유도합니다.',
    variables: []
  },
  promotion: {
    name: '프로모션 안내',
    description: '특별 할인이나 이벤트를 안내합니다.',
    variables: ['title', 'content']
  },
  custom: {
    name: '직접 입력',
    description: '메시지를 직접 작성합니다.',
    variables: []
  }
};

export default function SMSModal({ isOpen, onClose, selectedCustomers, onSuccess }: SMSModalProps) {
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
      // 잔여건수 조회 실패해도 모달은 정상 작동
      setRemainingSMS(null);
    }
  };

  const handleSend = async () => {
    setLoading(true);
    setError('');

    try {
      if (messageType === 'custom') {
        // 직접 입력한 메시지 발송
        await api.post('/sms/send', {
          customer_ids: selectedCustomers.map(c => c.customer_id),
          message: customMessage
        });
      } else {
        // 템플릿 메시지 발송
        await api.post('/sms/send-template', {
          customer_ids: selectedCustomers.map(c => c.customer_id),
          template_type: messageType,
          template_data: templateData
        });
      }

      alert('SMS가 성공적으로 발송되었습니다.');
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
          <h2 className="text-xl font-semibold">SMS 발송</h2>
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
              수신자: {selectedCustomers.length}명
            </span>
          </div>
          <div className="mt-1 text-xs text-gray-500">
            {selectedCustomers.slice(0, 3).map(c => c.name).join(', ')}
            {selectedCustomers.length > 3 && ` 외 ${selectedCustomers.length - 3}명`}
          </div>
        </div>

        {/* 메시지 타입 선택 */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            메시지 유형
          </label>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(SMS_TEMPLATES).map(([key, template]) => (
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
                placeholder="예: 6월 특별 할인"
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
              {messageType === 'birthday' ? (
                <div className="text-sm text-gray-600 whitespace-pre-wrap">
                  {selectedCustomers.length === 1 ? 
                    `[AIBIO 센터] 생일 축하
${selectedCustomers[0].name}님, 생일을 진심으로 축하드립니다! 🎂

특별한 날, 건강한 하루 보내세요.
생일 고객 할인 혜택도 준비되어 있습니다.

문의: 02-2039-2783` :
                    `[AIBIO 센터] 생일 축하
{고객명}님, 생일을 진심으로 축하드립니다! 🎂

특별한 날, 건강한 하루 보내세요.
생일 고객 할인 혜택도 준비되어 있습니다.

문의: 02-2039-2783`}
                </div>
              ) : messageType === 'dormant' ? (
                <div className="text-sm text-gray-600 whitespace-pre-wrap">
                  {selectedCustomers.length === 1 ? 
                    `[AIBIO 센터]
${selectedCustomers[0].name}님, 오랜만입니다.
마지막 방문(${selectedCustomers[0].last_visit_date || '미방문'}) 이후 새로운 서비스가 추가되었습니다.

재방문 고객 할인 혜택을 확인해보세요.

예약: 02-2039-2783` :
                    `[AIBIO 센터]
{고객명}님, 오랜만입니다.
마지막 방문({마지막 방문일}) 이후 새로운 서비스가 추가되었습니다.

재방문 고객 할인 혜택을 확인해보세요.

예약: 02-2039-2783`}
                </div>
              ) : (
                <p className="text-sm text-gray-600">
                  선택한 템플릿으로 자동 생성된 메시지가 발송됩니다.
                </p>
              )}
              
              {/* 메시지 길이 표시 */}
              {(messageType === 'birthday' || messageType === 'dormant') && (
                <div className="mt-2 text-xs text-gray-500 text-right">
                  {messageType === 'birthday' ? '약 80자 / SMS' : '약 95자 / LMS'}
                </div>
              )}
              
              {selectedCustomers.length > 1 && (
                <div className="mt-3 p-2 bg-blue-50 rounded">
                  <p className="text-xs text-blue-700">
                    <span className="font-medium">참고:</span> {"{고객명}"} 부분은 각 고객의 실제 이름으로 자동 치환됩니다.
                    {messageType === 'dormant' && " {마지막 방문일}은 고객별 실제 방문일로 표시됩니다."}
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
            disabled={loading || (messageType === 'custom' && !customMessage.trim())}
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
                발송하기
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}