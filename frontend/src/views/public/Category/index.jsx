import { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  Chip
} from '@mui/material';
import { motion } from 'framer-motion';
import PostCard from '@/components/PostCard';
import Sidebar from '@/components/Blog/Sidebar';
import Pagination from '@/components/Pagination';
import Breadcrumb from '@/components/Breadcrumb';

const MotionBox = motion.create(Box);

// Sample category data (will be replaced with API data)
const categoryData = {
  design: {
    name: 'Design',
    description: 'Articles about UI/UX design, design systems, and visual aesthetics.',
    count: 12
  },
  technology: {
    name: 'Technology',
    description: 'Latest trends and insights in software development and tech innovation.',
    count: 18
  },
  startups: {
    name: 'Startups',
    description: 'Entrepreneurship, funding, and building successful startups.',
    count: 8
  },
  productivity: {
    name: 'Productivity',
    description: 'Tips and strategies for getting more done efficiently.',
    count: 6
  },
  marketing: {
    name: 'Marketing',
    description: 'Digital marketing, growth hacking, and brand building.',
    count: 10
  }
};

// Sample posts data (will be replaced with API data)
const samplePosts = [
  {
    id: 1,
    slug: 'design-thinking-guide',
    title: 'Design Thinking: A Practical Guide for Beginners',
    excerpt: 'Learn the fundamentals of design thinking and how to apply it to solve complex problems.',
    category: 'Design',
    author: { full_name: 'Emma Wilson', avatar: '' },
    created_at: '2024-12-27',
    read_time: '6 min read',
    featured_image: 'https://images.unsplash.com/photo-1558655146-d09347e92766?w=800&h=600&fit=crop'
  },
  {
    id: 2,
    slug: 'ux-research-methods',
    title: 'Essential UX Research Methods Every Designer Should Know',
    excerpt: 'A comprehensive guide to user research techniques for better product design.',
    category: 'Design',
    author: { full_name: 'Emma Wilson', avatar: '' },
    created_at: '2024-12-22',
    read_time: '10 min read',
    featured_image: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=600&fit=crop'
  },
  {
    id: 3,
    slug: 'building-design-systems',
    title: 'Building Scalable Design Systems from Scratch',
    excerpt: 'How to create and maintain a design system that grows with your product.',
    category: 'Design',
    author: { full_name: 'Michael Torres', avatar: '' },
    created_at: '2024-12-20',
    read_time: '8 min read',
    featured_image: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&h=600&fit=crop'
  }
];

/**
 * Category Page
 * Displays posts filtered by category with breadcrumb navigation
 */
export default function Category() {
  const { slug } = useParams();
  const [page, setPage] = useState(1);
  const postsPerPage = 6;

  // TODO: Replace with API call
  const category = categoryData[slug] || { name: slug, description: '', count: 0 };
  const posts = samplePosts; // Filter by category in real implementation
  const totalPages = Math.ceil(posts.length / postsPerPage);

  const handlePageChange = (event, value) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const breadcrumbItems = [
    { label: 'Blog', to: '/blog' },
    { label: category.name }
  ];

  return (
    <Box>
      {/* Category Header */}
      <Box
        sx={{
          bgcolor: 'grey.50',
          py: { xs: 6, md: 8 },
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Container maxWidth="lg">
          <Breadcrumb items={breadcrumbItems} />
          
          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Chip
              label="Category"
              size="small"
              sx={{
                mb: 2,
                bgcolor: 'accent.main',
                color: 'white',
                fontWeight: 600
              }}
            />
            <Typography
              variant="h2"
              sx={{ fontWeight: 700, mb: 2 }}
            >
              {category.name}
            </Typography>
            <Typography
              variant="body1"
              color="text.secondary"
              sx={{ maxWidth: 600 }}
            >
              {category.description}
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mt: 2 }}
            >
              {category.count} articles
            </Typography>
          </MotionBox>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
        <Grid container spacing={4}>
          {/* Posts Grid */}
          <Grid size={{ xs: 12, lg: 8 }}>
            <Grid container spacing={3}>
              {posts.map((post, index) => (
                <Grid size={{ xs: 12, sm: 6 }} key={post.id}>
                  <PostCard post={post} animationDelay={index * 0.05} />
                </Grid>
              ))}
            </Grid>

            {/* Pagination */}
            {totalPages > 1 && (
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
              />
            )}
          </Grid>

          {/* Sidebar */}
          <Grid size={{ xs: 12, lg: 4 }}>
            <Sidebar activeCategory={slug} />
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
