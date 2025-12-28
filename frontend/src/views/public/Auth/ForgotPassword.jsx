import { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Stack,
  Alert,
  InputAdornment
} from '@mui/material';
import { motion } from 'framer-motion';
import { IconMail, IconArrowLeft } from '@tabler/icons-react';
import Logo from '@/components/Logo';
import { requestPasswordReset } from '@/api';

const MotionBox = motion.create(Box);

/**
 * Forgot Password Page
 */
export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await requestPasswordReset(email);
      setSubmitted(true);
    } catch (err) {
      console.error('Password reset error:', err);
      // Handle different error types
      if (err.response?.status === 404) {
        // Don't reveal if email exists for security, show success anyway
        setSubmitted(true);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.message) {
        setError(err.message);
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        bgcolor: 'grey.50'
      }}
    >
      <Container maxWidth="sm">
        <MotionBox
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          sx={{
            bgcolor: 'background.paper',
            p: { xs: 4, md: 6 },
            borderRadius: 3,
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
          }}
        >
          {/* Logo */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <RouterLink to="/" style={{ display: 'inline-block' }}>
              <Logo />
            </RouterLink>
          </Box>

          {submitted ? (
            // Success State
            <>
              <Box
                sx={{
                  width: 64,
                  height: 64,
                  borderRadius: '50%',
                  bgcolor: 'success.lighter',
                  color: 'success.main',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3
                }}
              >
                <IconMail size={32} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 600, textAlign: 'center', mb: 2 }}>
                Check your email
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 4 }}>
                If an account exists for <strong>{email}</strong>, we've sent a password reset link. 
                Please check your inbox and follow the instructions.
              </Typography>
              <Button
                fullWidth
                component={RouterLink}
                to="/auth/login"
                variant="outlined"
                startIcon={<IconArrowLeft size={18} />}
                sx={{ py: 1.5 }}
              >
                Back to Sign In
              </Button>
            </>
          ) : (
            // Form State
            <>
              <Typography variant="h4" sx={{ fontWeight: 700, textAlign: 'center', mb: 1 }}>
                Forgot Password?
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 4 }}>
                No worries! Enter your email and we'll send you reset instructions.
              </Typography>

              {/* Error Alert */}
              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit}>
                <Stack spacing={3}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (error) setError('');
                    }}
                    required
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">
                            <IconMail size={20} />
                          </InputAdornment>
                        )
                      }
                    }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={loading}
                    sx={{
                      bgcolor: 'primary.main',
                      py: 1.5,
                      '&:hover': { bgcolor: 'primary.dark' }
                    }}
                  >
                    {loading ? 'Sending...' : 'Send Reset Link'}
                  </Button>
                </Stack>
              </form>

              {/* Back to Login */}
              <Typography variant="body2" sx={{ textAlign: 'center', mt: 4 }}>
                Remember your password?{' '}
                <Typography
                  component={RouterLink}
                  to="/auth/login"
                  variant="body2"
                  sx={{
                    color: 'primary.main',
                    fontWeight: 600,
                    textDecoration: 'none',
                    '&:hover': { textDecoration: 'underline' }
                  }}
                >
                  Sign in
                </Typography>
              </Typography>
            </>
          )}
        </MotionBox>
      </Container>
    </Box>
  );
}

