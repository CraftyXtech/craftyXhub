import { useEffect, useState } from 'react';
import { Box, Container, Grid, Typography, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import { getCategories } from '@/api/services/categoryService';

const MotionPaper = motion.create(Paper);

const defaultTopics = [
  {
    id: 1,
    title: 'Business Signals',
    subtitle: 'Track layoffs, pricing shifts, valuations, and the pressure shaping modern companies.',
    image: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&auto=format&fit=crop',
    color: '#EB8A2F',
    bgColor: 'linear-gradient(135deg, #EB8A2F 0%, #C76718 100%)',
    link: '/category/business-and-finance'
  },
  {
    id: 2,
    title: 'AI & Crypto',
    subtitle: 'Follow AI, crypto, and the infrastructure behind the next wave of tech.',
    image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&auto=format&fit=crop',
    color: '#0F8BFF',
    bgColor: 'linear-gradient(135deg, #0F8BFF 0%, #0B5FCC 100%)',
    link: '/category/tech-and-innovation'
  }
];

export default function ExploreTopics() {
  const [topics] = useState(defaultTopics);
  const [businessLink, setBusinessLink] = useState('/#categories');
  const [techInnovationLink, setTechInnovationLink] = useState('/#categories');

  useEffect(() => {
    const loadTopicLinks = async () => {
      try {
        const categories = await getCategories();

        const businessCategory = categories.find((category) => (
          ['Business & Finance', 'Business'].includes(category.name)
          || ['business-and-finance', 'business'].includes(category.slug)
        ));
        const techCategory = categories.find((category) => (
          ['Tech & Innovation', 'Technology'].includes(category.name)
          || ['tech-and-innovation', 'technology'].includes(category.slug)
        ));

        if (businessCategory?.slug) {
          setBusinessLink(`/category/${businessCategory.slug}`);
        }

        if (techCategory?.slug) {
          setTechInnovationLink(`/category/${techCategory.slug}`);
        }
      } catch (error) {
        console.error('Failed to resolve Explore Topics links:', error);
      }
    };

    loadTopicLinks();
  }, []);

  return (
    <Box sx={{ py: { xs: 6, md: 10 }, bgcolor: '#1a1a1a' }}>
      <Container maxWidth="lg">
        {/* Section Header */}
        <Box sx={{ mb: 5 }}>
          <Typography
            variant="h3"
            sx={{
              color: 'white',
              fontWeight: 700,
              fontSize: { xs: '2rem', md: '2.5rem' }
            }}
          >
            Explore more topics
          </Typography>
        </Box>

        {/* Topics Grid */}
        <Grid container spacing={3}>
          {topics.map((topic, index) => (
            <Grid
              size={{ xs: 12, md: topic.id === 1 ? 8 : 4 }}
              key={topic.id}
            >
              <MotionPaper
                component={RouterLink}
                to={topic.id === 1 ? businessLink : techInnovationLink}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ scale: 1.02 }}
                sx={{
                  position: 'relative',
                  height: { xs: 300, md: 400 },
                  borderRadius: 3,
                  overflow: 'hidden',
                  textDecoration: 'none',
                  cursor: 'pointer',
                  background: topic.bgColor,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'flex-end',
                  p: 4,
                  transition: 'all 0.3s ease',
                  '&::before': topic.image ? {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundImage: `url(${topic.image})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    opacity: 0.9,
                    zIndex: 0
                  } : {},
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0) 100%)',
                    zIndex: 1
                  }
                }}
              >
                {/* Icons for multi-icon topics */}
                {topic.icons && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: { xs: 20, md: 30 },
                      right: { xs: 20, md: 30 },
                      display: 'flex',
                      gap: 2,
                      zIndex: 2
                    }}
                  >
                    {topic.icons.map(({ Icon, color }, i) => (
                      <Box
                        key={i}
                        sx={{
                          width: { xs: 60, md: 80 },
                          height: { xs: 60, md: 80 },
                          borderRadius: '50%',
                          bgcolor: color,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                        }}
                      >
                        <Icon size={32} color="white" />
                      </Box>
                    ))}
                  </Box>
                )}

                {/* Content */}
                <Box sx={{ position: 'relative', zIndex: 2 }}>
                  <Typography
                    variant="h4"
                    sx={{
                      color: 'white',
                      fontWeight: 700,
                      mb: 1,
                      fontSize: { xs: '1.5rem', md: '2rem' }
                    }}
                  >
                    {topic.title}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: 'rgba(255,255,255,0.9)',
                      fontSize: { xs: '0.95rem', md: '1.1rem' }
                    }}
                  >
                    {topic.subtitle}
                  </Typography>
                </Box>
              </MotionPaper>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
}
