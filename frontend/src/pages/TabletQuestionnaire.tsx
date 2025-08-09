import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import { api } from '../lib/api';
import { formatPhoneNumber } from '../lib/utils/format';

interface Question {
  question_id: number;
  question_type: string;
  question_text: string;
  question_subtext?: string;
  options?: Array<{value: string; label: string}>;
  validation_rules?: any;
  ui_config?: any;
}

interface QuestionnaireProgress {
  current_section: string;
  answered_questions: number;
  total_questions: number;
  completion_rate: number;
  next_question?: Question;
  estimated_time_remaining: number;
}

interface Customer {
  customer_id: number;
  name: string;
  phone: string;
}

export default function TabletQuestionnaire() {
  const navigate = useNavigate();
  const [step, setStep] = useState<'customer' | 'inbody' | 'questionnaire' | 'complete'>('customer');

  // Customer selection
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // InBody data
  const [inbodyData, setInbodyData] = useState({
    weight: '',
    height: '',
    body_fat_percentage: '',
    skeletal_muscle_mass: '',
    phase_angle: '',
  });

  // Questionnaire
  const [responseId, setResponseId] = useState<number | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState<any>(null);
  const [progress, setProgress] = useState<QuestionnaireProgress | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch customers
  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/api/v1/customers', { params: { limit: 1000 } });
      if (response.data?.data) {
        setCustomers(response.data.data);
      } else if (Array.isArray(response.data)) {
        setCustomers(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const startQuestionnaire = async () => {
    if (!selectedCustomer) return;

    setLoading(true);
    try {
      // Save InBody data if provided
      if (inbodyData.weight && inbodyData.height) {
        await api.post('/api/v1/inbody/records', {
          customer_id: selectedCustomer.customer_id,
          weight: parseFloat(inbodyData.weight),
          body_fat_percentage: inbodyData.body_fat_percentage ? parseFloat(inbodyData.body_fat_percentage) : null,
          skeletal_muscle_mass: inbodyData.skeletal_muscle_mass ? parseFloat(inbodyData.skeletal_muscle_mass) : null,
          phase_angle: inbodyData.phase_angle ? parseFloat(inbodyData.phase_angle) : null,
        });
      }

      // Start questionnaire
      const response = await api.post('/api/v1/questionnaire/start', {
        customer_id: selectedCustomer.customer_id,
        template_id: 1,
        device_id: 'web-browser',
        app_version: '1.0.0',
      });

      setResponseId(response.data.response_id);
      setStep('questionnaire');
      fetchProgress(response.data.response_id);
    } catch (error) {
      console.error('Failed to start questionnaire:', error);
      alert('문진 시작에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchProgress = async (respId: number) => {
    try {
      const response = await api.get(`/api/v1/questionnaire/responses/${respId}/progress`);
      setProgress(response.data);
      if (response.data.next_question) {
        setCurrentQuestion(response.data.next_question);
        setCurrentAnswer(null);
      } else {
        // Complete
        setStep('complete');
      }
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    }
  };

  const submitAnswer = async () => {
    if (!responseId || !currentQuestion || currentAnswer === null) return;

    setLoading(true);
    try {
      await api.post(`/api/v1/questionnaire/responses/${responseId}/answers`, {
        question_id: currentQuestion.question_id,
        answer: currentAnswer,
        time_spent_seconds: 10,
      });

      // Fetch next question
      fetchProgress(responseId);
    } catch (error) {
      console.error('Failed to submit answer:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeQuestionnaire = async () => {
    if (!responseId) return;

    try {
      await api.post(`/api/v1/questionnaire/responses/${responseId}/complete`, {
        response_id: responseId,
        force_complete: true,
      });
      alert('문진이 완료되었습니다!');
      navigate('/');
    } catch (error) {
      console.error('Failed to complete questionnaire:', error);
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.phone.includes(searchTerm)
  );

  const renderQuestion = () => {
    if (!currentQuestion) return null;

    switch (currentQuestion.question_type) {
      case 'single_choice':
        return (
          <div className="space-y-3">
            {currentQuestion.options?.map(option => (
              <button
                key={option.value}
                onClick={() => setCurrentAnswer(option.value)}
                className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                  currentAnswer === option.value
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="text-lg">{option.label}</span>
              </button>
            ))}
          </div>
        );

      case 'multiple_choice':
        const selectedValues = currentAnswer || [];
        return (
          <div className="space-y-3">
            {currentQuestion.options?.map(option => (
              <button
                key={option.value}
                onClick={() => {
                  if (selectedValues.includes(option.value)) {
                    setCurrentAnswer(selectedValues.filter((v: string) => v !== option.value));
                  } else {
                    setCurrentAnswer([...selectedValues, option.value]);
                  }
                }}
                className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                  selectedValues.includes(option.value)
                    ? 'border-indigo-600 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span className="text-lg">{option.label}</span>
              </button>
            ))}
          </div>
        );

      case 'scale':
        const min = currentQuestion.validation_rules?.min || 0;
        const max = currentQuestion.validation_rules?.max || 10;
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="text-5xl font-bold text-indigo-600">
                {currentAnswer || min}
              </div>
            </div>
            <input
              type="range"
              min={min}
              max={max}
              value={currentAnswer || min}
              onChange={(e) => setCurrentAnswer(parseInt(e.target.value))}
              className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-gray-600">
              <span>{min}</span>
              <span>{max}</span>
            </div>
          </div>
        );

      case 'text':
        return (
          <textarea
            value={currentAnswer || ''}
            onChange={(e) => setCurrentAnswer(e.target.value)}
            className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            rows={4}
            placeholder="답변을 입력해주세요"
          />
        );

      case 'number':
        return (
          <input
            type="number"
            value={currentAnswer || ''}
            onChange={(e) => setCurrentAnswer(e.target.value ? parseFloat(e.target.value) : null)}
            className="w-full p-4 text-2xl text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            placeholder="0"
          />
        );

      default:
        return <div>지원하지 않는 질문 유형입니다.</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
      <div className="w-full max-w-4xl">
        {/* Progress Bar */}
        {step === 'questionnaire' && progress && (
          <div className="bg-white rounded-t-2xl p-6 border-b">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>{progress.current_section === 'basic' ? '기본 정보' :
                     progress.current_section === 'health_status' ? '건강 상태' :
                     progress.current_section === 'goals' ? '목표 설정' : progress.current_section}</span>
              <span>{progress.answered_questions} / {progress.total_questions}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-indigo-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress.completion_rate}%` }}
              />
            </div>
            {progress.estimated_time_remaining > 0 && (
              <div className="text-right text-sm text-gray-500 mt-2">
                예상 남은 시간: 약 {Math.ceil(progress.estimated_time_remaining / 60)}분
              </div>
            )}
          </div>
        )}

        <div className="bg-white rounded-b-2xl shadow-xl p-8">
          {/* Customer Selection */}
          {step === 'customer' && (
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-8">태블릿 문진 (개발중)</h1>

              <input
                type="text"
                placeholder="이름 또는 전화번호로 검색"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full p-4 mb-6 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              />

              <div className="max-h-96 overflow-y-auto space-y-2">
                {filteredCustomers.map(customer => (
                  <button
                    key={customer.customer_id}
                    onClick={() => setSelectedCustomer(customer)}
                    className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                      selectedCustomer?.customer_id === customer.customer_id
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-semibold">{customer.name}</div>
                    <div className="text-sm text-gray-600">{formatPhoneNumber(customer.phone)}</div>
                  </button>
                ))}
              </div>

              <button
                onClick={() => setStep('inbody')}
                disabled={!selectedCustomer}
                className="mt-6 w-full py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 transition-colors"
              >
                다음
              </button>
            </div>
          )}

          {/* InBody Input */}
          {step === 'inbody' && (
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-8">인바디 측정값 입력 (선택사항)</h1>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">체중 (kg)</label>
                  <input
                    type="number"
                    value={inbodyData.weight}
                    onChange={(e) => setInbodyData({...inbodyData, weight: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    placeholder="예: 70"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">키 (cm)</label>
                  <input
                    type="number"
                    value={inbodyData.height}
                    onChange={(e) => setInbodyData({...inbodyData, height: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    placeholder="예: 170"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">체지방률 (%)</label>
                  <input
                    type="number"
                    value={inbodyData.body_fat_percentage}
                    onChange={(e) => setInbodyData({...inbodyData, body_fat_percentage: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    placeholder="예: 20"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">골격근량 (kg)</label>
                  <input
                    type="number"
                    value={inbodyData.skeletal_muscle_mass}
                    onChange={(e) => setInbodyData({...inbodyData, skeletal_muscle_mass: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    placeholder="예: 30"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">위상각</label>
                  <input
                    type="number"
                    value={inbodyData.phase_angle}
                    onChange={(e) => setInbodyData({...inbodyData, phase_angle: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    placeholder="예: 5.5"
                  />
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <button
                  onClick={() => setStep('customer')}
                  className="flex-1 py-4 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  이전
                </button>
                <button
                  onClick={startQuestionnaire}
                  disabled={loading}
                  className="flex-1 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 flex items-center justify-center"
                >
                  {loading ? <Loader2 className="animate-spin mr-2" /> : null}
                  문진 시작
                </button>
              </div>

              <button
                onClick={startQuestionnaire}
                className="mt-3 w-full py-3 text-indigo-600 hover:text-indigo-700"
              >
                인바디 측정 건너뛰기
              </button>
            </div>
          )}

          {/* Questionnaire */}
          {step === 'questionnaire' && currentQuestion && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {currentQuestion.question_text}
              </h2>
              {currentQuestion.question_subtext && (
                <p className="text-gray-600 mb-6">{currentQuestion.question_subtext}</p>
              )}

              <div className="my-8">
                {renderQuestion()}
              </div>

              <div className="flex gap-4">
                <button
                  onClick={submitAnswer}
                  disabled={loading || currentAnswer === null}
                  className="flex-1 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 flex items-center justify-center"
                >
                  {loading ? <Loader2 className="animate-spin mr-2" /> : null}
                  다음
                  <ChevronRight className="ml-2" />
                </button>
              </div>
            </div>
          )}

          {/* Completion */}
          {step === 'complete' && (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">문진이 완료되었습니다!</h1>
              <p className="text-xl text-gray-600 mb-8">상담 직원이 곧 안내해드리겠습니다.</p>

              <button
                onClick={completeQuestionnaire}
                className="px-8 py-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                처음으로
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
