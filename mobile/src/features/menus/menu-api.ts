import { useQuery } from '@tanstack/react-query';

import { apiClient } from '@/shared/api/client';
import type { MenuItem, MenuListResponse } from '@/shared/api/types';

async function listMenus(): Promise<MenuItem[]> {
  const response = await apiClient.get<MenuListResponse>('/menus', { params: { scope: 'app' } });
  return response.data.menus;
}

export function useMenus() {
  return useQuery({ queryKey: ['menus', 'app'], queryFn: listMenus, staleTime: 5 * 60_000 });
}
