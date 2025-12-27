import { Routes, Route } from 'react-router-dom';
import PublicLayout from '@/layouts/PublicLayout';
import Home from '@/views/public/Home';
import BlogDetail from '@/views/public/BlogDetail';

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="/blog/:id" element={<BlogDetail />} />
        <Route path="/blog-demo" element={<BlogDetail />} />
      </Route>
    </Routes>
  );
}

export default App;
