import { useState } from 'react';
import { AppBar, Toolbar, Box, Typography, IconButton, Badge, Menu, MenuItem, Avatar, Stack, Divider, ListItemIcon } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import NotificationsNoneOutlinedIcon from '@mui/icons-material/NotificationsNoneOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import { useAuth } from '../../context/AuthContext';
import { DRAWER_WIDTH } from './Sidebar';
import { useEffect } from 'react';
import * as notificationsService from '../../services/notificationsService';

export default function Topbar({ title }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    notificationsService.getNotifications().then((list) => {
      setUnread(list.filter((n) => !n.read).length);
    });
  }, []);

  const initials = user?.name?.split(' ').map((n) => n[0]).slice(0, 2).join('') || 'U';

  return (
    <AppBar position="fixed" color="inherit" sx={{ bgcolor: 'background.paper', width: `calc(100% - ${DRAWER_WIDTH}px)`, ml: `${DRAWER_WIDTH}px` }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Typography variant="h6" sx={{ fontSize: '1.05rem' }}>{title}</Typography>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <IconButton onClick={() => navigate('/notifications')}>
            <Badge badgeContent={unread} color="error">
              <NotificationsNoneOutlinedIcon />
            </Badge>
          </IconButton>
          <Divider orientation="vertical" flexItem sx={{ my: 1 }} />
          <Stack
            direction="row" alignItems="center" spacing={1}
            sx={{ cursor: 'pointer', pl: 0.5 }}
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            <Avatar sx={{ width: 34, height: 34, bgcolor: 'primary.main', fontSize: '0.85rem' }}>{initials}</Avatar>
            <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
              <Typography variant="body2" sx={{ fontWeight: 600, lineHeight: 1.1 }}>{user?.name}</Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>{user?.role}</Typography>
            </Box>
          </Stack>
          <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={() => setAnchorEl(null)}>
            <MenuItem onClick={() => { setAnchorEl(null); navigate('/profile'); }}>
              <ListItemIcon><PersonOutlineOutlinedIcon fontSize="small" /></ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem onClick={async () => { setAnchorEl(null); await logout(); navigate('/login'); }}>
              <ListItemIcon><LogoutOutlinedIcon fontSize="small" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Stack>
      </Toolbar>
    </AppBar>
  );
}
