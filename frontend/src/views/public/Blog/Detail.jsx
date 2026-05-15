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
  IconBrandX,
  IconBrandLinkedin,
  IconBrandReddit,
  IconBrandWhatsapp,
  IconArrowLeft
} from '@tabler/icons-react';
import CommentSection from '@/components/CommentSection';
import Sidebar from '@/components/Blog/Sidebar';
import SaveToListMenu from '@/components/SaveToListMenu';
import ArticleCarousel from '@/components/ArticleCarousel';
import PostCard from '@/components/PostCard';
import { getPostBySlug, getRelatedPosts, togglePostLike, bookmarkPost, recordPublicView } from '@/api/services/postService';
import { getCategoryBySlug } from '@/api/services/categoryService';
import { getImageUrl } from '@/api/utils/imageUrl';
import { recordPostView } from '@/api/services/collectionService';
import { getApiBaseUrl } from '@/api/axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { Helmet } from 'react-helmet-async';
import useSWR from 'swr';

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
function SocialShare({ title, slug, uuid, shareVersion }) {
  const shareBaseUrl =
    import.meta.env.VITE_SHARE_BASE_URL ||
    (typeof window !== 'undefined' ? window.location.origin : getApiBaseUrl());
  const shareUrlPrefix =
    import.meta.env.VITE_SHARE_URL_PREFIX ||
    `${shareBaseUrl.replace(/\/$/, '')}/s`;
  const shareTarget = `${shareUrlPrefix.replace(/\/$/, '')}/${encodeURIComponent(uuid || slug)}`;
  const normalizedVersion = shareVersion
    ? new Date(shareVersion).getTime() || String(shareVersion).trim()
    : '';
  const shareUrl = normalizedVersion
    ? `${shareTarget}?v=${encodeURIComponent(normalizedVersion)}`
    : shareTarget;
  const encodedUrl = encodeURIComponent(shareUrl);
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
        rel="noopener noreferrer"
        aria-label="Share on X"
      >
        <IconBrandX size={18} />
      </IconButton>
      <IconButton
        component="a"
        href={`https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`}
        target="_blank"
        size="small"
        rel="noopener noreferrer"
        aria-label="Share on Facebook"
      >
        <IconBrandFacebook size={18} />
      </IconButton>
      <IconButton
        component="a"
        href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`}
        target="_blank"
        size="small"
        rel="noopener noreferrer"
        aria-label="Share on LinkedIn"
      >
        <IconBrandLinkedin size={18} />
      </IconButton>
      <IconButton
        component="a"
        href={`https://api.whatsapp.com/send?text=${encodedTitle}%20${encodedUrl}`}
        target="_blank"
        size="small"
        rel="noopener noreferrer"
        aria-label="Share on WhatsApp"
      >
        <IconBrandWhatsapp size={18} />
      </IconButton>
      <IconButton
        component="a"
        href={`https://www.reddit.com/submit?url=${encodedUrl}&title=${encodedTitle}`}
        target="_blank"
        size="small"
        rel="noopener noreferrer"
        aria-label="Share on Reddit"
      >
        <IconBrandReddit size={18} />
      </IconButton>
    </Stack>
  );
}

/**
 * Related Posts Component
 */
