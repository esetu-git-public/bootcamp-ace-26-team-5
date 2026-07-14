import api, { USE_MOCK, mockDelay } from './api';
import { mockClaims, computeDashboard, mockProviderDistribution, mockInsuranceDistribution } from './mockData';

function mapDashboardFromBackend(d) {
  if (!d) return null;
  const rawKpis = d.kpis || {};
  const risk = d.risk_distribution || { Low: 0, Medium: 0, High: 0 };
  
  const total = rawKpis.total_claims || 0;
  const fraud = rawKpis.fraud_claims || 0;
  const genuine = rawKpis.approved_claims || 0;
  const pending = rawKpis.pending_claims || 0;
  
  const fraudPct = total > 0 ? Math.round((fraud / total) * 1000) / 10 : 0.0;

  const monthlyClaims = (d.monthly_trend || []).map(t => ({
    name: t.month,
    total: t.claims,
    fraud: t.fraud
  }));

  const riskDistribution = [
    { name: 'Low', value: risk.Low || 0 },
    { name: 'Medium', value: risk.Medium || 0 },
    { name: 'High', value: risk.High || 0 }
  ];

  const statusDistribution = [
    { name: 'Approved', value: genuine },
    { name: 'Rejected', value: rawKpis.rejected_claims || 0 },
    { name: 'Pending Review', value: pending }
  ];

  return {
    kpis: {
      total,
      fraud,
      genuine,
      pending,
      highRisk: risk.High || 0,
      fraudPct,
      averageAmount: rawKpis.average_claim_amount || 0.0
    },
    monthlyClaims,
    riskDistribution,
    statusDistribution,
    recentClaims: [],
    providerDistribution: [],
    insuranceDistribution: []
  };
}

export async function getDashboard(role) {
  if (USE_MOCK) return mockDelay(computeDashboard(mockClaims), 500);
  
  // Choose endpoint explicitly based on role
  let endpoint = '/dashboard';
  if (role) {
     const cleanRole = role.toLowerCase();
     if (cleanRole === 'admin') endpoint = '/dashboard/admin';
     else if (cleanRole === 'claims officer') endpoint = '/dashboard/officer';
     else if (cleanRole === 'policyholder') endpoint = '/dashboard/customer';
  }
  
  const { data } = await api.get(endpoint);
  return mapDashboardFromBackend(data.data);
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
  return mapDashboardFromBackend(data.data);
}
