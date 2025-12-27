import { Box, Container, Typography, Card, CardContent, CardMedia, Chip, Stack, Avatar, Grid } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';

const MotionCard = motion.create(Card);

// Sample featured posts data
const featuredPosts = [
  {
    id: 1,
    title: 'The Future of Creative Writing in the Age of AI',
    excerpt: 'Exploring how artificial intelligence is reshaping the landscape of content creation and what it means for writers.',
    image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop',
    category: 'Technology',
    author: { name: 'Sarah Chen', avatar: '' },
    readTime: '8 min read',
    date: 'Dec 25, 2024'
  },
  {
    id: 2,
    title: 'Building a Personal Brand Through Authentic Storytelling',
    excerpt: 'Learn how to leverage your unique voice and experiences to create content that resonates with your audience.',
    image: 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&h=600&fit=crop',
    category: 'Marketing',
    author: { name: 'James Wilson', avatar: '' },
    readTime: '6 min read',
    date: 'Dec 24, 2024'
  },
  {
    id: 3,
    title: 'Minimalism in Design: Less is More',
    excerpt: 'Why the most impactful designs often embrace simplicity and how to apply these principles to your work.',
    image: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&h=600&fit=crop',
    category: 'Design',
    author: { name: 'Emma Taylor', avatar: '' },
    readTime: '5 min read',
    date: 'Dec 23, 2024'
  }
];

export default function FeaturedPosts() {
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
          {featuredPosts.map((post, index) => (
            <Grid size={{ xs: 12, md: 4 }} key={post.id}>
              <MotionCard
                component={RouterLink}
                to={`/blog/${post.id}`}
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
                  image={post.image}
                  alt={post.title}
                  sx={{
                    transition: 'transform 0.3s ease',
                    '&:hover': { transform: 'scale(1.05)' }
                  }}
                />
                <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                  <Chip
                    label={post.category}
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
                      src={post.author.avatar}
                      sx={{ width: 32, height: 32, bgcolor: 'grey.400' }}
                    >
                      {post.author.name[0]}
                    </Avatar>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="caption" fontWeight={600}>
                        {post.author.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {post.date} · {post.readTime}
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </MotionCard>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}
