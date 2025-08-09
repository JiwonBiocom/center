import React from 'react';
import { X } from 'lucide-react';

interface BaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  onSubmit?: (e: React.FormEvent) => void | Promise<void>;
  loading?: boolean;
  width?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  submitText?: string;
  cancelText?: string;
  showFooter?: boolean;
}

export default function BaseModal({
  isOpen,
  onClose,
  title,
  children,
  onSubmit,
  loading = false,
  width = '2xl',
  submitText = '저장',
  cancelText = '취소',
  showFooter = true
}: BaseModalProps) {
  if (!isOpen) return null;

  const widthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl'
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmit) {
      await onSubmit(e);
    }
  };

  const content = (
    <>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          {title}
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-500 transition-colors"
          type="button"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="modal-body">
        {children}
      </div>

      {showFooter && onSubmit && (
        <div className="flex justify-end gap-3 mt-6">
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {cancelText}
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '처리 중...' : submitText}
          </button>
        </div>
      )}
    </>
  );

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div 
        className="flex items-center justify-center min-h-screen px-4"
        onClick={handleBackdropClick}
      >
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        
        <div className={`relative bg-white rounded-lg w-full ${widthClasses[width]} p-6 max-h-[90vh] overflow-y-auto`}>
          {onSubmit ? (
            <form onSubmit={handleFormSubmit}>
              {content}
            </form>
          ) : (
            content
          )}
        </div>
      </div>
    </div>
  );
}