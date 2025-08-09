import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ServiceUsageData {
  service_name: string;
  usage_count: number;
}

interface ServiceUsageChartProps {
  data: ServiceUsageData[];
}

export default function ServiceUsageChart({ data }: ServiceUsageChartProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">서비스별 이용 현황</h2>
      {data.length > 0 ? (
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="service_name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="usage_count" fill="#8B5CF6" />
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-64 flex items-center justify-center text-gray-400">
          데이터 없음
        </div>
      )}
    </div>
  );
}