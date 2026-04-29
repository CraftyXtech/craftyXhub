import { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Stack,
  InputAdornment,
  Alert,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { IconMail, IconCheck } from '@tabler/icons-react';
import { subscribeToNewsletter } from '@/api/services/newsletterService';
import { getApiErrorMessage } from '@/utils/apiError';

const MotionBox = motion.create(Box);

export default function Newsletter() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError('Enter your email to subscribe.');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      await subscribeToNewsletter({ email: trimmedEmail, source: 'homepage' });
      setSubmitted(true);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not subscribe right now. Please try again.'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        py: { xs: 4, md: 8 },
        bgcolor: 'secondary.main',
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Background decoration */}
      <Box
        sx={{
          position: 'absolute',
          top: -100,
          right: -100,
          width: 300,
          height: 300,
          borderRadius: '50%',
          bgcolor: 'rgba(255,255,255,0.1)'
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: -50,
          left: -50,
          width: 200,
          height: 200,
          borderRadius: '50%',
          bgcolor: 'rgba(255,255,255,0.05)'
        }}
      />

      <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1 }}>
        <MotionBox
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          sx={{ textAlign: 'center' }}
        >
          <Typography variant="h3" fontWeight={700} sx={{ mb: 2 }}>
            Stay in the loop
          </Typography>
          <Typography
            variant="body1"
            sx={{ mb: 4, opacity: 0.9, maxWidth: 480, mx: 'auto' }}
          >
            Get the best articles, resources, and inspiration delivered straight to your inbox every week.
          </Typography>

          {!submitted ? (
            <Box
              component="form"
              onSubmit={handleSubmit}
              sx={{ maxWidth: 500, mx: 'auto' }}
            >
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <TextField
                  fullWidth
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  disabled={submitting}
                  onChange={(e) => setEmail(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <IconMail size={20} color="rgba(0,0,0,0.5)" />
                      </InputAdornment>
                    )
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      bgcolor: 'white',
                      '& fieldset': { borderColor: 'transparent' },
                      '&:hover fieldset': { borderColor: 'transparent' },
                      '&.Mui-focused fieldset': { borderColor: 'transparent' }
                    }
                  }}
                />
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={submitting}
                  startIcon={submitting ? <CircularProgress size={18} color="inherit" /> : null}
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    px: 4,
                    whiteSpace: 'nowrap',
                    '&:hover': {
                      bgcolor: 'primary.dark'
                    }
                  }}
                >
                  {submitting ? 'Subscribing' : 'Subscribe'}
                </Button>
              </Stack>
              {error && (
                <Alert severity="error" sx={{ mt: 2, textAlign: 'left' }} onClose={() => setError('')}>
                  {error}
                </Alert>
              )}
              <Typography variant="caption" sx={{ mt: 2, display: 'block', opacity: 0.7 }}>
                No spam, unsubscribe at any time.
              </Typography>
            </Box>
          ) : (
            <MotionBox
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1,
                bgcolor: 'rgba(255,255,255,0.2)',
                px: 3,
                py: 1.5,
                borderRadius: 2
              }}
            >
              <IconCheck size={20} />
              <Typography variant="body1" fontWeight={500}>
                Thanks for subscribing!
              </Typography>
            </MotionBox>
          )}
        </MotionBox>
      </Container>
    </Box>
  );
}
