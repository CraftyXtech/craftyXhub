import { Routes, Route, Navigate } from 'react-router-dom';

// Layouts
import PublicLayout from '@/layouts/PublicLayout';
import DashboardLayout from '@/layouts/DashboardLayout';

// Components
import RequireRole from '@/components/RequireRole';

// Public Views
import Home from '@/views/public/Home';
import BlogList from '@/views/public/Blog';
import BlogDetail from '@/views/public/Blog/Detail';
import Category from '@/views/public/Category';
import Author from '@/views/public/Author';
import About from '@/views/public/About';
import Login from '@/views/public/Auth/Login';
import Register from '@/views/public/Auth/Register';
import ForgotPassword from '@/views/public/Auth/ForgotPassword';

// Dashboard Views - Core
import DashboardOverview from '@/views/dashboard/Overview';
import Posts from '@/views/dashboard/Posts';
import PostForm from '@/views/dashboard/Posts/PostForm';
import Drafts from '@/views/dashboard/Drafts';
import Media from '@/views/dashboard/Media';
import Profile from '@/views/dashboard/Profile';

// Dashboard Views - Moderation (Editor+)
import CommentModeration from '@/views/dashboard/Moderation/Comments';
import PostReports from '@/views/dashboard/Moderation/Reports';

// Dashboard Views - Admin
import Users from '@/views/dashboard/Admin/Users';
import Analytics from '@/views/dashboard/Admin/Analytics';
import Categories from '@/views/dashboard/Admin/Categories';
import Tags from '@/views/dashboard/Admin/Tags';
import Settings from '@/views/dashboard/Admin/Settings';

function App() {
  return (
    <Routes>
      {/* Public Routes with Layout */}
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="/blog" element={<BlogList />} />
        <Route path="/blog/category/:slug" element={<Category />} />
        <Route path="/blog/:slug" element={<BlogDetail />} />
        <Route path="/author/:username" element={<Author />} />
        <Route path="/about" element={<About />} />
      </Route>

      {/* Auth Routes (standalone) */}
      <Route path="/auth/login" element={<Login />} />
      <Route path="/auth/register" element={<Register />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />

      {/* Dashboard Routes (protected) */}
      <Route path="/dashboard" element={<DashboardLayout />}>
        {/* All authenticated users */}
        <Route index element={<DashboardOverview />} />
        <Route path="posts" element={<Posts />} />
        <Route path="posts/create" element={<PostForm />} />
        <Route path="posts/edit/:id" element={<PostForm />} />
        <Route path="drafts" element={<Drafts />} />
        <Route path="media" element={<Media />} />
        <Route path="profile" element={<Profile />} />

        {/* Editor+ routes */}
        <Route
          path="ai-writer"
          element={
            <RequireRole role="moderator">
              <ComingSoon title="AI Writer" />
            </RequireRole>
          }
        />
        <Route
          path="moderation/comments"
          element={
            <RequireRole role="moderator">
              <CommentModeration />
            </RequireRole>
          }
        />
        <Route
          path="moderation/reports"
          element={
            <RequireRole role="moderator">
              <PostReports />
            </RequireRole>
          }
        />

        {/* Admin routes */}
        <Route
          path="users"
          element={
            <RequireRole role="admin">
              <Users />
            </RequireRole>
          }
        />
        <Route
          path="analytics"
          element={
            <RequireRole role="admin">
              <Analytics />
            </RequireRole>
          }
        />
        <Route
          path="categories"
          element={
            <RequireRole role="admin">
              <Categories />
            </RequireRole>
          }
        />
        <Route
          path="tags"
          element={
            <RequireRole role="admin">
              <Tags />
            </RequireRole>
          }
        />
        <Route
          path="settings"
          element={
            <RequireRole role="admin">
              <Settings />
            </RequireRole>
          }
        />
      </Route>

      {/* Catch-all redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// Placeholder for AI Writer (Phase 3)
function ComingSoon({ title }) {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center', 
      padding: '60px 20px',
      textAlign: 'center'
    }}>
      <h2 style={{ margin: 0, marginBottom: 8, color: '#14213D' }}>{title}</h2>
      <p style={{ margin: 0, color: '#666' }}>This page is coming soon.</p>
    </div>
  );
}

export default App;
