import { useState, useEffect } from 'react';
import { useParams, Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '@/api/AuthProvider';
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
  Skeleton,
  Alert
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  IconCalendar,
  IconClock,
  IconFolder,
  IconUser,
  IconHeart,
  IconBookmark,
  IconBrandFacebook,
  IconBrandTwitter,
  IconBrandLinkedin,
  IconArrowLeft
} from '@tabler/icons-react';
import CommentSection from '@/components/CommentSection';
import Sidebar from '@/components/Blog/Sidebar';
import SaveToListMenu from '@/components/SaveToListMenu';
import { getPostBySlug, getRelatedPosts, togglePostLike, bookmarkPost } from '@/api/services/postService';
import { getCategoryBySlug } from '@/api/services/categoryService';
import { getImageUrl } from '@/api/utils/imageUrl';
import { recordPostView } from '@/api/services/collectionService';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MotionBox = motion.create(Box);

/**
 * Author Box Component
 */
function AuthorBox({ author }) {
  if (!author) return null;
  
  return (
    <Card variant="outlined" sx={{ mb: 4 }}>
      <CardContent>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3} alignItems="center">
          <Avatar
            src={author.avatar || author.profile?.avatar}
            sx={{ width: 80, height: 80 }}
          >
            {author.full_name?.[0]}
          </Avatar>
          <Box sx={{ textAlign: { xs: 'center', sm: 'left' } }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              {author.full_name}
            </Typography>
            {author.profile?.bio && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {author.profile.bio}
              </Typography>
            )}
            <Button
              component={RouterLink}
              to={`/author/${author.username}`}
              size="small"
              sx={{ mt: 1 }}
            >
              View Profile
            </Button>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}

/**
 * Social Share Component
 */
