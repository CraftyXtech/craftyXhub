import { useEffect, useState } from 'react';
import { Box, Container, Skeleton, Typography, Chip, useTheme } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getCategories } from '@/api/services/categoryService';
import { getPostsForCategoryIds } from '@/api/services/postService';
import { getImageUrl } from '@/api/utils/imageUrl';

const MotionBox = motion.create(Box);

const FALLBACK_IMAGE =
  'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&h=600&fit=crop';

/**
 * CategoryCarouselSection — Magazine-style category section
 * Design: Left-aligned header with gradient underline, 4-column card grid,
 * minimal cards (image + category badge + date + title).
 */
export default function CategoryCarouselSection({
  title,
  parentSlug,
  limit = 12,
  background = 'background.default',
}) {
  const theme = useTheme();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchCategoryPosts = async () => {
      try {
        setLoading(true);
        const categories = await getCategories();
        const parentCategory = categories.find((category) => category.slug === parentSlug);

        if (!parentCategory) {
          if (isMounted) {
            setPosts([]);
          }
          return;
        }

        const categoryIds = [
          parentCategory.id,
          ...(parentCategory.subcategories || []).map((subcategory) => subcategory.id),
        ];
        const data = await getPostsForCategoryIds(categoryIds, { limit });

        if (isMounted) {
          setPosts(data.posts || []);
        }
      } catch (error) {
        console.error(`Failed to fetch ${title} posts:`, error);
        if (isMounted) {
          setPosts([]);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchCategoryPosts();

    return () => {
      isMounted = false;
    };
  }, [limit, parentSlug, title]);

  if (!loading && posts.length === 0) {
    return null;
  }

  // Show first 4 posts in the grid
  const visiblePosts = posts.slice(0, 4);

  return (
    <Box sx={{ py: { xs: 3, md: 4 }, bgcolor: background }}>
      <Container maxWidth="lg">
        {/* ── Section Header ── */}
        <MotionBox
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          sx={{ mb: 3 }}
        >
          {/* Title row */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 1.5,
            }}
          >
            {/* Left: icon + title */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Box
                sx={{
                  width: 32,
                  height: 32,
                  borderRadius: '6px',
                  bgcolor: 'primary.main',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.85rem',
                  fontWeight: 800,
                }}
              >
                {title.charAt(0)}
              </Box>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                  fontSize: { xs: '0.95rem', md: '1.05rem' },
                }}
              >
                {title}
              </Typography>
            </Box>

            {/* Right: "MORE →" link */}
            <Typography
              component={RouterLink}
              to={`/category/${parentSlug}`}
              variant="body2"
              sx={{
                color: 'primary.main',
                fontWeight: 700,
                textDecoration: 'none',
                letterSpacing: '0.06em',
                fontSize: '0.75rem',
                whiteSpace: 'nowrap',
                '&:hover': { textDecoration: 'underline' },
              }}
            >
              MORE {title.toUpperCase()} →
            </Typography>
          </Box>

          {/* Gradient underline */}
          <Box
            sx={{
              height: '3px',
              borderRadius: '2px',
              background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary?.main || '#f0c040'} 100%)`,
            }}
          />
        </MotionBox>

        {/* ── Card Grid ── */}
        {loading ? (
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(4, 1fr)',
              },
              gap: { xs: 2, md: 2.5 },
            }}
          >
            {[...Array(4)].map((_, index) => (
              <Box key={index}>
                <Skeleton variant="rounded" height={180} sx={{ mb: 1.5, borderRadius: '8px' }} />
                <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                  <Skeleton width={80} height={22} variant="rounded" />
                  <Skeleton width={100} height={18} />
                </Box>
                <Skeleton width="90%" height={22} />
                <Skeleton width="70%" height={22} />
              </Box>
            ))}
          </Box>
        ) : (
          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: {
                xs: '1fr',
                sm: 'repeat(2, 1fr)',
                md: 'repeat(4, 1fr)',
              },
              gap: { xs: 2, md: 2.5 },
            }}
          >
            {visiblePosts.map((post, index) => (
              <MagazineCard key={post.uuid || post.id || index} post={post} index={index} />
            ))}
          </Box>
        )}
      </Container>
    </Box>
  );
}

/**
 * MagazineCard — Minimal card: image + category badge + date + title
 * No excerpt, no "Read More", no elevation. Clean editorial look.
 */
function MagazineCard({ post, index }) {
  const {
    uuid,
    id,
    slug,
    title,
    featured_image,
    category,
    created_at,
  } = post;

  const postUrl = `/post/${slug || uuid || id}`;
  const imageUrl = getImageUrl(featured_image) || FALLBACK_IMAGE;
  const categoryName = category?.name || category || 'General';
  const categorySlug = category?.slug || '';

  const formattedDate = created_at
    ? new Date(created_at).toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      })
    : '';

  // Assign badge colors based on category for visual variety
  const badgeColors = {
    Business: { bg: '#6B21A8', color: '#fff' },
    Technology: { bg: '#1D4ED8', color: '#fff' },
    Entertainment: { bg: '#9333EA', color: '#fff' },
    Africa: { bg: '#16A34A', color: '#fff' },
    Athletics: { bg: '#DC2626', color: '#fff' },
  };
  const badge = badgeColors[categoryName] || { bg: '#6B21A8', color: '#fff' };

  return (
    <MotionBox
      component={RouterLink}
      to={postUrl}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      sx={{
        textDecoration: 'none',
        color: 'inherit',
        display: 'block',
        '&:hover .magazine-card-image': {
          transform: 'scale(1.05)',
        },
        '&:hover .magazine-card-title': {
          color: 'primary.main',
        },
      }}
    >
      {/* Image */}
      <Box
        sx={{
          position: 'relative',
          overflow: 'hidden',
          borderRadius: '8px',
          mb: 1.5,
          aspectRatio: '16 / 10',
          bgcolor: 'grey.200',
        }}
      >
        <Box
          className="magazine-card-image"
          component="img"
          src={imageUrl}
          alt={title}
          loading="lazy"
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: 'block',
            transition: 'transform 0.4s ease',
          }}
        />
      </Box>

      {/* Category badge + Date */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, flexWrap: 'wrap' }}>
        <Chip
          label={categoryName.toUpperCase()}
          size="small"
          sx={{
            height: 22,
            bgcolor: badge.bg,
            color: badge.color,
            fontWeight: 700,
            fontSize: '0.65rem',
            letterSpacing: '0.04em',
            borderRadius: '3px',
            '& .MuiChip-label': { px: 1 },
          }}
        />
        <Typography
          variant="caption"
          sx={{
            color: 'text.secondary',
            fontSize: '0.75rem',
          }}
        >
          {formattedDate}
        </Typography>
      </Box>

      {/* Title */}
      <Typography
        className="magazine-card-title"
        variant="subtitle2"
        sx={{
          fontWeight: 700,
          lineHeight: 1.4,
          fontSize: { xs: '0.85rem', md: '0.9rem' },
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          transition: 'color 0.2s ease',
        }}
      >
        {title}
      </Typography>
    </MotionBox>
  );
}
