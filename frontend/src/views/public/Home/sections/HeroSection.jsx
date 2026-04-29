import { Box, Container, Grid, Typography, Chip, IconButton, Stack, Skeleton } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useRef, useState, useEffect } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, Keyboard } from 'swiper/modules';
import { IconArrowRight, IconArrowLeft } from '@tabler/icons-react';
import { getFeaturedPosts, getHomepageTrendingPosts, getImageUrl, getRecentPosts } from '@/api/services/postService';

// Swiper styles
import 'swiper/css';

const FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1600&h=900&fit=crop';

function getPostUrl(post) {
  return `/post/${post.slug || post.uuid || post.id}`;
}

function HeroPostSlide({ post }) {
  const imageUrl = getImageUrl(post.featured_image) || FALLBACK_IMAGE;
  const categoryName = typeof post.category === 'object' ? post.category?.name : post.category;

  return (
    <Box
      component={RouterLink}
      to={getPostUrl(post)}
      sx={{
        position: 'relative',
        display: 'block',
        height: '100%',
        backgroundImage: `url(${imageUrl})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        textDecoration: 'none'
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background: 'linear-gradient(to top, rgba(0,0,0,0.55), rgba(0,0,0,0.08) 55%)'
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: { xs: 0, md: 50 },
          bgcolor: 'rgba(0,0,0,0.7)',
          py: { xs: 3, md: 4 },
          px: { xs: 3, md: 5 },
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          alignItems: { xs: 'flex-start', sm: 'center' },
          gap: { xs: 1, sm: 3 }
        }}
      >
        <Typography
          variant="overline"
          sx={{
            color: 'accent.main',
            fontWeight: 600,
            letterSpacing: 2,
            borderRight: '1px solid rgba(255,255,255,0.2)',
            pr: { xs: 0, sm: 3 },
            borderRightWidth: { xs: 0, sm: 1 }
          }}
        >
          {categoryName || 'Trending'}
        </Typography>
        <Typography
          variant="h5"
          sx={{
            color: 'white',
            fontWeight: 300,
            textDecoration: 'none',
            lineHeight: 1.2
          }}
        >
          {post.title}
        </Typography>
      </Box>
    </Box>
  );
}

// Featured Post Card Component
function FeaturedPostCard({ post, height = '100%' }) {
  const postUrl = getPostUrl(post);
  const imageUrl = getImageUrl(post.featured_image) || FALLBACK_IMAGE;
  const categoryName = typeof post.category === 'object' ? post.category?.name : post.category;
  const postDate = post.published_at || post.created_at;
  const formattedDate = postDate ? new Date(postDate).toLocaleDateString('en-US', { day: '2-digit', month: 'long', year: 'numeric' }) : '';

  return (
    <Box
      component={RouterLink}
      to={postUrl}
      sx={{
        position: 'relative',
        height: height,
        minHeight: 250,
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
        src={imageUrl}
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
          label={categoryName || 'Article'}
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
          {formattedDate}
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
  const [trendingPosts, setTrendingPosts] = useState([]);
  const [featuredPosts, setFeaturedPosts] = useState([]);
  const [trendingLoading, setTrendingLoading] = useState(true);
  const [featuredLoading, setFeaturedLoading] = useState(true);

  useEffect(() => {
    const fetchHomepagePosts = async () => {
      try {
        setTrendingLoading(true);
        setFeaturedLoading(true);
        const [trendingData, featuredData, recentData] = await Promise.all([
          getHomepageTrendingPosts({ limit: 3 }),
          getFeaturedPosts({ limit: 2 }),
          getRecentPosts({ limit: 6 }),
        ]);
        const curatedTrending = trendingData?.posts || [];
        const curatedFeatured = featuredData?.posts || [];
        const recentPosts = recentData?.posts || [];

        const resolvedTrending = curatedTrending.length > 0
          ? curatedTrending
          : recentPosts.slice(0, 3);

        const usedFeaturedIds = new Set(curatedFeatured.map((post) => post.uuid || post.id));
        const featuredFallbackPool = recentPosts.filter((post) => {
          const postId = post.uuid || post.id;
          if (!postId || usedFeaturedIds.has(postId)) {
            return false;
          }
          return !resolvedTrending.some((trendingPost) => (trendingPost.uuid || trendingPost.id) === postId);
        });

        const resolvedFeatured = curatedFeatured.length >= 2
          ? curatedFeatured.slice(0, 2)
          : [...curatedFeatured, ...featuredFallbackPool].slice(0, 2);

        setTrendingPosts(resolvedTrending);
        setFeaturedPosts(resolvedFeatured);
      } catch (err) {
        console.error('Failed to fetch homepage posts:', err);
      } finally {
        setTrendingLoading(false);
        setFeaturedLoading(false);
      }
    };

    fetchHomepagePosts();
  }, []);

  return (
    <Box sx={{ bgcolor: '#f8f4f0', pt: { xs: 4, md: 6 }, pb: { xs: 2, md: 3 }, px: { xs: 2, md: 6 } }}>
      <Container maxWidth={false}>
        <Grid container spacing={2}>
          {/* Left: Hero Slider */}
          <Grid size={{ xs: 12, lg: 6 }}>
            <Box sx={{ position: 'relative', height: { xs: 280, md: 380 } }}>
              {trendingLoading ? (
                <Skeleton variant="rounded" height="100%" />
              ) : trendingPosts.length > 0 ? (
                <Swiper
                  modules={[Autoplay, Keyboard]}
                  autoplay={trendingPosts.length > 1 ? { delay: 5000, disableOnInteraction: false } : false}
                  keyboard={{ enabled: true }}
                  loop={trendingPosts.length > 1}
                  style={{ height: '100%' }}
                  onSwiper={(swiper) => { swiperRef.current = swiper; }}
                >
                  {trendingPosts.map((post) => (
                    <SwiperSlide key={post.uuid || post.id}>
                      <HeroPostSlide post={post} />
                    </SwiperSlide>
                  ))}
                </Swiper>
              ) : (
                <Box
                  sx={{
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: 'grey.200',
                    color: 'text.secondary'
                  }}
                >
                  <Typography>No published stories available yet</Typography>
                </Box>
              )}

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
                  disabled={trendingPosts.length < 2}
                  sx={{
                    bgcolor: 'black',
                    color: 'white',
                    borderRadius: 0,
                    height: { xs: 40, md: 56 },
                    '&:hover': { bgcolor: 'grey.900' },
                    '&.Mui-disabled': { bgcolor: 'grey.900', color: 'grey.600' }
                  }}
                >
                  <IconArrowRight size={20} />
                </IconButton>
                <IconButton
                  onClick={() => swiperRef.current?.slidePrev()}
                  disabled={trendingPosts.length < 2}
                  sx={{
                    bgcolor: 'black',
                    color: 'white',
                    borderRadius: 0,
                    height: { xs: 48, md: 56 },
                    '&:hover': { bgcolor: 'grey.900' },
                    '&.Mui-disabled': { bgcolor: 'grey.900', color: 'grey.600' }
                  }}
                >
                  <IconArrowLeft size={20} />
                </IconButton>
              </Stack>
            </Box>
          </Grid>

          {/* Right: Featured Posts - Side by Side */}
          <Grid size={{ xs: 12, lg: 6 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ minHeight: { xs: 420, sm: 250, lg: 380 } }}>
              {featuredLoading ? (
                // Loading skeletons
                [...Array(2)].map((_, index) => (
                  <Box key={index} sx={{ flex: 1, height: { xs: 250, lg: 'auto' }, minHeight: 250 }}>
                    <Skeleton variant="rounded" height="100%" sx={{ minHeight: 250 }} />
                  </Box>
                ))
              ) : featuredPosts.length > 0 ? (
                featuredPosts.map((post) => (
                  <Box
                    key={post.uuid || post.id}
                    sx={{ flex: 1, height: { xs: 250, lg: 'auto' }, minHeight: 250 }}
                  >
                    <FeaturedPostCard post={post} height="100%" />
                  </Box>
                ))
              ) : (
                <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.200', minHeight: 250 }}>
                  <Typography color="text.secondary">No published stories available yet</Typography>
                </Box>
              )}
            </Stack>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
