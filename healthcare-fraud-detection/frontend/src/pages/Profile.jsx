import { Card, Stack, Typography, Avatar, Button, Divider, Chip } from '@mui/material';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const initials = user?.name?.split(' ').map((n) => n[0]).slice(0, 2).join('') || 'U';

  return (
    <DashboardLayout title="Profile">
      <Card sx={{ p: 4, maxWidth: 460 }}>
        <Stack alignItems="center" spacing={1.5}>
          <Avatar sx={{ width: 72, height: 72, bgcolor: 'primary.main', fontSize: '1.5rem' }}>{initials}</Avatar>
          <Typography variant="h6">{user?.name}</Typography>
          <Chip label={user?.role} color="primary" variant="outlined" size="small" />
        </Stack>
        <Divider sx={{ my: 3 }} />
        <Stack spacing={2}>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>Email</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>{user?.email}</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>User ID</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>{user?.id}</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>Role</Typography>
            <Typography variant="body2" sx={{ fontWeight: 600 }}>{user?.role}</Typography>
          </Stack>
        </Stack>
        <Divider sx={{ my: 3 }} />
        <Button
          fullWidth variant="outlined" color="error" startIcon={<LogoutOutlinedIcon />}
          onClick={async () => { await logout(); navigate('/login'); }}
        >
          Logout
        </Button>
      </Card>
    </DashboardLayout>
  );
}
