import { Card, Box, Typography, Stack } from '@mui/material';

export default function KpiCard({ label, value, icon, accent = '#1B4F9C', suffix = '' }) {
  return (
    <Card sx={{ p: 2.25, height: '100%' }}>
      <Stack direction="row" alignItems="flex-start" justifyContent="space-between">
        <Box>
          <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
            {label}
          </Typography>
          <Typography variant="h4" sx={{ mt: 0.5, color: 'text.primary' }}>
            {value}{suffix}
          </Typography>
        </Box>
        {icon && (
          <Box
            sx={{
              width: 40, height: 40, borderRadius: 2,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              bgcolor: `${accent}1A`, color: accent,
            }}
          >
            {icon}
          </Box>
        )}
      </Stack>
    </Card>
  );
}
