import { useState, useEffect } from 'react';
import { Box, Container, Grid, Skeleton, Typography } from '@mui/material';
import PostCard from '@/components/PostCard';
import SectionHeader from '@/components/SectionHeader';
import { getPopularPosts } from '@/api/services/postService';

export default function PopularPosts() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const data = await getPopularPosts({ limit: 3 });
        // API returns { posts: [...] } - extract the array
        setPosts(data?.posts || []);
      } catch (err) {
        console.error('Failed to fetch popular posts:', err);
        setError('Failed to load posts');
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  return (
    <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'grey.50' }}>
      <Container maxWidth="lg">
        <SectionHeader
          overline="Most Loved"
          title="Popular Articles"
          subtitle="Top picks from our readers this month"
        />

        <Grid container spacing={3}>
          {loading ? (
            // Loading skeletons
            [...Array(3)].map((_, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
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
              <Typography color="text.secondary" textAlign="center" py={4}>
                {error}
              </Typography>
            </Grid>
          ) : posts.length === 0 ? (
            <Grid size={{ xs: 12 }}>
              <Typography color="text.secondary" textAlign="center" py={4}>
                No popular posts yet. Check back soon!
              </Typography>
            </Grid>
          ) : (
            posts.map((post, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={post.uuid || post.id}>
                <PostCard post={post} animationDelay={index * 0.1} />
              </Grid>
            ))
          )}
        </Grid>
      </Container>
    </Box>
  );
}

