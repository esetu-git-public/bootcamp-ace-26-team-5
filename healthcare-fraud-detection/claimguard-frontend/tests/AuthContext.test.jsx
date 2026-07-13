import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth, ROLES } from './AuthContext.jsx';

// Mock the auth service so these tests exercise AuthContext's own logic
// (state management + localStorage persistence) without depending on
// claimsService/mockData internals or network timing.
vi.mock('../services/authService', () => ({
  login: vi.fn(),
  signup: vi.fn(),
  logout: vi.fn(),
}));

import * as authService from '../services/authService';

const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

const mockLoginResponse = {
  accessToken: 'mock-access-USR-001',
  refreshToken: 'mock-refresh-USR-001',
  user: { id: 'USR-001', name: 'Priya Sharma', email: 'officer@claimguard.ai', role: ROLES.OFFICER },
};

beforeEach(() => {
  vi.clearAllMocks();
  window.localStorage.clear();
});

describe('AuthContext — initial load', () => {
  it('starts with loading true, then resolves to no user when localStorage is empty', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.user).toBeNull();
  });

  it('hydrates the user from localStorage if a session already exists', async () => {
    window.localStorage.setItem('cg_user', JSON.stringify(mockLoginResponse.user));
    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.user).toEqual(mockLoginResponse.user);
  });
});

describe('AuthContext — login', () => {
  it('sets the user and persists tokens + user to localStorage on success', async () => {
    authService.login.mockResolvedValueOnce(mockLoginResponse);
    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.login('officer@claimguard.ai', 'demo1234');
    });

    expect(authService.login).toHaveBeenCalledWith('officer@claimguard.ai', 'demo1234');
    expect(result.current.user).toEqual(mockLoginResponse.user);
    expect(window.localStorage.getItem('cg_access_token')).toBe(mockLoginResponse.accessToken);
    expect(window.localStorage.getItem('cg_refresh_token')).toBe(mockLoginResponse.refreshToken);
    expect(JSON.parse(window.localStorage.getItem('cg_user'))).toEqual(mockLoginResponse.user);
  });

  it('does not set a user and leaves localStorage empty when credentials are invalid', async () => {
    const authError = new Error('Invalid email or password');
    authError.isAuthError = true;
    authService.login.mockRejectedValueOnce(authError);

    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await expect(result.current.login('wrong@claimguard.ai', 'bad')).rejects.toThrow('Invalid email or password');
    });

    expect(result.current.user).toBeNull();
    expect(window.localStorage.getItem('cg_access_token')).toBeNull();
  });
});

describe('AuthContext — signup', () => {
  it('creates and logs in a new Policyholder, persisting session state', async () => {
    const signupResponse = {
      accessToken: 'mock-access-USR-005',
      refreshToken: 'mock-refresh-USR-005',
      user: { id: 'USR-005', name: 'New User', email: 'newuser@example.com', role: ROLES.POLICYHOLDER },
    };
    authService.signup.mockResolvedValueOnce(signupResponse);

    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.signup({ name: 'New User', email: 'newuser@example.com', password: 'pw123456' });
    });

    expect(result.current.user).toEqual(signupResponse.user);
    expect(result.current.user.role).toBe(ROLES.POLICYHOLDER);
    expect(JSON.parse(window.localStorage.getItem('cg_user'))).toEqual(signupResponse.user);
  });

  it('surfaces a duplicate-email error without setting a user', async () => {
    const err = new Error('An account with this email already exists.');
    err.isAuthError = true;
    authService.signup.mockRejectedValueOnce(err);

    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await expect(
        result.current.signup({ name: 'Dup', email: 'officer@claimguard.ai', password: 'pw123456' })
      ).rejects.toThrow('already exists');
    });

    expect(result.current.user).toBeNull();
  });
});

describe('AuthContext — logout', () => {
  it('clears user state and all session keys from localStorage', async () => {
    authService.login.mockResolvedValueOnce(mockLoginResponse);
    authService.logout.mockResolvedValueOnce({ ok: true });

    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.login('officer@claimguard.ai', 'demo1234');
    });
    expect(result.current.user).not.toBeNull();

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(window.localStorage.getItem('cg_access_token')).toBeNull();
    expect(window.localStorage.getItem('cg_refresh_token')).toBeNull();
    expect(window.localStorage.getItem('cg_user')).toBeNull();
  });

  it('still clears local session state even if the logout API call fails', async () => {
    authService.login.mockResolvedValueOnce(mockLoginResponse);
    authService.logout.mockRejectedValueOnce(new Error('network error'));

    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.login('officer@claimguard.ai', 'demo1234');
    });

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(window.localStorage.getItem('cg_user')).toBeNull();
  });
});

describe('AuthContext — hasRole (access control)', () => {
  it('returns false for any role when no user is logged in', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.hasRole(ROLES.ADMIN)).toBe(false);
  });

  it('returns true only when the logged-in user\'s role is in the allowed list', async () => {
    authService.login.mockResolvedValueOnce(mockLoginResponse); // role: Claims Officer
    const { result } = renderHook(() => useAuth(), { wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.login('officer@claimguard.ai', 'demo1234');
    });

    expect(result.current.hasRole(ROLES.OFFICER)).toBe(true);
    expect(result.current.hasRole(ROLES.ADMIN, ROLES.OFFICER)).toBe(true); // multi-role check
    expect(result.current.hasRole(ROLES.ADMIN)).toBe(false);
    expect(result.current.hasRole(ROLES.INVESTIGATOR, ROLES.ADMIN)).toBe(false);
  });
});
