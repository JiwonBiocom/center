// 유입경로 옵션 상수 (정적 백업용)
export const REFERRAL_SOURCES = [
  '당근',
  '유튜브',
  '검색',
  '지인소개',
  '인스타그램',
  '기타'
] as const;

// 타입 정의
export type ReferralSource = typeof REFERRAL_SOURCES[number];
