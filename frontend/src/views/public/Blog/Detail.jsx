import { useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  Chip,
  Avatar,
  Stack,
  Button,
  Divider,
  IconButton,
  Card,
  CardContent,
  Skeleton
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  IconCalendar,
  IconClock,
  IconFolder,
  IconUser,
  IconHeart,
  IconBookmark,
  IconShare,
  IconBrandFacebook,
  IconBrandTwitter,
  IconBrandLinkedin
} from '@tabler/icons-react';
import CommentSection from '@/components/CommentSection';

const MotionBox = motion.create(Box);

// Sample post data (will be replaced with API data)
const samplePost = {
  id: 1,
  uuid: 'abc123',
  slug: 'design-thinking-guide',
  title: 'Design Thinking: A Practical Guide for Beginners',
  excerpt: 'Learn the fundamentals of design thinking and how to apply it to solve complex problems in your daily work.',
  content: `
    <p>Design thinking is a problem-solving methodology that puts human needs at the center of the development process. It's not just for designers—it's a powerful approach that anyone can use to tackle complex challenges.</p>
    
    <h2>What is Design Thinking?</h2>
    <p>At its core, design thinking is about understanding the people you're designing for, challenging assumptions, and redefining problems to identify alternative strategies and solutions.</p>
    
    <h2>The Five Stages of Design Thinking</h2>
    <p>The design thinking process consists of five key stages:</p>
    <ul>
      <li><strong>Empathize</strong> – Research and understand users' needs</li>
      <li><strong>Define</strong> – State the users' problems and needs</li>
      <li><strong>Ideate</strong> – Challenge assumptions and create ideas</li>
      <li><strong>Prototype</strong> – Start creating solutions</li>
      <li><strong>Test</strong> – Try out your solutions</li>
    </ul>
    
    <blockquote>
      "Design thinking is not just about aesthetics—it's about creating meaningful solutions that truly resonate with people."
    </blockquote>
    
    <h2>Getting Started</h2>
    <p>To begin your design thinking journey, start by observing the world around you. Pay attention to problems people face in their daily lives, and think about how you might solve them in unexpected ways.</p>
    
    <pre><code>// Example: A simple design thinking framework
const designThinking = {
  empathize: () => "Understand user needs",
  define: () => "State the problem",
  ideate: () => "Generate solutions",
  prototype: () => "Build quickly",
  test: () => "Learn and iterate"
};</code></pre>
    
    <p>Remember, design thinking is an iterative process. Don't be afraid to go back to earlier stages as you learn more about the problem you're trying to solve.</p>
  `,
  featured_image: 'https://images.unsplash.com/photo-1558655146-d09347e92766?w=1200&h=600&fit=crop',
  category: { name: 'Design', slug: 'design' },
  author: {
    full_name: 'Emma Wilson',
    username: 'emma_wilson',
    avatar: '',
    bio: 'Design Lead at Creative Studio. Passionate about user experience and design systems.'
  },
  published_at: '2024-12-27T10:00:00Z',
  reading_time: 6,
  tags: [
    { name: 'Design', slug: 'design' },
    { name: 'UX', slug: 'ux' },
    { name: 'Product', slug: 'product' }
  ],
  likes_count: 142
};

