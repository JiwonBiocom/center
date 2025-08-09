# CustomerDetailModal UI 컴포넌트 설계서

## 📋 문서 정보
- **작성일**: 2025-06-06
- **버전**: 1.0
- **관련 문서**: [PRD](./prd-customer-enhanced.md), [API 설계](./customer-enhanced-api-design.md)

---

## 🎨 컴포넌트 개요

### CustomerDetailModal
고객의 상세 정보를 표시하고 관리하는 모달 컴포넌트로, 6개의 탭으로 구성되어 있습니다.

### 주요 특징
- 반응형 디자인 (태블릿/모바일 지원)
- 실시간 데이터 업데이트
- 로딩 상태 및 에러 처리
- 권한별 접근 제어

---

## 🏗️ 컴포넌트 구조

```typescript
// types/customer-detail.ts
export interface CustomerDetail {
  customer: CustomerExtended;
  serviceHistory: ServiceSession[];
  activePackages: PackageUsage[];
  preferences: CustomerPreferences;
  analytics?: CustomerAnalytics;
  recommendations?: ServiceRecommendation[];
}

export interface CustomerDetailModalProps {
  customerId: number;
  isOpen: boolean;
  onClose: () => void;
  onUpdate?: (customer: CustomerExtended) => void;
}
```

### 폴더 구조
```
components/
└── customers/
    ├── CustomerDetailModal.tsx         // 메인 모달 컴포넌트
    ├── CustomerDetailModal.module.css  // 스타일
    ├── tabs/
    │   ├── BasicInfoTab.tsx           // 기본정보 탭
    │   ├── ServiceHistoryTab.tsx      // 서비스이력 탭
    │   ├── PackageManagementTab.tsx   // 패키지관리 탭
    │   ├── PreferencesTab.tsx         // 선호도 탭
    │   ├── AnalyticsTab.tsx           // 분석 탭
    │   └── RecommendationsTab.tsx     // 추천 탭
    └── widgets/
        ├── PackageUsageWidget.tsx      // 패키지 사용률 위젯
        ├── ServiceHistoryWidget.tsx    // 서비스 이력 위젯
        ├── SatisfactionChart.tsx       // 만족도 차트
        └── RecommendationCard.tsx      // 추천 카드
```

---

## 💻 메인 컴포넌트 구현

