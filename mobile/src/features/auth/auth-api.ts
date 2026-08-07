import { apiClient } from '@/shared/api/client';
import { tokenStore } from '@/shared/api/token-store';
import type { RegisterResponse, TokenPair, User } from '@/shared/api/types';

export type LoginInput = { email: string; password: string };
export type RegisterInput = LoginInput & { nickname: string };

export async function login(input: LoginInput): Promise<User> {
  const tokenResponse = await apiClient.post<TokenPair>('/auth/login', input);
  await tokenStore.save(tokenResponse.data);
  return getMe();
}

export async function register(input: RegisterInput): Promise<User> {
  const response = await apiClient.post<RegisterResponse>('/auth/register', input);
  await tokenStore.save(response.data.tokens);
  return response.data.user;
}

export async function getMe(): Promise<User> {
  const response = await apiClient.get<User>('/auth/me');
  return response.data;
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post('/auth/logout');
  } finally {
    await tokenStore.clear();
  }
}
