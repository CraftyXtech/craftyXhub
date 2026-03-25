import { Suspense, lazy } from 'react';
import { useAuth } from '@/api/AuthProvider';
import { isModerator } from '@/utils/roleUtils';

// Role-specific editors
const UserPostEditor = lazy(() => import('./UserPostEditor'));
const AdminPostEditor = lazy(() => import('./AdminPostEditor'));

/**
 * PostForm - Role-switching wrapper
 * 
 * Routes to the appropriate editor based on user role:
 * - Regular users → Medium-style BlockEditor
 * - Moderators/Admins → TinyMCE with AI panel
 */
export default function PostForm() {
  const { user } = useAuth();
  const hasModeratorAccess = isModerator(user?.role);

  // Render appropriate editor based on role
  return (
    <Suspense fallback={<div style={{ padding: '2rem', color: '#54657d' }}>Loading editor...</div>}>
      {hasModeratorAccess ? <AdminPostEditor /> : <UserPostEditor />}
    </Suspense>
  );
}
