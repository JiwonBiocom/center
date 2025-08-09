export const getStatusColor = (status: string) => {
  switch (status) {
    case 'confirmed': return 'bg-green-100 text-green-800';
    case 'pending': return 'bg-yellow-100 text-yellow-800';
    case 'cancelled': return 'bg-red-100 text-red-800';
    case 'completed': return 'bg-blue-100 text-blue-800';
    case 'no_show': return 'bg-gray-100 text-gray-800';
    default: return 'bg-gray-100 text-gray-800';
  }
};

export const getStatusText = (status: string) => {
  switch (status) {
    case 'confirmed': return '예약 확정';
    case 'pending': return '예약 대기';
    case 'cancelled': return '예약 취소';
    case 'completed': return '서비스 완료';
    case 'no_show': return '노쇼';
    default: return status;
  }
};