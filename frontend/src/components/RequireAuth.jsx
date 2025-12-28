import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/api/AuthProvider';
import { Box, CircularProgress } from '@mui/material';

/**
 * RequireAuth Component
 * Route guard that redirects unauthenticated users to login
 * 
 * @param {React.ReactNode} children - Protected content
 * @param {string} redirectTo - Path to redirect unauthenticated users (default: /auth/login)
 */
export default function RequireAuth({ children, redirectTo = '/auth/login' }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking auth
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          bgcolor: 'grey.100'
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save the attempted location for redirect after login
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // User is authenticated, render children
  return children;
}
