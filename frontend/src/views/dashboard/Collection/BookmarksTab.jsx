import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import CardActionArea from '@mui/material/CardActionArea';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import Skeleton from '@mui/material/Skeleton';

// Icons
import { IconBookmark, IconBookmarkOff } from '@tabler/icons-react';

// API
import { getUserBookmarks, bookmarkPost } from '@/api/services/postService';
import { getImageUrl } from '@/api/services/postService';

/**
 * Bookmarks Tab
 * Display user's bookmarked posts (quick saves)
 */
export default function BookmarksTab() {
  const navigate = useNavigate();
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  const fetchBookmarks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getUserBookmarks({ limit: 50 });
      setBookmarks(data.posts || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Failed to fetch bookmarks:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBookmarks();
  }, [fetchBookmarks]);

  const handleRemoveBookmark = async (e, postUuid) => {
    e.stopPropagation();
    try {
      await bookmarkPost(postUuid);
      fetchBookmarks();
    } catch (err) {
      console.error('Failed to remove bookmark:', err);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <Grid container spacing={3}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <Skeleton variant="rounded" height={280} />
          </Grid>
        ))}
      </Grid>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h6">
          {total} Bookmarked Post{total !== 1 ? 's' : ''}
        </Typography>
      </Stack>

      {/* Empty State */}
      {bookmarks.length === 0 ? (
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', textAlign: 'center', py: 8 }}>
          <IconBookmark size={48} color="#9E9E9E" />
          <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
            No Bookmarks Yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Bookmark posts to quickly save them for later reading.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/')}>
            Explore Posts
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {bookmarks.map((post) => (
            <Grid item xs={12} sm={6} md={4} key={post.uuid}>
              <Card 
                elevation={0} 
                sx={{ 
                  border: '1px solid', 
                  borderColor: 'divider',
                  height: '100%',
                  '&:hover': { borderColor: 'primary.main' }
                }}
              >
                <CardActionArea onClick={() => navigate(`/blog/${post.slug}`)}>
                  {post.featured_image && (
                    <CardMedia
                      component="img"
                      height="140"
                      image={getImageUrl(post.featured_image)}
                      alt={post.title}
                    />
                  )}
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          fontSize: '1rem',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical'
                        }}
                      >
                        {post.title}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) => handleRemoveBookmark(e, post.uuid)}
                        sx={{ color: '#f39F5A' }}
                      >
                        <IconBookmarkOff size={20} />
                      </IconButton>
                    </Stack>
                    {post.excerpt && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          mt: 1,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical'
                        }}
                      >
                        {post.excerpt}
                      </Typography>
                    )}
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                      {formatDate(post.created_at)}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}
