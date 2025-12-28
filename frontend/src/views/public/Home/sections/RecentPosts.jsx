import { Box, Container, Grid } from '@mui/material';
import PostCardOverlay from '@/components/PostCard/PostCardOverlay';
import SectionHeader from '@/components/SectionHeader';

// Sample data (will be replaced with API data)
const recentPosts = [
  {
    id: 1,
    slug: 'ai-revolution-2024',
    title: 'The AI Revolution: What It Means for Content Creators',
    category: 'Technology',
    featured_image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop'
  },
  {
    id: 2,
    slug: 'remote-work-future',
    title: 'Remote Work Is Here to Stay: Best Practices for 2024',
    category: 'Lifestyle',
    featured_image: 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800&h=600&fit=crop'
  }
];

export default function RecentPosts() {
  return (
    <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'grey.50' }}>
      <Container maxWidth="lg">
        <SectionHeader
          overline="Just Published"
          title="Recent Articles"
          subtitle="Fresh perspectives from our community of writers"
        />

        <Grid container spacing={3}>
          {recentPosts.map((post, index) => (
            <Grid size={{ xs: 12, md: 6 }} key={post.id}>
              <PostCardOverlay
                post={post}
                height={350}
                animationDelay={index * 0.1}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}
