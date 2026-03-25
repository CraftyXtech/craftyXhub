import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Layouts
const PublicLayout = lazy(() => import('@/layouts/PublicLayout'));
const DashboardLayout = lazy(() => import('@/layouts/DashboardLayout'));

// Components
import RequireRole from '@/components/RequireRole';
import RequireAuth from '@/components/RequireAuth';

// Public Views
const Home = lazy(() => import('@/views/public/Home'));
const BlogDetail = lazy(() => import('@/views/public/Blog/Detail'));
const Category = lazy(() => import('@/views/public/Category'));
const Author = lazy(() => import('@/views/public/Author'));
const About = lazy(() => import('@/views/public/About'));
const Login = lazy(() => import('@/views/public/Auth/Login'));
const Register = lazy(() => import('@/views/public/Auth/Register'));
const ForgotPassword = lazy(() => import('@/views/public/Auth/ForgotPassword'));
const ResetPassword = lazy(() => import('@/views/public/Auth/ResetPassword'));

// Dashboard Views - Core
const DashboardOverview = lazy(() => import('@/views/dashboard/Overview'));
const DashboardHome = lazy(() => import('@/views/dashboard/Home'));
const Posts = lazy(() => import('@/views/dashboard/Posts'));
const PostForm = lazy(() => import('@/views/dashboard/Posts/PostForm'));
const Drafts = lazy(() => import('@/views/dashboard/Drafts'));
const Bookmarks = lazy(() => import('@/views/dashboard/Bookmarks'));
const Media = lazy(() => import('@/views/dashboard/Media'));
const Profile = lazy(() => import('@/views/dashboard/Profile'));

// Dashboard Views - Social
const Followers = lazy(() => import('@/views/dashboard/Social/Followers'));
const Following = lazy(() => import('@/views/dashboard/Social/Following'));

// Dashboard Views - Notifications
const Notifications = lazy(() => import('@/views/dashboard/Notifications'));

// Dashboard Views - Collection
const Collection = lazy(() => import('@/views/dashboard/Collection'));
const ListDetail = lazy(() => import('@/views/dashboard/Collection/ListDetail'));

// Dashboard Views - Moderation (Editor+)
const CommentModeration = lazy(() => import('@/views/dashboard/Moderation/Comments'));
const PostReports = lazy(() => import('@/views/dashboard/Moderation/Reports'));

// Dashboard Views - Admin
const Users = lazy(() => import('@/views/dashboard/Admin/Users'));
const Analytics = lazy(() => import('@/views/dashboard/Admin/Analytics'));
const Categories = lazy(() => import('@/views/dashboard/Admin/Categories'));
const Tags = lazy(() => import('@/views/dashboard/Admin/Tags'));
const Settings = lazy(() => import('@/views/dashboard/Admin/Settings'));

function RouteFallback() {
  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'grid',
        placeItems: 'center',
        padding: '2rem',
        color: '#54657d',
        fontFamily: 'Inter, system-ui, sans-serif',
      }}
    >
      Loading...
    </div>
  );
}


function App() {
  return (
    <Suspense fallback={<RouteFallback />}>
      <Routes>
        {/* Public Routes with Layout */}
        <Route element={<PublicLayout />}>
          <Route index element={<Home />} />
          <Route path="/category/:slug" element={<Category />} />
          <Route path="/post/:slug" element={<BlogDetail />} />
          <Route path="/author/:username" element={<Author />} />
          <Route path="/about" element={<About />} />
        </Route>

        {/* Auth Routes (standalone) */}
        <Route path="/auth/login" element={<Login />} />
        <Route path="/auth/register" element={<Register />} />
        <Route path="/auth/forgot-password" element={<ForgotPassword />} />
        <Route path="/auth/reset-password" element={<ResetPassword />} />

        {/* Dashboard Routes (protected) */}
        <Route
          path="/dashboard"
          element={
            <RequireAuth>
              <DashboardLayout />
            </RequireAuth>
          }
        >
          {/* All authenticated users */}
          <Route index element={<DashboardOverview />} />
          <Route path="home" element={<DashboardHome />} />
          <Route path="posts" element={<Posts />} />
          <Route path="posts/create" element={<PostForm />} />
          <Route path="posts/edit/:id" element={<PostForm />} />
          <Route path="drafts" element={<Drafts />} />
          <Route path="bookmarks" element={<Bookmarks />} />
          <Route path="media" element={<Media />} />
          <Route path="profile" element={<Profile />} />
          <Route path="followers" element={<Followers />} />
          <Route path="following" element={<Following />} />
          <Route path="notifications" element={<Notifications />} />
          <Route path="collection" element={<Collection />} />
          <Route path="collection/list/:uuid" element={<ListDetail />} />

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
    </Suspense>
  );
}


export default App;
