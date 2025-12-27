import { Box, Container, Typography, Grid, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import {
  IconCode,
  IconPalette,
  IconRocket,
  IconBulb,
  IconHeart,
  IconWorld
} from '@tabler/icons-react';

const MotionPaper = motion.create(Paper);

const categories = [
  { name: 'Technology', icon: IconCode, count: 128, color: '#1F7DAD' },
  { name: 'Design', icon: IconPalette, count: 95, color: '#E91E63' },
  { name: 'Startups', icon: IconRocket, count: 76, color: '#FF9800' },
  { name: 'Ideas', icon: IconBulb, count: 154, color: '#9C27B0' },
  { name: 'Lifestyle', icon: IconHeart, count: 89, color: '#F44336' },
  { name: 'Culture', icon: IconWorld, count: 112, color: '#4CAF50' }
];

export default function Categories() {
  return (
    <Box sx={{ py: { xs: 8, md: 12 } }}>
      <Container maxWidth="lg">
        {/* Section Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography
            variant="overline"
            sx={{ color: 'text.secondary', fontWeight: 600 }}
          >
            Explore Topics
          </Typography>
          <Typography variant="h3" sx={{ mt: 1, fontWeight: 700 }}>
            Browse by category
          </Typography>
          <Typography
            variant="body1"
            sx={{ mt: 2, color: 'text.secondary', maxWidth: 500, mx: 'auto' }}
          >
            Find articles that match your interests across our diverse range of topics
          </Typography>
        </Box>

        {/* Categories Grid */}
        <Grid container spacing={3}>
          {categories.map((category, index) => (
            <Grid size={{ xs: 6, sm: 4, md: 2 }} key={category.name}>
              <MotionPaper
                component={RouterLink}
                to={`/blog?category=${category.name.toLowerCase()}`}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: index * 0.05 }}
                whileHover={{ y: -4, boxShadow: '0 8px 24px rgba(0,0,0,0.12)' }}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  textDecoration: 'none',
                  cursor: 'pointer',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 3,
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: category.color
                  }
                }}
              >
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    bgcolor: `${category.color}15`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  <category.icon size={24} color={category.color} />
                </Box>
                <Typography variant="subtitle2" fontWeight={600}>
                  {category.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {category.count} articles
                </Typography>
              </MotionPaper>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}
