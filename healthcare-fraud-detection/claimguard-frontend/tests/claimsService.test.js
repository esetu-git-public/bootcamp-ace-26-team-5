import { describe, it, expect, vi, beforeEach } from 'vitest';

// mockDelay normally waits 300-900ms to simulate network latency.
// We keep USE_MOCK's real value (true) but make the delay instant for fast tests.
vi.mock('./api', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    mockDelay: (data) => Promise.resolve(data),
  };
});

// Reset the module registry before each test so the in-memory `claimsStore`
// (a module-level `let` in claimsService.js) starts fresh from mockData
// instead of leaking claims submitted by a previous test.
beforeEach(() => {
  vi.resetModules();
});

async function loadService() {
  return import('./claimsService.js');
}

describe('claimsService.getClaims', () => {
  it('returns the full claim list when no filters are supplied', async () => {
    const { getClaims } = await loadService();
    const results = await getClaims();
    expect(Array.isArray(results)).toBe(true);
    expect(results.length).toBeGreaterThan(0);
  });

  it('sorts results by claim date, most recent first', async () => {
    const { getClaims } = await loadService();
    const results = await getClaims();
    for (let i = 1; i < results.length; i++) {
      const prev = results[i - 1].dates.claimDate;
      const curr = results[i].dates.claimDate;
      expect(prev >= curr).toBe(true);
    }
  });

  it('filters by search term across id, patient name, and provider', async () => {
    const { getClaims } = await loadService();
    const all = await getClaims();
    const sample = all[0];

    const byId = await getClaims({ search: sample.id });
    expect(byId.some((c) => c.id === sample.id)).toBe(true);

    const byPatient = await getClaims({ search: sample.patient.name.split(' ')[0] });
    expect(byPatient.length).toBeGreaterThan(0);
    expect(byPatient.every((c) => c.patient.name.toLowerCase().includes(sample.patient.name.split(' ')[0].toLowerCase()))).toBe(true);
  });

  it('search is case-insensitive', async () => {
    const { getClaims } = await loadService();
    const all = await getClaims();
    const sample = all[0];
    const results = await getClaims({ search: sample.id.toLowerCase() });
    expect(results.some((c) => c.id === sample.id)).toBe(true);
  });

  it('filters by exact risk level', async () => {
    const { getClaims } = await loadService();
    const results = await getClaims({ risk: 'High' });
    expect(results.every((c) => c.prediction.riskLevel === 'High')).toBe(true);
  });

  it('filters by exact status', async () => {
    const { getClaims } = await loadService();
    const results = await getClaims({ status: 'Approved' });
    expect(results.every((c) => c.status === 'Approved')).toBe(true);
  });

  it('riskOnly returns only High and Medium risk claims, excluding Low', async () => {
    const { getClaims } = await loadService();
    const results = await getClaims({ riskOnly: true });
    expect(results.length).toBeGreaterThan(0);
    expect(results.every((c) => ['High', 'Medium'].includes(c.prediction.riskLevel))).toBe(true);
    expect(results.some((c) => c.prediction.riskLevel === 'Low')).toBe(false);
  });

  it('ownerId scopes results to only that policyholder\'s claims (patient data isolation)', async () => {
    const { getClaims } = await loadService();
    const all = await getClaims();
    const anOwner = all.find((c) => c.submittedBy)?.submittedBy;
    if (!anOwner) return; // seed data shape guard
    const results = await getClaims({ ownerId: anOwner });
    expect(results.length).toBeGreaterThan(0);
    expect(results.every((c) => c.submittedBy === anOwner)).toBe(true);
  });

  it('combines multiple filters with AND semantics', async () => {
    const { getClaims } = await loadService();
    const results = await getClaims({ risk: 'High', status: 'Pending Review' });
    expect(results.every((c) => c.prediction.riskLevel === 'High' && c.status === 'Pending Review')).toBe(true);
  });
});

describe('claimsService.getClaim', () => {
  it('returns the matching claim by id', async () => {
    const { getClaims, getClaim } = await loadService();
    const all = await getClaims();
    const target = all[0];
    const result = await getClaim(target.id);
    expect(result).not.toBeNull();
    expect(result.id).toBe(target.id);
  });

  it('returns null for an id that does not exist', async () => {
    const { getClaim } = await loadService();
    const result = await getClaim('CLM-DOES-NOT-EXIST');
    expect(result).toBeNull();
  });
});

