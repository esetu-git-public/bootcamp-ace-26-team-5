import { useState } from 'react';
import {
  Grid, Card, Typography, TextField, MenuItem, Button, Stack, Divider, Box, Chip, Alert,
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import HourglassEmptyOutlinedIcon from '@mui/icons-material/HourglassEmptyOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import * as claimsService from '../services/claimsService';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const diagnoses = [
  { code: 'I10', label: 'I10 - Essential Hypertension' },
  { code: 'E11', label: 'E11 - Type 2 Diabetes Mellitus' },
  { code: 'M25', label: 'M25 - Active Pain / Joint Pain' },
  { code: 'J45', label: 'J45 - Asthma / Chronic Bronchitis' },
  { code: 'M54', label: 'M54 - Dorsalgia / Lower Back Pain' },
  { code: 'I25', label: 'I25 - Chronic Ischemic Heart Disease' }
];

const procedures = [
  { code: '99213', label: '99213 - Outpatient Visit (15-min, Low Complexity)' },
  { code: '99214', label: '99214 - Outpatient Visit (25-min, Moderate Complexity)' },
  { code: '36415', label: '36415 - Venipuncture / Blood Draw' },
  { code: '71045', label: '71045 - Chest X-Ray (Single View)' },
  { code: '93000', label: '93000 - Electrocardiogram (ECG / EKG)' },
  { code: '99283', label: '99283 - Emergency Dept Visit (Moderate Severity)' }
];

const providers = [
  'Apollo Hospital',
  'Sunrise General Hospital',
  'MedCore Clinic',
  'Lakeview Health',
  'Metro Surgical Center',
  'Harborview Medical',
  'Care Hospital'
];

const initialForm = {
  age: '',
  serviceDate: new Date().toISOString().split('T')[0],
  provider: 'Apollo Hospital',
  diagnosis: 'I10',
  procedure: '99214',
  claimAmount: '',
  lengthOfStay: '0'
};

function SectionCard({ title, children }) {
  return (
    <Card sx={{ p: 3 }}>
      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>{title}</Typography>
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

  const setField = (key) => (e) => {
    const value = e.target.value;
    setForm((f) => ({ ...f, [key]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const payload = {
        age: Number(form.age),
        serviceDate: form.serviceDate,
        provider: form.provider.trim(),
        diagnosis: form.diagnosis,
        procedure: form.procedure,
        claimAmount: Number(form.claimAmount),
        lengthOfStay: Number(form.lengthOfStay || 0)
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
              <SectionCard title="Patient Details">
                <Grid item xs={12} sm={6}>
                  <TextField 
                    label="Patient Age" 
                    type="number" 
                    fullWidth 
                    required 
                    value={form.age} 
                    onChange={setField('age')} 
                    helperText="Age in years (e.g. 45)"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField 
                    label="Service / Treatment Date" 
                    type="date" 
                    fullWidth 
                    required 
                    InputLabelProps={{ shrink: true }} 
                    value={form.serviceDate} 
                    onChange={setField('serviceDate')} 
                  />
                </Grid>
              </SectionCard>

              <SectionCard title="Medical Information">
                <Grid item xs={12} sm={6}>
                  <TextField 
                    select 
                    label="Diagnosis Code (ICD-10)" 
                    fullWidth 
                    required 
                    value={form.diagnosis} 
                    onChange={setField('diagnosis')}
                  >
                    {diagnoses.map((d) => (
                      <MenuItem key={d.code} value={d.code}>{d.label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField 
                    select 
                    label="Procedure Code (CPT)" 
                    fullWidth 
                    required 
                    value={form.procedure} 
                    onChange={setField('procedure')}
                  >
                    {procedures.map((p) => (
                      <MenuItem key={p.code} value={p.code}>{p.label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField 
                    select
                    label="Healthcare Provider / Clinic" 
                    fullWidth 
                    required 
                    value={form.provider} 
                    onChange={setField('provider')} 
                  >
                    {providers.map((p) => (
                      <MenuItem key={p} value={p}>{p}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField 
                    label="Hospital Length of Stay (days)" 
                    type="number" 
                    fullWidth 
                    value={form.lengthOfStay} 
                    onChange={setField('lengthOfStay')} 
                    helperText="0 for outpatient treatment"
                  />
                </Grid>
              </SectionCard>

              <SectionCard title="Financials">
                <Grid item xs={12}>
                  <TextField 
                    label="Claim Amount ($)" 
                    type="number" 
                    fullWidth 
                    required 
                    value={form.claimAmount} 
                    onChange={setField('claimAmount')} 
                    placeholder="e.g. 250.00"
                  />
                </Grid>
              </SectionCard>

              {error && <Alert severity="error">{error}</Alert>}

              <Stack direction="row" spacing={1.5}>
                <Button type="submit" variant="contained" size="large" disabled={submitting}>
                  {submitting ? 'Analyzing and Routing…' : 'Submit Claim'}
                </Button>
                <Button variant="text" onClick={resetForm}>Reset</Button>
              </Stack>
            </Stack>
          </form>
        </Grid>

        {result && (
          <Grid item xs={12} md={5}>
            <Card sx={{ p: 4, position: 'sticky', top: 90, textAlign: 'center' }}>
              <Stack alignItems="center" spacing={2.5}>
                {result.status === 'Approved' ? (
                  <>
                    <CheckCircleOutlineIcon color="success" sx={{ fontSize: 72 }} />
                    <Typography variant="h6" sx={{ color: 'success.main', fontWeight: 600 }}>Claim Auto-Approved!</Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      Great news! Your claim **{result.id}** for **${result.financial.claimAmount.toLocaleString()}** has been successfully parsed, checked against our fraud engine, and **approved instantly**.
                    </Typography>
                  </>
                ) : (
                  <>
                    <HourglassEmptyOutlinedIcon color="warning" sx={{ fontSize: 72 }} />
                    <Typography variant="h6" sx={{ color: 'warning.main', fontWeight: 600 }}>Claim Pending Review</Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                      Your claim **{result.id}** for **${result.financial.claimAmount.toLocaleString()}** has been received and routed. It is currently **Under Review** by our claims team. You will receive an instant notification when it is processed.
                    </Typography>
                  </>
                )}
                
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
