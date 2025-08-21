import React, { useState } from 'react';
import { api } from '../../../lib/api';
import type { InBodyRecord, InBodyRecordCreate, InBodyRecordUpdate } from '../../../types/inbody';
import InBodySection from '../InBodySection';
import InBodyModal from '../InBodyModal';

interface InBodyTabProps {
  customerId: number;
  inbodyRecords: InBodyRecord[];
  onRefresh: () => void;
}

const InBodyTab: React.FC<InBodyTabProps> = ({
  customerId,
  inbodyRecords,
  onRefresh
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState<InBodyRecord | undefined>();
  const [modalMode, setModalMode] = useState<'create' | 'edit'>('create');

  const handleAddRecord = () => {
    setEditingRecord(undefined);
    setModalMode('create');
    setIsModalOpen(true);
  };

  const handleEditRecord = (record: InBodyRecord) => {
    setEditingRecord(record);
    setModalMode('edit');
    setIsModalOpen(true);
  };

  const handleDeleteRecord = async (recordId: number) => {
    if (!window.confirm('정말로 이 인바디 기록을 삭제하시겠습니까?')) {
      return;
    }

    try {
      await api.delete(`/inbody/${recordId}`);
      onRefresh();
    } catch (error) {
      console.error('Failed to delete inbody record:', error);
      alert('인바디 기록 삭제에 실패했습니다.');
    }
  };

  const handleSaveRecord = async (data: InBodyRecordCreate | InBodyRecordUpdate) => {
    try {
      if (modalMode === 'create') {
        await api.post('inbody/', data);
      } else if (editingRecord) {
        await api.put(`inbody/${editingRecord.record_id}`, data);
      }
      onRefresh();
      setIsModalOpen(false);
    } catch (error) {
      console.error('Failed to save inbody record:', error);
      throw error;
    }
  };

  return (
    <>
      <InBodySection
        customerId={customerId}
        inbodyRecords={inbodyRecords}
        onAddRecord={handleAddRecord}
        onEditRecord={handleEditRecord}
        onDeleteRecord={handleDeleteRecord}
      />

      <InBodyModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRecord}
        customerId={customerId}
        record={editingRecord}
        mode={modalMode}
      />
    </>
  );
};

export default InBodyTab;
