import { useMemo } from 'react';
import { CssBaseline } from '@mui/material';
import { createTheme, ThemeProvider as MuiThemeProvider } from '@mui/material/styles';

// Theme pieces
import palette from './palette';
import typography from './typography';
import shadows from './shadows';
import componentOverrides from './overrides';

export default function ThemeProvider({ children }) {
  const mode = 'light'; // Can be made dynamic for dark mode support

  const themeOptions = useMemo(
    () => ({
      palette: palette(mode),
      typography: typography(),
      shadows: shadows(),
      shape: {
        borderRadius: 8
      },
      breakpoints: {
        values: {
          xs: 0,
          sm: 600,
          md: 900,
          lg: 1200,
          xl: 1536
        }
      }
    }),
    [mode]
  );

  const theme = createTheme(themeOptions);
  theme.components = componentOverrides(theme);

  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </MuiThemeProvider>
  );
}
