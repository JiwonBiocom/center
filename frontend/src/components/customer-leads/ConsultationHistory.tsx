import { useState, useEffect } from 'react';
import { Plus, Calendar, User, FileText, Clock, Edit, Trash2 } from 'lucide-react';
import { api } from '../../lib/api';
import ConsultationModal from './ConsultationModal';

interface Consultation {
  consultation_id: number;
  lead_id: number;
  consultation_date: string;
  consultation_type: string;
  consulted_by: string;
  consultation_content: string;
  next_action?: string;
  next_action_date?: string;
  created_by: number;
  created_by_name?: string;
  created_at: string;
}

interface ConsultationHistoryProps {
  leadId: number;
  leadName: string;
}

const consultationTypeLabels: Record<string, string> = {
  'phone': '전화 상담',
  'visit': '방문 상담',
  'online': '온라인 상담',
  'follow_up': '후속 상담'
};

const consultationTypeColors: Record<string, string> = {
  'phone': 'bg-blue-100 text-blue-800',
  'visit': 'bg-purple-100 text-purple-800',
  'online': 'bg-green-100 text-green-800',
  'follow_up': 'bg-yellow-100 text-yellow-800'
};

export default function ConsultationHistory({ leadId, leadName }: ConsultationHistoryProps) {
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingConsultation, setEditingConsultation] = useState<Consultation | null>(null);

  useEffect(() => {
    fetchConsultations();
  }, [leadId]);

  const fetchConsultations = async () => {
    try {
      const response = await api.get(`/api/v1/customer-leads/${leadId}/consultations`);
      setConsultations(response.data);
    } catch (error) {
      console.error('Failed to fetch consultations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (consultationId: number) => {
    if (!window.confirm('정말로 이 상담 기록을 삭제하시겠습니까?')) return;

    try {
      await api.delete(`/api/v1/customer-leads/${leadId}/consultations/${consultationId}`);
      fetchConsultations();
    } catch (error) {
      console.error('Failed to delete consultation:', error);
      alert('상담 기록 삭제에 실패했습니다.');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            {leadName}님의 상담 이력
          </h3>
          <button
            onClick={() => {
              setEditingConsultation(null);
              setIsModalOpen(true);
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            상담 추가
          </button>
        </div>

        {consultations.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">아직 상담 이력이 없습니다.</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="mt-4 text-indigo-600 hover:text-indigo-700"
            >
              첫 상담 기록 추가하기
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {consultations.map((consultation) => (
              <div
                key={consultation.consultation_id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-3">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      consultationTypeColors[consultation.consultation_type] || 'bg-gray-100 text-gray-800'
                    }`}>
                      {consultationTypeLabels[consultation.consultation_type] || consultation.consultation_type}
                    </span>
                    <div className="flex items-center text-sm text-gray-600">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(consultation.consultation_date)}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => {
                        setEditingConsultation(consultation);
                        setIsModalOpen(true);
                      }}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(consultation.consultation_id)}
                      className="text-gray-400 hover:text-red-600"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <User className="w-4 h-4 text-gray-400 mt-0.5" />
                    <div className="flex-1">
                      <span className="text-sm text-gray-600">상담자: </span>
                      <span className="text-sm font-medium text-gray-900">
                        {consultation.consulted_by}
                      </span>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded p-3">
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">
                      {consultation.consultation_content}
                    </p>
                  </div>

                  {consultation.next_action && (
                    <div className="mt-3 p-3 bg-yellow-50 rounded">
                      <div className="flex items-start gap-2">
                        <Clock className="w-4 h-4 text-yellow-600 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-yellow-800">다음 조치사항</p>
                          <p className="text-sm text-yellow-700 mt-1">
                            {consultation.next_action}
                          </p>
                          {consultation.next_action_date && (
                            <p className="text-xs text-yellow-600 mt-1">
                              예정일: {new Date(consultation.next_action_date).toLocaleDateString('ko-KR')}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500 mt-2">
                    작성자: {consultation.created_by_name || `ID: ${consultation.created_by}`} • 
                    작성일: {formatDate(consultation.created_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 상담 추가/수정 모달 */}
      <ConsultationModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingConsultation(null);
        }}
        onSuccess={() => {
          setIsModalOpen(false);
          setEditingConsultation(null);
          fetchConsultations();
        }}
        leadId={leadId}
        consultationData={editingConsultation}
      />
    </div>
  );
}