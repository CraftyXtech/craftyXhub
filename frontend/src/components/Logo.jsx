import { Box, Typography } from '@mui/material';
import branding from '@/branding.json';

export default function Logo({ variant = 'dark', showText = true }) {
  const color = variant === 'light' ? 'white' : 'text.primary';
  const accentColor = 'primary.main';

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      {/* Logo Icon */}
      <Box
        sx={{
          width: 36,
          height: 36,
          borderRadius: 2,
          bgcolor: accentColor,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Typography
          variant="h6"
          sx={{
            color: 'white',
            fontWeight: 700,
            fontSize: '1.25rem'
          }}
        >
          C
        </Typography>
      </Box>

      {/* Logo Text */}
      {showText && (
        <Typography
          variant="h6"
          sx={{
            color: color,
            fontWeight: 700,
            letterSpacing: '-0.02em'
          }}
        >
          {branding.brandName}
        </Typography>
      )}
    </Box>
  );
}
