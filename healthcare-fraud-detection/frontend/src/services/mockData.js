const providers = ['Sunrise General Hospital', 'MedCore Clinic', 'Lakeview Health', 'Metro Surgical Center', 'Harborview Medical'];
const diagnoses = ['Type 2 Diabetes', 'Fractured Femur', 'Acute Appendicitis', 'Hypertension', 'Coronary Artery Disease', 'Pneumonia'];
const procedures = ['Knee Replacement', 'Appendectomy', 'Cardiac Catheterization', 'MRI Scan', 'Physical Therapy', 'Blood Panel'];
const insuranceTypes = ['Private', 'Medicare', 'Medicaid', 'Employer Group'];
const states = ['California', 'Texas', 'New York', 'Florida', 'Illinois', 'Ohio'];
const specialties = ['Orthopedics', 'Cardiology', 'General Surgery', 'Internal Medicine', 'Radiology'];

const names = ['Ava Thompson', 'Liam Carter', 'Noah Patel', 'Emma Rodriguez', 'Olivia Chen', 'Ethan Brooks', 'Sophia Nguyen', 'Mason Reyes', 'Isabella Kim', 'James Whitfield', 'Mia Sullivan', 'Lucas Ferreira'];

function seededRandom(seed) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}
const rand = seededRandom(42);
const pick = (arr) => arr[Math.floor(rand() * arr.length)];

// Matches the seed policyholder demo account (patient@claimguard.ai) in authService.js,
// so that account has some claim history to show out of the box.
export const DEMO_POLICYHOLDER_ID = 'USR-004';
export const DEMO_POLICYHOLDER_NAME = 'Ava Thompson';

function buildClaim(i) {
  const probability = Math.round(rand() * 1000) / 1000;
  const risk = probability > 0.7 ? 'High' : probability > 0.35 ? 'Medium' : 'Low';
  const prediction = probability > 0.55 ? 'Fraud' : 'Genuine';
  const statusPool = risk === 'High'
    ? ['Pending Review', 'Under Investigation', 'Rejected', 'Approved']
    : ['Approved', 'Approved', 'Pending Review'];
  const amount = Math.round((500 + rand() * 48000) * 100) / 100;
  const day = 1 + Math.floor(rand() * 27);
  const month = 1 + Math.floor(rand() * 7); // Jan - Jul 2026
  const date = `2026-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;

  const explanationsPool = [
    'Claim amount significantly above provider average',
    'Length of hospital stay exceeds diagnosis norm',
    'Patient filed 4+ claims in the last 90 days',
    'Provider flagged for high claim volume this quarter',
    'Mismatch between diagnosis and billed procedure',
    'Claim submitted outside normal business hours',
    'Policy inactive at time of service date',
  ];
  const explanations = risk === 'Low' ? [] : [explanationsPool[0], explanationsPool[1], explanationsPool[Math.floor(rand() * explanationsPool.length)]]
    .filter((v, idx, arr) => arr.indexOf(v) === idx);

  return {
    id: `CLM-${String(1000 + i)}`,
    patient: {
      name: pick(names),
      age: 20 + Math.floor(rand() * 55),
      gender: rand() > 0.5 ? 'Female' : 'Male',
      state: pick(states),
    },
    insurance: {
      type: pick(insuranceTypes),
      policyNumber: `POL-${100000 + Math.floor(rand() * 899999)}`,
    },
    medical: {
      diagnosis: pick(diagnoses),
      procedure: pick(procedures),
      provider: pick(providers),
      specialty: pick(specialties),
    },
    financial: {
      claimAmount: amount,
      approvedAmount: prediction === 'Fraud' ? 0 : Math.round(amount * (0.7 + rand() * 0.3) * 100) / 100,
    },
    hospital: {
      visitType: rand() > 0.5 ? 'Inpatient' : 'Outpatient',
      lengthOfStay: rand() > 0.5 ? Math.ceil(rand() * 10) : 0,
    },
    history: { previousVisits: Math.floor(rand() * 6) },
    dates: { serviceDate: date, claimDate: date },
    prediction: {
      label: prediction,
      probability,
      riskLevel: risk,
      explanations,
    },
    status: pick(statusPool),
    createdAt: date,
    notes: [],
    // Legacy seed claims aren't tied to a policyholder account by default
    // (staff submitted them). A handful matching the demo policyholder's
    // name are re-attributed below so that account has claim history.
    submittedBy: null,
    submittedByName: null,
  };
}

export const mockClaims = Array.from({ length: 42 }, (_, i) => buildClaim(i)).map((c) =>
  c.patient.name === DEMO_POLICYHOLDER_NAME
    ? { ...c, submittedBy: DEMO_POLICYHOLDER_ID, submittedByName: DEMO_POLICYHOLDER_NAME }
    : c
);

export function computeDashboard(claims) {
  const total = claims.length;
  const fraud = claims.filter((c) => c.prediction.label === 'Fraud').length;
  const genuine = total - fraud;
  const pending = claims.filter((c) => c.status === 'Pending Review').length;
  const highRisk = claims.filter((c) => c.prediction.riskLevel === 'High').length;
  const fraudPct = total ? Math.round((fraud / total) * 1000) / 10 : 0;

  const monthlyMap = {};
  claims.forEach((c) => {
    const m = c.dates.claimDate.slice(0, 7);
    monthlyMap[m] = monthlyMap[m] || { month: m, claims: 0, fraud: 0 };
    monthlyMap[m].claims += 1;
    if (c.prediction.label === 'Fraud') monthlyMap[m].fraud += 1;
  });
  const monthlyClaims = Object.values(monthlyMap).sort((a, b) => a.month.localeCompare(b.month));

  const riskDistribution = ['Low', 'Medium', 'High'].map((level) => ({
    level,
    count: claims.filter((c) => c.prediction.riskLevel === level).length,
  }));

  const statusDistribution = ['Approved', 'Pending Review', 'Under Investigation', 'Rejected'].map((status) => ({
    status,
    count: claims.filter((c) => c.status === status).length,
  }));

  return {
    kpis: { total, fraud, genuine, pending, highRisk, fraudPct },
    monthlyClaims,
    riskDistribution,
    statusDistribution,
    recentClaims: [...claims].sort((a, b) => b.dates.claimDate.localeCompare(a.dates.claimDate)).slice(0, 8),
  };
}

export const mockNotifications = mockClaims
  .filter((c) => c.prediction.riskLevel === 'High')
  .slice(0, 10)
  .map((c, i) => ({
    id: `NTF-${i + 1}`,
    claimId: c.id,
    title: 'High Risk Claim Detected',
    probability: c.prediction.probability,
    patient: c.patient.name,
    claimAmount: c.financial.claimAmount,
    time: c.createdAt,
    read: i > 4,
  }));

export const mockProviderDistribution = providers.map((p) => ({
  provider: p,
  claims: mockClaims.filter((c) => c.medical.provider === p).length,
}));

export const mockInsuranceDistribution = insuranceTypes.map((t) => ({
  type: t,
  claims: mockClaims.filter((c) => c.insurance.type === t).length,
}));
