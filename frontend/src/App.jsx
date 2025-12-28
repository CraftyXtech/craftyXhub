import { Routes, Route } from 'react-router-dom';
import PublicLayout from '@/layouts/PublicLayout';
import Home from '@/views/public/Home';
import BlogList from '@/views/public/Blog';
import BlogDetail from '@/views/public/Blog/Detail';
import Category from '@/views/public/Category';
import Author from '@/views/public/Author';
import About from '@/views/public/About';
import Login from '@/views/public/Auth/Login';
import Register from '@/views/public/Auth/Register';
import ForgotPassword from '@/views/public/Auth/ForgotPassword';

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

      {/* Auth Routes (no layout - standalone pages) */}
      <Route path="/auth/login" element={<Login />} />
      <Route path="/auth/register" element={<Register />} />
      <Route path="/auth/forgot-password" element={<ForgotPassword />} />
    </Routes>
  );
}

export default App;
