import { Navigate } from 'react-router-dom';
import { useAuth } from '@/api/AuthProvider';
import { hasRole } from '@/utils/roleUtils';

/**
 * RequireRole Component
 * Route guard that checks user role and redirects if unauthorized
 * 
 * @param {string} role - Minimum required role ('user', 'moderator', 'admin')
 * @param {React.ReactNode} children - Protected content
 * @param {string} redirectTo - Path to redirect unauthorized users (default: /dashboard)
 */
export default function RequireRole({ role, children, redirectTo = '/dashboard' }) {
  const { user, isAuthenticated, loading } = useAuth();

  // Show nothing while checking auth
  if (loading) {
    return null;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/auth/login" replace />;
  }

  // Check if user has required role
  const userRole = user?.role || 'user';
  const authorized = hasRole(userRole, role);

  if (!authorized) {
    // User doesn't have permission, redirect to dashboard
    return <Navigate to={redirectTo} replace />;
  }

  // User is authorized, render children
  return children;
}
