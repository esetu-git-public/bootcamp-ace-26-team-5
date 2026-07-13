import { Box, Drawer, List, ListItemButton, ListItemIcon, ListItemText, Typography, Stack } from '@mui/material';
import { NavLink, useLocation } from 'react-router-dom';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import NoteAddOutlinedIcon from '@mui/icons-material/NoteAddOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import FindInPageOutlinedIcon from '@mui/icons-material/FindInPageOutlined';
import BarChartOutlinedIcon from '@mui/icons-material/BarChartOutlined';
import NotificationsNoneOutlinedIcon from '@mui/icons-material/NotificationsNoneOutlined';
import { useAuth, ROLES } from '../../context/AuthContext';

const DRAWER_WIDTH = 248;

const navItems = [
  { label: 'Dashboard', to: '/dashboard', icon: <DashboardOutlinedIcon />, roles: [ROLES.POLICYHOLDER, ROLES.OFFICER, ROLES.INVESTIGATOR, ROLES.ADMIN] },
  { label: 'Submit Claim', to: '/claims/submit', icon: <NoteAddOutlinedIcon />, roles: [ROLES.POLICYHOLDER, ROLES.OFFICER] },
  { label: 'Claim History', to: '/claims', labelByRole: { [ROLES.POLICYHOLDER]: 'My Claims' }, icon: <HistoryOutlinedIcon />, roles: [ROLES.POLICYHOLDER, ROLES.OFFICER, ROLES.INVESTIGATOR, ROLES.ADMIN] },
  { label: 'Investigation', to: '/investigation', icon: <FindInPageOutlinedIcon />, roles: [ROLES.INVESTIGATOR, ROLES.ADMIN] },
  { label: 'Reports', to: '/reports', icon: <BarChartOutlinedIcon />, roles: [ROLES.ADMIN, ROLES.INVESTIGATOR] },
  { label: 'Notifications', to: '/notifications', icon: <NotificationsNoneOutlinedIcon />, roles: [ROLES.OFFICER, ROLES.INVESTIGATOR, ROLES.ADMIN] },
];

export { DRAWER_WIDTH };

export default function Sidebar() {
  const { user } = useAuth();
  const location = useLocation();
  const items = navItems.filter((item) => item.roles.includes(user?.role));

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box', borderRight: '1px solid #E2E8F0' },
      }}
    >
      <Stack direction="row" alignItems="center" spacing={1.25} sx={{ px: 2.5, py: 2.5 }}>
        <Box sx={{ width: 34, height: 34, borderRadius: 1.5, bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <ShieldOutlinedIcon sx={{ color: '#fff', fontSize: 20 }} />
        </Box>
        <Box>
          <Typography variant="subtitle1" sx={{ lineHeight: 1.1 }}>ClaimGuard</Typography>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>Fraud Detection System</Typography>
        </Box>
      </Stack>

      <List sx={{ px: 1.5 }}>
        {items.map((item) => {
          const active = location.pathname.startsWith(item.to);
          return (
            <ListItemButton
              key={item.to}
              component={NavLink}
              to={item.to}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                color: active ? 'primary.main' : 'text.secondary',
                bgcolor: active ? 'primary.light' : 'transparent',
                '&:hover': { bgcolor: active ? 'primary.light' : '#F1F5F9' },
              }}
            >
              <ListItemIcon sx={{ minWidth: 36, color: active ? 'primary.main' : 'text.secondary' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primaryTypographyProps={{ fontWeight: active ? 700 : 500, fontSize: '0.9rem' }} primary={item.labelByRole?.[user?.role] || item.label} />
            </ListItemButton>
          );
        })}
      </List>
    </Drawer>
  );
}
