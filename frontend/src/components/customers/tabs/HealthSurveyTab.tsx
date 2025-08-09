import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Calendar, FileText, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { api } from '../../../lib/api'

interface HealthSurveyTabProps {
  customerId: number
}

interface QuestionnaireResponse {
  response_id: number
  started_at: string
  completed_at: string | null
  is_completed: boolean
  completion_rate: number
  device_id: string
  app_version: string
  answers: Answer[]
}

interface Answer {
  answer_id: number
  question_id: number
  answer_value: string | null
  answer_number: number | null
  answer_json: any
  answered_at: string
  question: Question
}

interface Question {
  question_id: number
  question_text: string
  question_subtext: string | null
  question_type: string
  section: string
  options: QuestionOption[] | null
}

interface QuestionOption {
  value: string
  label: string
}

export default function HealthSurveyTab({ customerId }: HealthSurveyTabProps) {
  const [selectedResponse, setSelectedResponse] = useState<QuestionnaireResponse | null>(null)

  // 고객의 건강설문 목록 조회
  const { data: questionnaires, isLoading } = useQuery({
    queryKey: ['customer-questionnaires', customerId],
    queryFn: async () => {
      const response = await api.get(`/questionnaire/customers/${customerId}/responses`)
      return response.data as QuestionnaireResponse[]
    },
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatAnswer = (answer: Answer) => {
    const { question } = answer
    
    if (answer.answer_value) {
      // Single choice 또는 text 답변
      if (question.question_type === 'single_choice' && question.options) {
        const option = question.options.find(opt => opt.value === answer.answer_value)
        return option?.label || answer.answer_value
      }
      return answer.answer_value
    }
    
    if (answer.answer_number !== null) {
      // Number 또는 scale 답변
      return answer.answer_number.toString()
    }
    
    if (answer.answer_json) {
      // Multiple choice 답변
      if (question.question_type === 'multiple_choice' && answer.answer_json.selected) {
        const selectedValues = answer.answer_json.selected as string[]
        if (question.options) {
          const labels = selectedValues.map(value => {
            const option = question.options!.find(opt => opt.value === value)
            return option?.label || value
          })
          return labels.join(', ')
        }
        return selectedValues.join(', ')
      }
      return JSON.stringify(answer.answer_json)
    }
    
    return '답변 없음'
  }

  const getSectionName = (section: string) => {
    const sectionNames: Record<string, string> = {
      'basic': '기본 정보',
      'health_status': '건강 상태',
      'goals': '목표 설정',
      'stress_mental': '스트레스 및 정신건강',
      'digestive': '소화기 건강',
      'hormone': '호르몬 및 대사',
      'musculoskeletal': '근골격계'
    }
    return sectionNames[section] || section
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  if (!questionnaires || questionnaires.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">건강설문 기록이 없습니다</h3>
          <p className="text-gray-500">
            이 고객의 건강설문 기록이 없습니다.<br />
            태블릿 문진을 통해 건강설문을 진행해보세요.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 h-full flex gap-6">
      {/* 건강설문 목록 */}
      <div className="w-1/3 border-r pr-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">건강설문 기록</h3>
        <div className="space-y-3">
          {questionnaires.map((questionnaire) => (
            <button
              key={questionnaire.response_id}
              onClick={() => setSelectedResponse(questionnaire)}
              className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                selectedResponse?.response_id === questionnaire.response_id
                  ? 'border-indigo-600 bg-indigo-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {questionnaire.is_completed ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-yellow-600" />
                  )}
                  <span className="font-medium">
                    {questionnaire.is_completed ? '완료' : '미완료'}
                  </span>
                </div>
                <span className="text-sm text-gray-500">
                  {Math.round(questionnaire.completion_rate)}%
                </span>
              </div>
              
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                <Calendar className="w-4 h-4" />
                <span>시작: {formatDate(questionnaire.started_at)}</span>
              </div>
              
              {questionnaire.completed_at && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="w-4 h-4" />
                  <span>완료: {formatDate(questionnaire.completed_at)}</span>
                </div>
              )}
              
              <div className="mt-2 text-xs text-gray-500">
                기기: {questionnaire.device_id} | 버전: {questionnaire.app_version}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 선택된 건강설문 상세 */}
      <div className="flex-1">
        {selectedResponse ? (
          <div>
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                건강설문 상세 ({formatDate(selectedResponse.started_at)})
              </h3>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span>완료율: {Math.round(selectedResponse.completion_rate)}%</span>
                <span>총 답변: {selectedResponse.answers.length}개</span>
                {selectedResponse.is_completed && (
                  <span className="text-green-600 font-medium">✓ 완료됨</span>
                )}
              </div>
            </div>

            {/* 답변 목록 */}
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {selectedResponse.answers.map((answer) => (
                <div key={answer.answer_id} className="bg-gray-50 rounded-lg p-4">
                  <div className="mb-2">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded">
                        {getSectionName(answer.question.section)}
                      </span>
                      <span className="text-xs text-gray-500">
                        {formatDate(answer.answered_at)}
                      </span>
                    </div>
                    <h4 className="font-medium text-gray-900">
                      {answer.question.question_text}
                    </h4>
                    {answer.question.question_subtext && (
                      <p className="text-sm text-gray-600 mt-1">
                        {answer.question.question_subtext}
                      </p>
                    )}
                  </div>
                  
                  <div className="mt-3 p-3 bg-white rounded border">
                    <span className="text-gray-900">{formatAnswer(answer)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">
                좌측에서 건강설문을 선택하여 상세 내용을 확인하세요.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}