import { useState, useEffect } from 'react';
import { Box, Container, Typography, Card, CardContent, CardMedia, Chip, Stack, Avatar, Grid, Skeleton } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import { getFeaturedPosts } from '@/api/services/postService';
import { getImageUrl } from '@/api/utils/imageUrl';

const MotionCard = motion.create(Card);

export default function FeaturedPosts() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const data = await getFeaturedPosts({ limit: 3 });
        setPosts(data.posts || []);
      } catch (err) {
        console.error('Failed to fetch featured posts:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, []);

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Don't render section if no posts
  if (!loading && posts.length === 0) {
    return null;
  }

  return (
    <Box sx={{ py: { xs: 8, md: 12 }, bgcolor: 'grey.50' }}>
      <Container maxWidth="lg">
        {/* Section Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography
            variant="overline"
            sx={{ color: 'text.secondary', fontWeight: 600 }}
          >
            Featured Articles
          </Typography>
          <Typography variant="h3" sx={{ mt: 1, fontWeight: 700 }}>
            Latest from our writers
          </Typography>
          <Typography
            variant="body1"
            sx={{ mt: 2, color: 'text.secondary', maxWidth: 600, mx: 'auto' }}
          >
            Discover thoughtful perspectives and insights from our community of creators
          </Typography>
        </Box>

        {/* Posts Grid */}
        <Grid container spacing={4}>
          {loading ? (
            // Loading skeletons
            [...Array(3)].map((_, index) => (
              <Grid size={{ xs: 12, md: 4 }} key={index}>
                <Card sx={{ height: '100%' }}>
                  <Skeleton variant="rectangular" height={200} />
                  <CardContent>
                    <Skeleton variant="text" width={60} height={24} sx={{ mb: 2 }} />
                    <Skeleton variant="text" height={32} />
                    <Skeleton variant="text" width="90%" />
                    <Skeleton variant="text" width="80%" sx={{ mb: 3 }} />
                    <Stack direction="row" spacing={1.5} alignItems="center">
                      <Skeleton variant="circular" width={32} height={32} />
                      <Box>
                        <Skeleton variant="text" width={80} />
                        <Skeleton variant="text" width={100} />
                      </Box>
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))
          ) : (
            posts.map((post, index) => (
              <Grid size={{ xs: 12, md: 4 }} key={post.id || post.uuid}>
                <MotionCard
                  component={RouterLink}
                  to={`/post/${post.slug}`}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  whileHover={{ y: -8 }}
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    textDecoration: 'none',
                    cursor: 'pointer',
                    overflow: 'hidden'
                  }}
                >
                  <CardMedia
                    component="img"
                    height="200"
                    image={getImageUrl(post.featured_image) || '/placeholder.jpg'}
                    alt={post.title}
                    sx={{
                      transition: 'transform 0.3s ease',
                      '&:hover': { transform: 'scale(1.05)' }
                    }}
                  />
                  <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                    <Chip
                      label={post.category?.name || 'General'}
                      size="small"
                      sx={{
                        alignSelf: 'flex-start',
                        mb: 2,
                        bgcolor: 'grey.100',
                        color: 'text.primary',
                        fontWeight: 600
                      }}
                    />
                    <Typography variant="h6" fontWeight={600} sx={{ mb: 1.5 }}>
                      {post.title}
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 3, flexGrow: 1 }}
                    >
                      {post.excerpt}
                    </Typography>
                    <Stack direction="row" alignItems="center" spacing={1.5}>
                      <Avatar
                        src={post.author?.profile?.avatar}
                        sx={{ width: 32, height: 32, bgcolor: 'grey.400' }}
                      >
                        {post.author?.full_name?.[0] || 'A'}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="caption" fontWeight={600}>
                          {post.author?.full_name || 'Anonymous'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {formatDate(post.published_at)} · {post.reading_time || 5} min read
                        </Typography>
                      </Box>
                    </Stack>
                  </CardContent>
                </MotionCard>
              </Grid>
            ))
          )}
        </Grid>
      </Container>
    </Box>
  );
}
