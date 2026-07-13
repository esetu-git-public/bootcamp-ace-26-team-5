import { useState } from 'react';
import {
  Grid, Card, Typography, TextField, MenuItem, Button, Stack, Divider, Box, Chip, Alert,
} from '@mui/material';
import DashboardLayout from '../components/layout/DashboardLayout';
import RiskGauge from '../components/common/RiskGauge';
import { RiskChip } from '../components/common/RiskChip';
import * as claimsService from '../services/claimsService';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const genders = ['Male', 'Female', 'Other'];
const insuranceTypes = ['Private', 'Medicare', 'Medicaid', 'Employer Group'];
const visitTypes = ['Inpatient', 'Outpatient'];

const initialForm = {
  patient: { name: '', age: '', gender: '', state: '' },
  insurance: { type: '', policyNumber: '' },
  medical: { diagnosis: '', procedure: '', provider: '', specialty: '' },
  financial: { claimAmount: '', approvedAmount: '' },
  hospital: { visitType: '', lengthOfStay: '' },
  history: { previousVisits: '' },
  dates: { serviceDate: '', claimDate: '' },
};

function SectionCard({ title, children }) {
  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="subtitle1" sx={{ mb: 2 }}>{title}</Typography>
      <Grid container spacing={2}>{children}</Grid>
    </Card>
  );
}

