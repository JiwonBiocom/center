/**
 * HTTPS and Mixed Content Checker
 * Ensures the application always uses HTTPS in production
 */

export function checkHTTPS() {
  // Only run in browser environment
  if (typeof window === 'undefined') return;

  const isProduction = window.location.hostname.includes('railway.app') ||
                      window.location.hostname.includes('vercel.app') ||
                      window.location.hostname.includes('netlify.app');

  if (isProduction) {
    // Check if the page itself is loaded over HTTP
    if (window.location.protocol === 'http:') {
      console.error('🚨 CRITICAL: Production site is being accessed via HTTP!');
      console.error('Redirecting to HTTPS...');
      
      // Force redirect to HTTPS
      window.location.href = window.location.href.replace('http:', 'https:');
      return;
    }

    // Log security context
    console.log('🔒 Security Check:', {
      protocol: window.location.protocol,
      hostname: window.location.hostname,
      isSecureContext: window.isSecureContext,
      apiUrl: import.meta.env.VITE_API_URL
    });

    // Monitor for mixed content errors
    window.addEventListener('error', (e) => {
      if (e.message && e.message.includes('Mixed Content')) {
        console.error('🚨 Mixed Content Error Detected:', e);
      }
    }, true);

    // Override fetch to detect HTTP requests in production
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      const [resource, config] = args;
      
      if (typeof resource === 'string' && resource.includes('railway.app')) {
        if (resource.startsWith('http://')) {
          console.error('🚨 Attempting HTTP request to production API:', resource);
          // Force HTTPS
          const httpsUrl = resource.replace('http://', 'https://');
          console.warn('🔄 Redirecting to HTTPS:', httpsUrl);
          return originalFetch(httpsUrl, config);
        }
      }
      
      return originalFetch.apply(this, args);
    };
  }
}

// Auto-run on import
checkHTTPS();