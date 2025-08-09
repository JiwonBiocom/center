import { useState, useEffect, useCallback, useRef } from 'react';

interface UseInfiniteScrollOptions {
  threshold?: number;
  hasMore: boolean;
  loading: boolean;
}

/**
 * 무한 스크롤 훅 - 대량 데이터 로딩 최적화
 */
export function useInfiniteScroll(
  callback: () => void,
  options: UseInfiniteScrollOptions
) {
  const { threshold = 100, hasMore, loading } = options;
  const observerRef = useRef<IntersectionObserver | null>(null);
  const [element, setElement] = useState<HTMLElement | null>(null);

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries;
      if (target.isIntersecting && hasMore && !loading) {
        callback();
      }
    },
    [callback, hasMore, loading]
  );

  useEffect(() => {
    if (element) {
      if (observerRef.current) observerRef.current.disconnect();
      
      observerRef.current = new IntersectionObserver(handleObserver, {
        rootMargin: `${threshold}px`,
      });
      
      observerRef.current.observe(element);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [element, handleObserver, threshold]);

  return setElement;
}