import React from 'react';
import { Heart, Star, Clock } from 'lucide-react';

const CustomerSatisfactionSection: React.FC = () => {
  return (
    <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <Heart className="h-6 w-6 text-pink-500" />
          고객 만족도 지표
        </h2>
      </div>
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">업데이트 예정</h3>
            <p className="text-gray-500 text-sm">
              고객 만족도 측정 시스템이 곧 도입될 예정입니다.
            </p>
            <div className="mt-4 flex items-center justify-center gap-2">
              <Star className="h-4 w-4 text-yellow-400" />
              <Star className="h-4 w-4 text-yellow-400" />
              <Star className="h-4 w-4 text-yellow-400" />
              <Star className="h-4 w-4 text-yellow-400" />
              <Star className="h-4 w-4 text-yellow-400" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerSatisfactionSection;