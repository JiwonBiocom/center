export default function DashboardHeader() {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
      <p className="text-gray-600 mt-2">오늘의 비즈니스 현황을 한눈에 확인하세요</p>
      <p className="text-amber-600 mt-1 text-sm">
        고객 예약 데이터 지속 업데이트 필요(현재는 데이터 정확하지 않을 수 있음)
      </p>
    </div>
  );
}