import { useAuth } from '@/api/AuthProvider';
import { isModerator } from '@/utils/roleUtils';

// Role-specific editors
import UserPostEditor from './UserPostEditor';
import AdminPostEditor from './AdminPostEditor';

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
  if (hasModeratorAccess) {
    return <AdminPostEditor />;
  }

  return <UserPostEditor />;
}
