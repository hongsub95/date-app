import { createContext, type PropsWithChildren, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { setUnauthorizedHandler } from '@/shared/api/auth-events';
import { tokenStore } from '@/shared/api/token-store';
import type { User } from '@/shared/api/types';
import * as authApi from './auth-api';

type AuthStatus = 'loading' | 'authenticated' | 'anonymous';

type AuthContextValue = {
  status: AuthStatus;
  user: User | null;
  login: typeof authApi.login;
  register: typeof authApi.register;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [user, setUser] = useState<User | null>(null);

  const becomeAnonymous = useCallback(() => {
    setUser(null);
    setStatus('anonymous');
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(becomeAnonymous);
    return () => setUnauthorizedHandler(null);
  }, [becomeAnonymous]);

  useEffect(() => {
    async function bootstrap() {
      const refreshToken = await tokenStore.getRefreshToken();
      if (!refreshToken) {
        becomeAnonymous();
        return;
      }
      try {
        setUser(await authApi.getMe());
        setStatus('authenticated');
      } catch {
        await tokenStore.clear();
        becomeAnonymous();
      }
    }
    bootstrap();
  }, [becomeAnonymous]);

  const login = useCallback(async (input: authApi.LoginInput) => {
    const nextUser = await authApi.login(input);
    setUser(nextUser);
    setStatus('authenticated');
    return nextUser;
  }, []);

  const register = useCallback(async (input: authApi.RegisterInput) => {
    const nextUser = await authApi.register(input);
    setUser(nextUser);
    setStatus('authenticated');
    return nextUser;
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      becomeAnonymous();
    }
  }, [becomeAnonymous]);

  const value = useMemo(() => ({ status, user, login, register, logout }), [status, user, login, register, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside AuthProvider');
  return value;
}