// Author Box Component
function AuthorBox({ author }) {
  return (
    <Card variant="outlined" sx={{ mb: 4 }}>
      <CardContent sx={{ display: 'flex', gap: 3, alignItems: 'flex-start' }}>
        <Avatar
          src={author?.avatar}
          sx={{ width: 80, height: 80, bgcolor: 'primary.main' }}
        >
          {author?.full_name?.[0] || 'A'}
        </Avatar>
        <Box>
          <Typography variant="overline" color="text.secondary">
            Written by
          </Typography>
          <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
            {author?.full_name || 'Anonymous'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {author?.bio || 'No bio available.'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

// Social Share Icons
function SocialShare({ title, url }) {
  const shareUrl = url || window.location.href;
  const encodedUrl = encodeURIComponent(shareUrl);
  const encodedTitle = encodeURIComponent(title || '');

  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
        Share:
      </Typography>
      <IconButton
        size="small"
        component="a"
        href={`https://facebook.com/sharer/sharer.php?u=${encodedUrl}`}
        target="_blank"
        rel="noopener noreferrer"
        sx={{ color: '#3b5998' }}
      >
        <IconBrandFacebook size={18} />
      </IconButton>
      <IconButton
        size="small"
        component="a"
        href={`https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`}
        target="_blank"
        rel="noopener noreferrer"
        sx={{ color: '#1da1f2' }}
      >
        <IconBrandTwitter size={18} />
      </IconButton>
      <IconButton
        size="small"
        component="a"
        href={`https://linkedin.com/shareArticle?mini=true&url=${encodedUrl}&title=${encodedTitle}`}
        target="_blank"
        rel="noopener noreferrer"
        sx={{ color: '#0077b5' }}
      >
        <IconBrandLinkedin size={18} />
      </IconButton>
    </Stack>
  );
}

// Related Posts Component
function RelatedPosts({ posts }) {
  return (
    <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: 'grey.100' }}>
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="overline" color="text.secondary">
            You may also like
          </Typography>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            Related Posts
          </Typography>
        </Box>
        <Grid container spacing={3}>
          {posts.map((post) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={post.id}>
              <Card
                component={RouterLink}
                to={`/blog/${post.slug}`}
                sx={{
                  textDecoration: 'none',
                  height: '100%',
                  '&:hover img': { transform: 'scale(1.05)' }
                }}
              >
                <Box sx={{ overflow: 'hidden' }}>
                  <Box
                    component="img"
                    src={post.featured_image}
                    alt={post.title}
                    sx={{
                      width: '100%',
                      height: 200,
                      objectFit: 'cover',
                      transition: 'transform 0.3s'
                    }}
                  />
                </Box>
                <CardContent>
                  <Chip
                    label={post.category?.name || post.category}
                    size="small"
                    sx={{
                      mb: 1,
                      bgcolor: 'transparent',
                      color: 'primary.main',
                      border: '1px solid',
                      borderColor: 'primary.main',
                      fontWeight: 600,
                      fontSize: '0.65rem'
                    }}
                  />
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {post.title}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}

// Related posts sample data
const relatedPosts = [
  {
    id: 2,
    slug: 'ux-research-methods',
    title: 'Essential UX Research Methods Every Designer Should Know',
    category: 'UX',
    featured_image: 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=600&fit=crop'
  },
  {
    id: 3,
    slug: 'building-design-systems',
    title: 'Building Scalable Design Systems from Scratch',
    category: 'Design',
    featured_image: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&h=600&fit=crop'
  },
  {
    id: 4,
    slug: 'user-centered-design',
    title: 'The Principles of User-Centered Design',
    category: 'Product',
    featured_image: 'https://images.unsplash.com/photo-1553484771-371a605b060b?w=800&h=600&fit=crop'
  }
];

export default function BlogDetail() {
  const { slug } = useParams();
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [likesCount, setLikesCount] = useState(samplePost.likes_count);

  // TODO: Replace with actual API call using slug
  const post = samplePost;
  const loading = false;

  const handleLike = () => {
    setIsLiked(!isLiked);
    setLikesCount(prev => isLiked ? prev - 1 : prev + 1);
  };

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Skeleton variant="text" width="60%" height={60} />
        <Skeleton variant="rectangular" height={400} sx={{ my: 4 }} />
        <Skeleton variant="text" />
        <Skeleton variant="text" />
        <Skeleton variant="text" width="80%" />
      </Container>
    );
  }

  return (
    <Box>
      {/* Article Content */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 8 } }}>
        <Grid container spacing={4}>
          {/* Main Content */}
          <Grid size={{ xs: 12, lg: 8 }}>
            {/* Meta Info */}
            <Stack
              direction="row"
              spacing={3}
              sx={{ mb: 3, flexWrap: 'wrap', gap: 1 }}
            >
              {post.published_at && (
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  <IconCalendar size={16} color="#14213D" />
                  <Typography variant="body2" color="text.secondary">
                    {formatDate(post.published_at)}
                  </Typography>
                </Stack>
              )}
              {post.reading_time && (
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  <IconClock size={16} color="#14213D" />
                  <Typography variant="body2" color="text.secondary">
                    {post.reading_time} min read
                  </Typography>
                </Stack>
              )}
              {post.category && (
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  <IconFolder size={16} color="#14213D" />
                  <Typography
                    component={RouterLink}
                    to={`/blog/category/${post.category.slug}`}
                    variant="body2"
                    color="primary.main"
                    sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                  >
                    {post.category.name}
                  </Typography>
                </Stack>
              )}
              {post.author && (
                <Stack direction="row" alignItems="center" spacing={0.5}>
                  <IconUser size={16} color="#14213D" />
                  <Typography variant="body2" color="text.secondary">
                    By{' '}
                    <Typography
                      component={RouterLink}
                      to={`/author/${post.author.username}`}
                      variant="body2"
                      color="primary.main"
                      sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                    >
                      {post.author.full_name}
                    </Typography>
                  </Typography>
                </Stack>
              )}
            </Stack>

            {/* Title */}
            <Typography
              variant="h3"
              sx={{ fontWeight: 700, mb: 4, lineHeight: 1.2 }}
            >
              {post.title}
            </Typography>

            {/* Featured Image */}
            {post.featured_image && (
              <MotionBox
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                sx={{ mb: 4 }}
              >
                <Box
                  component="img"
                  src={post.featured_image}
                  alt={post.title}
                  sx={{
                    width: '100%',
                    borderRadius: 2,
                    maxHeight: 500,
                    objectFit: 'cover'
                  }}
                />
              </MotionBox>
            )}

            {/* Excerpt */}
            {post.excerpt && (
              <Typography
                variant="h6"
                sx={{
                  mb: 4,
                  fontWeight: 400,
                  fontStyle: 'italic',
                  color: 'text.secondary'
                }}
              >
                {post.excerpt}
              </Typography>
            )}

            {/* Content */}
            <Box
              sx={{
                mb: 4,
                '& h2': {
                  typography: 'h5',
                  fontWeight: 600,
                  mt: 4,
                  mb: 2
                },
                '& p': {
                  typography: 'body1',
                  mb: 2,
                  lineHeight: 1.8
                },
                '& ul, & ol': {
                  pl: 3,
                  mb: 2,
                  '& li': { mb: 1 }
                },
                '& blockquote': {
                  borderLeft: 4,
                  borderColor: 'primary.main',
                  pl: 3,
                  py: 2,
                  my: 3,
                  bgcolor: 'grey.50',
                  fontStyle: 'italic',
                  '& p': { mb: 0 }
                },
                '& pre': {
                  bgcolor: '#1a1a1a',
                  p: 3,
                  borderRadius: 2,
                  overflow: 'auto',
                  my: 3
                },
                '& pre code': {
                  fontFamily: '"JetBrains Mono Variable", monospace',
                  color: '#e0e0e0',
                  fontSize: '0.875rem',
                  bgcolor: 'transparent',
                  p: 0,
                  borderRadius: 0,
                  display: 'block',
                  whiteSpace: 'pre'
                },
                '& :not(pre) > code': {
                  fontFamily: '"JetBrains Mono Variable", monospace',
                  bgcolor: 'grey.100',
                  px: 0.5,
                  py: 0.25,
                  borderRadius: 0.5,
                  fontSize: '0.875rem'
                }
              }}
              dangerouslySetInnerHTML={{ __html: post.content }}
            />

            <Divider sx={{ my: 4 }} />

            {/* Tags & Actions */}
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              justifyContent="space-between"
              alignItems={{ xs: 'flex-start', sm: 'center' }}
              spacing={2}
              sx={{ mb: 4 }}
            >
              {/* Tags */}
              <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                {post.tags?.map((tag) => (
                  <Chip
                    key={tag.slug}
                    label={tag.name}
                    component={RouterLink}
                    to={`/blog/tag/${tag.slug}`}
                    clickable
                    size="small"
                    variant="outlined"
                    sx={{ borderColor: 'grey.300' }}
                  />
                ))}
              </Stack>

              {/* Actions */}
              <Stack direction="row" spacing={1} alignItems="center">
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<IconHeart size={18} fill={isLiked ? 'currentColor' : 'none'} />}
                  onClick={handleLike}
                  sx={{
                    borderColor: isLiked ? 'error.main' : 'grey.300',
                    color: isLiked ? 'error.main' : 'text.primary'
                  }}
                >
                  {likesCount}
                </Button>
                <IconButton
                  onClick={handleBookmark}
                  sx={{
                    border: '1px solid',
                    borderColor: isBookmarked ? 'primary.main' : 'grey.300',
                    color: isBookmarked ? 'primary.main' : 'text.secondary'
                  }}
                >
                  <IconBookmark size={18} fill={isBookmarked ? 'currentColor' : 'none'} />
                </IconButton>
              </Stack>
            </Stack>

            {/* Author Box */}
            <AuthorBox author={post.author} />

            {/* Social Share */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 4 }}>
              <SocialShare title={post.title} />
            </Box>
          </Grid>

          {/* Sidebar */}
          <Grid size={{ xs: 12, lg: 4 }}>
            {/* Sidebar content can be added here */}
            {/* Search, Categories, Popular Posts, etc. */}
          </Grid>
        </Grid>
      </Container>

      {/* Related Posts */}
      <RelatedPosts posts={relatedPosts} />

      {/* Comments */}
      <CommentSection postUuid={post.uuid} />
    </Box>
  );
}
