import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  FormControl,
  Select,
  MenuItem,
  Stack,
  Skeleton
} from '@mui/material';
import { motion } from 'framer-motion';
import PostCard from '@/components/PostCard';
import Sidebar from '@/components/Blog/Sidebar';
import Pagination from '@/components/Pagination';
import SectionHeader from '@/components/SectionHeader';
import { getPosts } from '@/api/services/postService';

const MotionBox = motion.create(Box);

/**
 * Blog List Page
 * Displays all blog posts with filtering, sorting, and pagination
 */
export default function BlogList() {
  const [sortBy, setSortBy] = useState('latest');
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [posts, setPosts] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const postsPerPage = 6;

  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        skip: (page - 1) * postsPerPage,
        limit: postsPerPage,
        published: true
      };

      // Add search if provided
      if (search) {
        params.search = search;
      }

      const response = await getPosts(
        params.skip,
        params.limit,
        params.published
      );
      
      setPosts(response.posts || response.items || response || []);
      setTotal(response.total || (Array.isArray(response) ? response.length : 0));
    } catch (err) {
      console.error('Failed to fetch posts:', err);
      setError('Failed to load posts');
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const totalPages = Math.ceil(total / postsPerPage) || 1;

  const handleSortChange = (event) => {
    setSortBy(event.target.value);
    setPage(1); // Reset to first page on sort change
  };

  const handlePageChange = (event, value) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = (query) => {
    setSearch(query);
    setPage(1); // Reset to first page on search
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
                {loading ? 'Loading...' : `Showing ${posts.length} of ${total} articles`}
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
              {loading ? (
                // Loading skeletons
                [...Array(6)].map((_, index) => (
                  <Grid size={{ xs: 12, sm: 6 }} key={index}>
                    <Box>
                      <Skeleton variant="rounded" height={200} sx={{ mb: 2 }} />
                      <Skeleton width="60%" height={20} sx={{ mb: 1 }} />
                      <Skeleton width="90%" height={24} sx={{ mb: 1 }} />
                      <Skeleton width="100%" height={40} />
                    </Box>
                  </Grid>
                ))
              ) : error ? (
                <Grid size={{ xs: 12 }}>
                  <Typography color="error" textAlign="center" py={4}>
                    {error}
                  </Typography>
                </Grid>
              ) : posts.length === 0 ? (
                <Grid size={{ xs: 12 }}>
                  <Typography color="text.secondary" textAlign="center" py={4}>
                    {search ? `No articles found for "${search}"` : 'No articles available yet.'}
                  </Typography>
                </Grid>
              ) : (
                posts.map((post, index) => (
                  <Grid size={{ xs: 12, sm: 6 }} key={post.uuid || post.id}>
                    <PostCard post={post} animationDelay={index * 0.05} />
                  </Grid>
                ))
              )}
            </Grid>

            {/* Pagination */}
            {!loading && totalPages > 1 && (
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

