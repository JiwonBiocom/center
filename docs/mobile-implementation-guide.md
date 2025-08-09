# AIBIO 모바일 구현 가이드

## 🚀 즉시 적용 가능한 모바일 최적화

### 1. 현재 시스템 기반 빠른 개선안

#### A. Layout.tsx 모바일 대응
```tsx
// 모바일에서 사이드바를 햄버거 메뉴로 변경
const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

return (
  <div className="min-h-screen bg-gray-50">
    {/* Mobile Header */}
    <div className="lg:hidden">
      <header className="bg-white shadow-sm p-4 flex justify-between items-center">
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          <Menu className="w-6 h-6" />
        </button>
        <img src="/aibio-logo.png" className="h-8" />
        <NotificationBell />
      </header>
    </div>
    
    {/* Sidebar - hidden on mobile, slide-in menu */}
    <div className={`
      fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform 
      ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      transition-transform duration-300 ease-in-out
      lg:relative lg:translate-x-0
    `}>
      {/* 기존 사이드바 내용 */}
    </div>
  </div>
);
```

#### B. 모바일 최적화 대시보드
```tsx
// Dashboard.tsx 모바일 버전
export default function Dashboard() {
  const isMobile = useMediaQuery('(max-width: 768px)');
  
  if (isMobile) {
    return <MobileDashboard />;
  }
  
  return <DesktopDashboard />;
}

// MobileDashboard.tsx
function MobileDashboard() {
  return (
    <div className="p-4 pb-20"> {/* 하단 탭바 공간 확보 */}
      {/* 오늘의 요약 카드 */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white mb-4">
        <h2 className="text-lg font-bold">좋은 아침입니다! 👋</h2>
        <p className="text-sm opacity-90">{new Date().toLocaleDateString('ko-KR', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        })}</p>
      </div>
      
      {/* 주요 지표 - 가로 스크롤 */}
      <div className="flex gap-3 overflow-x-auto pb-2 mb-4">
        <StatCard title="오늘 예약" value="12명" />
        <StatCard title="예상 매출" value="523만원" />
        <StatCard title="대기 고객" value="3명" />
      </div>
      
      {/* 긴급 알림 */}
      <QuickAlerts />
      
      {/* 오늘의 예약 타임라인 */}
      <TodayTimeline />
    </div>
  );
}
```

### 2. 모바일 전용 컴포넌트

#### A. 하단 탭 네비게이션
```tsx
// components/MobileTabBar.tsx
export default function MobileTabBar() {
  const location = useLocation();
  
  const tabs = [
    { path: '/', icon: Home, label: '홈' },
    { path: '/reservations', icon: Calendar, label: '예약' },
    { path: '/quick-search', icon: Search, label: '검색' },
    { path: '/notifications', icon: Bell, label: '알림' },
    { path: '/menu', icon: Menu, label: '메뉴' },
  ];
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 lg:hidden">
      <div className="flex justify-around items-center h-16">
        {tabs.map(tab => (
          <Link
            key={tab.path}
            to={tab.path}
            className={`flex flex-col items-center justify-center flex-1 h-full ${
              location.pathname === tab.path ? 'text-blue-600' : 'text-gray-600'
            }`}
          >
            <tab.icon className="w-5 h-5 mb-1" />
            <span className="text-xs">{tab.label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
```

#### B. 스와이프 가능한 예약 카드
```tsx
// components/SwipeableReservationCard.tsx
import { useSwipeable } from 'react-swipeable';

export default function SwipeableReservationCard({ reservation, onStatusChange }) {
  const [swipeProgress, setSwipeProgress] = useState(0);
  
  const handlers = useSwipeable({
    onSwiping: (eventData) => {
      setSwipeProgress(eventData.deltaX);
    },
    onSwipedLeft: () => {
      if (swipeProgress < -100) {
        onStatusChange('cancelled');
      }
      setSwipeProgress(0);
    },
    onSwipedRight: () => {
      if (swipeProgress > 100) {
        onStatusChange('completed');
      }
      setSwipeProgress(0);
    },
  });
  
  return (
    <div {...handlers} className="relative overflow-hidden">
      {/* 배경 액션 표시 */}
      <div className="absolute inset-0 flex items-center justify-between px-4">
        <span className="text-green-600 font-bold">완료</span>
        <span className="text-red-600 font-bold">취소</span>
      </div>
      
      {/* 예약 카드 */}
      <div 
        className="bg-white p-4 rounded-lg shadow transform transition-transform"
        style={{ transform: `translateX(${swipeProgress}px)` }}
      >
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-semibold">{reservation.customerName}</h3>
            <p className="text-sm text-gray-600">{reservation.serviceName}</p>
            <p className="text-xs text-gray-500">{reservation.time}</p>
          </div>
          <StatusBadge status={reservation.status} />
        </div>
      </div>
    </div>
  );
}
```

