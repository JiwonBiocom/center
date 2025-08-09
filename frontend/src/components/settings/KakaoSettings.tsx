import { useState, useEffect } from 'react';
import { MessageSquare, AlertCircle, Save, TestTube, Key } from 'lucide-react';
import { api } from '../../lib/api';

interface KakaoTemplate {
  template_id: number;
  template_code: string;
  template_name: string;
  message_content: string;
  is_active: boolean;
  created_at: string;
}

export default function KakaoSettings() {
  const [templates, setTemplates] = useState<KakaoTemplate[]>([]);
  const [apiKeys, setApiKeys] = useState({
    rest_api_key: '',
    admin_key: '',
    sender_key: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [testPhone, setTestPhone] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // API 키 정보 가져오기
      const keysResponse = await api.get('/api/v1/settings/kakao/keys');
      setApiKeys(keysResponse.data);

      // 템플릿 목록 가져오기
      const templatesResponse = await api.get('/api/v1/settings/kakao/templates');
      setTemplates(templatesResponse.data);
    } catch (error) {
      console.error('Failed to fetch Kakao settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveKeys = async () => {
    setSaving(true);
    setMessage('');

    try {
      await api.put('/api/v1/settings/kakao/keys', apiKeys);
      setMessage('API 키가 저장되었습니다.');
    } catch (error) {
      setMessage('API 키 저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  const handleTestMessage = async () => {
    if (!testPhone || !selectedTemplate) {
      setMessage('전화번호와 템플릿을 선택해주세요.');
      return;
    }

    try {
      await api.post('/api/v1/settings/kakao/test', {
        phone: testPhone,
        template_code: selectedTemplate
      });
      setMessage('테스트 메시지가 발송되었습니다.');
    } catch (error: any) {
      setMessage(error.response?.data?.detail || '테스트 메시지 발송에 실패했습니다.');
    }
  };

  const handleToggleTemplate = async (templateId: number, isActive: boolean) => {
    try {
      await api.put(`/api/v1/settings/kakao/templates/${templateId}`, {
        is_active: isActive
      });
      fetchData();
    } catch (error) {
      console.error('Failed to update template:', error);
    }
  };

  if (loading) {
    return <div className="text-center py-8">로딩 중...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-6">카카오톡 알림 설정</h2>
        
        {/* API 키 설정 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">API 키 설정</h3>
            <Key className="w-5 h-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                REST API 키
              </label>
              <input
                type="password"
                value={apiKeys.rest_api_key}
                onChange={(e) => setApiKeys({ ...apiKeys, rest_api_key: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="카카오 REST API 키를 입력하세요"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Admin 키
              </label>
              <input
                type="password"
                value={apiKeys.admin_key}
                onChange={(e) => setApiKeys({ ...apiKeys, admin_key: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="카카오 Admin 키를 입력하세요"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                발신자 키
              </label>
              <input
                type="text"
                value={apiKeys.sender_key}
                onChange={(e) => setApiKeys({ ...apiKeys, sender_key: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="알림톡 발신자 키를 입력하세요"
              />
            </div>

            <button
              onClick={handleSaveKeys}
              disabled={saving}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
            >
              <Save className="w-4 h-4" />
              {saving ? '저장 중...' : '저장'}
            </button>
          </div>
        </div>

        {/* 알림톡 템플릿 관리 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">알림톡 템플릿</h3>
            <MessageSquare className="w-5 h-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            {templates.map(template => (
              <div key={template.template_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{template.template_name}</h4>
                    <p className="text-sm text-gray-500 mt-1">템플릿 코드: {template.template_code}</p>
                    <pre className="mt-2 p-3 bg-gray-50 rounded text-sm whitespace-pre-wrap">
                      {template.message_content}
                    </pre>
                  </div>
                  <label className="ml-4 flex items-center">
                    <input
                      type="checkbox"
                      checked={template.is_active}
                      onChange={(e) => handleToggleTemplate(template.template_id, e.target.checked)}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">활성화</span>
                  </label>
                </div>
              </div>
            ))}

            {templates.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                등록된 템플릿이 없습니다.
              </div>
            )}
          </div>
        </div>

        {/* 테스트 발송 */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">테스트 발송</h3>
            <TestTube className="w-5 h-5 text-gray-400" />
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                수신 전화번호
              </label>
              <input
                type="text"
                value={testPhone}
                onChange={(e) => setTestPhone(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="010-0000-0000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                템플릿 선택
              </label>
              <select
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">템플릿을 선택하세요</option>
                {templates.filter(t => t.is_active).map(template => (
                  <option key={template.template_id} value={template.template_code}>
                    {template.template_name}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={handleTestMessage}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              <MessageSquare className="w-4 h-4" />
              테스트 발송
            </button>
          </div>
        </div>

        {/* 메시지 표시 */}
        {message && (
          <div className={`mt-4 p-3 rounded-md flex items-start ${
            message.includes('실패') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
          }`}>
            <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {/* 안내 사항 */}
        <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
          <h4 className="font-medium text-yellow-900 mb-2">카카오톡 알림톡 사용 안내</h4>
          <ul className="text-sm text-yellow-800 space-y-1">
            <li>• 알림톡 사용을 위해서는 카카오 비즈니스 채널 등록이 필요합니다.</li>
            <li>• 템플릿은 카카오 검수 승인 후 사용 가능합니다.</li>
            <li>• 발신자 키는 카카오 비즈니스 채널에서 확인할 수 있습니다.</li>
            <li>• API 키는 안전하게 보관해주세요.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}