### CustomerDetailModal.tsx
```tsx
import React, { useState, useEffect } from 'react';
import { Modal, Tabs, Spin, Alert, Button } from 'antd';
import { UserOutlined, HistoryOutlined, GiftOutlined, HeartOutlined, LineChartOutlined, BulbOutlined } from '@ant-design/icons';
import { useCustomerDetail } from '@/hooks/useCustomerDetail';
import BasicInfoTab from './tabs/BasicInfoTab';
import ServiceHistoryTab from './tabs/ServiceHistoryTab';
import PackageManagementTab from './tabs/PackageManagementTab';
import PreferencesTab from './tabs/PreferencesTab';
import AnalyticsTab from './tabs/AnalyticsTab';
import RecommendationsTab from './tabs/RecommendationsTab';
import styles from './CustomerDetailModal.module.css';

const { TabPane } = Tabs;

export const CustomerDetailModal: React.FC<CustomerDetailModalProps> = ({
  customerId,
  isOpen,
  onClose,
  onUpdate
}) => {
  const [activeTab, setActiveTab] = useState('1');
  const { data, loading, error, refetch } = useCustomerDetail(customerId);
  
  // 탭 변경 시 필요한 데이터 로드
  useEffect(() => {
    if (activeTab === '5' || activeTab === '6') {
      // 분석/추천 탭은 별도 API 호출
      refetch({ includeAnalytics: true });
    }
  }, [activeTab]);

  const handleSave = async (updatedData: Partial<CustomerExtended>) => {
    try {
      await updateCustomer(customerId, updatedData);
      onUpdate?.(data.customer);
      message.success('고객 정보가 업데이트되었습니다.');
    } catch (error) {
      message.error('업데이트 실패');
    }
  };

  if (loading) {
    return (
      <Modal 
        open={isOpen} 
        onCancel={onClose}
        footer={null}
        width={1200}
        centered
      >
        <div className={styles.loadingContainer}>
          <Spin size="large" tip="데이터를 불러오는 중..." />
        </div>
      </Modal>
    );
  }

  if (error) {
    return (
      <Modal 
        open={isOpen} 
        onCancel={onClose}
        footer={null}
        width={1200}
      >
        <Alert
          message="오류 발생"
          description="고객 정보를 불러올 수 없습니다."
          type="error"
          showIcon
        />
      </Modal>
    );
  }

  return (
    <Modal
      title={
        <div className={styles.modalHeader}>
          <h2>{data?.customer.name} 고객 상세 정보</h2>
          <div className={styles.customerBadges}>
            <span className={`${styles.badge} ${styles[data?.customer.membership_level]}`}>
              {data?.customer.membership_level}
            </span>
            <span className={`${styles.badge} ${styles[data?.customer.risk_level]}`}>
              {data?.customer.risk_level === 'stable' ? '안정' : '주의'}
            </span>
          </div>
        </div>
      }
      open={isOpen}
      onCancel={onClose}
      width={1200}
      bodyStyle={{ padding: 0 }}
      footer={[
        <Button key="close" onClick={onClose}>
          닫기
        </Button>,
        <Button key="save" type="primary" onClick={() => handleSave(data)}>
          저장
        </Button>
      ]}
    >
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        className={styles.tabs}
        tabBarStyle={{ marginBottom: 0 }}
      >
        <TabPane
          tab={
            <span>
              <UserOutlined />
              기본정보
            </span>
          }
          key="1"
        >
          <BasicInfoTab 
            customer={data?.customer} 
            onUpdate={handleSave}
          />
        </TabPane>
        
        <TabPane
          tab={
            <span>
              <HistoryOutlined />
              서비스이력
            </span>
          }
          key="2"
        >
          <ServiceHistoryTab 
            serviceHistory={data?.serviceHistory}
            customerId={customerId}
          />
        </TabPane>
        
        <TabPane
          tab={
            <span>
              <GiftOutlined />
              패키지관리
            </span>
          }
          key="3"
        >
          <PackageManagementTab 
            packages={data?.activePackages}
            customerId={customerId}
          />
        </TabPane>
        
        <TabPane
          tab={
            <span>
              <HeartOutlined />
              선호도
            </span>
          }
          key="4"
        >
          <PreferencesTab 
            preferences={data?.preferences}
            customerId={customerId}
            onUpdate={handleSave}
          />
        </TabPane>
        
        <TabPane
          tab={
            <span>
              <LineChartOutlined />
              분석
            </span>
          }
          key="5"
        >
          <AnalyticsTab 
            analytics={data?.analytics}
            customerId={customerId}
          />
        </TabPane>
        
        <TabPane
          tab={
            <span>
              <BulbOutlined />
              추천
            </span>
          }
          key="6"
        >
          <RecommendationsTab 
            recommendations={data?.recommendations}
            customerId={customerId}
          />
        </TabPane>
      </Tabs>
    </Modal>
  );
};
```

---

## 📑 탭 컴포넌트 상세 설계

