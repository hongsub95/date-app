import type { Href } from 'expo-router';
import { Redirect } from 'expo-router';

import { useMenus } from '@/features/menus/menu-api';
import { LoadingScreen } from '@/shared/components/loading-screen';
import { ErrorState } from '@/shared/components/error-state';

export default function TabIndexScreen() {
  const menus = useMenus();

  if (menus.isLoading) return <LoadingScreen message="메뉴를 불러오고 있어요." />;
  if (menus.isError) return <ErrorState message="메뉴를 불러오지 못했습니다." onRetry={() => menus.refetch()} />;

  const firstPath = menus.data?.find((menu) => menu.path)?.path;
  if (!firstPath) return <ErrorState message="사용 가능한 메뉴가 없습니다." />;

  return <Redirect href={firstPath as Href} />;
}
