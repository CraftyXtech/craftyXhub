import { useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  Avatar,
  Stack,
  IconButton,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  IconBrandTwitter,
  IconBrandLinkedin,
  IconWorld,
  IconArticle,
  IconHeart
} from '@tabler/icons-react';
import PostCard from '@/components/PostCard';
import Breadcrumb from '@/components/Breadcrumb';

const MotionBox = motion.create(Box);
const MotionCard = motion.create(Card);

// Sample author data (will be replaced with API data)
const authorData = {
  emma_wilson: {
    username: 'emma_wilson',
    full_name: 'Emma Wilson',
    avatar: '',
    bio: 'Design Lead at Creative Studio. Passionate about user experience and design systems. With over 10 years of experience in product design, I help teams build beautiful, functional products.',
    location: 'San Francisco, CA',
    website: 'https://emmawilson.design',
    twitter: 'emmawilson',
    linkedin: 'emmawilson',
    stats: {
      posts: 24,
      likes: 1520
    }
  },
  james_chen: {
    username: 'james_chen',
    full_name: 'James Chen',
    avatar: '',
    bio: 'Venture Partner at TechCapital. Former founder with 2 successful exits. Writing about startups, fundraising, and building teams.',
    location: 'New York, NY',
    website: 'https://jameschen.vc',
    twitter: 'jameschen',
    linkedin: 'jameschen',
    stats: {
      posts: 18,
      likes: 980
    }
  }
};

// Sample posts data (will be replaced with API data)
const authorPosts = [
  {
    id: 1,
    slug: 'design-thinking-guide',
    title: 'Design Thinking: A Practical Guide for Beginners',
    excerpt: 'Learn the fundamentals of design thinking and how to apply it to solve complex problems.',
    category: 'Design',
    author: { full_name: 'Emma Wilson', username: 'emma_wilson' },
    created_at: '2024-12-27',
    read_time: '6 min read',
    featured_image: 'https://images.unsplash.com/photo-1558655146-d09347e92766?w=800&h=600&fit=crop'
  },
  {
    id: 2,
    slug: 'ux-research-methods',
    title: 'Essential UX Research Methods Every Designer Should Know',
    excerpt: 'A comprehensive guide to user research techniques for better product design.',
    category: 'Design',
    author: { full_name: 'Emma Wilson', username: 'emma_wilson' },
    created_at: '2024-12-22',
    read_time: '10 min read',
    featured_image: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=600&fit=crop'
  },
  {
    id: 3,
    slug: 'building-design-systems',
    title: 'Building Scalable Design Systems from Scratch',
    excerpt: 'How to create and maintain a design system that grows with your product.',
    category: 'Design',
    author: { full_name: 'Emma Wilson', username: 'emma_wilson' },
    created_at: '2024-12-20',
    read_time: '8 min read',
    featured_image: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&h=600&fit=crop'
  }
];

/**
 * Author Page
 * Displays author profile and their published posts
 */
export default function Author() {
  const { username } = useParams();
  const [showAllPosts, setShowAllPosts] = useState(false);

  // TODO: Replace with API call
  const author = authorData[username] || {
    username,
    full_name: username,
    bio: 'Author not found.',
    stats: { posts: 0, likes: 0 }
  };

  const posts = authorPosts; // Filter by author in real implementation
  const displayedPosts = showAllPosts ? posts : posts.slice(0, 6);

  const breadcrumbItems = [
    { label: 'Blog', to: '/blog' },
    { label: author.full_name }
  ];

  return (
    <Box>
      {/* Author Header */}
      <Box
        sx={{
          bgcolor: 'grey.50',
          py: { xs: 6, md: 8 },
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Container maxWidth="lg">
          <Breadcrumb items={breadcrumbItems} />

          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Grid container spacing={4} alignItems="center">
              {/* Avatar */}
              <Grid size={{ xs: 12, md: 'auto' }}>
                <Avatar
                  src={author.avatar}
                  sx={{
                    width: 120,
                    height: 120,
                    bgcolor: 'primary.main',
                    fontSize: '3rem',
                    mx: { xs: 'auto', md: 0 }
                  }}
                >
                  {author.full_name?.[0] || 'A'}
                </Avatar>
              </Grid>

              {/* Info */}
              <Grid size={{ xs: 12, md: true }}>
                <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                    {author.full_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    @{author.username}
                    {author.location && ` · ${author.location}`}
                  </Typography>
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    sx={{ mb: 3, maxWidth: 600 }}
                  >
                    {author.bio}
                  </Typography>

                  {/* Stats & Social */}
                  <Stack
                    direction="row"
                    spacing={4}
                    alignItems="center"
                    justifyContent={{ xs: 'center', md: 'flex-start' }}
                  >
                    {/* Stats */}
                    <Stack direction="row" spacing={3}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <IconArticle size={18} />
                        <Typography variant="body2">
                          <strong>{author.stats.posts}</strong> Posts
                        </Typography>
                      </Stack>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <IconHeart size={18} />
                        <Typography variant="body2">
                          <strong>{author.stats.likes}</strong> Likes
                        </Typography>
                      </Stack>
                    </Stack>

                    <Divider orientation="vertical" flexItem />

                    {/* Social Links */}
                    <Stack direction="row" spacing={1}>
                      {author.website && (
                        <IconButton
                          component="a"
                          href={author.website}
                          target="_blank"
                          size="small"
                          sx={{ color: 'text.secondary' }}
                        >
                          <IconWorld size={20} />
                        </IconButton>
                      )}
                      {author.twitter && (
                        <IconButton
                          component="a"
                          href={`https://twitter.com/${author.twitter}`}
                          target="_blank"
                          size="small"
                          sx={{ color: '#1DA1F2' }}
                        >
                          <IconBrandTwitter size={20} />
                        </IconButton>
                      )}
                      {author.linkedin && (
                        <IconButton
                          component="a"
                          href={`https://linkedin.com/in/${author.linkedin}`}
                          target="_blank"
                          size="small"
                          sx={{ color: '#0077B5' }}
                        >
                          <IconBrandLinkedin size={20} />
                        </IconButton>
                      )}
                    </Stack>
                  </Stack>
                </Box>
              </Grid>
            </Grid>
          </MotionBox>
        </Container>
      </Box>

      {/* Author's Posts */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 4 }}>
          Articles by {author.full_name}
        </Typography>

        <Grid container spacing={3}>
          {displayedPosts.map((post, index) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={post.id}>
              <PostCard post={post} animationDelay={index * 0.05} />
            </Grid>
          ))}
        </Grid>

        {/* Show More */}
        {posts.length > 6 && !showAllPosts && (
          <Box sx={{ textAlign: 'center', mt: 5 }}>
            <Typography
              variant="body2"
              color="primary.main"
              sx={{
                cursor: 'pointer',
                fontWeight: 600,
                '&:hover': { textDecoration: 'underline' }
              }}
              onClick={() => setShowAllPosts(true)}
            >
              View all {posts.length} articles →
            </Typography>
          </Box>
        )}
      </Container>
    </Box>
  );
}
