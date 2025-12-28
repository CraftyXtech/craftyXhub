import { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  FormControl,
  Select,
  MenuItem,
  Stack
} from '@mui/material';
import { motion } from 'framer-motion';
import PostCard from '@/components/PostCard';
import Sidebar from '@/components/Blog/Sidebar';
import Pagination from '@/components/Pagination';
import SectionHeader from '@/components/SectionHeader';

const MotionBox = motion.create(Box);

// Sample posts data (will be replaced with API data)
const samplePosts = [
  {
    id: 1,
    slug: 'design-thinking-guide',
    title: 'Design Thinking: A Practical Guide for Beginners',
    excerpt: 'Learn the fundamentals of design thinking and how to apply it to solve complex problems in your daily work.',
    category: 'Design',
    author: { full_name: 'Emma Wilson', avatar: '' },
    created_at: '2024-12-27',
    read_time: '6 min read',
    featured_image: 'https://images.unsplash.com/photo-1558655146-d09347e92766?w=800&h=600&fit=crop'
  },
  {
    id: 2,
    slug: 'startup-funding-tips',
    title: 'Startup Funding in 2024: What VCs Are Looking For',
    excerpt: 'Insights from top venture capitalists on what makes a startup investment-worthy in the current market.',
    category: 'Startups',
    author: { full_name: 'James Chen', avatar: '' },
    created_at: '2024-12-26',
    read_time: '8 min read',
    featured_image: 'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&h=600&fit=crop'
  },
  {
    id: 3,
    slug: 'productivity-hacks',
    title: '10 Productivity Hacks That Actually Work',
    excerpt: 'Evidence-based strategies to boost your productivity without burning out.',
    category: 'Productivity',
    author: { full_name: 'Sarah Miller', avatar: '' },
    created_at: '2024-12-25',
    read_time: '5 min read',
    featured_image: 'https://images.unsplash.com/photo-1483058712412-4245e9b90334?w=800&h=600&fit=crop'
  },
  {
    id: 4,
    slug: 'future-of-web3',
    title: 'Web3 in 2024: Beyond the Hype',
    excerpt: 'A realistic look at where Web3 technology stands and its practical applications today.',
    category: 'Technology',
    author: { full_name: 'Alex Johnson', avatar: '' },
    created_at: '2024-12-24',
    read_time: '7 min read',
    featured_image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&h=600&fit=crop'
  },
  {
    id: 5,
    slug: 'marketing-trends-2025',
    title: 'Top Marketing Trends to Watch in 2025',
    excerpt: 'Stay ahead of the curve with these emerging marketing strategies and technologies.',
    category: 'Marketing',
    author: { full_name: 'Lisa Park', avatar: '' },
    created_at: '2024-12-23',
    read_time: '6 min read',
    featured_image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop'
  },
  {
    id: 6,
    slug: 'ux-research-methods',
    title: 'Essential UX Research Methods Every Designer Should Know',
    excerpt: 'A comprehensive guide to user research techniques for better product design.',
    category: 'Design',
    author: { full_name: 'Emma Wilson', avatar: '' },
    created_at: '2024-12-22',
    read_time: '10 min read',
    featured_image: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=600&fit=crop'
  }
];

/**
 * Blog List Page
 * Displays all blog posts with filtering, sorting, and pagination
 */
export default function BlogList() {
  const [sortBy, setSortBy] = useState('latest');
  const [page, setPage] = useState(1);
  const postsPerPage = 6;

  // TODO: Replace with API call
  const posts = samplePosts;
  const totalPages = Math.ceil(posts.length / postsPerPage);

  const handleSortChange = (event) => {
    setSortBy(event.target.value);
    setPage(1); // Reset to first page on sort change
  };

  const handlePageChange = (event, value) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = (query) => {
    console.log('Search query:', query);
    // TODO: Implement search with API
  };

  return (
    <Box>
      {/* Page Header */}
      <Box
        sx={{
          bgcolor: 'grey.50',
          py: { xs: 6, md: 8 },
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Container maxWidth="lg">
          <SectionHeader
            overline="Our Blog"
            title="Articles & Insights"
            subtitle="Discover stories, thinking, and expertise from writers on any topic"
          />
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
        <Grid container spacing={4}>
          {/* Posts Grid */}
          <Grid size={{ xs: 12, lg: 8 }}>
            {/* Sort Controls */}
            <MotionBox
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 4
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Showing {posts.length} articles
              </Typography>
              <Stack direction="row" spacing={2} alignItems="center">
                <Typography variant="body2" color="text.secondary">
                  Sort by:
                </Typography>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <Select
                    value={sortBy}
                    onChange={handleSortChange}
                    sx={{ 
                      bgcolor: 'background.paper',
                      '& .MuiSelect-select': { py: 1 }
                    }}
                  >
                    <MenuItem value="latest">Latest</MenuItem>
                    <MenuItem value="popular">Popular</MenuItem>
                    <MenuItem value="oldest">Oldest</MenuItem>
                  </Select>
                </FormControl>
              </Stack>
            </MotionBox>

            {/* Posts Grid */}
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
            <Sidebar onSearch={handleSearch} />
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
