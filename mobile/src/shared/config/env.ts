const apiBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL?.replace(/\/$/, '');

if (!apiBaseUrl && __DEV__) {
  console.warn('EXPO_PUBLIC_API_BASE_URL이 없습니다. mobile/.env.local을 설정해주세요.');
}

export function getApiBaseUrl(): string {
  if (!apiBaseUrl) {
    throw new Error('EXPO_PUBLIC_API_BASE_URL is required');
  }
  return apiBaseUrl;
}
