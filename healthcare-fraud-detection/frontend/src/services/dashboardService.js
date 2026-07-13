import api, { USE_MOCK, mockDelay } from './api';
import { mockClaims, computeDashboard, mockProviderDistribution, mockInsuranceDistribution } from './mockData';

export async function getDashboard() {
  if (USE_MOCK) return mockDelay(computeDashboard(mockClaims), 500);
  const { data } = await api.get('/dashboard');
  return data;
}

export async function getReports() {
  if (USE_MOCK) {
    const base = computeDashboard(mockClaims);
    return mockDelay({
      ...base,
      providerDistribution: mockProviderDistribution,
      insuranceDistribution: mockInsuranceDistribution,
    }, 500);
  }
  const { data } = await api.get('/reports');
  return data;
}
