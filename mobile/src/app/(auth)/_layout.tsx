import { Redirect, Stack } from 'expo-router';

import { useAuth } from '@/features/auth/auth-context';
import { LoadingScreen } from '@/shared/components/loading-screen';

export default function AuthLayout() {
  const { status } = useAuth();

  if (status === 'loading') {
    return <LoadingScreen message="로그인 정보를 확인하고 있어요." />;
  }

  if (status === 'authenticated') {
    return <Redirect href="/(tabs)" />;
  }

  return <Stack screenOptions={{ headerShown: false }} />;
}
