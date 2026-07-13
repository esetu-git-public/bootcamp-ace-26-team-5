import { Box, Typography, Stack } from '@mui/material';
import { riskColor } from '../../theme/theme';

// Semi-circular gauge showing fraud probability (0-1)
export default function RiskGauge({ probability = 0, riskLevel = 'Low', size = 180 }) {
  const pct = Math.min(1, Math.max(0, probability));
  const radius = size / 2 - 12;
  const circumference = Math.PI * radius;
  const dashOffset = circumference * (1 - pct);
  const color = riskColor(riskLevel);
  const cx = size / 2;
  const cy = size / 2;

  return (
    <Stack alignItems="center" spacing={0.5}>
      <Box sx={{ position: 'relative', width: size, height: size / 2 + 20 }}>
        <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
          <path
            d={`M 12 ${cy} A ${radius} ${radius} 0 0 1 ${size - 12} ${cy}`}
            fill="none"
            stroke="#E2E8F0"
            strokeWidth="14"
            strokeLinecap="round"
          />
          <path
            d={`M 12 ${cy} A ${radius} ${radius} 0 0 1 ${size - 12} ${cy}`}
            fill="none"
            stroke={color}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ transition: 'stroke-dashoffset 0.6s ease, stroke 0.3s ease' }}
          />
        </svg>
        <Box sx={{ position: 'absolute', top: '58%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
          <Typography variant="h4" sx={{ color, lineHeight: 1 }}>
            {Math.round(pct * 100)}%
          </Typography>
          <Typography variant="caption" sx={{ color: 'text.secondary' }}>
            fraud probability
          </Typography>
        </Box>
      </Box>
    </Stack>
  );
}
