import { Box, Typography, Card, CardContent, CardMedia, Chip, Stack, Avatar } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';

const MotionCard = motion.create(Card);

/**
 * PostCard - Classic blog card with image on top
 * Used for Latest Posts, Popular Posts grids
 */
export default function PostCard({ post, animationDelay = 0 }) {
  const {
    id,
    slug,
    title,
    excerpt,
    featured_image,
    category,
    author,
    created_at,
    read_time
  } = post;

  const postUrl = `/blog/${slug || id}`;
  const imageUrl = featured_image || 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&h=600&fit=crop';
  const authorName = author?.full_name || author?.username || 'Anonymous';
  const categoryName = category?.name || category || 'General';
  const formattedDate = created_at ? new Date(created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }) : '';

  return (
    <MotionCard
      component={RouterLink}
      to={postUrl}
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: animationDelay }}
      whileHover={{ y: -8 }}
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        textDecoration: 'none',
        cursor: 'pointer',
        overflow: 'hidden',
        bgcolor: 'background.paper'
      }}
    >
      {/* Image */}
      <Box sx={{ position: 'relative', overflow: 'hidden' }}>
        <CardMedia
          component="img"
          height="200"
          image={imageUrl}
          alt={title}
          sx={{
            transition: 'transform 0.4s ease',
            '&:hover': { transform: 'scale(1.05)' }
          }}
        />
      </Box>

      {/* Content */}
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', p: 3 }}>
        {/* Category */}
        <Chip
          label={categoryName}
          size="small"
          sx={{
            alignSelf: 'flex-start',
            mb: 2,
            bgcolor: 'transparent',
            color: 'primary.main',
            fontWeight: 600,
            fontSize: '0.7rem',
            border: '1px solid',
            borderColor: 'primary.main'
          }}
        />

        {/* Title */}
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            mb: 1.5,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {title}
        </Typography>

        {/* Excerpt */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 3,
            flexGrow: 1,
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {excerpt}
        </Typography>

        {/* Meta & Read More */}
        <Stack direction="row" alignItems="center" justifyContent="space-between">
          <Typography variant="caption" color="text.secondary">
            {formattedDate} {read_time && `· ${read_time}`}
          </Typography>
          <Typography
            variant="caption"
            fontWeight={600}
            color="primary.main"
            sx={{
              '&:hover': { textDecoration: 'underline' }
            }}
          >
            Read More →
          </Typography>
        </Stack>
      </CardContent>
    </MotionCard>
  );
}
