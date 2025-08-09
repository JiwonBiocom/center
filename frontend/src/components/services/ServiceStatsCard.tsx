import React from 'react';

interface ServiceStatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'purple' | 'yellow' | 'indigo';
  isText?: boolean;
}

const colorClasses = {
  blue: 'bg-blue-50 text-blue-700 border-blue-200',
  green: 'bg-green-50 text-green-700 border-green-200',
  purple: 'bg-purple-50 text-purple-700 border-purple-200',
  yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
  indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200'
};

const iconColorClasses = {
  blue: 'text-blue-500',
  green: 'text-green-500',
  purple: 'text-purple-500',
  yellow: 'text-yellow-500',
  indigo: 'text-indigo-500'
};

export default function ServiceStatsCard({ 
  title, 
  value, 
  icon, 
  color, 
  isText = false 
}: ServiceStatsCardProps) {
  return (
    <div className={`border rounded-lg p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className={`text-lg font-semibold mt-1 ${isText ? 'text-sm' : ''}`}>
            {isText ? value : typeof value === 'number' ? value.toLocaleString() : value}
          </p>
        </div>
        <div className={`${iconColorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}