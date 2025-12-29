import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
import Avatar from '@mui/material/Avatar';
import Skeleton from '@mui/material/Skeleton';
import Alert from '@mui/material/Alert';
import Pagination from '@mui/material/Pagination';

// Icons
import {
  IconUserPlus,
  IconRefresh,
  IconUserMinus,
  IconMoodEmpty
} from '@tabler/icons-react';

// API
import { useAuth } from '@/api/AuthProvider';
import { getFollowing, unfollowUser } from '@/api/services/userService';

/**
 * Following Page
 * Display list of users the current user is following
 */
export default function Following() {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [following, setFollowing] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [unfollowingId, setUnfollowingId] = useState(null);
  
  const itemsPerPage = 12;

  // Load following
  const loadFollowing = useCallback(async () => {
    if (!user?.uuid) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await getFollowing(user.uuid, {
        skip: (page - 1) * itemsPerPage,
        limit: itemsPerPage
      });
      setFollowing(response.following || response || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Failed to load following:', err);
      setError(err.message || 'Failed to load following');
    } finally {
      setLoading(false);
    }
  }, [user?.uuid, page]);

  useEffect(() => {
    loadFollowing();
  }, [loadFollowing]);

  // Unfollow user
  const handleUnfollow = async (followingUuid) => {
    setUnfollowingId(followingUuid);
    try {
      await unfollowUser(followingUuid);
      // Remove from local state
      setFollowing(prev => prev.filter(u => u.uuid !== followingUuid));
      setTotal(prev => prev - 1);
    } catch (err) {
      console.error('Failed to unfollow:', err);
      setError('Failed to unfollow user. Please try again.');
    } finally {
      setUnfollowingId(null);
    }
  };

  // View user profile
  const handleViewProfile = (username) => {
    navigate(`/author/${username}`);
  };

  const totalPages = Math.ceil(total / itemsPerPage);

  // Render loading skeleton
  const renderSkeleton = () => (
    <Grid container spacing={3}>
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Grid key={i} size={{ xs: 12, sm: 6, md: 4 }}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Stack direction="row" spacing={2} alignItems="center">
                <Skeleton variant="circular" width={56} height={56} />
                <Box sx={{ flexGrow: 1 }}>
                  <Skeleton width="60%" height={24} />
                  <Skeleton width="40%" />
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  // Render empty state
  const renderEmptyState = () => (
    <Box sx={{ textAlign: 'center', py: 8, px: 2 }}>
      <IconMoodEmpty size={64} color="#9E9E9E" />
      <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
        Not Following Anyone Yet
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}>
        Follow authors whose content you enjoy to see their posts in your feed and stay updated with their latest work.
      </Typography>
      <Button
        variant="contained"
        onClick={() => navigate('/')}
      >
        Discover Authors
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
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
            <IconUserPlus size={28} />
            <Typography variant="h4" fontWeight={600}>
              Following
            </Typography>
          </Stack>
          <Typography variant="body1" color="text.secondary">
            {!loading && !error && (
              <>You are following {total} {total === 1 ? 'person' : 'people'}</>
            )}
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<IconRefresh size={18} />}
          onClick={loadFollowing}
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
            <Button color="inherit" size="small" onClick={loadFollowing}>
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
      ) : following.length === 0 ? (
        renderEmptyState()
      ) : (
        <>
          <Grid container spacing={3}>
            {following.map((followedUser) => (
              <Grid key={followedUser.uuid || followedUser.id} size={{ xs: 12, sm: 6, md: 4 }}>
                <Card 
                  elevation={0}
                  sx={{ 
                    border: '1px solid',
                    borderColor: 'divider',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      borderColor: 'primary.main',
                      boxShadow: 2
                    }
                  }}
                >
                  <CardContent>
                    <Stack direction="row" spacing={2} alignItems="center">
                      <Avatar
                        src={followedUser.avatar_url}
                        sx={{ 
                          width: 56, 
                          height: 56,
                          cursor: 'pointer'
                        }}
                        onClick={() => handleViewProfile(followedUser.username)}
                      >
                        {followedUser.full_name?.[0] || followedUser.username?.[0] || '?'}
                      </Avatar>
                      <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                        <Typography 
                          variant="subtitle1" 
                          fontWeight={600}
                          sx={{ 
                            cursor: 'pointer',
                            '&:hover': { color: 'primary.main' },
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                          onClick={() => handleViewProfile(followedUser.username)}
                        >
                          {followedUser.full_name || followedUser.username}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          color="text.secondary"
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          @{followedUser.username}
                        </Typography>
                        {followedUser.bio && (
                          <Typography 
                            variant="caption" 
                            color="text.secondary"
                            sx={{
                              display: '-webkit-box',
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                              mt: 0.5
                            }}
                          >
                            {followedUser.bio}
                          </Typography>
                        )}
                      </Box>
                    </Stack>
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        startIcon={<IconUserMinus size={16} />}
                        onClick={() => handleUnfollow(followedUser.uuid)}
                        disabled={unfollowingId === followedUser.uuid}
                      >
                        Unfollow
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          )}
        </>
      )}
    </Box>
  );
}
