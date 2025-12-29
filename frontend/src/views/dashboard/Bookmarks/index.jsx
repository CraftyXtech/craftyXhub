import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import CardActions from '@mui/material/CardActions';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import Skeleton from '@mui/material/Skeleton';
import Alert from '@mui/material/Alert';
import Tooltip from '@mui/material/Tooltip';

// Icons
import {
  IconBookmark,
  IconBookmarkOff,
  IconEye,
  IconRefresh,
  IconMoodEmpty,
  IconArrowRight
} from '@tabler/icons-react';

// API
import { getUserBookmarks, bookmarkPost, getImageUrl } from '@/api/services/postService';

/**
 * Bookmarks Page
 * Display user's saved/bookmarked posts
 */
export default function Bookmarks() {
  const navigate = useNavigate();
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [removingId, setRemovingId] = useState(null);

  // Load bookmarks
  const loadBookmarks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getUserBookmarks();
      setBookmarks(response.posts || response || []);
    } catch (err) {
      console.error('Failed to load bookmarks:', err);
      setError(err.message || 'Failed to load bookmarks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBookmarks();
  }, [loadBookmarks]);

  // Remove bookmark
  const handleRemoveBookmark = async (postUuid) => {
    setRemovingId(postUuid);
    try {
      await bookmarkPost(postUuid);
      // Remove from local state
      setBookmarks(prev => prev.filter(post => post.uuid !== postUuid));
    } catch (err) {
      console.error('Failed to remove bookmark:', err);
      setError('Failed to remove bookmark. Please try again.');
    } finally {
      setRemovingId(null);
    }
  };

  // View post
  const handleViewPost = (post) => {
    navigate(`/post/${post.slug || post.uuid}`);
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Render loading skeleton
  const renderSkeleton = () => (
    <Grid container spacing={3}>
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Grid key={i} size={{ xs: 12, sm: 6, md: 4 }}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <Skeleton variant="rectangular" height={180} />
            <CardContent>
              <Skeleton width="60%" height={24} sx={{ mb: 1 }} />
              <Skeleton width="100%" />
              <Skeleton width="80%" />
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  // Render empty state
  const renderEmptyState = () => (
    <Box 
      sx={{ 
        textAlign: 'center', 
        py: 8,
        px: 2
      }}
    >
      <IconMoodEmpty size={64} color="#9E9E9E" />
      <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
        No Bookmarks Yet
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}>
        Start bookmarking articles to save them for later reading. Browse our posts to find something interesting!
      </Typography>
      <Button
        variant="contained"
        endIcon={<IconArrowRight size={18} />}
        onClick={() => navigate('/')}
      >
        Explore Posts
      </Button>
    </Box>
  );

  return (
    <Box>
      {/* Header */}
      <Stack 
        direction={{ xs: 'column', sm: 'row' }} 
        justifyContent="space-between" 
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        spacing={2}
        sx={{ mb: 4 }}
      >
        <Box>
          <Typography variant="h4" fontWeight={600} gutterBottom>
            My Bookmarks
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {!loading && !error && (
              <>
                {bookmarks.length} saved article{bookmarks.length !== 1 ? 's' : ''}
              </>
            )}
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<IconRefresh size={18} />}
          onClick={loadBookmarks}
          disabled={loading}
        >
          Refresh
        </Button>
      </Stack>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={loadBookmarks}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      )}

      {/* Content */}
      {loading ? (
        renderSkeleton()
      ) : bookmarks.length === 0 ? (
        renderEmptyState()
      ) : (
        <Grid container spacing={3}>
          {bookmarks.map((post) => (
            <Grid key={post.uuid || post.id} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card 
                elevation={0}
                sx={{ 
                  border: '1px solid',
                  borderColor: 'divider',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    boxShadow: 2
                  }
                }}
              >
                {/* Image */}
                {post.featured_image && (
                  <CardMedia
                    component="img"
                    height="180"
                    image={getImageUrl(post.featured_image)}
                    alt={post.title}
                    sx={{ 
                      cursor: 'pointer',
                      objectFit: 'cover'
                    }}
                    onClick={() => handleViewPost(post)}
                  />
                )}
                
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Category */}
                  {post.category && (
                    <Chip
                      label={post.category.name || post.category}
                      size="small"
                      color="primary"
                      variant="outlined"
                      sx={{ mb: 1.5, fontSize: '0.7rem' }}
                    />
                  )}
                  
                  {/* Title */}
                  <Typography 
                    variant="subtitle1" 
                    fontWeight={600}
                    sx={{ 
                      mb: 1,
                      cursor: 'pointer',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      '&:hover': {
                        color: 'primary.main'
                      }
                    }}
                    onClick={() => handleViewPost(post)}
                  >
                    {post.title}
                  </Typography>
                  
                  {/* Excerpt */}
                  {post.excerpt && (
                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                      sx={{ 
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}
                    >
                      {post.excerpt}
                    </Typography>
                  )}
                  
                  {/* Meta */}
                  <Stack direction="row" spacing={2} alignItems="center">
                    {post.author && (
                      <Typography variant="caption" color="text.secondary">
                        By {post.author.full_name || post.author.username || post.author}
                      </Typography>
                    )}
                    {post.published_at && (
                      <Typography variant="caption" color="text.secondary">
                        {formatDate(post.published_at)}
                      </Typography>
                    )}
                  </Stack>
                </CardContent>
                
                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Button
                    size="small"
                    startIcon={<IconEye size={16} />}
                    onClick={() => handleViewPost(post)}
                  >
                    Read
                  </Button>
                  <Tooltip title="Remove bookmark">
                    <IconButton
                      size="small"
                      color="warning"
                      onClick={() => handleRemoveBookmark(post.uuid)}
                      disabled={removingId === post.uuid}
                    >
                      <IconBookmarkOff size={18} />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
