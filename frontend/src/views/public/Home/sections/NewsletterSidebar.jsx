import { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { IconMail, IconCheck } from '@tabler/icons-react';
import { subscribeToNewsletter } from '@/api/services/newsletterService';
import { getApiErrorMessage } from '@/utils/apiError';

const MotionBox = motion.create(Box);

export default function NewsletterSidebar() {
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
      await subscribeToNewsletter({ email: trimmedEmail, source: 'homepage_sidebar' });
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
        position: 'sticky',
        top: 100,
      }}
    >
      {/* Header Bar - Dark navy like reference image */}
      <Box
        sx={{
          bgcolor: '#1a1a2e',
          color: 'white',
          px: 2.5,
          py: 1.5,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          borderRadius: '8px 8px 0 0',
        }}
      >
        <IconMail size={20} />
        <Typography variant="subtitle1" sx={{ fontWeight: 700, letterSpacing: 0.5 }}>
          Newsletter
        </Typography>
      </Box>

      {/* Content */}
      <Box
        sx={{
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderTop: 'none',
          borderRadius: '0 0 8px 8px',
          p: 2.5,
        }}
      >
        {!submitted ? (
          <>
            <Typography
              variant="body2"
              sx={{
                color: 'text.secondary',
                mb: 2.5,
                lineHeight: 1.6,
              }}
            >
              Get the best articles, resources, and inspiration delivered straight to
              your inbox every week.
            </Typography>

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                type="email"
                placeholder="Email Address"
                value={email}
                disabled={submitting}
                onChange={(e) => setEmail(e.target.value)}
                size="small"
                sx={{
                  mb: 1.5,
                  '& .MuiOutlinedInput-root': {
                    bgcolor: '#f5f5f5',
                    borderRadius: '6px',
                    '& fieldset': { borderColor: '#e0e0e0' },
                    '&:hover fieldset': { borderColor: '#bbb' },
                    '&.Mui-focused fieldset': { borderColor: 'primary.main' },
                  },
                }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={submitting}
                startIcon={
                  submitting ? <CircularProgress size={16} color="inherit" /> : null
                }
                sx={{
                  bgcolor: '#e74c6f',
                  color: 'white',
                  fontWeight: 600,
                  textTransform: 'none',
                  borderRadius: '6px',
                  py: 1,
                  fontSize: '0.9rem',
                  '&:hover': {
                    bgcolor: '#d63d60',
                  },
                }}
              >
                {submitting ? 'Subscribing...' : 'Subscribe'}
              </Button>

              {error && (
                <Alert
                  severity="error"
                  sx={{ mt: 1.5, fontSize: '0.75rem' }}
                  onClose={() => setError('')}
                >
                  {error}
                </Alert>
              )}
            </Box>

            <Typography
              variant="caption"
              sx={{
                mt: 2,
                display: 'block',
                color: 'text.disabled',
                fontSize: '0.7rem',
              }}
            >
              No spam, unsubscribe at any time.
            </Typography>
          </>
        ) : (
          <MotionBox
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 1,
              py: 3,
            }}
          >
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: '50%',
                bgcolor: 'success.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 1,
              }}
            >
              <IconCheck size={24} color="white" />
            </Box>
            <Typography variant="body2" fontWeight={600} textAlign="center">
              Thanks for subscribing!
            </Typography>
            <Typography variant="caption" color="text.secondary" textAlign="center">
              Check your inbox for confirmation.
            </Typography>
          </MotionBox>
        )}
      </Box>
    </Box>
  );
}
