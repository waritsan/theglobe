export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'https://app-api-hla54ovhrzo3e.azurewebsites.net',
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
