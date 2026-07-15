import api, { USE_MOCK, mockDelay } from './api';

// Simple mock database for local development/testing in mock mode
const mockFeedbackDb = [];

export async function submitFeedback(payload) {
  if (USE_MOCK) {
    const existing = mockFeedbackDb.find(f => f.claim_id === Number(payload.claim_id));
    if (existing) {
      throw new Error("Feedback has already been submitted for this claim.");
    }
    const newFb = {
      feedback_id: mockFeedbackDb.length + 1,
      claim_id: Number(payload.claim_id),
      user_id: 99,
      is_incorrect: payload.is_incorrect,
      actual_label: payload.actual_label,
      feedback_text: payload.feedback_text,
      model_version: payload.model_version || 'v1.0',
      created_at: new Date().toISOString()
    };
    mockFeedbackDb.push(newFb);
    return mockDelay({ data: newFb, message: "Feedback submitted successfully" }, 300);
  }

  const { data } = await api.post('/feedback', payload);
  return data;
}

export async function getClaimFeedback(claimId) {
  if (USE_MOCK) {
    const fb = mockFeedbackDb.find(f => f.claim_id === Number(claimId));
    return mockDelay({ data: fb || null }, 200);
  }

  const { data } = await api.get(`/feedback/claim/${claimId}`);
  return data;
}

export async function getFeedbackStats() {
  if (USE_MOCK) {
    const total = 100;
    const disagreements = mockFeedbackDb.filter(f => f.is_incorrect).length + 4;
    const fp = mockFeedbackDb.filter(f => f.is_incorrect && f.actual_label === 'Not Fraud').length + 3;
    const fn = mockFeedbackDb.filter(f => f.is_incorrect && f.actual_label === 'Fraud').length + 1;
    
    return mockDelay({
      data: {
        totalPredictions: total,
        disagreements: disagreements,
        disagreementRate: Math.round((disagreements / total) * 1000) / 10,
        accuracy: Math.round(((total - disagreements) / total) * 1000) / 10,
        falsePositives: fp,
        falseNegatives: fn,
        labelDistribution: [
          { name: 'Flagged Fraud (Missed by Model)', value: fn },
          { name: 'Flagged Genuine (False Alarm)', value: fp }
        ]
      }
    }, 300);
  }

  const { data } = await api.get('/feedback/stats');
  return data;
}

export async function getFeedbackList() {
  if (USE_MOCK) {
    return mockDelay({
      data: mockFeedbackDb.map(f => ({
        ...f,
        claim_number: `CLM-${f.claim_id}`,
        predicted_label: f.actual_label === 'Fraud' ? 'Not Fraud' : 'Fraud',
        risk_level: f.actual_label === 'Fraud' ? 'Low' : 'High',
        user_name: 'Mock Officer'
      }))
    }, 300);
  }

  const { data } = await api.get('/feedback');
  return data;
}
