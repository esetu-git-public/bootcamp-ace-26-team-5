import { useEffect, useState } from 'react';
import { Card, Stack, Typography, IconButton, Box, LinearProgress } from '@mui/material';
import ReportProblemOutlinedIcon from '@mui/icons-material/ReportProblemOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import MarkEmailReadOutlinedIcon from '@mui/icons-material/MarkEmailReadOutlined';
import DashboardLayout from '../components/layout/DashboardLayout';
import EmptyState from '../components/common/EmptyState';
import * as notificationsService from '../services/notificationsService';
import { useNavigate } from 'react-router-dom';
import theme from '../theme/theme';

export default function Notifications() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const load = () => {
    setLoading(true);
    notificationsService.getNotifications().then((data) => { setItems(data); setLoading(false); });
  };

  useEffect(load, []);

  const handleRead = async (id, e) => {
    e.stopPropagation();
    await notificationsService.markAsRead(id);
    load();
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    await notificationsService.deleteNotification(id);
    load();
  };

  return (
    <DashboardLayout title="Notifications">
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      {!loading && items.length === 0 ? (
        <EmptyState title="No notifications" description="High-risk fraud alerts will appear here as claims are submitted." />
      ) : (
        <Stack spacing={1.5}>
          {items.map((n) => (
            <Card
              key={n.id}
              onClick={() => navigate(`/claims/${n.claimId}`)}
              sx={{
                p: 2, cursor: 'pointer',
                bgcolor: n.read ? 'background.paper' : theme.tokens.blueLight,
                borderColor: n.read ? 'divider' : `${theme.tokens.blue}55`,
              }}
            >
              <Stack direction="row" alignItems="flex-start" spacing={1.5}>
                <Box sx={{
                  width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
                  bgcolor: `${theme.tokens.high}1F`, color: theme.tokens.high,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <ReportProblemOutlinedIcon fontSize="small" />
                </Box>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 700 }}>{n.title}</Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    {n.patient} · Claim {n.claimId} · ${n.claimAmount.toLocaleString()} · probability {Math.round(n.probability * 100)}%
                  </Typography>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>{n.time}</Typography>
                </Box>
                <Stack direction="row" spacing={0.5}>
                  {!n.read && (
                    <IconButton size="small" onClick={(e) => handleRead(n.id, e)} title="Mark as read">
                      <MarkEmailReadOutlinedIcon fontSize="small" />
                    </IconButton>
                  )}
                  <IconButton size="small" onClick={(e) => handleDelete(n.id, e)} title="Delete">
                    <DeleteOutlineOutlinedIcon fontSize="small" />
                  </IconButton>
                </Stack>
              </Stack>
            </Card>
          ))}
        </Stack>
      )}
    </DashboardLayout>
  );
}
