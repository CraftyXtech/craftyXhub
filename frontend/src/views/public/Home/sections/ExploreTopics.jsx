import { useEffect, useState } from 'react';
import { Box, Container, Grid, Typography, Paper, Skeleton } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import { getCategories } from '@/api/services/categoryService';
import { getImageUrl } from '@/api/utils/imageUrl';

const MotionPaper = motion.create(Paper);

// Fallback color palette — used when a category has no explicit theme color
const fallbackColors = [
  { bgColor: 'linear-gradient(135deg, #EB8A2F 0%, #C76718 100%)' },
  { bgColor: 'linear-gradient(135deg, #0F8BFF 0%, #0B5FCC 100%)' },
  { bgColor: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)' },
  { bgColor: 'linear-gradient(135deg, #10B981 0%, #059669 100%)' }
];

/**
 * ExploreTopics — Dynamic "Explore more topics" section
 *
 * Renders categories that have a `cover_image` set by the admin.
 * If no categories have cover images, the entire section is hidden.
 *
 * Layout:
 *  - 1 topic  → full width
 *  - 2 topics → 8 / 4 split
 *  - 3 topics → 8 / 4 (row 1) + 12 (row 2)  or  5 / 4 / 3
 *  - 4 topics → 8 / 4 (row 1) + 4 / 8 (row 2)
 */
export default function ExploreTopics() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTopics = async () => {
      try {
        setLoading(true);
        const categories = await getCategories();
        // Only show categories where the admin has set a cover image
        const featured = categories
          .filter((cat) => cat.cover_image)
          .slice(0, 4); // max 4 topics
        setTopics(featured);
      } catch (error) {
        console.error('Failed to load explore topics:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTopics();
  }, []);

  // Determine grid column width based on index and total count
  const getGridSize = (index, total) => {
    if (total === 1) return { xs: 12 };
    if (total === 2) return { xs: 12, md: index === 0 ? 8 : 4 };
    if (total === 3) {
      if (index === 0) return { xs: 12, md: 8 };
      return { xs: 12, sm: 6, md: 4 };
    }
    // 4 topics: alternating 8/4 then 4/8
    if (index === 0) return { xs: 12, md: 8 };
    if (index === 1) return { xs: 12, md: 4 };
    if (index === 2) return { xs: 12, md: 4 };
    return { xs: 12, md: 8 };
  };

  // Don't render the section if no topics have cover images
  if (!loading && topics.length === 0) {
    return null;
  }

  return (
    <Box sx={{ py: { xs: 3, md: 4 }, bgcolor: '#1a1a1a' }}>
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
          {loading ? (
            // Loading skeletons — show 2 placeholders matching the default layout
            <>
              <Grid size={{ xs: 12, md: 8 }}>
                <Skeleton
                  variant="rounded"
                  height={400}
                  sx={{ borderRadius: 3, bgcolor: 'rgba(255,255,255,0.08)' }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <Skeleton
                  variant="rounded"
                  height={400}
                  sx={{ borderRadius: 3, bgcolor: 'rgba(255,255,255,0.08)' }}
                />
              </Grid>
            </>
          ) : (
            topics.map((topic, index) => {
              const colorSet = fallbackColors[index % fallbackColors.length];
              const imageUrl = getImageUrl(topic.cover_image) || topic.cover_image;

              return (
                <Grid
                  size={getGridSize(index, topics.length)}
                  key={topic.id || topic.slug}
                >
                  <MotionPaper
                    component={RouterLink}
                    to={`/category/${topic.slug}`}
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
                      background: colorSet.bgColor,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'flex-end',
                      p: 4,
                      transition: 'all 0.3s ease',
                      '&::before': imageUrl ? {
                        content: '""',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundImage: `url(${imageUrl})`,
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
                        {topic.name}
                      </Typography>
                      {(topic.tagline || topic.description) && (
                        <Typography
                          variant="body1"
                          sx={{
                            color: 'rgba(255,255,255,0.9)',
                            fontSize: { xs: '0.95rem', md: '1.1rem' }
                          }}
                        >
                          {topic.tagline || topic.description}
                        </Typography>
                      )}
                    </Box>
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
