import { createTheme } from '@mui/material/styles';

// ClaimGuard design tokens
// Primary: deep clinical blue | Accent: teal for "safe" signals | Risk scale: green/amber/red
const tokens = {
  navy: '#0B2545',
  blue: '#1B4F9C',
  blueLight: '#EAF1FC',
  teal: '#0E7C86',
  bg: '#F4F6F9',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  textPrimary: '#101828',
  textSecondary: '#5B6B82',
  low: '#1E9E6B',
  medium: '#D8A400',
  high: '#D6483C',
};

export const riskColor = (level) => {
  const l = (level || '').toLowerCase();
  if (l === 'high') return tokens.high;
  if (l === 'medium') return tokens.medium;
  if (l === 'low') return tokens.low;
  return tokens.textSecondary;
};

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: tokens.blue, dark: tokens.navy, light: tokens.blueLight },
    secondary: { main: tokens.teal },
    error: { main: tokens.high },
    warning: { main: tokens.medium },
    success: { main: tokens.low },
    background: { default: tokens.bg, paper: tokens.surface },
    text: { primary: tokens.textPrimary, secondary: tokens.textSecondary },
    divider: tokens.border,
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: "'Inter', 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif",
    h1: { fontWeight: 700 },
    h2: { fontWeight: 700 },
    h3: { fontWeight: 700 },
    h4: { fontWeight: 700, letterSpacing: -0.5 },
    h5: { fontWeight: 700, letterSpacing: -0.3 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 600 },
    button: { fontWeight: 600, textTransform: 'none' },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: `1px solid ${tokens.border}`,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: `1px solid ${tokens.border}`,
          boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, boxShadow: 'none' },
        contained: { boxShadow: 'none', '&:hover': { boxShadow: 'none' } },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 600 } },
    },
    MuiAppBar: {
      styleOverrides: {
        root: { boxShadow: 'none', borderBottom: `1px solid ${tokens.border}` },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: { fontWeight: 700, color: tokens.textSecondary, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: 0.4 },
      },
    },
  },
});

theme.tokens = tokens;
export default theme;
