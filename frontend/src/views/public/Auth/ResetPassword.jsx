import { useState } from 'react';
import { Link as RouterLink, useSearchParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Stack,
  Alert,
  InputAdornment,
  IconButton
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  IconLock,
  IconArrowLeft,
  IconEye,
  IconEyeOff,
  IconCheck
} from '@tabler/icons-react';
import Logo from '@/components/Logo';
import { resetPassword } from '@/api';

const MotionBox = motion.create(Box);

/**
 * Reset Password Page (Step 2)
 * User lands here from the email link with ?token=xxx
 * They enter their new password and submit.
 */
export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, newPassword, confirmPassword);
      setSuccess(true);
    } catch (err) {
      console.error('Reset password error:', err);
      if (err.response?.data?.detail) {
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

  // No token in URL — invalid link
  if (!token) {
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
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <RouterLink to="/" style={{ display: 'inline-block' }}>
                <Logo />
              </RouterLink>
            </Box>
            <Alert severity="error" sx={{ mb: 3 }}>
              Invalid or missing reset token. Please request a new password reset link.
            </Alert>
            <Button
              fullWidth
              component={RouterLink}
              to="/auth/forgot-password"
              variant="outlined"
              startIcon={<IconArrowLeft size={18} />}
              sx={{ py: 1.5 }}
            >
              Request New Reset Link
            </Button>
          </MotionBox>
        </Container>
      </Box>
    );
  }

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

          {success ? (
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
                <IconCheck size={32} />
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 600, textAlign: 'center', mb: 2 }}>
                Password Reset!
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 4 }}>
                Your password has been successfully updated. You can now sign in with your new password.
              </Typography>
              <Button
                fullWidth
                component={RouterLink}
                to="/auth/login"
                variant="contained"
                sx={{ py: 1.5 }}
              >
                Sign In
              </Button>
            </>
          ) : (
            // Form State
            <>
              <Typography variant="h4" sx={{ fontWeight: 700, textAlign: 'center', mb: 1 }}>
                Reset Password
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 4 }}>
                Enter your new password below.
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
                    label="New Password"
                    type={showPassword ? 'text' : 'password'}
                    value={newPassword}
                    onChange={(e) => {
                      setNewPassword(e.target.value);
                      if (error) setError('');
                    }}
                    required
                    helperText="Must be at least 8 characters"
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">
                            <IconLock size={20} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                              size="small"
                            >
                              {showPassword ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                            </IconButton>
                          </InputAdornment>
                        )
                      }
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Confirm New Password"
                    type={showConfirm ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value);
                      if (error) setError('');
                    }}
                    required
                    slotProps={{
                      input: {
                        startAdornment: (
                          <InputAdornment position="start">
                            <IconLock size={20} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowConfirm(!showConfirm)}
                              edge="end"
                              size="small"
                            >
                              {showConfirm ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                            </IconButton>
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
                    {loading ? 'Resetting...' : 'Reset Password'}
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
