// Debug helper to check API configuration
export function debugAPIConfig() {
  const config = {
    VITE_API_URL: import.meta.env.VITE_API_URL,
    MODE: import.meta.env.MODE,
    PROD: import.meta.env.PROD,
    DEV: import.meta.env.DEV,
    BASE_URL: import.meta.env.BASE_URL,
    windowLocation: window.location.href,
    protocol: window.location.protocol,
  };

  console.log('🔍 API Configuration Debug:', config);
  
  // Check if we're on production domain but using HTTP
  if (window.location.hostname.includes('railway.app') && window.location.protocol === 'http:') {
    console.error('🚨 CRITICAL: Production site is being accessed via HTTP!');
  }
  
  return config;
}