describe('claimsService.submitClaim — fraud risk scoring', () => {
  const basePayload = {
    patient: { name: 'Test Patient', age: 40, gender: 'Female', state: 'California' },
    insurance: { type: 'Private', policyNumber: 'POL-000000' },
    financial: { claimAmount: 1000 },
    hospital: { lengthOfStay: 1 },
    history: { previousVisits: 0 },
    medical: { provider: 'Test Clinic' },
    dates: { claimDate: '2026-07-13' },
  };

  it('flags a claim with all fraud indicators as High risk and Pending Review, regardless of random jitter', async () => {
    const { submitClaim } = await loadService();
    const payload = {
      ...basePayload,
      financial: { claimAmount: 50000 },   // > 20000 -> +0.35
      hospital: { lengthOfStay: 10 },      // > 6     -> +0.25
      history: { previousVisits: 5 },      // > 3     -> +0.20
      // base = 0.80, plus 0-0.20 random jitter => always > 0.7
    };
    const result = await submitClaim(payload);
    expect(result.prediction.riskLevel).toBe('High');
    expect(result.status).toBe('Pending Review');
    expect(result.prediction.probability).toBeGreaterThan(0.7);
  });

  it('leaves a claim with no fraud indicators as Low risk and auto-Approved, regardless of random jitter', async () => {
    const { submitClaim } = await loadService();
    const payload = {
      ...basePayload,
      financial: { claimAmount: 500 },     // <= 20000 -> +0.05 base only
      hospital: { lengthOfStay: 2 },       // <= 6
      history: { previousVisits: 1 },      // <= 3
      // base = 0.05, plus 0-0.20 random jitter => max 0.25, always < 0.35
    };
    const result = await submitClaim(payload);
    expect(result.prediction.riskLevel).toBe('Low');
    expect(result.status).toBe('Approved');
    expect(result.prediction.probability).toBeLessThan(0.35);
  });

  it('generates a matching explanation for each triggered fraud indicator', async () => {
    const { submitClaim } = await loadService();
    const payload = {
      ...basePayload,
      financial: { claimAmount: 25000 },
      hospital: { lengthOfStay: 8 },
      history: { previousVisits: 4 },
    };
    const result = await submitClaim(payload);
    expect(result.prediction.explanations).toContain('Claim amount significantly above provider average');
    expect(result.prediction.explanations).toContain('Length of hospital stay exceeds diagnosis norm');
    expect(result.prediction.explanations).toContain('Patient filed multiple claims in a short period');
  });

  it('assigns a unique CLM- prefixed id and adds the new claim to the store', async () => {
    const { submitClaim, getClaims } = await loadService();
    const before = await getClaims();
    const result = await submitClaim(basePayload);
    expect(result.id).toMatch(/^CLM-\d+$/);
    // Note: getClaims() sorts by claimDate, so the newest submission is not
    // necessarily first in the returned list — only that it now exists in it.
    const after = await getClaims();
    expect(after.length).toBe(before.length + 1);
    expect(after.some((c) => c.id === result.id)).toBe(true);
  });

  it('initializes a new claim with an empty notes array', async () => {
    const { submitClaim } = await loadService();
    const result = await submitClaim(basePayload);
    expect(result.notes).toEqual([]);
  });
});

describe('claimsService.updateClaim', () => {
  it('patches only the specified fields on the matching claim', async () => {
    const { getClaims, updateClaim } = await loadService();
    const all = await getClaims();
    const target = all[0];
    const updated = await updateClaim(target.id, { status: 'Under Investigation' });
    expect(updated.status).toBe('Under Investigation');
    expect(updated.id).toBe(target.id);
  });

  it('does not affect other claims', async () => {
    const { getClaims, updateClaim } = await loadService();
    const all = await getClaims();
    const [first, second] = all;
    await updateClaim(first.id, { status: 'Rejected' });
    const untouched = (await getClaims()).find((c) => c.id === second.id);
    expect(untouched.status).toBe(second.status);
  });
});

describe('claimsService.addNote', () => {
  it('appends a timestamped note to the claim', async () => {
    const { getClaims, addNote } = await loadService();
    const all = await getClaims();
    const target = all[0];
    const updated = await addNote(target.id, 'Reviewed supporting documents.');
    const lastNote = updated.notes[updated.notes.length - 1];
    expect(lastNote.text).toBe('Reviewed supporting documents.');
    expect(lastNote.at).toBeTruthy();
  });

  it('preserves existing notes when adding a new one', async () => {
    const { getClaims, addNote } = await loadService();
    const all = await getClaims();
    const target = all[0];
    const afterFirst = await addNote(target.id, 'First note.');
    const afterSecond = await addNote(target.id, 'Second note.');
    expect(afterSecond.notes.length).toBe(afterFirst.notes.length + 1);
  });
});
