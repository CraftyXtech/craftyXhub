import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Typography,
  Avatar,
  Stack,
  IconButton,
  Divider,
  Skeleton,
  Alert,
  Button
} from '@mui/material';
import { motion } from 'framer-motion';
import {
  IconBrandTwitter,
  IconBrandLinkedin,
  IconWorld,
  IconArticle,
  IconHeart
} from '@tabler/icons-react';
import PostCard from '@/components/PostCard';
import Breadcrumb from '@/components/Breadcrumb';
import { getUserByUsername } from '@/api/services/userService';
import { getPostsByAuthor } from '@/api/services/postService';

const MotionBox = motion.create(Box);

/**
 * Author Page
 * Displays author profile and their published posts
 */
export default function Author() {
  const { username } = useParams();
  const [author, setAuthor] = useState(null);
  const [posts, setPosts] = useState([]);
  const [totalPosts, setTotalPosts] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAllPosts, setShowAllPosts] = useState(false);

  // Fetch author and their posts
  useEffect(() => {
    const fetchAuthorData = async () => {
      if (!username) return;
      
      try {
        setLoading(true);
        setError(null);
        
        // Fetch author profile
        const authorData = await getUserByUsername(username);
        setAuthor(authorData);
        
        // Fetch author's posts
        if (authorData?.uuid) {
          const postsData = await getPostsByAuthor(authorData.uuid, { limit: 100 });
          setPosts(postsData.posts || []);
          setTotalPosts(postsData.total || 0);
        }
      } catch (err) {
        console.error('Failed to fetch author:', err);
        setError(err.message || 'Author not found');
      } finally {
        setLoading(false);
      }
    };

    fetchAuthorData();
  }, [username]);

  const displayedPosts = showAllPosts ? posts : posts.slice(0, 6);
  
  const breadcrumbItems = [
    { label: 'Home', to: '/' },
    { label: author?.full_name || username }
  ];

  // Loading state
  if (loading) {
    return (
      <Box>
        <Box sx={{ bgcolor: 'grey.50', py: { xs: 6, md: 8 } }}>
          <Container maxWidth="lg">
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={4} alignItems="center">
              <Skeleton variant="circular" width={120} height={120} />
              <Box sx={{ flex: 1, width: '100%' }}>
                <Skeleton variant="text" width="40%" height={48} />
                <Skeleton variant="text" width="60%" />
                <Skeleton variant="text" width="80%" />
              </Box>
            </Stack>
          </Container>
        </Box>
        <Container maxWidth="lg" sx={{ py: 6 }}>
          <Grid container spacing={3}>
            {[...Array(3)].map((_, i) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={i}>
                <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
                <Skeleton variant="text" height={32} sx={{ mt: 2 }} />
                <Skeleton variant="text" width="80%" />
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>
    );
  }

  // Error state
  if (error || !author) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <Alert severity="error" sx={{ mb: 4, maxWidth: 400, mx: 'auto' }}>
          {error || 'Author not found'}
        </Alert>
        <Button variant="contained" href="/">
          Back to Home
        </Button>
      </Container>
    );
  }

  // Get profile data safely
  const profile = author.profile || {};
  const stats = {
    posts: totalPosts,
    likes: author.total_likes || 0
  };

  return (
    <Box>
      {/* Author Header */}
      <Box
        sx={{
          bgcolor: 'grey.50',
          py: { xs: 6, md: 8 },
          borderBottom: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Container maxWidth="lg">
          <Breadcrumb items={breadcrumbItems} />

          <MotionBox
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Grid container spacing={4} alignItems="center">
              {/* Avatar */}
              <Grid size={{ xs: 12, md: 'auto' }}>
                <Avatar
                  src={profile.avatar}
                  sx={{
                    width: 120,
                    height: 120,
                    bgcolor: 'primary.main',
                    fontSize: '3rem',
                    mx: { xs: 'auto', md: 0 }
                  }}
                >
                  {author.full_name?.[0] || 'A'}
                </Avatar>
              </Grid>

              {/* Info */}
              <Grid size={{ xs: 12, md: true }}>
                <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
                  <Typography variant="h3" sx={{ fontWeight: 700, mb: 1 }}>
                    {author.full_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    @{author.username}
                    {profile.location && ` · ${profile.location}`}
                  </Typography>
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    sx={{ mb: 3, maxWidth: 600 }}
                  >
                    {profile.bio || 'No bio available.'}
                  </Typography>

                  {/* Stats & Social */}
                  <Stack
                    direction="row"
                    spacing={4}
                    alignItems="center"
                    justifyContent={{ xs: 'center', md: 'flex-start' }}
                  >
                    {/* Stats */}
                    <Stack direction="row" spacing={3}>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <IconArticle size={18} />
                        <Typography variant="body2">
                          <strong>{stats.posts}</strong> Posts
                        </Typography>
                      </Stack>
                      <Stack direction="row" spacing={1} alignItems="center">
                        <IconHeart size={18} />
                        <Typography variant="body2">
                          <strong>{stats.likes}</strong> Likes
                        </Typography>
                      </Stack>
                    </Stack>

                    <Divider orientation="vertical" flexItem />

                    {/* Social Links */}
                    <Stack direction="row" spacing={1}>
                      {profile.website && (
                        <IconButton
                          component="a"
                          href={profile.website}
                          target="_blank"
                          size="small"
                          sx={{ color: 'text.secondary' }}
                        >
                          <IconWorld size={20} />
                        </IconButton>
                      )}
                      {profile.twitter && (
                        <IconButton
                          component="a"
                          href={`https://twitter.com/${profile.twitter}`}
                          target="_blank"
                          size="small"
                          sx={{ color: '#1DA1F2' }}
                        >
                          <IconBrandTwitter size={20} />
                        </IconButton>
                      )}
                      {profile.linkedin && (
                        <IconButton
                          component="a"
                          href={`https://linkedin.com/in/${profile.linkedin}`}
                          target="_blank"
                          size="small"
                          sx={{ color: '#0077B5' }}
                        >
                          <IconBrandLinkedin size={20} />
                        </IconButton>
                      )}
                    </Stack>
                  </Stack>
                </Box>
              </Grid>
            </Grid>
          </MotionBox>
        </Container>
      </Box>

      {/* Author's Posts */}
      <Container maxWidth="lg" sx={{ py: { xs: 4, md: 6 } }}>
        <Typography variant="h4" sx={{ fontWeight: 600, mb: 4 }}>
          Articles by {author.full_name}
        </Typography>

        {posts.length > 0 ? (
          <Grid container spacing={3}>
            {displayedPosts.map((post, index) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={post.id || post.uuid}>
                <PostCard post={post} animationDelay={index * 0.05} />
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography color="text.secondary">
              No published posts yet
            </Typography>
          </Box>
        )}

        {/* Show More */}
        {posts.length > 6 && !showAllPosts && (
          <Box sx={{ textAlign: 'center', mt: 5 }}>
            <Typography
              variant="body2"
              color="primary.main"
              sx={{
                cursor: 'pointer',
                fontWeight: 600,
                '&:hover': { textDecoration: 'underline' }
              }}
              onClick={() => setShowAllPosts(true)}
            >
              View all {posts.length} articles →
            </Typography>
          </Box>
        )}
      </Container>
    </Box>
  );
}
