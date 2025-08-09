interface CustomerPaginationProps {
  totalCount: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}

export default function CustomerPagination({
  totalCount,
  currentPage,
  pageSize,
  onPageChange
}: CustomerPaginationProps) {
  const totalPages = Math.ceil(totalCount / pageSize);

  if (totalCount <= pageSize) {
    return null;
  }

  return (
    <div className="mt-6 flex items-center justify-between">
      <div className="text-sm text-gray-700">
        <span className="font-medium">{totalCount}</span>명 중{' '}
        <span className="font-medium">
          {Math.min((currentPage - 1) * pageSize + 1, totalCount)}
        </span>
        -
        <span className="font-medium">
          {Math.min(currentPage * pageSize, totalCount)}
        </span>
        명 표시
      </div>
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className="relative inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          이전
        </button>
        <span className="text-sm text-gray-700">
          {currentPage} / {totalPages} 페이지
        </span>
        <button
          onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage >= totalPages}
          className="relative inline-flex items-center px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus-visible:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          다음
        </button>
      </div>
    </div>
  );
}