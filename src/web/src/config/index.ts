export const config = {
  // Prefer env, default to local API for dev to avoid stale Azure hostnames
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3100',
  applicationInsightsConnectionString: import.meta.env.VITE_APPLICATIONINSIGHTS_CONNECTION_STRING || '',
};

export const getApiUrl = (endpoint: string): string => {
  const baseUrl = config.apiBaseUrl;
  // If baseUrl is a full URL (starts with http), use it directly
  if (baseUrl.startsWith('http')) {
    return `${baseUrl}${endpoint}`;
  }
  // Otherwise, treat it as a relative path
  return `${baseUrl}${endpoint}`;
};
