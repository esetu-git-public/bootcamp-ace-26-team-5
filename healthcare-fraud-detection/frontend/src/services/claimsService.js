import api, { USE_MOCK, mockDelay } from './api';
import { mockClaims } from './mockData';

let claimsStore = [...mockClaims];

function mapClaimFromBackend(c) {
  if (!c) return null;
  const policyholder = c.policy?.policyholder || {};
  const prediction = c.prediction || {};
  
  // Calculate age from birth date if available
  let age = 45;
  if (policyholder.date_of_birth) {
    const dob = new Date(policyholder.date_of_birth);
    age = new Date().getFullYear() - dob.getFullYear();
  }

  // Normalize status string from database
  let displayStatus = 'Pending Review';
  if (c.claim_status === 'approved') displayStatus = 'Approved';
  else if (c.claim_status === 'rejected') displayStatus = 'Rejected';
  else if (c.claim_status === 'under_review') displayStatus = 'Under Investigation';

  return {
    id: c.claim_number || `CLM-${c.claim_id}`,
    dbId: c.claim_id, // preserve database key
    patient: {
      name: policyholder.full_name || 'Ava Thompson',
      age: age,
      gender: policyholder.gender || 'Female',
      state: policyholder.state || 'TX',
    },
    insurance: {
      type: c.policy?.insurance_type || 'Private',
      policyNumber: c.policy?.policy_number || 'POL-MOCK-1234',
    },
    medical: {
      diagnosis: c.incident_description?.includes('diagnosis') ? c.incident_description.split(':')[1]?.trim() : 'Type 2 Diabetes',
      procedure: 'MRI Scan',
      provider: 'Sunrise General Hospital',
      specialty: 'Radiology',
    },
    financial: {
      claimAmount: c.claim_amount,
      approvedAmount: c.claim_status === 'approved' ? c.claim_amount : 0,
    },
    hospital: {
      visitType: 'Outpatient',
      lengthOfStay: 2,
    },
    history: { previousVisits: 1 },
    dates: {
      serviceDate: c.incident_date || c.claim_date,
      claimDate: c.claim_date,
    },
    prediction: {
      label: prediction.predicted_label || 'Genuine',
      probability: prediction.fraud_probability || 0.0,
      riskLevel: prediction.risk_level || 'Low',
      explanations: prediction.remarks ? prediction.remarks.split(',').map(s => s.trim()) : [],
    },
    status: displayStatus,
    createdAt: c.created_at,
    notes: [],
  };
}

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

  // Real API mapping
  // If ownerId is present, we pass it as submitted_by parameter
  const apiParams = {
     page: params.page || 1,
     per_page: params.per_page || 100,
     q: params.search || params.q || ''
  };
  if (params.status) {
     apiParams.status = params.status === 'Pending Review' ? 'submitted' :
                        params.status === 'Under Investigation' ? 'under_review' :
                        params.status.toLowerCase();
  }
  
  // Use standard GET /api/claims or GET /api/investigation depending on role
  let url = '/claims';
  if (params.riskOnly) {
     url = '/investigation';
  }
  
  const { data } = await api.get(url, { params: apiParams });
  // If investigation queue is fetched, the structure is a direct list, otherwise nested under claims key
  const rawList = Array.isArray(data.data) ? data.data : (data.data?.claims || []);
  return rawList.map(mapClaimFromBackend);
}

export async function getClaim(id) {
  if (USE_MOCK) {
    const claim = claimsStore.find((c) => c.id === id);
    return mockDelay(claim || null, 300);
  }
  
  // Lookup claim by claim number search query, then retrieve detail
  const { data } = await api.get('/claims', { params: { q: id } });
  const rawList = data.data?.claims || [];
  if (rawList.length > 0) {
     const claimSummary = rawList.find(c => c.claim_number === id) || rawList[0];
     const resDetail = await api.get(`/claims/${claimSummary.claim_id}`);
     return mapClaimFromBackend(resDetail.data.data);
  }
  return null;
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
  
  // Real API mapping
  const backendPayload = {
     patientName: payload.patient.name,
     claimAmount: payload.financial.claimAmount,
     gender: payload.patient.gender,
     age: payload.patient.age,
     diagnosis: payload.medical.diagnosis || 'I10',
     hospital: payload.medical.provider || 'General Hospital'
  };
  const { data } = await api.post('/claims', backendPayload);
  return mapClaimFromBackend(data.data);
}

export async function updateClaim(id, patch) {
  if (USE_MOCK) {
    claimsStore = claimsStore.map((c) => (c.id === id ? { ...c, ...patch } : c));
    return mockDelay(claimsStore.find((c) => c.id === id), 400);
  }
  
  const claim = await getClaim(id);
  if (claim) {
     // Map Display Status to DB status
     let dbStatus = patch.status || 'submitted';
     if (dbStatus === 'Pending Review') dbStatus = 'submitted';
     else if (dbStatus === 'Under Investigation') dbStatus = 'under_review';
     else dbStatus = dbStatus.toLowerCase();
     
     const { data } = await api.patch(`/claims/${claim.dbId}`, { status: dbStatus });
     return mapClaimFromBackend(data.data);
  }
  return null;
}

export async function addNote(id, note) {
  if (USE_MOCK) {
    claimsStore = claimsStore.map((c) =>
      c.id === id ? { ...c, notes: [...c.notes, { text: note, at: new Date().toISOString() }] } : c
    );
    return mockDelay(claimsStore.find((c) => c.id === id), 300);
  }
  
  const claim = await getClaim(id);
  if (claim) {
     const { data } = await api.patch(`/claims/${claim.dbId}`, { note });
     return mapClaimFromBackend(data.data);
  }
  return null;
}
