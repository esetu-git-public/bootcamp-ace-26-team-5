import { useState } from 'react';
import { Box, Paper, TextField, Button, Typography, Stack, Alert, InputAdornment, IconButton } from '@mui/material';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    setLoading(true);
    try {
      await signup({ name, email, password });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Unable to create account. Please try again.');
    } finally {
      setLoading(false);
    }
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
          <Typography variant="h5">Create Account</Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center' }}>
            Sign up as a policyholder to submit and track your own claims.
          </Typography>
        </Stack>

        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            {error && <Alert severity="error">{error}</Alert>}
            <TextField
              label="Full Name" value={name} required fullWidth
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
            />
            <TextField
              label="Email" type="email" value={email} required fullWidth
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
            <TextField
              label="Password" type={showPassword ? 'text' : 'password'} value={password} required fullWidth
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              helperText="At least 6 characters"
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
            <TextField
              label="Confirm Password" type={showPassword ? 'text' : 'password'} value={confirmPassword} required fullWidth
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
            />
            <Button type="submit" variant="contained" size="large" disabled={loading}>
              {loading ? 'Creating account…' : 'Sign Up'}
            </Button>
          </Stack>
        </form>

        <Typography variant="body2" sx={{ textAlign: 'center', mt: 2.5, color: 'text.secondary' }}>
          Already have an account?{' '}
          <Typography component={RouterLink} to="/login" variant="body2" sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none' }}>
            Log in
          </Typography>
        </Typography>
      </Paper>
    </Box>
  );
}
