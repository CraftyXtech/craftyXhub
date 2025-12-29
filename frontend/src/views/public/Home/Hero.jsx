import { Box, Container, Typography, Button, Stack } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import { IconArrowRight, IconSparkles } from '@tabler/icons-react';

const MotionBox = motion.create(Box);

export default function Hero() {
  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: '85vh',
        display: 'flex',
        alignItems: 'center',
        overflow: 'hidden',
        bgcolor: 'background.default'
      }}
    >
      {/* Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: `
            radial-gradient(circle at 20% 50%, rgba(31, 125, 173, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(31, 125, 173, 0.05) 0%, transparent 40%)
          `,
          zIndex: 0
        }}
      />

      <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
        <Box sx={{ maxWidth: 720, mx: 'auto', textAlign: 'center' }}>
          {/* Badge */}
          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1,
                px: 2,
                py: 0.75,
                borderRadius: 6,
                bgcolor: 'primary.lighter',
                color: 'primary.dark',
                mb: 4
              }}
            >
              <IconSparkles size={16} />
              <Typography variant="caption" fontWeight={600}>
                Welcome to CraftyXHub
              </Typography>
            </Box>
          </MotionBox>

          {/* Main Heading */}
          <MotionBox
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <Typography
              variant="h1"
              sx={{
                fontSize: { xs: '2.5rem', sm: '3.5rem', md: '4rem' },
                fontWeight: 700,
                lineHeight: 1.1,
                mb: 3,
                color: 'text.primary'
              }}
            >
              Share Ideas.
              <br />
              <Box component="span" sx={{ color: 'text.primary' }}>
                Inspire Others.
              </Box>
            </Typography>
          </MotionBox>

          {/* Subtitle */}
          <MotionBox
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Typography
              variant="h6"
              sx={{
                color: 'text.secondary',
                fontWeight: 400,
                maxWidth: 540,
                mx: 'auto',
                mb: 5,
                lineHeight: 1.7
              }}
            >
              Your creative content hub where writers, thinkers, and creators come together to share stories and discover new perspectives.
            </Typography>
          </MotionBox>

          {/* CTA Buttons */}
          <MotionBox
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={2}
              justifyContent="center"
            >
              <Button
                component={RouterLink}
                to="/auth/register"
                variant="contained"
                color="secondary"
                size="large"
                endIcon={<IconArrowRight size={18} />}
                sx={{
                  px: 4,
                  py: 1.5,
                  bgcolor: 'secondary.main',
                  '&:hover': {
                    bgcolor: 'secondary.dark'
                  }
                }}
              >
                Start Writing
              </Button>
              <Button
                onClick={() => window.scrollTo({ top: 600, behavior: 'smooth' })}
                variant="outlined"
                color="secondary"
                size="large"
                sx={{
                  px: 4,
                  py: 1.5,
                  borderColor: 'grey.300',
                  '&:hover': {
                    borderColor: 'grey.400',
                    bgcolor: 'grey.50'
                  }
                }}
              >
                Explore Articles
              </Button>
            </Stack>
          </MotionBox>

          {/* Stats */}
          <MotionBox
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            sx={{ mt: 8 }}
          >
            <Stack
              direction="row"
              spacing={{ xs: 4, md: 8 }}
              justifyContent="center"
              divider={
                <Box sx={{ width: 1, bgcolor: 'divider', alignSelf: 'stretch' }} />
              }
            >
              {[
                { value: '10K+', label: 'Active Writers' },
                { value: '50K+', label: 'Published Articles' },
                { value: '1M+', label: 'Monthly Readers' }
              ].map((stat) => (
                <Box key={stat.label} sx={{ textAlign: 'center' }}>
                  <Typography
                    variant="h4"
                    fontWeight={700}
                    color="text.primary"
                  >
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </MotionBox>
        </Box>
      </Container>
    </Box>
  );
}
