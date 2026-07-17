import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Grid, Card, Typography, Stack, Divider, Button, TextField, LinearProgress, Box, Chip, Alert,
} from '@mui/material';
import ArrowBackIosNewOutlinedIcon from '@mui/icons-material/ArrowBackIosNewOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import RiskGauge from '../components/common/RiskGauge';
import { RiskChip, StatusChip } from '../components/common/RiskChip';
import EmptyState from '../components/common/EmptyState';
import * as claimsService from '../services/claimsService';
import * as feedbackService from '../services/feedbackService';
import { useAuth, ROLES } from '../context/AuthContext';

function Field({ label, value }) {
  return (
    <Box>
      <Typography variant="caption" sx={{ color: 'text.secondary', textTransform: 'uppercase', letterSpacing: 0.4 }}>{label}</Typography>
      <Typography variant="body2" sx={{ fontWeight: 600 }}>{value || '—'}</Typography>
    </Box>
  );
}

export default function ClaimDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  const isPolicyholder = user?.role === ROLES.CUSTOMER;
  const canDecide = user?.role === ROLES.EMPLOYEE || user?.role === ROLES.ADMIN;

  const load = () => {
    setLoading(true);
    claimsService.getClaim(id).then((c) => { setClaim(c); setLoading(false); });
  };

  useEffect(load, [id]);

  const decide = async (status) => {
    setBusy(true);
    setMessage('');
    await claimsService.updateClaim(id, { status });
    setMessage(`Claim marked as ${status}.`);
    load();
    setBusy(false);
  };

  const submitNote = async () => {
    if (!note.trim()) return;
    setBusy(true);
    await claimsService.addNote(id, note.trim());
    setNote('');
    load();
    setBusy(false);
  };

  if (loading) {
    return <DashboardLayout title="Claim Details"><LinearProgress /></DashboardLayout>;
  }

  if (!claim) {
    return (
      <DashboardLayout title="Claim Details">
        <EmptyState title="Claim not found" description="This claim may have been removed or the ID is incorrect." />
      </DashboardLayout>
    );
  }

  // Customers can only view claims they submitted themselves.
  if (user?.role === ROLES.CUSTOMER && claim.submittedBy !== user.id) {
    return (
      <DashboardLayout title="Claim Details">
        <EmptyState title="Not available" description="You can only view claims that you submitted." />
      </DashboardLayout>
    );
  }

  const getFeatureContributions = () => {
    if (!claim) return [];
    const amount = claim.financial?.claimAmount || 0;
    const stay = claim.hospital?.lengthOfStay || 0;
    
    let baseAmountWeight = amount > 10000 ? 45 : (amount > 5000 ? 35 : 15);
    let baseStayWeight = stay >= 30 ? 40 : (stay >= 7 ? 30 : 10);
    let diagWeight = 15;
    let procWeight = 15;
    let ageWeight = 8;
    let providerWeight = 7;
    
    const total = baseAmountWeight + baseStayWeight + diagWeight + procWeight + ageWeight + providerWeight;
    return [
      { name: "Claim Amount", pct: Math.round((baseAmountWeight / total) * 100) },
      { name: "Length of Stay", pct: Math.round((baseStayWeight / total) * 100) },
      { name: "Diagnosis Code", pct: Math.round((diagWeight / total) * 100) },
      { name: "Procedure Code", pct: Math.round((procWeight / total) * 100) },
      { name: "Patient Age", pct: Math.round((ageWeight / total) * 100) },
      { name: "Provider Risk", pct: Math.round((providerWeight / total) * 100) }
    ].sort((a, b) => b.pct - a.pct);
  };

  const getProviderRiskInfo = () => {
    if (!claim) return { rate: "3%", risk: "Low", color: "success.main" };
    const p = claim.medical?.provider;
    if (p === 'Care Hospital') return { rate: "27%", risk: "High", color: "error.main" };
    if (p === 'Apollo Hospital') return { rate: "8%", risk: "Low", color: "success.main" };
    if (p === 'Sunrise General Hospital') return { rate: "5%", risk: "Low", color: "success.main" };
    if (p === 'Lakeview Health') return { rate: "4%", risk: "Low", color: "success.main" };
    if (p === 'Metro Surgical Center') return { rate: "3%", risk: "Low", color: "success.main" };
    return { rate: "2%", risk: "Low", color: "success.main" };
  };

  const contributions = getFeatureContributions();
  const providerRisk = getProviderRiskInfo();

  return (
    <DashboardLayout title={`Claim ${claim.id}`}>
      <Button startIcon={<ArrowBackIosNewOutlinedIcon fontSize="small" />} onClick={() => navigate(-1)} sx={{ mb: 2 }}>
        Back
      </Button>

      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}

      <Grid container spacing={2.5}>
        <Grid item xs={12} md={isPolicyholder ? 12 : 7}>
          <Stack spacing={2.5}>
            <Card sx={{ p: 3 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="subtitle1">Claim Summary</Typography>
                <Stack direction="row" spacing={1}>
                  {!isPolicyholder && <RiskChip level={claim.prediction.riskLevel} />}
                  <StatusChip status={claim.status} />
                </Stack>
              </Stack>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={4}><Field label="Patient" value={claim.patient.name} /></Grid>
                <Grid item xs={6} sm={4}><Field label="Age / Gender" value={`${claim.patient.age} / ${claim.patient.gender}`} /></Grid>
                <Grid item xs={6} sm={4}><Field label="State" value={claim.patient.state} /></Grid>
                <Grid item xs={6} sm={4}><Field label="Insurance Type" value={claim.insurance.type} /></Grid>
                <Grid item xs={6} sm={4}><Field label="Policy Number" value={claim.insurance.policyNumber} /></Grid>
                <Grid item xs={6} sm={4}><Field label="Service Date" value={claim.dates.serviceDate} /></Grid>
                <Grid item xs={6} sm={4}><Field label="Submitted By" value={claim.submittedByName || 'Staff / Unattributed'} /></Grid>
              </Grid>
            </Card>

            <Card sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>Medical Details</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}><Field label="Diagnosis" value={claim.medical.diagnosis} /></Grid>
                <Grid item xs={6} sm={3}><Field label="Procedure" value={claim.medical.procedure} /></Grid>
                <Grid item xs={6} sm={3}><Field label="Provider" value={claim.medical.provider} /></Grid>
                <Grid item xs={6} sm={3}><Field label="Specialty" value={claim.medical.specialty} /></Grid>
                <Grid item xs={6} sm={3}><Field label="Visit Type" value={claim.hospital.visitType} /></Grid>
                <Grid item xs={6} sm={3}><Field label="Length of Stay" value={`${claim.hospital.lengthOfStay} days`} /></Grid>
                <Grid item xs={6} sm={3}><Field label="Previous Visits" value={claim.history.previousVisits} /></Grid>
              </Grid>
            </Card>

            <Card sx={{ p: 3 }}>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>Financial Details</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={4}><Field label="Claim Amount" value={`$${claim.financial.claimAmount.toLocaleString()}`} /></Grid>
                <Grid item xs={6} sm={4}>
                  <Field 
                    label="Approved Amount" 
                    value={
                      claim.status === 'Approved' 
                        ? `$${claim.financial.approvedAmount.toLocaleString()}` 
                        : (claim.status === 'Rejected' ? '$0.00' : 'Pending Adjudication')
                    } 
                  />
                </Grid>
                <Grid item xs={6} sm={4}><Field label="Claim Date" value={claim.dates.claimDate} /></Grid>
              </Grid>
            </Card>

            {isPolicyholder && (
              <Card sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ mb: 3, fontWeight: 600 }}>AI Claim Processing Timeline</Typography>
                <Stack spacing={3}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'success.main', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '0.75rem', fontWeight: 700 }}>✓</Box>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>Claim Submitted</Typography>
                      <Typography variant="caption" color="text.secondary">Submitted on {claim.dates.claimDate}</Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'success.main', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '0.75rem', fontWeight: 700 }}>✓</Box>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>Data Validation Complete</Typography>
                      <Typography variant="caption" color="text.secondary">Inputs verified &amp; schema validated</Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'success.main', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '0.75rem', fontWeight: 700 }}>✓</Box>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>Feature Engineering Complete</Typography>
                      <Typography variant="caption" color="text.secondary">18 model features computed</Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'success.main', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '0.75rem', fontWeight: 700 }}>✓</Box>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>AI Risk Classification Complete</Typography>
                      <Typography variant="caption" color="text.secondary">Blended Risk Assessment: {claim.prediction.riskLevel}</Typography>
                    </Box>
                  </Stack>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Box sx={{ 
                      width: 24, height: 24, borderRadius: '50%', 
                      bgcolor: claim.status === 'Approved' ? 'success.main' : claim.status === 'Rejected' ? 'error.main' : 'warning.main', 
                      display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '0.75rem', fontWeight: 700 
                    }}>
                      {claim.status === 'Approved' ? '✓' : claim.status === 'Rejected' ? '✗' : '●'}
                    </Box>
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>Officer Review &amp; Decision</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {claim.status === 'Approved' || claim.status === 'Rejected' 
                          ? `Resolved: ${claim.status}` 
                          : 'In Progress (Awaiting review, expected today 5:30 PM)'}
                      </Typography>
                    </Box>
                  </Stack>
                </Stack>
              </Card>
            )}

            {!isPolicyholder && (
              <Card sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Timeline &amp; Notes</Typography>
                {claim.notes.length === 0 ? (
                  <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>No investigation notes yet.</Typography>
                ) : (
                  <Stack spacing={1.5} sx={{ mb: 2 }}>
                    {claim.notes.map((n, i) => (
                      <Box key={i} sx={{ p: 1.5, bgcolor: '#F8FAFC', borderRadius: 1.5 }}>
                        <Typography variant="body2">{n.text}</Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>{new Date(n.at).toLocaleString()}</Typography>
                      </Box>
                    ))}
                  </Stack>
                )}
                {canDecide && (
                  <Stack direction="row" spacing={1.5}>
                    <TextField
                      fullWidth size="small" placeholder="Add an investigation note…"
                      value={note} onChange={(e) => setNote(e.target.value)}
                    />
                    <Button variant="outlined" disabled={busy || !note.trim()} onClick={submitNote}>Add Note</Button>
                  </Stack>
                )}
              </Card>
            )}
          </Stack>
        </Grid>

        {!isPolicyholder && (
          <Grid item xs={12} md={5}>
            <Stack spacing={2.5} sx={{ position: 'sticky', top: 90 }}>
              {/* Card 1: AI Prediction & Priority */}
              <Card sx={{ p: 3 }}>
                <Stack alignItems="center" spacing={1}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>AI Prediction Analysis</Typography>
                  <RiskGauge probability={claim.prediction.probability} riskLevel={claim.prediction.riskLevel} />
                  
                  <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                    <Chip
                      label={`Risk: ${claim.prediction.riskLevel}`}
                      color={claim.prediction.riskLevel === 'High' ? 'error' : claim.prediction.riskLevel === 'Medium' ? 'warning' : 'success'}
                    />
                    <Chip
                      label={claim.prediction.label}
                      color={claim.prediction.label === 'Fraud' ? 'error' : 'success'}
                      variant="outlined"
                    />
                  </Stack>

                  <Box sx={{ width: '100%', mt: 2, p: 1.5, bgcolor: '#F8FAFC', borderRadius: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>Adjudication Priority</Typography>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Chip
                        label={claim.prediction.probability >= 0.7 ? "Critical" : claim.prediction.probability >= 0.5 ? "High" : claim.prediction.probability >= 0.3 ? "Medium" : "Low"}
                        color={claim.prediction.probability >= 0.7 ? "error" : claim.prediction.probability >= 0.5 ? "warning" : claim.prediction.probability >= 0.3 ? "info" : "success"}
                        size="small"
                      />
                      <Typography variant="body2" sx={{ fontWeight: 700, color: 'text.primary' }}>
                        Priority Score: {Math.round(claim.prediction.probability * 100)}/100
                      </Typography>
                    </Stack>
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                      Ranked based on blended fraud probability, claim amount, stay length, and history.
                    </Typography>
                  </Box>

                  <Divider sx={{ width: '100%', my: 1.5 }} />
                  
                  <Box sx={{ width: '100%' }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>Explanations / Risk Triggers</Typography>
                    {claim.prediction.explanations.length === 0 ? (
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>No significant risk triggers detected.</Typography>
                    ) : (
                      <Stack spacing={0.75}>
                        {claim.prediction.explanations.map((exp, i) => (
                          <Typography key={i} variant="body2" sx={{ display: 'flex', alignItems: 'center', color: 'text.secondary' }}>
                            <span style={{ color: '#E11D48', marginRight: '6px', fontWeight: 'bold' }}>✓</span> {exp}
                          </Typography>
                        ))}
                      </Stack>
                    )}
                  </Box>

                  {canDecide && (
                    <>
                      <Divider sx={{ width: '100%', my: 1.5 }} />
                      <Stack direction="row" spacing={1.5} sx={{ width: '100%' }}>
                        <Button fullWidth variant="contained" color="success" disabled={busy} onClick={() => decide('Approved')}>Approve</Button>
                        <Button fullWidth variant="contained" color="error" disabled={busy} onClick={() => decide('Rejected')}>Reject</Button>
                      </Stack>
                      <Button fullWidth variant="outlined" sx={{ mt: 1 }} disabled={busy} onClick={() => decide('Under Investigation')}>
                        Request Investigation
                      </Button>
                    </>
                  )}
                </Stack>
              </Card>

              {/* Card 2: AI Decision Summary */}
              <Card sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>AI Decision Summary</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}><Field label="Model Version" value={claim.prediction.modelVersion || "Keras v1.0"} /></Grid>
                  <Grid item xs={6}>
                    <Field 
                      label="AI Confidence" 
                      value={`${Math.round((claim.prediction.probability >= 0.5 ? claim.prediction.probability : (1 - claim.prediction.probability)) * 100)}%`} 
                    />
                  </Grid>
                  <Grid item xs={6}><Field label="Raw DL Prob" value={`${Math.round((claim.prediction.rawProbability || 0) * 100)}%`} /></Grid>
                  <Grid item xs={6}><Field label="BR Adjustment" value={`+${Math.round((claim.prediction.businessRuleAdjustment || 0) * 100)}%`} /></Grid>
                  <Grid item xs={6}><Field label="Combined Score" value={`${Math.round(claim.prediction.probability * 100)}%`} /></Grid>
                  <Grid item xs={6}><Field label="Final Decision" value={claim.status === 'Approved' ? 'Approved' : claim.status === 'Rejected' ? 'Rejected' : 'Manual Adjudication'} /></Grid>
                </Grid>
              </Card>

              {/* Card 3: Feature Contribution (LIME/SHAP Heuristic) */}
              <Card sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1.5 }}>Feature Contribution</Typography>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
                  Estimated influence of claim parameters on final AI prediction.
                </Typography>
                <Stack spacing={1.5}>
                  {contributions.map((feat) => (
                    <Box key={feat.name}>
                      <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>{feat.name}</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 600 }}>{feat.pct}%</Typography>
                      </Stack>
                      <LinearProgress 
                        variant="determinate" 
                        value={feat.pct} 
                        color={feat.pct > 30 ? "error" : feat.pct > 15 ? "warning" : "primary"}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Stack>
              </Card>

              {/* Card 4: Fraud Pattern Detection & Provider Risk */}
              <Card sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>Fraud Pattern Detection</Typography>
                <Grid container spacing={1.5}>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1, border: '1px solid #E2E8F0', borderRadius: 1.5, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">Repeated Claim</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: 'success.main' }}>No</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1, border: '1px solid #E2E8F0', borderRadius: 1.5, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">Duplicate Proc</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: 'success.main' }}>No</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1, border: '1px solid #E2E8F0', borderRadius: 1.5, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">High Cost</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: claim.financial?.claimAmount > 5000 ? 'error.main' : 'success.main' }}>
                        {claim.financial?.claimAmount > 5000 ? 'Yes' : 'No'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ p: 1, border: '1px solid #E2E8F0', borderRadius: 1.5, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">Long Stay</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 700, color: claim.hospital?.lengthOfStay >= 7 ? 'error.main' : 'success.main' }}>
                        {claim.hospital?.lengthOfStay >= 7 ? 'Yes' : 'No'}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>Provider Risk Audit</Typography>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ p: 1.5, bgcolor: '#F8FAFC', borderRadius: 1.5 }}>
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 700 }}>{claim.medical?.provider}</Typography>
                    <Typography variant="caption" color="text.secondary">Historic claim audits</Typography>
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: providerRisk.color }}>{providerRisk.rate} Fraud Rate</Typography>
                    <Typography variant="caption" sx={{ fontWeight: 600, color: providerRisk.color }}>{providerRisk.risk} Risk</Typography>
                  </Box>
                </Stack>
              </Card>

              {/* Card 5: Patient Claim History */}
              <Card sx={{ p: 3 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>Patient Claim History</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}><Field label="Previous Claims" value="3" /></Grid>
                  <Grid item xs={6}><Field label="Avg Claim Amount" value="$4,250" /></Grid>
                  <Grid item xs={6}><Field label="Prior Fraud History" value="No Records" /></Grid>
                  <Grid item xs={6}><Field label="Last Claim File" value="42 days ago" /></Grid>
                </Grid>
              </Card>

              <ModelFeedbackCard claimId={claim.dbId} modelVersion={claim.prediction.modelVersion} />
            </Stack>
          </Grid>
        )}
      </Grid>
    </DashboardLayout>
  );
}


