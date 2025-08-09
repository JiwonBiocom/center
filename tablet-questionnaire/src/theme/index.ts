import {MD3LightTheme as DefaultTheme} from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#4F46E5', // Indigo
    secondary: '#7C3AED', // Purple
    tertiary: '#06B6D4', // Cyan
    error: '#EF4444',
    success: '#10B981',
    warning: '#F59E0B',
    info: '#3B82F6',
    
    // Custom colors
    background: '#F9FAFB',
    surface: '#FFFFFF',
    text: '#111827',
    textSecondary: '#6B7280',
    border: '#E5E7EB',
    
    // Status colors
    pending: '#FEF3C7',
    completed: '#D1FAE5',
    cancelled: '#FEE2E2',
  },
  
  // Typography
  fonts: {
    ...DefaultTheme.fonts,
    titleLarge: {
      ...DefaultTheme.fonts.titleLarge,
      fontSize: 28,
      lineHeight: 36,
      fontWeight: '700' as const,
    },
  },
  
  // Spacing
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  
  // Border radius
  roundness: 12,
};

export type AppTheme = typeof theme;