import { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { Save, Info, Users, DollarSign, Calendar } from 'lucide-react';

interface MembershipCriteria {
  bronze: LevelCriteria;
  silver: LevelCriteria;
  gold: LevelCriteria;
  platinum: LevelCriteria;
}

interface LevelCriteria {
  name: string;
  annual_revenue_min: number;
  annual_revenue_max?: number;
  total_visits_min: number;
  total_visits_max?: number;
  benefits: {
    discount_rate: number;
    test_vouchers?: number;
    supplements?: number;
    sessions?: number;
    dedicated_consultant?: boolean;
    description: string;
  };
}

interface StatusDescriptions {
  customer_status: {
    [key: string]: {
      name: string;
      description: string;
      color: string;
    };
  };
}

export default function MembershipSettings() {
  const [criteria, setCriteria] = useState<MembershipCriteria | null>(null);
  const [statusDescriptions, setStatusDescriptions] = useState<StatusDescriptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'criteria' | 'descriptions'>('criteria');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const [criteriaRes, descriptionsRes] = await Promise.all([
        api.get('/api/v1/membership/criteria'),
        api.get('/api/v1/membership/status-descriptions')
      ]);
      
      setCriteria(criteriaRes.data);
      setStatusDescriptions(descriptionsRes.data);
    } catch (error) {
      console.error('Failed to fetch membership settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCriteriaChange = (level: keyof MembershipCriteria, field: string, value: any) => {
    if (!criteria) return;
    
    const fields = field.split('.');
    const newCriteria = { ...criteria };
    
    if (fields.length === 1) {
      (newCriteria[level] as any)[field] = value;
    } else if (fields.length === 2 && fields[0] === 'benefits') {
      newCriteria[level].benefits = {
        ...newCriteria[level].benefits,
        [fields[1]]: value
      };
    }
    
    setCriteria(newCriteria);
  };

  const handleSave = async () => {
    if (!criteria) return;
    
    setSaving(true);
    try {
      await api.put('/api/v1/membership/criteria', criteria);
      alert('회원 등급 기준이 성공적으로 저장되었습니다.');
    } catch (error) {
      console.error('Failed to save criteria:', error);
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setSaving(false);
    }
  };

  const handleUpdateAllCustomers = async () => {
    if (!confirm('모든 고객의 등급과 상태를 재계산하시겠습니까? 이 작업은 시간이 걸릴 수 있습니다.')) {
      return;
    }
    
    try {
      const response = await api.post('/api/v1/membership/update-all-customers');
      alert(response.data.message);
    } catch (error) {
      console.error('Failed to update customers:', error);
      alert('고객 정보 업데이트 중 오류가 발생했습니다.');
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex">
          <button
            onClick={() => setActiveTab('criteria')}
            className={`py-4 px-6 border-b-2 font-medium text-sm ${
              activeTab === 'criteria'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            회원 등급 기준
          </button>
          <button
            onClick={() => setActiveTab('descriptions')}
            className={`py-4 px-6 border-b-2 font-medium text-sm ${
              activeTab === 'descriptions'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            상태 설명
          </button>
        </nav>
      </div>

      <div className="p-6">
        {activeTab === 'criteria' && criteria && (
          <div>
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">회원 등급 기준 설정</h3>
              <p className="text-sm text-gray-600">
                각 등급별 기준을 설정합니다. 연 매출과 누적 방문 횟수를 모두 만족해야 해당 등급이 부여됩니다.
              </p>
            </div>

            <div className="space-y-6">
              {Object.entries(criteria).map(([level, data]) => (
                <div key={level} className="border rounded-lg p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4 capitalize">
                    {data.name} ({level})
                  </h4>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <DollarSign className="inline w-4 h-4 mr-1" />
                        최소 연매출 (원)
                      </label>
                      <input
                        type="number"
                        value={data.annual_revenue_min}
                        onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'annual_revenue_min', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    
                    {level !== 'platinum' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          <DollarSign className="inline w-4 h-4 mr-1" />
                          최대 연매출 (원)
                        </label>
                        <input
                          type="number"
                          value={data.annual_revenue_max || ''}
                          onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'annual_revenue_max', parseInt(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <Calendar className="inline w-4 h-4 mr-1" />
                        최소 방문 횟수
                      </label>
                      <input
                        type="number"
                        value={data.total_visits_min}
                        onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'total_visits_min', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                    
                    {level !== 'platinum' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          <Calendar className="inline w-4 h-4 mr-1" />
                          최대 방문 횟수
                        </label>
                        <input
                          type="number"
                          value={data.total_visits_max || ''}
                          onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'total_visits_max', parseInt(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                    )}
                  </div>

                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">혜택</h5>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">할인율 (%)</label>
                        <input
                          type="number"
                          value={data.benefits.discount_rate}
                          onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'benefits.discount_rate', parseInt(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                      </div>
                      
                      {level !== 'bronze' && (
                        <>
                          <div>
                            <label className="block text-sm text-gray-600 mb-1">검사권</label>
                            <input
                              type="number"
                              value={data.benefits.test_vouchers || ''}
                              onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'benefits.test_vouchers', parseInt(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm text-gray-600 mb-1">영양제</label>
                            <input
                              type="number"
                              value={data.benefits.supplements || ''}
                              onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'benefits.supplements', parseInt(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                            />
                          </div>
                          
                          <div>
                            <label className="block text-sm text-gray-600 mb-1">세션</label>
                            <input
                              type="number"
                              value={data.benefits.sessions || ''}
                              onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'benefits.sessions', parseInt(e.target.value))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                            />
                          </div>
                        </>
                      )}
                    </div>
                    
                    <div className="mt-3">
                      <label className="block text-sm text-gray-600 mb-1">혜택 설명</label>
                      <input
                        type="text"
                        value={data.benefits.description}
                        onChange={(e) => handleCriteriaChange(level as keyof MembershipCriteria, 'benefits.description', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-between">
              <button
                onClick={handleUpdateAllCustomers}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                <Users className="inline w-4 h-4 mr-2" />
                모든 고객 재계산
              </button>
              
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                <Save className="inline w-4 h-4 mr-2" />
                {saving ? '저장 중...' : '저장'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'descriptions' && statusDescriptions && (
          <div>
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">고객 상태 설명</h3>
              <p className="text-sm text-gray-600">
                관리자와 스탭이 참고할 수 있는 고객 상태에 대한 설명입니다.
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">고객 상태</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(statusDescriptions.customer_status).map(([key, value]) => (
                    <div key={key} className="border rounded-lg p-4">
                      <div className="flex items-center mb-2">
                        <div className={`w-3 h-3 rounded-full mr-2 ${
                          value.color === 'green' ? 'bg-green-500' :
                          value.color === 'yellow' ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`} />
                        <h5 className="font-medium text-gray-900">{value.name}</h5>
                      </div>
                      <p className="text-sm text-gray-600">{value.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex">
                <Info className="w-5 h-5 text-blue-400 mr-2 flex-shrink-0" />
                <div className="text-sm text-blue-700">
                  <p className="font-medium mb-1">자동 업데이트 정보</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>고객 상태는 마지막 방문일을 기준으로 자동 계산됩니다.</li>
                    <li>회원 등급은 연매출과 누적 방문 횟수를 기준으로 자동 계산됩니다.</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}