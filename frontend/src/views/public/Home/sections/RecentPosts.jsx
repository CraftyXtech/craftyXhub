import { useState, useEffect } from 'react';
import { Box, Container, Grid, Skeleton } from '@mui/material';
import PostCardOverlay from '@/components/PostCard/PostCardOverlay';
import SectionHeader from '@/components/SectionHeader';
import { getRecentPosts } from '@/api/services/postService';

export default function RecentPosts() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const data = await getRecentPosts({ limit: 2 });
        setPosts(data.posts || []);
      } catch (err) {
        console.error('Failed to fetch recent posts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  // Don't render section if no posts
  if (!loading && posts.length === 0) {
    return null;
  }

  return (
    <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'grey.50' }}>
      <Container maxWidth="lg">
        <SectionHeader
          overline="Just Published"
          title="Recent Articles"
          subtitle="Fresh perspectives from our community of writers"
        />

        <Grid container spacing={3}>
          {loading ? (
            // Loading skeletons
            [...Array(2)].map((_, index) => (
              <Grid size={{ xs: 12, md: 6 }} key={index}>
                <Skeleton variant="rectangular" height={350} sx={{ borderRadius: 2 }} />
              </Grid>
            ))
          ) : (
            posts.map((post, index) => (
              <Grid size={{ xs: 12, md: 6 }} key={post.id || post.uuid}>
                <PostCardOverlay
                  post={post}
                  height={350}
                  animationDelay={index * 0.1}
                />
              </Grid>
            ))
          )}
        </Grid>
      </Container>
    </Box>
  );
}
