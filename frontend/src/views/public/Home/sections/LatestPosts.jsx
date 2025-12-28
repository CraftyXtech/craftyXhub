import { Box, Container, Grid, Button } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { IconArrowRight } from '@tabler/icons-react';
import PostCard from '@/components/PostCard';
import SectionHeader from '@/components/SectionHeader';

// Sample data (will be replaced with API data)
const latestPosts = [
  {
    id: 3,
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
    id: 4,
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
    id: 5,
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
    id: 6,
    slug: 'future-of-web3',
    title: 'Web3 in 2024: Beyond the Hype',
    excerpt: 'A realistic look at where Web3 technology stands and its practical applications today.',
    category: 'Technology',
    author: { full_name: 'Alex Johnson', avatar: '' },
    created_at: '2024-12-24',
    read_time: '7 min read',
    featured_image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&h=600&fit=crop'
  }
];

export default function LatestPosts() {
  return (
    <Box sx={{ py: { xs: 6, md: 10 } }}>
      <Container maxWidth="lg">
        <SectionHeader
          overline="Explore"
          title="Latest Articles"
          subtitle="Discover fresh insights from our community of writers"
        />

        <Grid container spacing={3}>
          {latestPosts.map((post, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={post.id}>
              <PostCard post={post} animationDelay={index * 0.1} />
            </Grid>
          ))}
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
