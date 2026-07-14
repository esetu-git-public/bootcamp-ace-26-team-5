import { useState } from 'react';
import { Box, Paper, TextField, Button, Typography, Stack, Alert, InputAdornment, IconButton, Divider } from '@mui/material';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { USE_MOCK } from '../services/api';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      const dest = location.state?.from?.pathname || '/dashboard';
      navigate(dest, { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Unable to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (demoEmail) => {
    setEmail(demoEmail);
    setPassword('demo1234');
  };

  return (
    <Box sx={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      bgcolor: 'background.default', p: 2,
    }}>
      <Paper sx={{ width: '100%', maxWidth: 420, p: 4 }}>
        <Stack alignItems="center" spacing={1} sx={{ mb: 3 }}>
          <Box sx={{ width: 46, height: 46, borderRadius: 2, bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ShieldOutlinedIcon sx={{ color: '#fff' }} />
          </Box>
          <Typography variant="h5">ClaimGuard</Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            AI-Powered Healthcare Claim Fraud Detection
          </Typography>
        </Stack>

        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Email" type="email" value={email} required fullWidth
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
            <TextField
              label="Password" type={showPassword ? 'text' : 'password'} value={password} required fullWidth
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword((s) => !s)} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? 'Signing in…' : 'Log In'}
            </Button>
          </Stack>
        </form>

        <Typography variant="body2" sx={{ textAlign: 'center', mt: 2.5, color: 'text.secondary' }}>
          New here?{' '}
          <Typography component={RouterLink} to="/signup" variant="body2" sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none' }}>
            Create a policyholder account
          </Typography>
        </Typography>

        {USE_MOCK && (
          <Box sx={{ mt: 3 }}>
            <Divider sx={{ mb: 1.5 }}>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>demo accounts</Typography>
            </Divider>
            <Stack spacing={0.75}>
              {[
                ['patient@claimguard.ai', 'Policyholder'],
                ['officer@claimguard.ai', 'Claims Officer'],
                ['investigator@claimguard.ai', 'Fraud Investigator'],
                ['admin@claimguard.ai', 'Admin'],
              ].map(([demoEmail, role]) => (
                <Button key={demoEmail} size="small" variant="outlined" onClick={() => fillDemo(demoEmail)} sx={{ justifyContent: 'space-between' }}>
                  <span>{role}</span>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>{demoEmail}</Typography>
                </Button>
              ))}
            </Stack>
            <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary', textAlign: 'center' }}>
              password: demo1234
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
}
