import { Chip } from '@mui/material';
import { riskColor } from '../../theme/theme';

export function RiskChip({ level }) {
  const color = riskColor(level);
  return (
    <Chip
      label={level}
      size="small"
      sx={{
        bgcolor: `${color}1F`,
        color,
        border: `1px solid ${color}55`,
      }}
    />
  );
}

const statusColors = {
  'Approved': '#1E9E6B',
  'Rejected': '#D6483C',
  'Pending Review': '#D8A400',
  'Under Investigation': '#1B4F9C',
};

export function StatusChip({ status }) {
  const color = statusColors[status] || '#5B6B82';
  return (
    <Chip
      label={status}
      size="small"
      variant="outlined"
      sx={{ color, borderColor: `${color}66`, bgcolor: `${color}0D` }}
    />
  );
}
