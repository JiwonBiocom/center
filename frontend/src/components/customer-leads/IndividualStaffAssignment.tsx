import { useState } from 'react';
import { User } from 'lucide-react';
import StaffAssignmentModal from './StaffAssignmentModal';
import { api } from '../../lib/api';

interface IndividualStaffAssignmentProps {
  leadId: number;
  currentStaffId?: number;
  currentStaffName?: string;
  onAssigned: () => void;
}

export default function IndividualStaffAssignment({
  leadId,
  currentStaffId,
  currentStaffName,
  onAssigned
}: IndividualStaffAssignmentProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAssign = async (staffId: number) => {
    try {
      await api.post('/api/v1/customer-leads/assign-staff', {
        lead_ids: [leadId],
        staff_id: staffId
      });
      onAssigned();
      setIsModalOpen(false);
    } catch (error) {
      console.error('Failed to assign staff:', error);
      alert('담당자 지정에 실패했습니다.');
    }
  };

  return (
    <>
      <button
        onClick={() => setIsModalOpen(true)}
        className="inline-flex items-center gap-1 text-sm text-gray-600 hover:text-indigo-600 transition-colors"
        title="담당자 지정/변경"
      >
        <User className="w-4 h-4" />
        <span>{currentStaffName || '미지정'}</span>
      </button>

      <StaffAssignmentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAssign={handleAssign}
        selectedLeadsCount={1}
        currentStaffId={currentStaffId}
      />
    </>
  );
}