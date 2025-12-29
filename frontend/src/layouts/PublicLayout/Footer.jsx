import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  Link,
  IconButton,
  Divider,
  Stack
} from '@mui/material';
import { IconBrandTwitter, IconBrandFacebook, IconBrandInstagram, IconBrandLinkedin } from '@tabler/icons-react';
import Logo from '@/components/Logo';

const footerLinks = {
  company: [
    { label: 'About', path: '/about' },
    { label: 'Careers', path: '/careers' }
  ],
  resources: [
    { label: 'Newsletter', path: '/newsletter' },
    { label: 'Help Center', path: '/help' }
  ],
  legal: [
    { label: 'Privacy Policy', path: '/privacy' },
    { label: 'Terms of Service', path: '/terms' }
  ]
};

const socialLinks = [
  { icon: IconBrandTwitter, href: '#', label: 'Twitter' },
  { icon: IconBrandFacebook, href: '#', label: 'Facebook' },
  { icon: IconBrandInstagram, href: '#', label: 'Instagram' },
  { icon: IconBrandLinkedin, href: '#', label: 'LinkedIn' }
];

export default function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        bgcolor: 'secondary.main',
        color: 'white',
        pt: 8,
        pb: 4
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          {/* Brand Column */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Logo variant="light" />
            <Typography variant="body2" sx={{ mt: 2, color: 'grey.400', maxWidth: 280 }}>
              Your creative content hub. Share ideas, discover stories, and connect with creators worldwide.
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 3 }}>
              {socialLinks.map((social) => (
                <IconButton
                  key={social.label}
                  component="a"
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={social.label}
                  sx={{
                    color: 'grey.400',
                    '&:hover': {
                      color: 'primary.main',
                      bgcolor: 'rgba(31, 125, 173, 0.1)'
                    }
                  }}
                >
                  <social.icon size={20} />
                </IconButton>
              ))}
            </Stack>
          </Grid>

          {/* Links Columns */}
          <Grid size={{ xs: 6, sm: 4, md: 2 }}>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
              Company
            </Typography>
            <Stack spacing={1.5}>
              {footerLinks.company.map((link) => (
                <Link
                  key={link.label}
                  component={RouterLink}
                  to={link.path}
                  sx={{ color: 'grey.400', '&:hover': { color: 'primary.main' } }}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          <Grid size={{ xs: 6, sm: 4, md: 2 }}>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
              Resources
            </Typography>
            <Stack spacing={1.5}>
              {footerLinks.resources.map((link) => (
                <Link
                  key={link.label}
                  component={RouterLink}
                  to={link.path}
                  sx={{ color: 'grey.400', '&:hover': { color: 'primary.main' } }}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>
          </Grid>

          <Grid size={{ xs: 6, sm: 4, md: 2 }}>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 2 }}>
              Legal
            </Typography>
            <Stack spacing={1.5}>
              {footerLinks.legal.map((link) => (
                <Link
                  key={link.label}
                  component={RouterLink}
                  to={link.path}
                  sx={{ color: 'grey.400', '&:hover': { color: 'primary.main' } }}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4, borderColor: 'grey.800' }} />

        {/* Copyright */}
        <Typography variant="body2" sx={{ color: 'grey.500', textAlign: 'center' }}>
          © {new Date().getFullYear()} CraftyXHub. All rights reserved.
        </Typography>
      </Container>
    </Box>
  );
}
