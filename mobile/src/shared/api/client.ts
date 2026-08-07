import { create, AxiosError, type InternalAxiosRequestConfig } from 'axios';

import { getApiBaseUrl } from '@/shared/config/env';
import { notifyUnauthorized } from './auth-events';
import { tokenStore } from './token-store';
import type { ApiErrorPayload, TokenPair } from './types';

type RetryableRequest = InternalAxiosRequestConfig & { _retry?: boolean };

export const apiClient = create({ timeout: 15_000 });
const refreshClient = create({ timeout: 15_000 });

apiClient.interceptors.request.use(async (config) => {
  config.baseURL = getApiBaseUrl();
  const accessToken = await tokenStore.getAccessToken();
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
  return config;
});

let refreshPromise: Promise<TokenPair> | null = null;

async function refreshTokens(): Promise<TokenPair> {
  const refreshToken = await tokenStore.getRefreshToken();
  if (!refreshToken) throw new Error('Missing refresh token');

  const response = await refreshClient.post<TokenPair>(
    '/auth/refresh',
    { refresh_token: refreshToken },
    { baseURL: getApiBaseUrl() },
  );
  await tokenStore.save(response.data);
  return response.data;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorPayload>) => {
    const original = error.config as RetryableRequest | undefined;
    const shouldRefresh =
      error.response?.status === 401 &&
      error.response.data?.code === 'UNAUTHORIZED' &&
      original &&
      !original._retry &&
      !original.url?.endsWith('/auth/refresh');

    if (!shouldRefresh) throw error;
    original._retry = true;

    try {
      refreshPromise ??= refreshTokens().finally(() => {
        refreshPromise = null;
      });
      const tokens = await refreshPromise;
      original.headers.Authorization = `Bearer ${tokens.access_token}`;
      return apiClient(original);
    } catch (refreshError) {
      await tokenStore.clear();
      notifyUnauthorized();
      throw refreshError;
    }
  },
);