### 1. BasicInfoTab (기본정보 탭)
```tsx
// tabs/BasicInfoTab.tsx
import React, { useState } from 'react';
import { Form, Input, Select, DatePicker, Row, Col, Card } from 'antd';
import { CustomerExtended } from '@/types';
import styles from './BasicInfoTab.module.css';

interface BasicInfoTabProps {
  customer: CustomerExtended;
  onUpdate: (data: Partial<CustomerExtended>) => void;
}

export const BasicInfoTab: React.FC<BasicInfoTabProps> = ({ customer, onUpdate }) => {
  const [form] = Form.useForm();
  const [isEditing, setIsEditing] = useState(false);

  const handleSubmit = (values: any) => {
    onUpdate(values);
    setIsEditing(false);
  };

  return (
    <div className={styles.container}>
      <Form
        form={form}
        layout="vertical"
        initialValues={customer}
        onFinish={handleSubmit}
        disabled={!isEditing}
      >
        <Row gutter={24}>
          <Col span={12}>
            <Card title="기본 정보" className={styles.infoCard}>
              <Form.Item label="이름" name="name" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item label="생년" name="birth_year">
                <Input type="number" min={1900} max={new Date().getFullYear()} />
              </Form.Item>
              <Form.Item label="성별" name="gender">
                <Select>
                  <Select.Option value="male">남성</Select.Option>
                  <Select.Option value="female">여성</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item label="직업" name="occupation">
                <Input />
              </Form.Item>
            </Card>
          </Col>
          
          <Col span={12}>
            <Card title="연락 정보" className={styles.infoCard}>
              <Form.Item label="전화번호" name="phone" rules={[{ required: true }]}>
                <Input />
              </Form.Item>
              <Form.Item label="이메일" name="email">
                <Input type="email" />
              </Form.Item>
              <Form.Item label="주소" name="address">
                <Input.TextArea rows={2} />
              </Form.Item>
              <Form.Item label="비상연락처" name="emergency_contact">
                <Input />
              </Form.Item>
            </Card>
          </Col>
        </Row>
        
        <Row gutter={24}>
          <Col span={12}>
            <Card title="관리 정보" className={styles.infoCard}>
              <Form.Item label="담당자" name="assigned_staff">
                <Select>
                  <Select.Option value="이직원">이직원</Select.Option>
                  <Select.Option value="김직원">김직원</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item label="등급" name="membership_level">
                <Select>
                  <Select.Option value="basic">일반</Select.Option>
                  <Select.Option value="premium">프리미엄</Select.Option>
                  <Select.Option value="vip">VIP</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item label="상태" name="customer_status">
                <Select>
                  <Select.Option value="active">활성</Select.Option>
                  <Select.Option value="inactive">비활성</Select.Option>
                </Select>
              </Form.Item>
            </Card>
          </Col>
          
          <Col span={12}>
            <Card title="특이 사항" className={styles.infoCard}>
              <Form.Item label="건강 관심사" name="health_goals">
                <Input.TextArea rows={3} />
              </Form.Item>
              <Form.Item label="메모" name="notes">
                <Input.TextArea rows={3} />
              </Form.Item>
            </Card>
          </Col>
        </Row>
      </Form>
    </div>
  );
};
```

### 2. ServiceHistoryTab (서비스이력 탭)
```tsx
// tabs/ServiceHistoryTab.tsx
import React, { useState } from 'react';
import { Table, Tag, Rate, Timeline, Statistic, Row, Col, Card } from 'antd';
import { ServiceSession } from '@/types';
import ServiceHistoryWidget from '../widgets/ServiceHistoryWidget';
import styles from './ServiceHistoryTab.module.css';

interface ServiceHistoryTabProps {
  serviceHistory: ServiceSession[];
  customerId: number;
}

export const ServiceHistoryTab: React.FC<ServiceHistoryTabProps> = ({ 
  serviceHistory, 
  customerId 
}) => {
  const [viewMode, setViewMode] = useState<'table' | 'timeline'>('table');

  // 서비스별 통계 계산
  const serviceStats = calculateServiceStats(serviceHistory);

  const columns = [
    {
      title: '날짜',
      dataIndex: 'service_date',
      key: 'service_date',
      render: (date: string) => new Date(date).toLocaleDateString('ko-KR'),
      sorter: (a: any, b: any) => new Date(a.service_date).getTime() - new Date(b.service_date).getTime()
    },
    {
      title: '서비스',
      dataIndex: 'service_name',
      key: 'service_name',
      render: (name: string, record: ServiceSession) => (
        <Tag color={getServiceColor(record.service_type)}>
          {name}
        </Tag>
      )
    },
    {
      title: '시간',
      dataIndex: 'duration_minutes',
      key: 'duration_minutes',
      render: (minutes: number) => `${minutes}분`
    },
    {
      title: '만족도',
      dataIndex: 'satisfaction_rating',
      key: 'satisfaction_rating',
      render: (rating: number) => <Rate disabled defaultValue={rating} />
    },
    {
      title: '담당자',
      dataIndex: 'staff_name',
      key: 'staff_name'
    },
    {
      title: '메모',
      dataIndex: 'session_notes',
      key: 'session_notes',
      ellipsis: true
    }
  ];

  return (
    <div className={styles.container}>
      {/* 서비스 이용 요약 */}
      <Card title="서비스 이용 요약" className={styles.summaryCard}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="총 방문"
              value={serviceHistory.length}
              suffix="회"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="최근 방문"
              value={getLastVisitDays(serviceHistory)}
              suffix="일 전"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="평균 주기"
              value={getAverageInterval(serviceHistory)}
              suffix="일"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="평균 만족도"
              value={getAverageSatisfaction(serviceHistory)}
              suffix="점"
              precision={1}
            />
          </Col>
        </Row>
        
        {/* 서비스별 이용 현황 */}
        <ServiceHistoryWidget stats={serviceStats} />
      </Card>

      {/* 서비스 이력 테이블/타임라인 */}
      <Card 
        title="서비스 이력"
        extra={
          <Radio.Group value={viewMode} onChange={e => setViewMode(e.target.value)}>
            <Radio.Button value="table">테이블</Radio.Button>
            <Radio.Button value="timeline">타임라인</Radio.Button>
          </Radio.Group>
        }
      >
        {viewMode === 'table' ? (
          <Table
            columns={columns}
            dataSource={serviceHistory}
            rowKey="session_id"
            pagination={{ pageSize: 10 }}
          />
        ) : (
          <Timeline mode="left">
            {serviceHistory.map(session => (
              <Timeline.Item
                key={session.session_id}
                label={new Date(session.service_date).toLocaleDateString('ko-KR')}
                color={getServiceColor(session.service_type)}
              >
                <div className={styles.timelineItem}>
                  <h4>{session.service_name}</h4>
                  <p>{session.duration_minutes}분 | {session.staff_name}</p>
                  <Rate disabled defaultValue={session.satisfaction_rating} />
                  {session.session_notes && <p>{session.session_notes}</p>}
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        )}
      </Card>
    </div>
  );
};
```