function RelatedPosts({ posts }) {
  const validPosts = (posts || []).filter((relatedPost) => relatedPost?.slug || relatedPost?.uuid);

  if (validPosts.length === 0) return null;
  
  return (
    <Box sx={{ bgcolor: 'grey.50', pt: 4, pb: 6 }}>
      <Container maxWidth="lg">
        <Typography variant="h5" sx={{ fontWeight: 600, mb: 4 }}>
          Related Articles
        </Typography>
        <ArticleCarousel
          items={validPosts}
          renderItem={(relatedPost) => <PostCard post={relatedPost} />}
          itemsPerView={{ xs: 1, sm: 2, md: 3, lg: 3 }}
          gap={3}
          showArrows={validPosts.length > 3}
          arrowPosition="outside"
        />
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
  
  // User interaction state
  const [isLiked, setIsLiked] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);

  // Use SWR for main post
  const { 
    data: post, 
    error, 
    isLoading: loading 
  } = useSWR(
    slug ? `/api/v1/posts/slug/${slug}` : null,
    () => getPostBySlug(slug),
    { revalidateOnFocus: false }
  );

  // Sync likes state when post data changes
  useEffect(() => {
    if (post) {
      setLikesCount(post.likes_count || 0);
    }
  }, [post]);

  // Use SWR for related posts
  const { data: relatedData } = useSWR(
    post?.slug ? `/api/v1/posts/${post.slug}/related` : null,
    () => getRelatedPosts(post.slug, { limit: 12 }),
    { revalidateOnFocus: false }
  );
  
  const relatedPosts = (relatedData?.posts || []).filter(
    (relatedPost) => relatedPost?.slug !== post?.slug && (relatedPost?.slug || relatedPost?.uuid)
  );

  // Use SWR for category data
  const { data: categoryData } = useSWR(
    post?.category?.slug ? `/api/v1/categories/slug/${post.category.slug}` : null,
    () => getCategoryBySlug(post.category.slug),
    { revalidateOnFocus: false }
  );

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
  }, [slug]);

  // Record public view count (works for ALL visitors, IP-deduplicated on backend)
  useEffect(() => {
    if (post?.uuid) {
      recordPublicView(post.uuid);
    }
  }, [post?.uuid]);

  // Track reading history for authenticated users
  useEffect(() => {
    if (post?.uuid && isAuthenticated) {
      recordPostView(post.uuid).catch(err => {
        console.error('Failed to record view:', err);
      });
    }
  }, [post?.uuid, isAuthenticated]);

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
          {error?.message || (typeof error === 'string' ? error : 'Post not found')}
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

  const publishedAtMs = post.published_at ? new Date(post.published_at).getTime() : null;
  const updatedAtMs = post.updated_at ? new Date(post.updated_at).getTime() : null;
  const showUpdatedAt = Boolean(
    updatedAtMs && (!publishedAtMs || updatedAtMs - publishedAtMs > 60_000)
  );

  // Prepare SEO Data
  const seoTitle = post.meta_title || post.title;
  const seoDescription = post.meta_description || post.excerpt || '';
  const postUrl = typeof window !== 'undefined' ? window.location.href : '';
  const imageUrl = post.featured_image ? getImageUrl(post.featured_image) : '';
  const publishedTime = post.published_at ? new Date(post.published_at).toISOString() : '';
  const modifiedTime = post.updated_at ? new Date(post.updated_at).toISOString() : '';
  
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "mainEntityOfPage": {
      "@type": "WebPage",
      "@id": postUrl
    },
    "headline": seoTitle,
    "description": seoDescription,
    "image": imageUrl ? [imageUrl] : [],
    "datePublished": publishedTime,
    "dateModified": modifiedTime || publishedTime,
    "author": {
      "@type": "Person",
      "name": post.author?.full_name || post.author?.username || 'CraftyXHub Author',
      "url": `${typeof window !== 'undefined' ? window.location.origin : ''}/author/${post.author?.username}`
    },
    "publisher": {
      "@type": "Organization",
      "name": "CraftyXHub",
      "logo": {
        "@type": "ImageObject",
        "url": `${typeof window !== 'undefined' ? window.location.origin : ''}/logo.png`
      }
    }
  };

  return (
    <Box>
      <Helmet>
        <title>{seoTitle} | CraftyXHub</title>
        <meta name="description" content={seoDescription} />
        
        {/* Open Graph */}
        <meta property="og:title" content={seoTitle} />
        <meta property="og:description" content={seoDescription} />
        <meta property="og:url" content={postUrl} />
        {imageUrl && <meta property="og:image" content={imageUrl} />}
        <meta property="og:type" content="article" />
        <meta property="og:site_name" content="CraftyXHub" />
        {publishedTime && <meta property="article:published_time" content={publishedTime} />}
        {modifiedTime && <meta property="article:modified_time" content={modifiedTime} />}
        {post.author && <meta property="article:author" content={post.author.full_name} />}
        {post.category && <meta property="article:section" content={post.category.name} />}
        {post.tags?.map(tag => (
          <meta property="article:tag" content={tag.name} key={tag.slug} />
        ))}
        
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={seoTitle} />
        <meta name="twitter:description" content={seoDescription} />
        {imageUrl && <meta name="twitter:image" content={imageUrl} />}
        
        {/* JSON-LD Structured Data */}
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
      </Helmet>

      {/* Article Content */}
      <Container maxWidth="lg" sx={{ pt: { xs: 4, md: 8 }, pb: 0 }}>
        <Grid container spacing={4}>
          {/* Main Content */}
          <Grid size={{ xs: 12, lg: 8 }}>
            {/* Meta Info */}
            <Box sx={{ mb: 3 }}>
              {/* Mobile Layout */}
              <Grid container spacing={1.5} sx={{ display: { xs: 'flex', md: 'none' } }}>
                <Grid size={{ xs: 12 }}>
                  <Stack direction="row" alignItems="center" spacing={2} flexWrap="wrap" useFlexGap sx={{ rowGap: 1 }}>
                    {post.category && (
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <IconFolder size={16} color="#666" />
                        <Typography
                          component={RouterLink}
                          to={`/category/${post.category.slug}`}
                          variant="body2"
                          color="primary.main"
                          fontWeight={600}
                          sx={{ textDecoration: 'none' }}
                        >
                          {post.category.name}
                        </Typography>
                      </Stack>
                    )}
                    {(showUpdatedAt || post.published_at) && (
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <IconCalendar size={16} color="#666" />
                        <Typography variant="caption" color="text.secondary">
                          {showUpdatedAt
                            ? `Updated ${formatDate(post.updated_at)}`
                            : formatDate(post.published_at)}
                        </Typography>
                      </Stack>
                    )}
                  </Stack>
                </Grid>
                {post.reading_time && (
                  <Grid size={{ xs: 6 }}>
                    <Stack direction="row" alignItems="center" spacing={0.5}>
                      <IconClock size={16} color="#666" />
                      <Typography variant="caption" color="text.secondary">
                        {post.reading_time} min read
                      </Typography>
                    </Stack>
                  </Grid>
                )}
              </Grid>

              {/* Desktop Layout */}
              <Stack
                direction="row"
                spacing={3}
                sx={{ display: { xs: 'none', md: 'flex' }, flexWrap: 'wrap', gap: 1 }}
              >
                {(showUpdatedAt || post.published_at) && (
                  <Stack direction="row" alignItems="center" spacing={0.5}>
                    <IconCalendar size={16} color="#14213D" />
                    <Typography variant="body2" color="text.secondary">
                      {showUpdatedAt
                        ? `Updated ${formatDate(post.updated_at)}`
                        : `Published ${formatDate(post.published_at)}`}
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
              </Stack>
            </Box>

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
                // Enhanced ordered list styling (industry standard)
                '& ol': {
                  listStyle: 'none',
                  counterReset: 'list-counter',
                  pl: 0,
                  mb: 3,
                },
                '& ol > li': {
                  counterIncrement: 'list-counter',
                  position: 'relative',
                  pl: 4,
                  mb: 2.5,
                  '&::before': {
                    content: 'counter(list-counter) "."',
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    fontWeight: 700,
                    color: 'text.primary',
                  },
                },
                // Bold headings within list items get block display
                '& ol > li > strong:first-child, & ol > li > p:first-child > strong:first-child': {
                  display: 'block',
                  mb: 0.5,
                  fontWeight: 600,
                },
                // Description text following the bold heading - proper indentation
                '& ol > li > p': {
                  mb: 1,
                  pl: 0, // Already indented by parent li padding
                },
                // Unordered lists
                '& ul': {
                  listStyle: 'none',
                  pl: 0,
                  mb: 3,
                },
                '& ul > li': {
                  position: 'relative',
                  pl: 3,
                  mb: 1.5,
                  '&::before': {
                    content: '"•"',
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    fontWeight: 'bold',
                    color: 'primary.main',
                  },
                },
                // Nested lists
                '& ol ol, & ol ul, & ul ol, & ul ul': {
                  mt: 1.5,
                  mb: 1.5,
                },
                '& blockquote': {
                  borderLeft: '4px solid',
                  borderColor: 'primary.main',
                  pl: 3,
                  py: 2,
                  px: 3,
                  my: 3,
                  mx: 0,
                  bgcolor: 'action.hover',
                  borderRadius: '0 8px 8px 0',
                  fontStyle: 'italic',
                  color: 'text.secondary',
                  '& p': { mb: 0 },
                  '& p:first-of-type::before': {
                    content: '"\\201C"',
                    fontSize: '2rem',
                    lineHeight: 0,
                    verticalAlign: '-0.4em',
                    mr: 0.5,
                    color: 'primary.main',
                    fontWeight: 700,
                  },
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
                },
              '& img': {
                  maxWidth: '100%',
                  height: 'auto',
                  borderRadius: 1,
                  my: 2,
                  display: 'block',
                },
                '& a': {
                  color: 'primary.main',
                  textDecoration: 'underline',
                  textDecorationColor: 'rgba(25, 118, 210, 0.4)',
                  textUnderlineOffset: '2px',
                  fontWeight: 500,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    textDecorationColor: 'primary.main',
                    color: 'primary.dark',
                  },
                },
              }}
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={{
                  img: ({ node, ...props }) => (
                    <Box
                      component="img"
                      {...props}
                      sx={{
                        maxWidth: '100%',
                        height: 'auto',
                        borderRadius: 1,
                        my: 2,
                        display: 'block',
                      }}
                    />
                  ),
                  a: ({ node, href, children, ...props }) => (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      {...props}
                    >
                      {children}
                    </a>
                  ),
                }}
                urlTransform={(url) => url}
              >
                {post.content}
              </ReactMarkdown>
            </Box>

            <Divider sx={{ my: 4 }} />

            {/* Tags Only */}
            {post.tags?.length > 0 && (
              <Stack
                direction="row"
                spacing={1}
                flexWrap="wrap"
                gap={1}
                sx={{ mb: 4 }}
              >
                {post.tags.map((tag) => (
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
            )}

            {/* Author & Actions Box */}
            <Card variant="outlined" sx={{ mb: 4, borderRadius: 2 }}>
              <CardContent sx={{ py: 2, px: { xs: 2, sm: 3 }, '&:last-child': { pb: 2 } }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2} sx={{ width: '100%' }}>
                  {post.author && (
                    <Stack 
                      direction="row" 
                      spacing={1.5} 
                      alignItems="center"
                      component={RouterLink}
                      to={`/author/${post.author.username}`}
                      sx={{ textDecoration: 'none', color: 'inherit', '&:hover': { opacity: 0.8 } }}
                    >
                      <Avatar 
                        sx={{ width: 40, height: 40, bgcolor: 'primary.main', color: 'white' }}
                      >
                        <IconUser size={24} />
                      </Avatar>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {post.author.full_name}
                      </Typography>
                    </Stack>
                  )}
                  
                  {/* Actions */}
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<IconHeart size={18} fill={isLiked ? 'currentColor' : 'none'} />}
                      onClick={handleLike}
                      sx={{
                        borderColor: isLiked ? 'error.main' : 'grey.300',
                        color: isLiked ? 'error.main' : 'text.primary',
                        borderRadius: 2
                      }}
                    >
                      {likesCount}
                    </Button>
                    {isAuthenticated ? (
                      <SaveToListMenu
                        postUuid={post.uuid}
                        isBookmarked={isBookmarked}
                        onBookmarkChange={setIsBookmarked}
                      />
                    ) : (
                      <IconButton
                        onClick={handleBookmark}
                        sx={{
                          border: '1px solid',
                          borderColor: 'grey.300',
                          color: 'text.secondary',
                          borderRadius: 2
                        }}
                      >
                        <IconBookmark size={18} />
                      </IconButton>
                    )}
                  </Stack>
                </Stack>
              </CardContent>
            </Card>

            {/* Social Share */}
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <SocialShare
                title={post.title}
                slug={post.slug}
                uuid={post.uuid}
                shareVersion={post.updated_at || post.published_at}
              />
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
