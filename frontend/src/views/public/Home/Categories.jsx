import { useState, useEffect } from 'react';
import { Box, Container, Typography, Grid, Paper, Skeleton } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import {
  IconCode,
  IconPalette,
  IconRocket,
  IconBulb,
  IconHeart,
  IconWorld,
  IconBriefcase,
  IconBook,
  IconCamera,
  IconMusic,
  IconDeviceLaptop,
  IconSchool,
  IconTrendingUp,
  IconStar,
  IconMoneybag,
  IconCpu,
  IconBuildingStore,
  IconVideo,
  IconArticle,
  IconNews
} from '@tabler/icons-react';
import { getCategories } from '@/api/services/categoryService';

const MotionPaper = motion.create(Paper);

// Icon mapping for specific categories
const iconMap = {
  technology: IconCode,
  design: IconPalette,
  startups: IconRocket,
  ideas: IconBulb,
  lifestyle: IconHeart,
  culture: IconWorld,
  business: IconBriefcase,
  education: IconBook,
  photography: IconCamera,
  music: IconMusic,
  'web development': IconDeviceLaptop,
  'software engineering': IconCpu,
  tutorials: IconSchool,
  career: IconMoneybag,
  'popular content': IconTrendingUp,
  featured: IconStar,
  marketing: IconBuildingStore,
  video: IconVideo,
  news: IconNews
};

// Fallback icons for random assignment
const fallbackIcons = [
  IconBulb,
  IconArticle,
  IconStar,
  IconRocket,
  IconWorld,
  IconBook
];

// Color mapping for specific categories
const colorMap = {
  technology: '#1F7DAD',
  design: '#E91E63',
  startups: '#FF9800',
  ideas: '#9C27B0',
  lifestyle: '#F44336',
  culture: '#4CAF50',
  business: '#2196F3',
  education: '#673AB7',
  photography: '#795548',
  music: '#009688',
  'web development': '#3F51B5',
  'software engineering': '#607D8B',
  tutorials: '#FF5722',
  career: '#795548',
  'popular content': '#FFC107',
  featured: '#FF9800',
  marketing: '#00BCD4',
  video: '#F44336',
  news: '#2196F3'
};

// Fallback colors
const fallbackColors = [
  '#1F7DAD', '#E91E63', '#FF9800', '#9C27B0', '#F44336', '#4CAF50',
  '#2196F3', '#673AB7', '#795548', '#009688', '#607D8B'
];

// Helper to get deterministic random choice based on string
const getFromHash = (str, array) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % array.length;
  return array[index];
};

export default function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await getCategories();
        setCategories(data.slice(0, 6)); // Show max 6 categories
      } catch (error) {
        console.error('Failed to fetch categories:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  const getIcon = (name) => {
    const key = name?.toLowerCase();
    if (iconMap[key]) return iconMap[key];
    return getFromHash(key, fallbackIcons);
  };

  const getColor = (name) => {
    const key = name?.toLowerCase();
    if (colorMap[key]) return colorMap[key];
    return getFromHash(key + 'color', fallbackColors);
  };

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
        <Grid container spacing={3} justifyContent="center">
          {loading ? (
            // Loading skeletons
            [...Array(6)].map((_, index) => (
              <Grid size={{ xs: 6, sm: 4, md: 4, lg: 2 }} key={index}>
                <Skeleton variant="rounded" height={140} sx={{ borderRadius: 3 }} />
              </Grid>
            ))
          ) : categories.length === 0 ? (
            <Grid size={12}>
              <Typography color="text.secondary" textAlign="center">
                No categories available
              </Typography>
            </Grid>
          ) : (
            categories.map((category, index) => {
              const IconComponent = getIcon(category.name);
              const color = getColor(category.name);
              
              return (
                <Grid size={{ xs: 6, sm: 4, md: 4, lg: 2 }} key={category.uuid || category.id}>
                  <MotionPaper
                    component={RouterLink}
                    to={`/category/${category.slug || category.name?.toLowerCase()}`}
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
                      minHeight: 140,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      '&:hover': {
                        borderColor: color
                      }
                    }}
                  >
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: `${color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        mb: 2
                      }}
                    >
                      <IconComponent size={24} color={color} />
                    </Box>
                    <Typography variant="subtitle2" fontWeight={600} sx={{ wordBreak: 'break-word' }}>
                      {category.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {category.post_count || 0} articles
                    </Typography>
                  </MotionPaper>
                </Grid>
              );
            })
          )}
        </Grid>
      </Container>
    </Box>
  );
}