### 3. PackageManagementTab (패키지관리 탭)
```tsx
// tabs/PackageManagementTab.tsx
import React from 'react';
import { Card, Progress, Tag, Button, Space, Alert } from 'antd';
import { PackageUsage } from '@/types';
import PackageUsageWidget from '../widgets/PackageUsageWidget';
import styles from './PackageManagementTab.module.css';

interface PackageManagementTabProps {
  packages: PackageUsage[];
  customerId: number;
}

export const PackageManagementTab: React.FC<PackageManagementTabProps> = ({ 
  packages, 
  customerId 
}) => {
  const activePackages = packages.filter(pkg => pkg.status === 'active');
  const expiredPackages = packages.filter(pkg => pkg.status === 'expired');

  return (
    <div className={styles.container}>
      {/* 활성 패키지 */}
      <Card title="활성 패키지" className={styles.packageCard}>
        {activePackages.length === 0 ? (
          <Alert
            message="활성 패키지 없음"
            description="현재 사용 중인 패키지가 없습니다."
            type="info"
            showIcon
          />
        ) : (
          activePackages.map(pkg => (
            <PackageUsageWidget key={pkg.package_usage_id} package={pkg} />
          ))
        )}
      </Card>

      {/* 사용 패턴 분석 */}
      <Card title="사용 패턴 분석" className={styles.analysisCard}>
        <div className={styles.patternList}>
          <div className={styles.patternItem}>
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
            <span>브레인, 펄스 서비스 선호 (이용률 70% 이상)</span>
          </div>
          <div className={styles.patternItem}>
            <ClockCircleOutlined style={{ color: '#1890ff' }} />
            <span>주 1-2회 규칙적 방문 패턴</span>
          </div>
          <div className={styles.patternItem}>
            <CalendarOutlined style={{ color: '#722ed1' }} />
            <span>오전 시간대 예약 선호</span>
          </div>
          <div className={styles.patternItem}>
            <ExclamationCircleOutlined style={{ color: '#fa8c16' }} />
            <span>AI바이크 미이용 - 추천 필요</span>
          </div>
        </div>
      </Card>

      {/* 패키지 히스토리 */}
      {expiredPackages.length > 0 && (
        <Card title="이전 패키지" className={styles.historyCard}>
          <Table
            dataSource={expiredPackages}
            columns={[
              {
                title: '패키지명',
                dataIndex: 'package_name',
                key: 'package_name'
              },
              {
                title: '이용 기간',
                key: 'period',
                render: (_, record) => 
                  `${formatDate(record.purchase_date)} ~ ${formatDate(record.expiry_date)}`
              },
              {
                title: '이용률',
                key: 'usage_rate',
                render: (_, record) => 
                  <Progress percent={record.usage_rate} size="small" />
              }
            ]}
            pagination={false}
          />
        </Card>
      )}
    </div>
  );
};
```

