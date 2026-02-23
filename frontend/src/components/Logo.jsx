import { Box } from '@mui/material';
import branding from '@/branding.json';

export default function Logo({ variant = 'dark', showText = true }) {
  const src = showText ? branding.logo.main : branding.logo.icon;
  const alt = showText ? branding.brandName : 'Logo';

  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <img
        src={src}
        alt={alt}
        style={{ height: 40, width: 'auto', filter: variant === 'light' ? 'brightness(0) invert(1)' : 'none' }}
      />
    </Box>
  );
}
