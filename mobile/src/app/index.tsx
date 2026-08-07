import { Redirect } from 'expo-router';

import { LoadingScreen } from '@/shared/components/loading-screen';
import { useAuth } from '@/features/auth/auth-context';

export default function IndexScreen() {
  const { status } = useAuth();

  if (status === 'loading') {
    return <LoadingScreen message="로그인 정보를 확인하고 있어요." />;
  }

  return <Redirect href={status === 'authenticated' ? '/(tabs)' : '/(auth)/login'} />;
}
