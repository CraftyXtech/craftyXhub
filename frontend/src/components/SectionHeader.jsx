import { Box, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { motion } from 'framer-motion';

const MotionBox = motion.create(Box);

/**
 * SectionHeader - Reusable section title component
 */
export default function SectionHeader({ 
  overline, 
  title, 
  subtitle,
  align = 'left',
  moreLink,
  moreLinkText,
  sx = {}
}) {
  return (
    <MotionBox
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      sx={{ 
        textAlign: align, 
        mb: 6,
        ...sx 
      }}
    >
      {overline && (
        <Typography
          variant="overline"
          sx={{ color: 'text.secondary', fontWeight: 600 }}
        >
          {overline}
        </Typography>
      )}

      {/* Title row with optional "More" link */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: moreLink ? 'space-between' : (align === 'center' ? 'center' : 'flex-start'),
        }}
      >
        <Typography variant="h3" sx={{ mt: overline ? 1 : 0, fontWeight: 700 }}>
          {title}
        </Typography>
        {moreLink && (
          <Typography
            component={RouterLink}
            to={moreLink}
            variant="body2"
            sx={{
              color: 'primary.main',
              fontWeight: 700,
              textDecoration: 'none',
              whiteSpace: 'nowrap',
              letterSpacing: '0.05em',
              '&:hover': { textDecoration: 'underline' },
            }}
          >
            {moreLinkText || `MORE ${title.toUpperCase()} →`}
          </Typography>
        )}
      </Box>

      {subtitle && (
        <Typography
          variant="body1"
          sx={{ mt: 2, color: 'text.secondary', maxWidth: 600, mx: align === 'center' ? 'auto' : 0 }}
        >
          {subtitle}
        </Typography>
      )}
    </MotionBox>
  );
}