---

## 🎨 스타일링 가이드

### 색상 팔레트
```css
/* CustomerDetailModal.module.css */
:root {
  --primary-color: #1890ff;
  --success-color: #52c41a;
  --warning-color: #faad14;
  --error-color: #f5222d;
  
  /* 서비스별 색상 */
  --service-brain: #722ed1;
  --service-pulse: #1890ff;
  --service-lymph: #52c41a;
  --service-red: #f5222d;
  --service-bike: #fa8c16;
  
  /* 멤버십 레벨 색상 */
  --level-basic: #8c8c8c;
  --level-premium: #1890ff;
  --level-vip: #faad14;
}

.modalHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.customerBadges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.badge.vip {
  background-color: var(--level-vip);
  color: white;
}

.badge.stable {
  background-color: var(--success-color);
  color: white;
}

.tabs {
  min-height: 500px;
}

.loadingContainer {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
```

### 반응형 디자인
```css
/* 태블릿 */
@media (max-width: 1024px) {
  .modalWidth {
    width: 95vw !important;
  }
  
  .infoCard {
    margin-bottom: 16px;
  }
}

/* 모바일 */
@media (max-width: 768px) {
  .tabs :global(.ant-tabs-nav) {
    overflow-x: auto;
  }
  
  .modalHeader {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .customerBadges {
    margin-top: 8px;
  }
}
```

---

## 🔌 통합 가이드

### 1. 고객 테이블에서 사용
```tsx
// pages/Customers.tsx
import { CustomerDetailModal } from '@/components/customers/CustomerDetailModal';

const CustomersPage = () => {
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | null>(null);
  
  const handleViewDetail = (customerId: number) => {
    setSelectedCustomerId(customerId);
  };
  
  return (
    <>
      <CustomerTable 
        onViewDetail={handleViewDetail}
      />
      
      {selectedCustomerId && (
        <CustomerDetailModal
          customerId={selectedCustomerId}
          isOpen={!!selectedCustomerId}
          onClose={() => setSelectedCustomerId(null)}
          onUpdate={(customer) => {
            // 테이블 데이터 갱신
            refetchCustomers();
          }}
        />
      )}
    </>
  );
};
```

### 2. 권한별 접근 제어
```tsx
// 권한에 따른 탭 표시 제어
const tabConfig = {
  basic: ['1', '2'], // 기본정보, 서비스이력만
  manager: ['1', '2', '3', '4'], // + 패키지관리, 선호도
  admin: ['1', '2', '3', '4', '5', '6'] // 모든 탭
};

const visibleTabs = tabConfig[userRole] || tabConfig.basic;
```

---

## 📱 모바일 최적화

### 터치 인터페이스
- 스와이프로 탭 전환
- 터치 친화적인 버튼 크기 (최소 44px)
- 플로팅 액션 버튼 추가

### 성능 최적화
- 탭 레이지 로딩
- 이미지 최적화
- 무한 스크롤 (서비스 이력)

---

## 🧪 테스트 시나리오

### 단위 테스트
```typescript
// CustomerDetailModal.test.tsx
describe('CustomerDetailModal', () => {
  it('should render all tabs', () => {
    const { getByText } = render(
      <CustomerDetailModal {...mockProps} />
    );
    
    expect(getByText('기본정보')).toBeInTheDocument();
    expect(getByText('서비스이력')).toBeInTheDocument();
    // ...
  });
  
  it('should load analytics data when analytics tab is selected', () => {
    // 분석 탭 선택 시 API 호출 확인
  });
});
```

### E2E 테스트
1. 모달 열기/닫기
2. 탭 전환
3. 데이터 수정 및 저장
4. 권한별 접근 제어

---

*이 문서는 CustomerDetailModal UI 컴포넌트의 상세 설계서입니다. 구현 시 참조하세요.*