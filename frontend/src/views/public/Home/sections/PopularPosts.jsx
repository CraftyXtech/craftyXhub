import { useState, useEffect } from 'react';
import { Box, Container, Grid, Skeleton, Typography } from '@mui/material';
import PostCard from '@/components/PostCard';
import SectionHeader from '@/components/SectionHeader';
import ArticleCarousel from '@/components/ArticleCarousel';
import { getPopularPosts } from '@/api/services/postService';

export default function PopularPosts() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        // Fetch more posts for carousel scrolling
        const data = await getPopularPosts({ limit: 12 });
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

  // Render individual post card
  const renderPostCard = (post, index) => (
    <PostCard post={post} animationDelay={index * 0.1} />
  );

  return (
    <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'grey.50' }}>
      <Container maxWidth="lg">
        <SectionHeader
          overline="Most Loved"
          title="Popular Articles"
          subtitle="Top picks from our readers this month"
        />

        {loading ? (
          // Loading skeletons - same grid layout
          <Grid container spacing={3}>
            {[...Array(3)].map((_, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={index}>
                <Box>
                  <Skeleton variant="rounded" height={200} sx={{ mb: 2 }} />
                  <Skeleton width="60%" height={20} sx={{ mb: 1 }} />
                  <Skeleton width="90%" height={24} sx={{ mb: 1 }} />
                  <Skeleton width="100%" height={40} />
                </Box>
              </Grid>
            ))}
          </Grid>
        ) : error ? (
          <Typography color="text.secondary" textAlign="center" py={4}>
            {error}
          </Typography>
        ) : posts.length === 0 ? (
          <Typography color="text.secondary" textAlign="center" py={4}>
            No popular posts yet. Check back soon!
          </Typography>
        ) : (
          <ArticleCarousel
            items={posts}
            renderItem={renderPostCard}
            itemsPerView={{ xs: 1, sm: 2, md: 3, lg: 3 }}
            gap={3}
            showArrows={posts.length > 3}
            arrowPosition="outside"
          />
        )}
      </Container>
    </Box>
  );
}

