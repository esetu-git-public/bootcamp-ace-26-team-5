import api, { USE_MOCK, mockDelay } from './api';

const demoUsers = {
  'officer@claimguard.ai': { password: 'demo1234', role: 'Claims Officer', name: 'Priya Sharma', id: 'USR-001' },
  'investigator@claimguard.ai': { password: 'demo1234', role: 'Fraud Investigator', name: 'Rahul Verma', id: 'USR-002' },
  'admin@claimguard.ai': { password: 'demo1234', role: 'Admin', name: 'Anjali Rao', id: 'USR-003' },
  'patient@claimguard.ai': { password: 'demo1234', role: 'Policyholder', name: 'Ava Thompson', id: 'USR-004' },
};

let nextSignupId = 5;

function mapUserFromBackend(u) {
  if (!u) return null;
  return {
    id: u.user_id,
    name: u.full_name,
    email: u.email,
    role: u.role,
  };
}

export async function login(email, password) {
  if (USE_MOCK) {
    const user = demoUsers[email];
    if (!user || user.password !== password) {
      const err = new Error('Invalid email or password');
      err.isAuthError = true;
      throw err;
    }
    return mockDelay({
      accessToken: `mock-access-${user.id}`,
      refreshToken: `mock-refresh-${user.id}`,
      user: { id: user.id, name: user.name, email, role: user.role },
    }, 600);
  }
  
  // Real API login
  const { data } = await api.post('/auth/login', { email, password });
  const payload = data.data;
  return {
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
    user: mapUserFromBackend(payload.user),
  };
}

export async function signup({ name, email, password }) {
  if (USE_MOCK) {
    const normalizedEmail = (email || '').trim().toLowerCase();
    if (!normalizedEmail || !password || !name) {
      const err = new Error('Name, email, and password are required.');
      err.isAuthError = true;
      throw err;
    }
    if (demoUsers[normalizedEmail]) {
      const err = new Error('An account with this email already exists.');
      err.isAuthError = true;
      throw err;
    }
    const id = `USR-${String(nextSignupId++).padStart(3, '0')}`;
    demoUsers[normalizedEmail] = { password, role: 'Policyholder', name, id };
    return mockDelay({
      accessToken: `mock-access-${id}`,
      refreshToken: `mock-refresh-${id}`,
      user: { id, name, email: normalizedEmail, role: 'Policyholder' },
    }, 600);
  }
  
  // Real API signup
  const { data } = await api.post('/auth/signup', { name, email, password });
  const payload = data.data;
  return {
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
    user: mapUserFromBackend(payload.user),
  };
}

export async function logout() {
  if (USE_MOCK) return mockDelay({ ok: true }, 150);
  return api.post('/auth/logout');
}

export async function fetchMe() {
  if (USE_MOCK) {
    const raw = sessionStorage.getItem('cg_user');
    return mockDelay(raw ? JSON.parse(raw) : null, 200);
  }
  const { data } = await api.get('/auth/me');
  return mapUserFromBackend(data.data);
}
