import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Divider,
  Stack,
  Alert,
  InputAdornment,
  IconButton,
  Checkbox,
  FormControlLabel
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  IconMail,
  IconLock,
  IconUser,
  IconEye,
  IconEyeOff,
  IconBrandGoogle,
  IconBrandGithub
} from '@tabler/icons-react';
import Logo from '@/components/Logo';
import { register as registerApi } from '@/api';

const MotionBox = motion.create(Box);

/**
 * Register Page
 */
export default function Register() {
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    if (!formData.agreeTerms) {
      setError('Please agree to the Terms & Conditions');
      setLoading(false);
      return;
    }

    try {
      // Split full name into first and last name
      const nameParts = formData.fullName.trim().split(' ');
      const firstName = nameParts[0] || '';
      const lastName = nameParts.slice(1).join(' ') || '';

      await registerApi({
        email: formData.email,
        password: formData.password,
        first_name: firstName,
        last_name: lastName,
        full_name: formData.fullName
      });
      
      setSuccess('Account created successfully! Redirecting to login...');
      
      // Redirect to login after a short delay
      setTimeout(() => {
        navigate('/auth/login', { 
          state: { message: 'Registration successful! Please sign in.' }
        });
      }, 1500);
    } catch (err) {
      console.error('Register error:', err);
      // Handle different error types
      if (err.response?.status === 400) {
        setError(err.response.data?.detail || 'Invalid registration data');
      } else if (err.response?.status === 409) {
        setError('An account with this email already exists');
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
        bgcolor: 'grey.50',
        py: 4
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

          {/* Header */}
          <Typography variant="h4" sx={{ fontWeight: 700, textAlign: 'center', mb: 1 }}>
            Create Account
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 4 }}>
            Join thousands of writers and readers
          </Typography>

          {/* Success Alert */}
          {success && (
            <Alert severity="success" sx={{ mb: 3 }}>
              {success}
            </Alert>
          )}

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
                label="Full Name"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                required
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <IconUser size={20} />
                      </InputAdornment>
                    )
                  }
                }}
              />
              <TextField
                fullWidth
                label="Email Address"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
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
              <TextField
                fullWidth
                label="Password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                required
                helperText="Minimum 6 characters"
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
                          {showPassword ? <IconEyeOff size={20} /> : <IconEye size={20} />}
                        </IconButton>
                      </InputAdornment>
                    )
                  }
                }}
              />
              <TextField
                fullWidth
                label="Confirm Password"
                name="confirmPassword"
                type={showPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <IconLock size={20} />
                      </InputAdornment>
                    )
                  }
                }}
              />

              <FormControlLabel
                control={
                  <Checkbox
                    name="agreeTerms"
                    checked={formData.agreeTerms}
                    onChange={handleChange}
                    size="small"
                  />
                }
                label={
                  <Typography variant="body2">
                    I agree to the{' '}
                    <Typography
                      component={RouterLink}
                      to="/terms"
                      variant="body2"
                      sx={{ color: 'primary.main', textDecoration: 'none' }}
                    >
                      Terms & Conditions
                    </Typography>
                  </Typography>
                }
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
                {loading ? 'Creating account...' : 'Create Account'}
              </Button>
            </Stack>
          </form>

          {/* Divider */}
          <Divider sx={{ my: 4 }}>
            <Typography variant="body2" color="text.secondary">
              or sign up with
            </Typography>
          </Divider>

          {/* Social Login */}
          <Stack direction="row" spacing={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<IconBrandGoogle size={20} />}
              sx={{ py: 1.5, color: 'text.primary', borderColor: 'grey.300' }}
            >
              Google
            </Button>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<IconBrandGithub size={20} />}
              sx={{ py: 1.5, color: 'text.primary', borderColor: 'grey.300' }}
            >
              GitHub
            </Button>
          </Stack>

          {/* Login Link */}
          <Typography variant="body2" sx={{ textAlign: 'center', mt: 4 }}>
            Already have an account?{' '}
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
        </MotionBox>
      </Container>
    </Box>
  );
}

