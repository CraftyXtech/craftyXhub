import { useEffect, useState } from 'react';
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
import { IconBrandX, IconBrandFacebook, IconBrandInstagram, IconBrandLinkedin } from '@tabler/icons-react';
import Logo from '@/components/Logo';
import { getPublicSettings } from '@/api/services/settingsService';

const footerLinks = {
  company: [
    { label: 'About', path: '/about' },
    { label: 'Careers', path: '/careers' }
  ],
  legal: [
    { label: 'Privacy Policy', path: '/privacy' },
    { label: 'Terms of Service', path: '/terms' }
  ]
};

const socialIconMap = {
  x: IconBrandX,
  twitter: IconBrandX,
  facebook: IconBrandFacebook,
  instagram: IconBrandInstagram,
  linkedin: IconBrandLinkedin
};

const getNavigationProps = (url) => {
  if (!url) {
    return { component: RouterLink, to: '/brief' };
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return {
      component: 'a',
      href: url,
      target: '_blank',
      rel: 'noopener noreferrer'
    };
  }
  return { component: RouterLink, to: url };
};

export default function Footer() {
  const [briefLink, setBriefLink] = useState({ label: 'Daily Brief', path: '/brief' });
  const [socialLinks, setSocialLinks] = useState([]);

  useEffect(() => {
    const loadFooterSettings = async () => {
      try {
        const settings = await getPublicSettings();
        setBriefLink({
          label: settings?.daily_brief_label || 'Daily Brief',
          path: settings?.daily_brief_url || '/brief'
        });
        setSocialLinks(
          (settings?.social_links || []).filter((item) => item.url && socialIconMap[item.platform?.toLowerCase()])
        );
      } catch (error) {
        console.error('Failed to load footer settings:', error);
        setSocialLinks([]);
      }
    };

    loadFooterSettings();
  }, []);

  const resourceLinks = [
    { label: briefLink.label, path: briefLink.path },
    { label: 'Help Center', path: '/help' }
  ];

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
            <Logo />
            <Typography variant="body2" sx={{ mt: 2, color: 'grey.400', maxWidth: 280, lineHeight: 1.6 }}>
              Your trusted source for news and insights on AI, technology, crypto, and business.
            </Typography>
            <Stack direction="row" spacing={1} sx={{ mt: 3 }}>
              {socialLinks.map((social) => (
                <IconButton
                  key={`${social.platform}-${social.label}`}
                  component="a"
                  href={social.url}
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
                  {(() => {
                    const Icon = socialIconMap[social.platform?.toLowerCase()];
                    return Icon ? <Icon size={20} /> : null;
                  })()}
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
              {resourceLinks.map((link) => (
                <Link
                  key={link.label}
                  {...getNavigationProps(link.path)}
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
