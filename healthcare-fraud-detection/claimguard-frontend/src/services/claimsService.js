import api, { USE_MOCK, mockDelay } from './api';
import { mockClaims } from './mockData';

// In-memory mutable copy so Approve/Reject/Notes persist for the session in mock mode
let claimsStore = [...mockClaims];

export async function getClaims(params = {}) {
  if (USE_MOCK) {
    let results = [...claimsStore];
    if (params.search) {
      const q = params.search.toLowerCase();
      results = results.filter((c) =>
        c.id.toLowerCase().includes(q) ||
        c.patient.name.toLowerCase().includes(q) ||
        c.medical.provider.toLowerCase().includes(q)
      );
    }
    if (params.risk) results = results.filter((c) => c.prediction.riskLevel === params.risk);
    if (params.status) results = results.filter((c) => c.status === params.status);
    if (params.riskOnly) results = results.filter((c) => ['High', 'Medium'].includes(c.prediction.riskLevel));
    if (params.ownerId) results = results.filter((c) => c.submittedBy === params.ownerId);
    results.sort((a, b) => b.dates.claimDate.localeCompare(a.dates.claimDate));
    return mockDelay(results, 400);
  }
  const { data } = await api.get('/claims', { params });
  return data;
}

export async function getClaim(id) {
  if (USE_MOCK) {
    const claim = claimsStore.find((c) => c.id === id);
    return mockDelay(claim || null, 300);
  }
  const { data } = await api.get(`/claims/${id}`);
  return data;
}

export async function submitClaim(payload) {
  if (USE_MOCK) {
    const probability = Math.min(0.99, Math.max(0.02,
      (payload.financial.claimAmount > 20000 ? 0.35 : 0.05) +
      (payload.hospital.lengthOfStay > 6 ? 0.25 : 0) +
      (payload.history.previousVisits > 3 ? 0.2 : 0) +
      Math.random() * 0.2
    ));
    const riskLevel = probability > 0.7 ? 'High' : probability > 0.35 ? 'Medium' : 'Low';
    const label = probability > 0.55 ? 'Fraud' : 'Genuine';
    const explanations = [];
    if (payload.financial.claimAmount > 20000) explanations.push('Claim amount significantly above provider average');
    if (payload.hospital.lengthOfStay > 6) explanations.push('Length of hospital stay exceeds diagnosis norm');
    if (payload.history.previousVisits > 3) explanations.push('Patient filed multiple claims in a short period');
    if (explanations.length === 0 && riskLevel !== 'Low') explanations.push('Provider flagged for elevated claim volume this quarter');

    const newClaim = {
      id: `CLM-${1000 + claimsStore.length}`,
      ...payload,
      prediction: { label, probability: Math.round(probability * 1000) / 1000, riskLevel, explanations },
      status: riskLevel === 'High' ? 'Pending Review' : 'Approved',
      createdAt: payload.dates.claimDate,
      notes: [],
    };
    claimsStore = [newClaim, ...claimsStore];
    return mockDelay(newClaim, 900);
  }
  const { data } = await api.post('/claims', payload);
  return data;
}

export async function updateClaim(id, patch) {
  if (USE_MOCK) {
    claimsStore = claimsStore.map((c) => (c.id === id ? { ...c, ...patch } : c));
    return mockDelay(claimsStore.find((c) => c.id === id), 400);
  }
  const { data } = await api.patch(`/claims/${id}`, patch);
  return data;
}

export async function addNote(id, note) {
  if (USE_MOCK) {
    claimsStore = claimsStore.map((c) =>
      c.id === id ? { ...c, notes: [...c.notes, { text: note, at: new Date().toISOString() }] } : c
    );
    return mockDelay(claimsStore.find((c) => c.id === id), 300);
  }
  const { data } = await api.patch(`/claims/${id}`, { note });
  return data;
}