function SocialShare({ title }) {
  const currentUrl = window.location.href;
  const encodedUrl = encodeURIComponent(currentUrl);
  const encodedTitle = encodeURIComponent(title);
  
  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <Typography variant="body2" color="text.secondary">
        Share:
      </Typography>
      <IconButton
        component="a"
        href={`https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`}
        target="_blank"
        size="small"
      >
        <IconBrandTwitter size={18} />
      </IconButton>
      <IconButton
        component="a"
        href={`https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`}
        target="_blank"
        size="small"
      >
        <IconBrandFacebook size={18} />
      </IconButton>
      <IconButton
        component="a"
        href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`}
        target="_blank"
        size="small"
      >
        <IconBrandLinkedin size={18} />
      </IconButton>
    </Stack>
  );
}

/**
 * Related Posts Component
 */
function RelatedPosts({ posts }) {
  if (!posts || posts.length === 0) return null;
  
  return (
    <Box sx={{ bgcolor: 'grey.50', py: 6 }}>
      <Container maxWidth="lg">
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 4 }}>
          Related Articles
        </Typography>
        <Grid container spacing={3}>
          {posts.map((post) => (
            <Grid size={{ xs: 12, md: 4 }} key={post.id || post.uuid}>
              <Card
                component={RouterLink}
                to={`/post/${post.slug}`}
                sx={{
                  textDecoration: 'none',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  '&:hover': { boxShadow: 4 }
                }}
              >
                <Box
                  component="img"
                  src={getImageUrl(post.featured_image) || 'https://via.placeholder.com/400x200'}
                  alt={post.title}
                  sx={{
                    width: '100%',
                    height: 180,
                    objectFit: 'cover'
                  }}
                />
                <CardContent>
                  <Typography variant="body2" color="primary.main" sx={{ mb: 1 }}>
                    {post.category?.name}
                  </Typography>
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

/**
 * Blog Detail Page
 * Displays a single post with author info, content, and related posts
 */
export default function BlogDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [relatedPosts, setRelatedPosts] = useState([]);
  const [categoryData, setCategoryData] = useState(null);
  
  // User interaction state
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);

  // Fetch post data
  useEffect(() => {
    const fetchPost = async () => {
      if (!slug) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // Fetch main post first (required for subsequent calls)
        const postData = await getPostBySlug(slug);
        setPost(postData);
        setLikesCount(postData.likes_count || 0);
        
        // Fetch related posts and category data IN PARALLEL
        const [relatedResult, categoryResult] = await Promise.all([
          // Related posts (use slug, not uuid)
          postData.slug 
            ? getRelatedPosts(postData.slug, { limit: 3 }).catch(() => ({ posts: [] }))
            : Promise.resolve({ posts: [] }),
          // Category data for sidebar
          postData.category?.slug
            ? getCategoryBySlug(postData.category.slug).catch(() => null)
            : Promise.resolve(null)
        ]);
        
        setRelatedPosts(relatedResult.posts || []);
        setCategoryData(categoryResult);
        
      } catch (err) {
        console.error('Failed to fetch post:', err);
        setError(err.message || 'Failed to load post');
        setPost(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [slug]);

  // Track reading history when post loads
  useEffect(() => {
    if (post?.uuid && isAuthenticated) {
      recordPostView(post.uuid).catch(err => {
        console.error('Failed to record view:', err);
      });
    }
  }, [slug]);

  const handleLike = async () => {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      navigate('/auth/login', { state: { from: { pathname: `/post/${slug}` } } });
      return;
    }
    
    // Optimistic update
    const wasLiked = isLiked;
    setIsLiked(!wasLiked);
    setLikesCount(prev => wasLiked ? prev - 1 : prev + 1);
    
    try {
      await togglePostLike(post.uuid);
    } catch (err) {
      console.error('Failed to toggle like:', err);
      // Rollback on error
      setIsLiked(wasLiked);
      setLikesCount(prev => wasLiked ? prev + 1 : prev - 1);
    }
  };

  const handleBookmark = async () => {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      navigate('/auth/login', { state: { from: { pathname: `/post/${slug}` } } });
      return;
    }
    
    // Optimistic update
    const wasBookmarked = isBookmarked;
    setIsBookmarked(!wasBookmarked);
    
    try {
      await bookmarkPost(post.uuid);
    } catch (err) {
      console.error('Failed to toggle bookmark:', err);
      // Rollback on error
      setIsBookmarked(wasBookmarked);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Skeleton variant="text" width="60%" height={60} />
        <Skeleton variant="rectangular" height={400} sx={{ my: 4, borderRadius: 2 }} />
        <Skeleton variant="text" />
        <Skeleton variant="text" />
        <Skeleton variant="text" width="80%" />
      </Container>
    );
  }

  // Error state
  if (error || !post) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <Alert severity="error" sx={{ mb: 4 }}>
          {error || 'Post not found'}
        </Alert>
        <Button
          component={RouterLink}
          to="/"
          startIcon={<IconArrowLeft />}
          variant="contained"
        >
          Back to Home
        </Button>
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
                    to={`/category/${post.category.slug}`}
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
                  src={getImageUrl(post.featured_image)}
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
                '& h1, & h2, & h3, & h4, & h5, & h6': {
                  fontWeight: 600,
                  mt: 4,
                  mb: 2
                },
                '& h2': {
                  typography: 'h5'
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
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {post.content}
              </ReactMarkdown>
            </Box>

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
                    key={tag.slug || tag.id}
                    label={tag.name}
                    component={RouterLink}
                    to={`/tag/${tag.slug}`}
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
                {isAuthenticated && (
                  <SaveToListMenu
                    postUuid={post.uuid}
                    isBookmarked={isBookmarked}
                    onBookmarkChange={setIsBookmarked}
                  />
                )}
                {!isAuthenticated && (
                  <IconButton
                    onClick={handleBookmark}
                    sx={{
                      border: '1px solid',
                      borderColor: 'grey.300',
                      color: 'text.secondary'
                    }}
                  >
                    <IconBookmark size={18} />
                  </IconButton>
                )}
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
            <Sidebar 
              category={categoryData} 
              activeCategory={post.category?.slug}
            />
          </Grid>
        </Grid>
      </Container>

      {/* Related Posts */}
      <RelatedPosts posts={relatedPosts} />

      {/* Comments */}
      <CommentSection postSlug={post.slug} />
    </Box>
  );
}
