import React, { useMemo } from 'react';
import { VariableSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

interface Column<T> {
  key: string;
  header: string;
  width: number;
  render: (item: T) => React.ReactNode;
}

interface VirtualizedTableProps<T> {
  data: T[];
  columns: Column<T>[];
  rowHeight?: number;
  headerHeight?: number;
  onRowClick?: (item: T) => void;
}

/**
 * 가상화된 테이블 컴포넌트 - 대량 데이터 렌더링 최적화
 */
export function VirtualizedTable<T extends { id: string | number }>({
  data,
  columns,
  rowHeight = 50,
  headerHeight = 40,
  onRowClick
}: VirtualizedTableProps<T>) {
  const totalWidth = useMemo(
    () => columns.reduce((sum, col) => sum + col.width, 0),
    [columns]
  );

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const item = data[index];
    
    return (
      <div
        style={style}
        className="flex border-b border-gray-200 hover:bg-gray-50 cursor-pointer"
        onClick={() => onRowClick?.(item)}
      >
        {columns.map((column) => (
          <div
            key={column.key}
            className="flex items-center px-4"
            style={{ width: column.width }}
          >
            {column.render(item)}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full">
      {/* 헤더 */}
      <div
        className="flex bg-gray-50 border-b border-gray-200 font-medium text-sm"
        style={{ height: headerHeight, minWidth: totalWidth }}
      >
        {columns.map((column) => (
          <div
            key={column.key}
            className="flex items-center px-4"
            style={{ width: column.width }}
          >
            {column.header}
          </div>
        ))}
      </div>

      {/* 가상화된 리스트 */}
      <div className="flex-1">
        <AutoSizer>
          {({ height, width }) => (
            <List
              height={height}
              itemCount={data.length}
              itemSize={() => rowHeight}
              width={width}
              overscanCount={5}
            >
              {Row}
            </List>
          )}
        </AutoSizer>
      </div>
    </div>
  );
}

export default React.memo(VirtualizedTable);