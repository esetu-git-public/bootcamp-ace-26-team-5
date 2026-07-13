import { Box, Typography, Stack } from '@mui/material';
import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined';

export default function EmptyState({ title = 'Nothing here yet', description = '', icon }) {
  return (
    <Stack alignItems="center" justifyContent="center" spacing={1.5} sx={{ py: 8, color: 'text.secondary' }}>
      <Box sx={{ fontSize: 40, opacity: 0.5 }}>
        {icon || <InboxOutlinedIcon sx={{ fontSize: 40 }} />}
      </Box>
      <Typography variant="subtitle1" sx={{ color: 'text.primary' }}>{title}</Typography>
      {description && <Typography variant="body2" sx={{ maxWidth: 360, textAlign: 'center' }}>{description}</Typography>}
    </Stack>
  );
}
