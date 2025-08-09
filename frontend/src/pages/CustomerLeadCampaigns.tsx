import { useState, useEffect } from 'react';
import { api } from '../lib/api';
import { Plus, Target, TrendingUp, Users, Calendar } from 'lucide-react';
import CampaignModal from '../components/customer-leads/CampaignModal';
import CampaignList from '../components/customer-leads/CampaignList';
import CampaignTargetsModal from '../components/customer-leads/CampaignTargetsModal';

interface Campaign {
  campaign_id: number;
  campaign_name: string;
  start_date: string;
  end_date?: string;
  target_criteria?: any;
  notes?: string;
  is_active: boolean;
  target_count: number;
  success_count: number;
  created_by?: number;
  created_by_name?: string;
  created_at: string;
  updated_at?: string;
}

interface CampaignStats {
  total_campaigns: number;
  active_campaigns: number;
  total_targets: number;
  total_conversions: number;
  overall_conversion_rate: number;
}

export default function CustomerLeadCampaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [stats, setStats] = useState<CampaignStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
  const [isTargetsModalOpen, setIsTargetsModalOpen] = useState(false);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);

  useEffect(() => {
    fetchCampaigns();
    fetchStats();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await api.get('/api/v1/customer-leads/campaigns');
      setCampaigns(response.data);
    } catch (error) {
      console.error('Failed to fetch campaigns:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/v1/customer-leads/campaigns/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleDelete = async (campaignId: number) => {
    if (!window.confirm('정말로 이 캠페인을 삭제하시겠습니까?')) return;
    
    try {
      await api.delete(`/api/v1/customer-leads/campaigns/${campaignId}`);
      fetchCampaigns();
      fetchStats();
    } catch (error) {
      console.error('Failed to delete campaign:', error);
      alert('캠페인 삭제에 실패했습니다.');
    }
  };

  const handleViewTargets = (campaign: Campaign) => {
    setSelectedCampaign(campaign);
    setIsTargetsModalOpen(true);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">재등록 캠페인 관리</h1>
            <p className="text-sm text-gray-600 mt-1">
              미활동 고객을 대상으로 재등록을 유도하는 캠페인을 관리합니다.
            </p>
          </div>
          
          <button
            onClick={() => {
              setEditingCampaign(null);
              setIsModalOpen(true);
            }}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            새 캠페인
          </button>
        </div>
        
        {/* 통계 카드 */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">전체 캠페인</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_campaigns}</p>
                </div>
                <Target className="w-8 h-8 text-gray-400" />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">진행중 캠페인</p>
                  <p className="text-2xl font-bold text-green-600 mt-1">{stats.active_campaigns}</p>
                </div>
                <Calendar className="w-8 h-8 text-green-400" />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">총 대상 인원</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stats.total_targets}</p>
                </div>
                <Users className="w-8 h-8 text-gray-400" />
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">평균 전환율</p>
                  <p className="text-2xl font-bold text-indigo-600 mt-1">{stats.overall_conversion_rate}%</p>
                </div>
                <TrendingUp className="w-8 h-8 text-indigo-400" />
              </div>
            </div>
          </div>
        )}
        
        {/* 캠페인 목록 */}
        <CampaignList
          campaigns={campaigns}
          loading={loading}
          onEdit={(campaign) => {
            setEditingCampaign(campaign);
            setIsModalOpen(true);
          }}
          onDelete={handleDelete}
          onViewTargets={handleViewTargets}
        />
      </div>

      {/* 모달 */}
      <CampaignModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingCampaign(null);
        }}
        onSuccess={() => {
          setIsModalOpen(false);
          setEditingCampaign(null);
          fetchCampaigns();
          fetchStats();
        }}
        campaignData={editingCampaign}
      />
      
      <CampaignTargetsModal
        isOpen={isTargetsModalOpen}
        onClose={() => {
          setIsTargetsModalOpen(false);
          setSelectedCampaign(null);
          fetchCampaigns();
          fetchStats();
        }}
        campaign={selectedCampaign}
      />
    </div>
  );
}