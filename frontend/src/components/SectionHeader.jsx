import { Box, Typography } from '@mui/material';
import { motion } from 'framer-motion';

const MotionBox = motion.create(Box);

/**
 * SectionHeader - Reusable section title component
 */
export default function SectionHeader({ 
  overline, 
  title, 
  subtitle,
  align = 'center',
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
      <Typography variant="h3" sx={{ mt: overline ? 1 : 0, fontWeight: 700 }}>
        {title}
      </Typography>
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
