import { useState, useEffect } from 'react';
import { Box, Container, Grid, Button, Skeleton, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { IconArrowRight } from '@tabler/icons-react';
import PostCard from '@/components/PostCard';
import SectionHeader from '@/components/SectionHeader';
import { getRecentPosts } from '@/api/services/postService';

export default function LatestPosts() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const data = await getRecentPosts(0, 4);
        setPosts(data || []);
      } catch (err) {
        console.error('Failed to fetch latest posts:', err);
        setError('Failed to load posts');
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  return (
    <Box sx={{ py: { xs: 6, md: 10 } }}>
      <Container maxWidth="lg">
        <SectionHeader
          overline="Explore"
          title="Latest Articles"
          subtitle="Discover fresh insights from our community of writers"
        />

        <Grid container spacing={3}>
          {loading ? (
            // Loading skeletons
            [...Array(4)].map((_, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
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
                No posts available yet. Check back soon!
              </Typography>
            </Grid>
          ) : (
            posts.map((post, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 3 }} key={post.uuid || post.id}>
                <PostCard post={post} animationDelay={index * 0.1} />
              </Grid>
            ))
          )}
        </Grid>

        {/* View All Button */}
        <Box sx={{ textAlign: 'center', mt: 5 }}>
          <Button
            component={RouterLink}
            to="/blog"
            variant="outlined"
            endIcon={<IconArrowRight size={18} />}
            sx={{
              borderColor: 'grey.300',
              color: 'text.primary',
              '&:hover': {
                borderColor: 'grey.400',
                bgcolor: 'grey.50'
              }
            }}
          >
            View All Articles
          </Button>
        </Box>
      </Container>
    </Box>
  );
}

