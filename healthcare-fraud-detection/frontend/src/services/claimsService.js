import api, { USE_MOCK, mockDelay } from './api';
import { mockClaims } from './mockData';

export let claimsStore = [...mockClaims];

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

  // Helper to map procedure to display label
  const procedureLabels = {
    '99213': '99213 - Outpatient Visit (15-min)',
    '99214': '99214 - Outpatient Visit (25-min)',
    '36415': '36415 - Blood Draw',
    '71045': '71045 - Chest X-Ray',
    '93000': '93000 - Electrocardiogram (ECG)',
    '99283': '99283 - Emergency Dept Visit'
  };

  // Helper to map diagnosis to display label
  const diagnosisLabels = {
    'I10': 'I10 - Essential Hypertension',
    'E11': 'E11 - Type 2 Diabetes',
    'M25': 'M25 - Joint Pain',
    'J45': 'J45 - Asthma',
    'M54': 'M54 - Lower Back Pain',
    'I25': 'I25 - Ischemic Heart Disease'
  };

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
      diagnosis: diagnosisLabels[c.diagnosis_code] || c.diagnosis_code || (c.incident_description?.includes('diagnosis') ? c.incident_description.split(':')[1]?.trim() : 'Type 2 Diabetes'),
      procedure: procedureLabels[c.procedure_code] || c.procedure_code || 'MRI Scan',
      provider: c.provider_name || 'Sunrise General Hospital',
      specialty: c.procedure_code?.startsWith('7') ? 'Radiology' : 'General Practice',
    },
    financial: {
      claimAmount: c.claim_amount,
      approvedAmount: c.claim_status === 'approved' ? c.claim_amount : 0,
    },
    hospital: {
      visitType: c.visit_type || (c.length_of_stay > 0 ? 'Inpatient' : 'Outpatient'),
      lengthOfStay: c.length_of_stay || 0,
    },
    history: { previousVisits: 1 },
    dates: {
      serviceDate: c.incident_date || c.claim_date,
      claimDate: c.claim_date,
    },
    prediction: {
      label: prediction.predicted_label || 'Genuine',
      probability: prediction.fraud_probability || 0.0,
      rawProbability: prediction.raw_probability !== undefined ? prediction.raw_probability : prediction.fraud_probability,
      businessRuleAdjustment: prediction.business_rule_adjustment !== undefined ? prediction.business_rule_adjustment : 0.0,
      riskLevel: prediction.risk_level || 'Low',
      explanations: prediction.remarks ? prediction.remarks.split(',').map(s => s.trim()) : [],
      modelVersion: prediction.model_version || 'v1.0',
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
      (payload.claimAmount > 5000 ? 0.35 : 0.05) +
      (payload.lengthOfStay > 6 ? 0.25 : 0) +
      Math.random() * 0.2
    ));
    const riskLevel = probability > 0.7 ? 'High' : probability > 0.35 ? 'Medium' : 'Low';
    const label = probability > 0.55 ? 'Fraud' : 'Genuine';
    const explanations = [];
    if (payload.claimAmount > 5000) explanations.push('Claim amount significantly above provider average');
    if (payload.lengthOfStay > 6) explanations.push('Length of hospital stay exceeds diagnosis norm');

    const diagnosisLabels = {
      'I10': 'I10 - Essential Hypertension',
      'E11': 'E11 - Type 2 Diabetes',
      'M25': 'M25 - Joint Pain',
      'J45': 'J45 - Asthma',
      'M54': 'M54 - Lower Back Pain',
      'I25': 'I25 - Ischemic Heart Disease'
    };

    const procedureLabels = {
      '99213': '99213 - Outpatient Visit (15-min)',
      '99214': '99214 - Outpatient Visit (25-min)',
      '36415': '36415 - Blood Draw',
      '71045': '71045 - Chest X-Ray',
      '93000': '93000 - Electrocardiogram (ECG)',
      '99283': '99283 - Emergency Dept Visit'
    };

    const newClaim = {
      id: `CLM-${10000 + claimsStore.length}`,
      dbId: claimsStore.length + 1,
      patient: {
        name: 'Ava Thompson',
        age: payload.age || 45,
        gender: 'Female',
        state: 'TX',
      },
      insurance: {
        type: 'Private',
        policyNumber: 'POL-MOCK-1234',
      },
      medical: {
        diagnosis: diagnosisLabels[payload.diagnosis] || payload.diagnosis,
        procedure: procedureLabels[payload.procedure] || payload.procedure,
        provider: payload.provider || 'Sunrise General Hospital',
        specialty: payload.procedure?.startsWith('7') ? 'Radiology' : 'General Practice',
      },
      financial: {
        claimAmount: payload.claimAmount,
        approvedAmount: riskLevel === 'Low' ? payload.claimAmount : 0,
      },
      hospital: {
        visitType: payload.lengthOfStay > 0 ? 'Inpatient' : 'Outpatient',
        lengthOfStay: payload.lengthOfStay || 0,
      },
      history: { previousVisits: 1 },
      dates: {
        serviceDate: payload.serviceDate,
        claimDate: new Date().toISOString().split('T')[0],
      },
      prediction: { 
        label, 
        probability: Math.round(probability * 1000) / 1000, 
        rawProbability: Math.round(Math.max(0.01, probability * 0.7) * 1000) / 1000,
        businessRuleAdjustment: Math.round(Math.max(0.0, probability * 0.3) * 1000) / 1000,
        riskLevel, 
        explanations,
        modelVersion: 'TensorFlow-Keras-v1.0.0'
      },
      status: riskLevel === 'Low' ? 'Approved' : 'Pending Review',
      createdAt: new Date().toISOString().split('T')[0],
      notes: [],
      submittedBy: 'USR-004'
    };
    claimsStore = [newClaim, ...claimsStore];
    return mockDelay(newClaim, 900);
  }
  
  // Real API mapping
  const backendPayload = {
     age: payload.age,
     serviceDate: payload.serviceDate,
     diagnosis: payload.diagnosis,
     procedure: payload.procedure,
     claimAmount: payload.claimAmount,
     lengthOfStay: payload.lengthOfStay || 0,
     provider: payload.provider
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
