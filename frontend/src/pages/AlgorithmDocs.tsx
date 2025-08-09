import { useState, useEffect } from 'react';
import { FileText, ChevronRight, Lock, Brain, Utensils } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';
import { api } from '../lib/api';

interface DocItem {
  title: string;
  path: string;
  icon: React.ReactNode;
  description: string;
}

export default function AlgorithmDocs() {
  const { user } = useAuth();
  const [selectedDoc, setSelectedDoc] = useState<string>('');
  const [docContent, setDocContent] = useState<string>('');
  const [loading, setLoading] = useState(false);

  // 관리자 권한 확인
  if (!user || user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  const documents: DocItem[] = [
    {
      title: '고객 문진 시뮬레이션',
      path: 'customer-questionnaire-simulation.html',
      icon: <FileText className="w-5 h-5" />,
      description: '고객이 경험하는 전체 문진 프로세스'
    },
    {
      title: '다이어트 프로그램',
      path: 'diet-simulation.html',
      icon: <Utensils className="w-5 h-5" />,
      description: '체력 수준별 맞춤형 다이어트 전략'
    },
    {
      title: 'AI 추천 알고리즘',
      path: 'AI_RECOMMENDATION_ALGORITHM.md',
      icon: <Brain className="w-5 h-5" />,
      description: 'InBody 데이터와 문진을 통한 AI 추천 시스템'
    }
  ];

  const loadDocument = async (path: string) => {
    setLoading(true);
    try {
      const response = await api.get(`/docs/algorithm/${path}`);
      setDocContent(response.data.content);
      setSelectedDoc(path);
    } catch (error) {
      console.error('문서 로딩 실패:', error);
      setDocContent('문서를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="p-8">
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <Lock className="w-6 h-6 text-red-500" />
            <h1 className="text-2xl font-bold text-gray-900">알고리즘 문서</h1>
          </div>
          <p className="text-sm text-gray-600">관리자 전용 - AI 추천 시스템 및 알고리즘 문서</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 문서 목록 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="p-4 border-b border-gray-200">
                <h2 className="font-semibold text-gray-900">문서 목록</h2>
              </div>
              <div className="p-2">
                {documents.map((doc, index) => (
                  <button
                    key={index}
                    onClick={() => loadDocument(doc.path)}
                    className={`w-full text-left p-3 rounded-lg hover:bg-gray-50 transition-colors ${
                      selectedDoc === doc.path ? 'bg-indigo-50 border border-indigo-200' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`${selectedDoc === doc.path ? 'text-indigo-600' : 'text-gray-500'}`}>
                          {doc.icon}
                        </div>
                        <div>
                          <h3 className={`font-medium ${
                            selectedDoc === doc.path ? 'text-indigo-600' : 'text-gray-900'
                          }`}>
                            {doc.title}
                          </h3>
                          <p className="text-xs text-gray-500 mt-1">{doc.description}</p>
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* 보안 안내 */}
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start gap-2">
                <Lock className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-medium text-red-800">보안 주의사항</h4>
                  <p className="text-sm text-red-700 mt-1">
                    이 문서들은 회사 기밀 정보를 포함하고 있습니다. 
                    무단 복사 및 외부 유출을 금지합니다.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 문서 내용 */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 min-h-[600px]">
              {!selectedDoc ? (
                <div className="flex items-center justify-center h-[600px] text-gray-500">
                  <div className="text-center">
                    <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>왼쪽 목록에서 문서를 선택하세요</p>
                  </div>
                </div>
              ) : loading ? (
                <div className="flex items-center justify-center h-[600px]">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="mt-3 text-gray-500">문서 로딩 중...</p>
                  </div>
                </div>
              ) : (
                <div className="p-6 overflow-auto max-h-[800px]">
                  {selectedDoc.endsWith('.html') ? (
                    <iframe
                      srcDoc={docContent}
                      className="w-full h-[700px] border-0"
                      title="Algorithm Document"
                    />
                  ) : (
                    <div className="prose max-w-none">
                      <pre className="whitespace-pre-wrap font-sans text-sm">{docContent}</pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}