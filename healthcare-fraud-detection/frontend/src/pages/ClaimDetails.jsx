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
              <Typography variant="subtitle1" sx={{ mb: 2 }}>Financial Details</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={4}><Field label="Claim Amount" value={`$${claim.financial.claimAmount.toLocaleString()}`} /></Grid>
                <Grid item xs={6} sm={4}><Field label="Approved Amount" value={`$${claim.financial.approvedAmount.toLocaleString()}`} /></Grid>
                <Grid item xs={6} sm={4}><Field label="Claim Date" value={claim.dates.claimDate} /></Grid>
              </Grid>
            </Card>

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
              <Card sx={{ p: 3 }}>
                <Stack alignItems="center" spacing={1}>
                  <Typography variant="subtitle1">AI Prediction</Typography>
                  <RiskGauge probability={claim.prediction.probability} riskLevel={claim.prediction.riskLevel} />
                  <Chip
                    label={claim.prediction.label}
                    color={claim.prediction.label === 'Fraud' ? 'error' : 'success'}
                    variant="outlined"
                  />
                  <Divider sx={{ width: '100%', my: 1.5 }} />
                  <Box sx={{ width: '100%' }}>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>Explanation</Typography>
                    {claim.prediction.explanations.length === 0 ? (
                      <Typography variant="body2" sx={{ color: 'text.secondary' }}>No risk factors detected.</Typography>
                    ) : (
                      <Stack spacing={0.75}>
                        {claim.prediction.explanations.map((exp, i) => (
                          <Typography key={i} variant="body2" sx={{ color: 'text.secondary' }}>• {exp}</Typography>
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

              <ModelFeedbackCard claimId={claim.id} modelVersion={claim.prediction.modelVersion} />
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