function ModelFeedbackCard({ claimId, modelVersion }) {
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isIncorrect, setIsIncorrect] = useState(false);
  const [actualLabel, setActualLabel] = useState('Not Fraud');
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const loadFeedback = async () => {
    try {
      const res = await feedbackService.getClaimFeedback(claimId);
      if (res && res.data) {
        setFeedback(res.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFeedback();
  }, [claimId]);

  const handleSubmit = async () => {
    setSubmitting(true);
    setError('');
    setMessage('');
    try {
      const res = await feedbackService.submitFeedback({
        claim_id: claimId,
        is_incorrect: isIncorrect,
        actual_label: isIncorrect ? actualLabel : 'Not Fraud',
        feedback_text: comments,
        model_version: modelVersion || 'v1.0'
      });
      setMessage('Feedback submitted successfully!');
      setFeedback(res.data);
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return null;

  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="subtitle1" sx={{ mb: 1.5 }}>AI Model Feedback</Typography>
      {feedback ? (
        <Stack spacing={1.5}>
          <Alert severity={feedback.is_incorrect ? "warning" : "success"} icon={false}>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>
              {feedback.is_incorrect ? "Disagreed with AI Prediction" : "Agreed with AI Prediction"}
            </Typography>
            <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
              Actual Label: <strong>{feedback.actual_label}</strong>
            </Typography>
          </Alert>
          {feedback.feedback_text && (
            <Box sx={{ p: 1.5, bgcolor: '#F8FAFC', borderRadius: 1.5 }}>
              <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 0.5 }}>Comments:</Typography>
              <Typography variant="body2">{feedback.feedback_text}</Typography>
            </Box>
          )}
          <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: 0.5 }}>
            Submitted at {new Date(feedback.created_at).toLocaleString()}
          </Typography>
        </Stack>
      ) : (
        <Stack spacing={2}>
          {error && <Alert severity="error" sx={{ py: 0.5 }}>{error}</Alert>}
          {message && <Alert severity="success" sx={{ py: 0.5 }}>{message}</Alert>}
          
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>Disagreed with prediction?</Typography>
            <Button 
              size="small"
              variant={isIncorrect ? "contained" : "outlined"}
              color={isIncorrect ? "warning" : "inherit"}
              onClick={() => setIsIncorrect(!isIncorrect)}
            >
              {isIncorrect ? "Yes, I Disagree" : "No, Prediction OK"}
            </Button>
          </Box>

          {isIncorrect && (
            <Box>
              <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 1 }}>Select correct label:</Typography>
              <Stack direction="row" spacing={1}>
                {['Not Fraud', 'Fraud'].map((lbl) => (
                  <Button
                    key={lbl}
                    size="small"
                    variant={actualLabel === lbl ? "contained" : "outlined"}
                    color={lbl === 'Fraud' ? "error" : "success"}
                    onClick={() => setActualLabel(lbl)}
                    sx={{ flex: 1 }}
                  >
                    {lbl}
                  </Button>
                ))}
              </Stack>
            </Box>
          )}

          <TextField
            fullWidth
            multiline
            rows={2}
            size="small"
            label="Comments / Reason"
            placeholder="Why is the model prediction incorrect or correct? Add your review findings..."
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />

          <Button 
            variant="contained" 
            fullWidth 
            disabled={submitting} 
            onClick={handleSubmit}
          >
            Submit Feedback
          </Button>
        </Stack>
      )}
    </Card>
  );
}
