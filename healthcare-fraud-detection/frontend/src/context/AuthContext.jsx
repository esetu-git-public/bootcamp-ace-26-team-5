import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import * as authService from '../services/authService';

const AuthContext = createContext(null);

export const ROLES = {
  CUSTOMER: 'customer',
  EMPLOYEE: 'employee',
  ADMIN: 'admin',
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const raw = sessionStorage.getItem('cg_user');
    if (raw) setUser(JSON.parse(raw));
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await authService.login(email, password);
    sessionStorage.setItem('cg_access_token', data.accessToken);
    sessionStorage.setItem('cg_refresh_token', data.refreshToken);
    sessionStorage.setItem('cg_user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }, []);

  const signup = useCallback(async (payload) => {
    const data = await authService.signup(payload);
    sessionStorage.setItem('cg_access_token', data.accessToken);
    sessionStorage.setItem('cg_refresh_token', data.refreshToken);
    sessionStorage.setItem('cg_user', JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(async () => {
    try { await authService.logout(); } catch (e) { /* noop */ }
    sessionStorage.removeItem('cg_access_token');
    sessionStorage.removeItem('cg_refresh_token');
    sessionStorage.removeItem('cg_user');
    setUser(null);
  }, []);

  const hasRole = useCallback((...roles) => !!user && roles.includes(user.role), [user]);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, hasRole }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
