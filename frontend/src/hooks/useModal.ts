import { useState, useCallback } from 'react';

interface UseModalReturn {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
}

export function useModal(initialState = false): UseModalReturn {
  const [isOpen, setIsOpen] = useState(initialState);

  const open = useCallback(() => {
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggle = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  return {
    isOpen,
    open,
    close,
    toggle
  };
}

interface UseModalWithDataReturn<T> extends UseModalReturn {
  data: T | null;
  openWithData: (data: T) => void;
  clearData: () => void;
}

export function useModalWithData<T>(initialState = false): UseModalWithDataReturn<T> {
  const modal = useModal(initialState);
  const [data, setData] = useState<T | null>(null);

  const openWithData = useCallback((newData: T) => {
    setData(newData);
    modal.open();
  }, [modal]);

  const close = useCallback(() => {
    modal.close();
    // 모달이 완전히 닫힌 후 데이터 클리어 (애니메이션 고려)
    setTimeout(() => {
      setData(null);
    }, 300);
  }, [modal]);

  const clearData = useCallback(() => {
    setData(null);
  }, []);

  return {
    ...modal,
    close,
    data,
    openWithData,
    clearData
  };
}