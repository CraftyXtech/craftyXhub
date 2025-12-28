import { Box, Container, Grid, Typography, Chip, IconButton, Stack } from '@mui/material';
import { motion } from 'framer-motion';
import { Link as RouterLink } from 'react-router-dom';
import { useRef } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, Keyboard } from 'swiper/modules';
import { IconArrowRight, IconArrowLeft } from '@tabler/icons-react';

// Swiper styles
import 'swiper/css';

const MotionBox = motion.create(Box);

// Hero slides data
const heroSlides = [
  {
    image: 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1600&h=900&fit=crop',
    label: 'Featured',
    title: 'Discover Stories That Inspire',
    to: '/blog?filter=featured'
  },
  {
    image: 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1600&h=900&fit=crop',
    label: 'Trending',
    title: 'What The Community Is Reading',
    to: '/blog?filter=trending'
  }
];

// Featured posts data
const featuredPosts = [
  {
    id: 1,
    slug: 'ai-revolution-2024',
    title: 'The AI Revolution: What It Means for Content Creators',
    category: 'Technology',
    date: '05 March 2024',
    featured_image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop'
  },
  {
    id: 2,
    slug: 'remote-work-future',
    title: 'Remote Work Is Here to Stay: Best Practices for 2024',
    category: 'Lifestyle',
    date: '28 February 2024',
    featured_image: 'https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800&h=600&fit=crop'
  }
];

// Featured Post Card Component
function FeaturedPostCard({ post, height = '100%' }) {
  const postUrl = `/blog/${post.slug || post.id}`;

  return (
    <Box
      component={RouterLink}
      to={postUrl}
      sx={{
        position: 'relative',
        height: height,
        display: 'block',
        overflow: 'hidden',
        textDecoration: 'none',
        '&:hover img': {
          transform: 'scale(1.05)'
        }
      }}
    >
      {/* Background Image */}
      <Box
        component="img"
        src={post.featured_image}
        alt={post.title}
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
        sx={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.1) 100%)'
        }}
      />

      {/* Category Chip */}
      <Box sx={{ position: 'absolute', top: 16, left: 16, zIndex: 1 }}>
        <Chip
          label={post.category}
          size="small"
          sx={{
            bgcolor: 'rgba(255,255,255,0.9)',
            color: 'text.primary',
            fontWeight: 600,
            fontSize: '0.65rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}
        />
      </Box>

      {/* Content */}
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          p: 2.5,
          color: 'white'
        }}
      >
        <Typography
          variant="caption"
          sx={{ opacity: 0.9, display: 'block', mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}
        >
          {post.date}
        </Typography>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: 'white',
            lineHeight: 1.3
          }}
        >
          {post.title}
        </Typography>
      </Box>
    </Box>
  );
}

export default function HeroSection() {
  const swiperRef = useRef(null);

  return (
    <Box sx={{ bgcolor: '#f8f4f0', py: { xs: 4, md: 6 }, px: { xs: 2, md: 6 } }}>
      <Container maxWidth={false}>
        <Grid container spacing={2}>
          {/* Left: Hero Slider */}
          <Grid size={{ xs: 12, lg: 6 }}>
            <Box sx={{ position: 'relative', height: { xs: 350, md: 500 } }}>
              <Swiper
                modules={[Autoplay, Keyboard]}
                autoplay={{ delay: 4000, disableOnInteraction: false }}
                keyboard={{ enabled: true }}
                loop={true}
                style={{ height: '100%' }}
                onSwiper={(swiper) => { swiperRef.current = swiper; }}
              >
                {heroSlides.map((slide, index) => (
                  <SwiperSlide key={index}>
                    <Box
                      sx={{
                        position: 'relative',
                        height: '100%',
                        backgroundImage: `url(${slide.image})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center'
                      }}
                    >
                      {/* Bottom Bar Overlay */}
                      <Box
                        sx={{
                          position: 'absolute',
                          bottom: 0,
                          left: 0,
                          right: 50,
                          bgcolor: 'rgba(0,0,0,0.7)',
                          py: { xs: 3, md: 4 },
                          px: { xs: 3, md: 5 },
                          display: 'flex',
                          alignItems: 'center',
                          gap: 3
                        }}
                      >
                        <Typography
                          component={RouterLink}
                          to={slide.to}
                          variant="overline"
                          sx={{
                            color: 'accent.main',
                            fontWeight: 600,
                            letterSpacing: 2,
                            textDecoration: 'none',
                            borderRight: '1px solid rgba(255,255,255,0.2)',
                            pr: 3,
                            '&:hover': { color: 'white' }
                          }}
                        >
                          {slide.label}
                        </Typography>
                        <Typography
                          component={RouterLink}
                          to={slide.to}
                          variant="h5"
                          sx={{
                            color: 'white',
                            fontWeight: 300,
                            textDecoration: 'none'
                          }}
                        >
                          {slide.title}
                        </Typography>
                      </Box>
                    </Box>
                  </SwiperSlide>
                ))}
              </Swiper>

              {/* Nav Arrows - Stacked on right */}
              <Stack
                sx={{
                  position: 'absolute',
                  bottom: 0,
                  right: 0,
                  zIndex: 10,
                  width: 50
                }}
              >
                <IconButton
                  onClick={() => swiperRef.current?.slideNext()}
                  sx={{
                    bgcolor: 'black',
                    color: 'white',
                    borderRadius: 0,
                    height: { xs: 50, md: 70 },
                    '&:hover': { bgcolor: 'grey.900' }
                  }}
                >
                  <IconArrowRight size={20} />
                </IconButton>
                <IconButton
                  onClick={() => swiperRef.current?.slidePrev()}
                  sx={{
                    bgcolor: 'black',
                    color: 'white',
                    borderRadius: 0,
                    height: { xs: 50, md: 70 },
                    '&:hover': { bgcolor: 'grey.900' }
                  }}
                >
                  <IconArrowLeft size={20} />
                </IconButton>
              </Stack>
            </Box>
          </Grid>

          {/* Right: Featured Posts - Side by Side */}
          <Grid size={{ xs: 12, lg: 6 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ height: { xs: 'auto', lg: 500 } }}>
              {featuredPosts.map((post, index) => (
                <MotionBox
                  key={post.id}
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  sx={{ flex: 1, minHeight: { xs: 250, lg: 'auto' } }}
                >
                  <FeaturedPostCard post={post} height="100%" />
                </MotionBox>
              ))}
            </Stack>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