#### C. 모바일 빠른 검색
```tsx
// pages/QuickSearch.tsx
export default function QuickSearch() {
  const [phone, setPhone] = useState('');
  const [results, setResults] = useState([]);
  
  const handlePhoneInput = (value: string) => {
    // 자동 하이픈 추가
    const cleaned = value.replace(/\D/g, '');
    const formatted = cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
    setPhone(formatted);
    
    // 실시간 검색
    if (cleaned.length >= 4) {
      searchCustomers(cleaned);
    }
  };
  
  return (
    <div className="p-4 pb-20">
      {/* 큰 전화번호 입력 필드 */}
      <div className="mb-6">
        <input
          type="tel"
          value={phone}
          onChange={(e) => handlePhoneInput(e.target.value)}
          placeholder="010-0000-0000"
          className="w-full text-2xl p-4 border-2 border-gray-300 rounded-lg text-center"
          autoFocus
        />
      </div>
      
      {/* 빠른 액션 버튼 */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <button className="bg-blue-500 text-white p-4 rounded-lg flex items-center justify-center">
          <Phone className="w-5 h-5 mr-2" />
          전화 걸기
        </button>
        <button className="bg-green-500 text-white p-4 rounded-lg flex items-center justify-center">
          <MessageSquare className="w-5 h-5 mr-2" />
          문자 보내기
        </button>
      </div>
      
      {/* 검색 결과 */}
      <div className="space-y-3">
        {results.map(customer => (
          <CustomerQuickCard key={customer.id} customer={customer} />
        ))}
      </div>
    </div>
  );
}
```

### 3. PWA 설정

#### manifest.json
```json
{
  "name": "AIBIO 센터 관리",
  "short_name": "AIBIO",
  "description": "AIBIO 센터 관리 시스템",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3B82F6",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

#### Service Worker
```javascript
// sw.js
const CACHE_NAME = 'aibio-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/offline.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 캐시에 있으면 캐시에서, 없으면 네트워크에서
        return response || fetch(event.request);
      })
      .catch(() => {
        // 오프라인일 때
        if (event.request.destination === 'document') {
          return caches.match('/offline.html');
        }
      })
  );
});
```

### 4. 모바일 특화 Hook

```typescript
// hooks/useMobileFeatures.ts
export function useMobileFeatures() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [deviceType, setDeviceType] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // 디바이스 타입 감지
    const checkDevice = () => {
      const width = window.innerWidth;
      if (width < 768) setDeviceType('mobile');
      else if (width < 1024) setDeviceType('tablet');
      else setDeviceType('desktop');
    };
    
    checkDevice();
    window.addEventListener('resize', checkDevice);
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('resize', checkDevice);
    };
  }, []);
  
  const vibrate = (pattern: number | number[] = 50) => {
    if ('vibration' in navigator) {
      navigator.vibrate(pattern);
    }
  };
  
  const share = async (data: ShareData) => {
    if (navigator.share) {
      try {
        await navigator.share(data);
      } catch (err) {
        console.error('Share failed:', err);
      }
    }
  };
  
  return {
    isOnline,
    deviceType,
    isMobile: deviceType === 'mobile',
    isTablet: deviceType === 'tablet',
    vibrate,
    share,
  };
}
```

### 5. 성능 최적화 전략

```typescript
// 이미지 레이지 로딩
const LazyImage = ({ src, alt, ...props }) => {
  const [imageSrc, setImageSrc] = useState('');
  const imgRef = useRef(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setImageSrc(src);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );
    
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    
    return () => observer.disconnect();
  }, [src]);
  
  return (
    <img
      ref={imgRef}
      src={imageSrc || '/placeholder.png'}
      alt={alt}
      {...props}
    />
  );
};

// 가상 스크롤링 (큰 리스트용)
import { FixedSizeList } from 'react-window';

const VirtualizedCustomerList = ({ customers }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <CustomerListItem customer={customers[index]} />
    </div>
  );
  
  return (
    <FixedSizeList
      height={window.innerHeight - 200} // 헤더, 탭바 제외
      itemCount={customers.length}
      itemSize={80}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
};
```

## 📋 체크리스트

### 즉시 구현 가능 (1일)
- [ ] 반응형 브레이크포인트 설정
- [ ] 모바일 네비게이션 메뉴
- [ ] 터치 친화적 버튼 크기 조정

### 단기 구현 (1주)
- [ ] 모바일 대시보드 레이아웃
- [ ] 하단 탭 네비게이션
- [ ] 스와이프 제스처 추가
- [ ] PWA 기본 설정

### 중기 구현 (2-3주)
- [ ] 오프라인 지원
- [ ] 푸시 알림
- [ ] 음성 입력
- [ ] 네이티브 앱 기능 연동

## 결론

현재 시스템을 기반으로 점진적으로 모바일 최적화를 진행하면 됩니다.
핵심은 기존 기능을 유지하면서 모바일 사용성을 개선하는 것입니다.