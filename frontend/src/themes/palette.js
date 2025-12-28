import { alpha } from '@mui/material/styles';

/**
 * CraftyXHub Color Palette
 * Black & White base with Oxford Blue (#14213D) accent
 */
export default function palette(mode) {
  const isLight = mode === 'light';

  // Core colors
  const primaryMain = '#14213D';  // Oxford Blue accent
  const textPrimary = '#1A1A1A'; // Near-black
  const textSecondary = '#666666'; // Dark gray

  return {
    mode,
    primary: {
      lighter: '#e8eaf0',
      light: '#4a5a7a',
      main: primaryMain,
      dark: '#0d1629',
      darker: '#060b14',
      contrastText: '#FFFFFF'
    },
    secondary: {
      lighter: '#F5F5F5',
      light: '#E0E0E0',
      main: '#1A1A1A',
      dark: '#0D0D0D',
      darker: '#000000',
      contrastText: '#FFFFFF'
    },
    error: {
      lighter: '#FFE7E7',
      light: '#FF9999',
      main: '#E53935',
      dark: '#B71C1C',
      darker: '#7F0000'
    },
    warning: {
      lighter: '#FFF8E1',
      light: '#FFD54F',
      main: '#FF9800',
      dark: '#EF6C00',
      darker: '#E65100'
    },
    success: {
      lighter: '#E8F5E9',
      light: '#81C784',
      main: '#4CAF50',
      dark: '#2E7D32',
      darker: '#1B5E20'
    },
    info: {
      lighter: '#E3F2FD',
      light: '#64B5F6',
      main: '#2196F3',
      dark: '#1565C0',
      darker: '#0D47A1'
    },
    // Warm amber accent for CTAs, highlights, featured labels
    accent: {
      lighter: '#fef3e8',
      light: '#f7b885',
      main: '#f39F5A',
      dark: '#d68640',
      darker: '#b86d2a',
      contrastText: '#FFFFFF'
    },
    grey: {
      50: '#FAFAFA',
      100: '#F5F5F5',
      200: '#EEEEEE',
      300: '#E0E0E0',
      400: '#BDBDBD',
      500: '#9E9E9E',
      600: '#757575',
      700: '#616161',
      800: '#424242',
      900: '#212121'
    },
    text: {
      primary: isLight ? textPrimary : '#FFFFFF',
      secondary: isLight ? textSecondary : '#B0B0B0',
      disabled: '#9E9E9E'
    },
    divider: isLight ? '#E5E5E5' : '#333333',
    background: {
      default: isLight ? '#FFFFFF' : '#121212',
      paper: isLight ? '#FAFAFA' : '#1E1E1E'
    },
    action: {
      hover: alpha(primaryMain, 0.08),
      selected: alpha(primaryMain, 0.12),
      disabled: alpha(textPrimary, 0.26),
      disabledBackground: alpha(textPrimary, 0.12)
    }
  };
}
