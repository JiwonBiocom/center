import React, { useState } from 'react';
import { Plus, TrendingUp, TrendingDown, Minus, Activity, BarChart3, Edit, Trash2 } from 'lucide-react';
import type { InBodyRecord } from '../../types/inbody';

interface InBodySectionProps {
  customerId: number;
  inbodyRecords: InBodyRecord[];
  onAddRecord: () => void;
  onEditRecord: (record: InBodyRecord) => void;
  onDeleteRecord: (recordId: number) => void;
}

const InBodySection: React.FC<InBodySectionProps> = ({
  inbodyRecords,
  onAddRecord,
  onEditRecord,
  onDeleteRecord
}) => {
  const [viewMode, setViewMode] = useState<'list' | 'chart'>('list');

  // 최신 기록
  const latestRecord = inbodyRecords.length > 0 ? inbodyRecords[0] : null;

  // 트렌드 계산
  const getTrend = (current?: number, previous?: number) => {
    if (!current || !previous) return null;
    if (current > previous) return 'up';
    if (current < previous) return 'down';
    return 'stable';
  };

  const getTrendIcon = (trend: string | null) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-green-500" />;
      case 'stable':
        return <Minus className="h-4 w-4 text-gray-500" />;
      default:
        return null;
    }
  };

  const formatValue = (value?: number, unit: string = '') => {
    return value ? `${value}${unit}` : '-';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Activity className="h-6 w-6 text-indigo-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900">인바디 정보</h3>
              <p className="text-sm text-gray-600">
                체성분 분석 및 건강 지표 관리
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex rounded-lg border border-gray-200">
              <button
                onClick={() => setViewMode('list')}
                className={`px-3 py-1 text-sm rounded-l-lg ${
                  viewMode === 'list'
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                목록
              </button>
              <button
                onClick={() => setViewMode('chart')}
                className={`px-3 py-1 text-sm rounded-r-lg ${
                  viewMode === 'chart'
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                차트
              </button>
            </div>
            <button
              onClick={onAddRecord}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm"
            >
              <Plus className="h-4 w-4" />
              인바디 추가
            </button>
          </div>
        </div>
      </div>

      <div className="p-6">
        {inbodyRecords.length === 0 ? (
          <div className="text-center py-8">
            <Activity className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              인바디 기록이 없습니다
            </h4>
            <p className="text-gray-600 mb-4">
              고객의 첫 번째 인바디 기록을 추가해보세요.
            </p>
            <button
              onClick={onAddRecord}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 mx-auto"
            >
              <Plus className="h-4 w-4" />
              첫 번째 기록 추가
            </button>
          </div>
        ) : (
          <>
            {viewMode === 'list' && (
              <div className="space-y-6">
                {/* 최신 기록 요약 */}
                {latestRecord && (
                  <div className="bg-indigo-50 rounded-lg p-4">
                    <h4 className="font-medium text-indigo-900 mb-3">
                      최근 측정 정보 ({formatDate(latestRecord.measurement_date)})
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                      <div className="text-center">
                        <div className="text-sm text-indigo-600 mb-1">체중</div>
                        <div className="font-semibold text-indigo-900">
                          {formatValue(latestRecord.weight, 'kg')}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-indigo-600 mb-1">체지방률</div>
                        <div className="font-semibold text-indigo-900">
                          {formatValue(latestRecord.body_fat_percentage, '%')}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-indigo-600 mb-1">골격근량</div>
                        <div className="font-semibold text-indigo-900">
                          {formatValue(latestRecord.skeletal_muscle_mass, 'kg')}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-indigo-600 mb-1">세포외수분비</div>
                        <div className="font-semibold text-indigo-900">
                          {formatValue(latestRecord.extracellular_water_ratio)}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-indigo-600 mb-1">위상각</div>
                        <div className="font-semibold text-indigo-900">
                          {formatValue(latestRecord.phase_angle, '°')}
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-indigo-600 mb-1">내장지방</div>
                        <div className="font-semibold text-indigo-900">
                          {formatValue(latestRecord.visceral_fat_level, '레벨')}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* 전체 기록 목록 */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">
                    전체 기록 ({inbodyRecords.length}건)
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            측정일
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            체중(kg)
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            체지방률(%)
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            골격근량(kg)
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            세포외수분비
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            위상각(°)
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            내장지방
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            측정자
                          </th>
                          <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                            관리
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {inbodyRecords.map((record, index) => {
                          const nextRecord = inbodyRecords[index + 1];
                          return (
                            <tr key={record.record_id} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-sm text-gray-900">
                                {formatDate(record.measurement_date)}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900">
                                <div className="flex items-center gap-2">
                                  {formatValue(record.weight)}
                                  {getTrendIcon(getTrend(record.weight, nextRecord?.weight))}
                                </div>
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900">
                                <div className="flex items-center gap-2">
                                  {formatValue(record.body_fat_percentage)}
                                  {getTrendIcon(getTrend(record.body_fat_percentage, nextRecord?.body_fat_percentage))}
                                </div>
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900">
                                {formatValue(record.skeletal_muscle_mass)}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900">
                                {formatValue(record.extracellular_water_ratio)}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900">
                                {formatValue(record.phase_angle)}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-900">
                                {formatValue(record.visceral_fat_level, ' 레벨')}
                              </td>
                              <td className="px-4 py-3 text-sm text-gray-600">
                                {record.measured_by || '-'}
                              </td>
                              <td className="px-4 py-3 text-right text-sm">
                                <div className="flex justify-end gap-2">
                                  <button
                                    onClick={() => onEditRecord(record)}
                                    className="text-indigo-600 hover:text-indigo-900"
                                    title="수정"
                                  >
                                    <Edit className="h-4 w-4" />
                                  </button>
                                  <button
                                    onClick={() => onDeleteRecord(record.record_id)}
                                    className="text-red-600 hover:text-red-900"
                                    title="삭제"
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {viewMode === 'chart' && (
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">
                  차트 기능 준비 중
                </h4>
                <p className="text-gray-600">
                  인바디 데이터 시각화 기능이 곧 추가될 예정입니다.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default InBodySection;