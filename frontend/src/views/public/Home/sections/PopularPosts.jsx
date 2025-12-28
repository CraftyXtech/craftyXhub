import { Box, Container, Grid } from '@mui/material';
import PostCard from '@/components/PostCard';
import SectionHeader from '@/components/SectionHeader';

// Sample data (will be replaced with API data)
const popularPosts = [
  {
    id: 7,
    slug: 'python-best-practices',
    title: 'Python Best Practices Every Developer Should Know',
    excerpt: 'Master Python with these essential coding patterns and practices used by top developers.',
    category: 'Programming',
    author: { full_name: 'David Kim', avatar: '' },
    created_at: '2024-12-20',
    read_time: '10 min read',
    featured_image: 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=600&fit=crop'
  },
  {
    id: 8,
    slug: 'mental-health-tech',
    title: 'Mental Health in the Tech Industry: Breaking the Stigma',
    excerpt: 'How the tech industry is finally addressing mental health and what you can do to support yourself.',
    category: 'Wellness',
    author: { full_name: 'Lisa Park', avatar: '' },
    created_at: '2024-12-18',
    read_time: '8 min read',
    featured_image: 'https://images.unsplash.com/photo-1544027993-37dbfe43562a?w=800&h=600&fit=crop'
  },
  {
    id: 9,
    slug: 'react-vs-vue-2024',
    title: 'React vs Vue in 2024: Which Should You Choose?',
    excerpt: 'An honest comparison of the two most popular frontend frameworks for modern web development.',
    category: 'Technology',
    author: { full_name: 'Mike Brown', avatar: '' },
    created_at: '2024-12-15',
    read_time: '12 min read',
    featured_image: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=600&fit=crop'
  }
];

export default function PopularPosts() {
  return (
    <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'grey.50' }}>
      <Container maxWidth="lg">
        <SectionHeader
          overline="Most Loved"
          title="Popular Articles"
          subtitle="Top picks from our readers this month"
        />

        <Grid container spacing={3}>
          {popularPosts.map((post, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={post.id}>
              <PostCard post={post} animationDelay={index * 0.1} />
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}
