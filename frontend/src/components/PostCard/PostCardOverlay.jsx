import { Box, Typography, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';

const MotionBox = motion.create(Box);

/**
 * PostCardOverlay - Card with full image background and text overlay
 * Used for Hero section and Recent Posts (metro style)
 */
export default function PostCardOverlay({ 
  post, 
  height = 300, 
  animationDelay = 0,
  showCategory = true 
}) {
  const {
    id,
    slug,
    title,
    category,
    featured_image
  } = post;

  const postUrl = `/blog/${slug || id}`;
  const imageUrl = featured_image || 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&h=600&fit=crop';
  const categoryName = category?.name || category || 'General';

  return (
    <MotionBox
      component={RouterLink}
      to={postUrl}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: animationDelay }}
      sx={{
        position: 'relative',
        height: height,
        borderRadius: 2,
        overflow: 'hidden',
        display: 'block',
        textDecoration: 'none',
        '&:hover img': {
          transform: 'scale(1.05)'
        },
        '&:hover .overlay': {
          bgcolor: 'rgba(0,0,0,0.6)'
        }
      }}
    >
      {/* Background Image */}
      <Box
        component="img"
        src={imageUrl}
        alt={title}
        sx={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transition: 'transform 0.4s ease'
        }}
      />

      {/* Gradient Overlay */}
      <Box
        className="overlay"
        sx={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.1) 100%)',
          transition: 'background-color 0.3s ease'
        }}
      />

      {/* Content */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          p: 3,
          color: 'white'
        }}
      >
        {showCategory && (
          <Chip
            label={categoryName}
            size="small"
            sx={{
              mb: 1.5,
              bgcolor: 'primary.main',
              color: 'white',
              fontWeight: 600,
              fontSize: '0.65rem'
            }}
          />
        )}
        <Typography
          variant="h5"
          sx={{
            fontWeight: 600,
            color: 'white',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            lineHeight: 1.3
          }}
        >
          {title}
        </Typography>
      </Box>
    </MotionBox>
  );
}
