import api, { USE_MOCK, mockDelay } from './api';
import { computeDashboard, mockProviderDistribution, mockInsuranceDistribution } from './mockData';
import { claimsStore } from './claimsService';

function mapDashboardFromBackend(d) {
  if (!d) return null;
  const rawKpis = d.kpis || {};
  const risk = d.risk_distribution || { Low: 0, Medium: 0, High: 0 };
  
  const total = rawKpis.total_claims || 0;
  const fraud = rawKpis.fraud_claims || 0;
  const genuine = rawKpis.approved_claims || 0;
  const pending = rawKpis.pending_claims || 0;
  
  const totalUsers = rawKpis.total_users || 0;
  const totalPolicies = rawKpis.total_policies || 0;
  const recentLogs = d.recent_logs || [];
  
  const fraudPct = total > 0 ? Math.round((fraud / total) * 1000) / 10 : 0.0;

  const monthlyClaims = (d.monthly_trend || []).map(t => ({
    month: t.month,
    claims: t.claims,
    fraud: t.fraud
  }));

  const riskDistribution = [
    { level: 'Low', count: risk.Low || 0 },
    { level: 'Medium', count: risk.Medium || 0 },
    { level: 'High', count: risk.High || 0 }
  ];

  const statusDistribution = [
    { status: 'Approved', count: genuine },
    { status: 'Rejected', count: rawKpis.rejected_claims || 0 },
    { status: 'Pending Review', count: pending }
  ];

  const providerDistribution = (d.provider_distribution || []).map(p => ({
    provider: p.provider,
    claims: p.claims
  }));

  const insuranceDistribution = (d.insurance_distribution || []).map(i => ({
    type: i.type,
    claims: i.claims
  }));

  return {
    kpis: {
      total,
      fraud,
      genuine,
      pending,
      totalUsers,
      totalPolicies,
      highRisk: risk.High || rawKpis.high_risk_claims || 0,
      mediumRisk: rawKpis.medium_risk_claims || 0,
      reviewedClaims: rawKpis.reviewed_claims || 0,
      fraudPct,
      averageAmount: rawKpis.average_claim_amount || 0.0
    },
    monthlyClaims,
    riskDistribution,
    statusDistribution,
    recentClaims: [],
    recentLogs,
    providerDistribution,
    insuranceDistribution
  };
}

export async function getDashboard(role) {
  if (USE_MOCK) return mockDelay(computeDashboard(claimsStore), 500);
  
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
    const base = computeDashboard(claimsStore);
    return mockDelay({
      ...base,
      providerDistribution: mockProviderDistribution,
      insuranceDistribution: mockInsuranceDistribution,
    }, 500);
  }
  const { data } = await api.get('/reports');
  return mapDashboardFromBackend(data.data);
}
