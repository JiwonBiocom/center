/**
 * 공통 포맷팅 유틸리티 함수
 * 날짜, 전화번호, 금액 등의 포맷팅을 담당
 */

/**
 * 날짜 포맷팅
 */
export const formatDate = (date: Date | string | null | undefined): string => {
  if (!date) return '-';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  // Invalid date check
  if (isNaN(d.getTime())) return '-';
  
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

/**
 * 날짜와 시간 포맷팅
 */
export const formatDateTime = (date: Date | string | null | undefined): string => {
  if (!date) return '-';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(d.getTime())) return '-';
  
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * ISO 날짜 문자열로 변환 (YYYY-MM-DD)
 */
export const formatDateToISO = (date: Date | string | null | undefined): string => {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  
  if (isNaN(d.getTime())) return '';
  
  return d.toISOString().split('T')[0];
};

/**
 * 전화번호 포맷팅
 */
export const formatPhoneNumber = (phone: string | null | undefined): string => {
  if (!phone) return '';
  
  // 숫자만 추출
  const cleaned = phone.replace(/\D/g, '');
  
  // 한국 휴대폰 번호 (11자리)
  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
  }
  
  // 한국 일반 전화번호 (10자리)
  if (cleaned.length === 10) {
    // 서울 (02)
    if (cleaned.startsWith('02')) {
      return cleaned.replace(/(\d{2})(\d{4})(\d{4})/, '$1-$2-$3');
    }
    // 기타 지역
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
  }
  
  // 기타 경우 원본 반환
  return phone;
};

/**
 * 전화번호에서 하이픈 제거
 */
export const unformatPhoneNumber = (phone: string | null | undefined): string => {
  if (!phone) return '';
  return phone.replace(/\D/g, '');
};

/**
 * 금액 포맷팅
 */
export const formatCurrency = (amount: number | string | null | undefined): string => {
  if (amount === null || amount === undefined) return '₩0';
  
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  
  if (isNaN(num)) return '₩0';
  
  return `₩${num.toLocaleString('ko-KR')}`;
};

/**
 * 숫자 포맷팅 (천 단위 구분)
 */
export const formatNumber = (num: number | string | null | undefined): string => {
  if (num === null || num === undefined) return '0';
  
  const n = typeof num === 'string' ? parseFloat(num) : num;
  
  if (isNaN(n)) return '0';
  
  return n.toLocaleString('ko-KR');
};

/**
 * 퍼센트 포맷팅
 */
export const formatPercent = (value: number | null | undefined, decimals: number = 1): string => {
  if (value === null || value === undefined) return '0%';
  
  return `${value.toFixed(decimals)}%`;
};

/**
 * 파일 크기 포맷팅
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

/**
 * 상대 시간 포맷팅 (예: 3일 전, 2시간 전)
 */
export const formatRelativeTime = (date: Date | string | null | undefined): string => {
  if (!date) return '';
  
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}일 전`;
  if (hours > 0) return `${hours}시간 전`;
  if (minutes > 0) return `${minutes}분 전`;
  return '방금 전';
};

/**
 * 객체로 모든 포맷터 export
 */
export const formatters = {
  date: formatDate,
  dateTime: formatDateTime,
  dateToISO: formatDateToISO,
  phone: formatPhoneNumber,
  unformatPhone: unformatPhoneNumber,
  currency: formatCurrency,
  number: formatNumber,
  percent: formatPercent,
  fileSize: formatFileSize,
  relativeTime: formatRelativeTime
} as const;