export default function SubmitClaim() {
  const { user } = useAuth();
  const [form, setForm] = useState(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const setField = (section, key) => (e) => {
    const value = e.target.value;
    setForm((f) => ({ ...f, [section]: { ...f[section], [key]: value } }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        patient: { ...form.patient, age: Number(form.patient.age) },
        financial: {
          claimAmount: Number(form.financial.claimAmount),
          approvedAmount: form.financial.approvedAmount ? Number(form.financial.approvedAmount) : 0,
        },
        hospital: { ...form.hospital, lengthOfStay: Number(form.hospital.lengthOfStay || 0) },
        history: { previousVisits: Number(form.history.previousVisits || 0) },
        // Tag the claim with whoever submitted it, so it shows up in their
        // own claim history and is attributable in officer/investigator/admin views.
        submittedBy: user?.id || null,
        submittedByName: user?.name || null,
      };
      const claim = await claimsService.submitClaim(payload);
      setResult(claim);
    } catch (err) {
      setError(err.response?.data?.message || 'Unable to submit claim. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const resetForm = () => {
    setForm(initialForm);
    setResult(null);
  };

  return (
    <DashboardLayout title="Submit Claim">
      <Grid container spacing={2.5}>
        <Grid item xs={12} md={result ? 7 : 12}>
          <form onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              <SectionCard title="Patient Information">
                <Grid item xs={12} sm={6}><TextField label="Name" fullWidth required value={form.patient.name} onChange={setField('patient', 'name')} /></Grid>
                <Grid item xs={12} sm={3}><TextField label="Age" type="number" fullWidth required value={form.patient.age} onChange={setField('patient', 'age')} /></Grid>
                <Grid item xs={12} sm={3}><TextField select label="Gender" fullWidth required value={form.patient.gender} onChange={setField('patient', 'gender')}>
                  {genders.map((g) => <MenuItem key={g} value={g}>{g}</MenuItem>)}
                </TextField></Grid>
                <Grid item xs={12} sm={6}><TextField label="State" fullWidth required value={form.patient.state} onChange={setField('patient', 'state')} /></Grid>
              </SectionCard>

              <SectionCard title="Insurance">
                <Grid item xs={12} sm={6}><TextField select label="Insurance Type" fullWidth required value={form.insurance.type} onChange={setField('insurance', 'type')}>
                  {insuranceTypes.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
                </TextField></Grid>
                <Grid item xs={12} sm={6}><TextField label="Policy Number" fullWidth required value={form.insurance.policyNumber} onChange={setField('insurance', 'policyNumber')} /></Grid>
              </SectionCard>

              <SectionCard title="Medical">
                <Grid item xs={12} sm={6}><TextField label="Diagnosis" fullWidth required value={form.medical.diagnosis} onChange={setField('medical', 'diagnosis')} /></Grid>
                <Grid item xs={12} sm={6}><TextField label="Procedure" fullWidth required value={form.medical.procedure} onChange={setField('medical', 'procedure')} /></Grid>
                <Grid item xs={12} sm={6}><TextField label="Provider" fullWidth required value={form.medical.provider} onChange={setField('medical', 'provider')} /></Grid>
                <Grid item xs={12} sm={6}><TextField label="Specialty" fullWidth required value={form.medical.specialty} onChange={setField('medical', 'specialty')} /></Grid>
              </SectionCard>

              <SectionCard title="Financial">
                <Grid item xs={12} sm={6}><TextField label="Claim Amount ($)" type="number" fullWidth required value={form.financial.claimAmount} onChange={setField('financial', 'claimAmount')} /></Grid>
                <Grid item xs={12} sm={6}><TextField label="Approved Amount ($)" type="number" fullWidth value={form.financial.approvedAmount} onChange={setField('financial', 'approvedAmount')} /></Grid>
              </SectionCard>

              <SectionCard title="Hospital">
                <Grid item xs={12} sm={6}><TextField select label="Visit Type" fullWidth required value={form.hospital.visitType} onChange={setField('hospital', 'visitType')}>
                  {visitTypes.map((v) => <MenuItem key={v} value={v}>{v}</MenuItem>)}
                </TextField></Grid>
                <Grid item xs={12} sm={6}><TextField label="Length of Stay (days)" type="number" fullWidth value={form.hospital.lengthOfStay} onChange={setField('hospital', 'lengthOfStay')} /></Grid>
              </SectionCard>

              <SectionCard title="History &amp; Dates">
                <Grid item xs={12} sm={3}><TextField label="Previous Visits" type="number" fullWidth value={form.history.previousVisits} onChange={setField('history', 'previousVisits')} /></Grid>
                <Grid item xs={12} sm={4.5}><TextField label="Service Date" type="date" fullWidth required InputLabelProps={{ shrink: true }} value={form.dates.serviceDate} onChange={setField('dates', 'serviceDate')} /></Grid>
                <Grid item xs={12} sm={4.5}><TextField label="Claim Date" type="date" fullWidth required InputLabelProps={{ shrink: true }} value={form.dates.claimDate} onChange={setField('dates', 'claimDate')} /></Grid>
              </SectionCard>

              {error && <Alert severity="error">{error}</Alert>}

              <Stack direction="row" spacing={1.5}>
                <Button type="submit" variant="contained" size="large" disabled={submitting}>
                  {submitting ? 'Analyzing…' : 'Submit Claim'}
                </Button>
                <Button variant="text" onClick={resetForm}>Reset</Button>
              </Stack>
            </Stack>
          </form>
        </Grid>

        {result && (
          <Grid item xs={12} md={5}>
            <Card sx={{ p: 3, position: 'sticky', top: 90 }}>
              <Stack alignItems="center" spacing={1}>
                <Typography variant="subtitle1">AI Prediction Result</Typography>
                <Chip label={result.id} size="small" variant="outlined" />
                <RiskGauge probability={result.prediction.probability} riskLevel={result.prediction.riskLevel} />
                <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                  <RiskChip level={result.prediction.riskLevel} />
                  <Chip
                    size="small"
                    label={result.prediction.label}
                    color={result.prediction.label === 'Fraud' ? 'error' : 'success'}
                    variant="outlined"
                  />
                </Stack>
                <Divider sx={{ width: '100%', my: 1 }} />
                <Box sx={{ width: '100%' }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>Explanation</Typography>
                  {result.prediction.explanations.length === 0 ? (
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>No risk factors detected.</Typography>
                  ) : (
                    <Stack spacing={0.75}>
                      {result.prediction.explanations.map((exp, i) => (
                        <Typography key={i} variant="body2" sx={{ color: 'text.secondary' }}>• {exp}</Typography>
                      ))}
                    </Stack>
                  )}
                </Box>
                <Divider sx={{ width: '100%', my: 1 }} />
                <Stack direction="row" spacing={1.5} sx={{ width: '100%' }}>
                  <Button fullWidth variant="outlined" onClick={() => navigate(`/claims/${result.id}`)}>View Details</Button>
                  <Button fullWidth variant="contained" onClick={resetForm}>Submit Another</Button>
                </Stack>
              </Stack>
            </Card>
          </Grid>
        )}
      </Grid>
    </DashboardLayout>
  );
}
