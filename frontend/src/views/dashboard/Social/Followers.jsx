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
import Chip from '@mui/material/Chip';
import Pagination from '@mui/material/Pagination';

// Icons
import {
  IconUsers,
  IconRefresh,
  IconUserPlus,
  IconUserCheck,
  IconMoodEmpty
} from '@tabler/icons-react';

// API
import { useAuth } from '@/api/AuthProvider';
import { getFollowers, followUser, unfollowUser } from '@/api/services/userService';

/**
 * Followers Page
 * Display list of users following the current user
 */
export default function Followers() {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [followers, setFollowers] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [followingStates, setFollowingStates] = useState({});
  const [loadingFollow, setLoadingFollow] = useState({});
  
  const itemsPerPage = 12;

  // Load followers
  const loadFollowers = useCallback(async () => {
    if (!user?.uuid) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await getFollowers(user.uuid, {
        skip: (page - 1) * itemsPerPage,
        limit: itemsPerPage
      });
      setFollowers(response.followers || response || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Failed to load followers:', err);
      setError(err.message || 'Failed to load followers');
    } finally {
      setLoading(false);
    }
  }, [user?.uuid, page]);

  useEffect(() => {
    loadFollowers();
  }, [loadFollowers]);

  // Toggle follow/unfollow
  const handleFollowToggle = async (followerUuid) => {
    setLoadingFollow(prev => ({ ...prev, [followerUuid]: true }));
    try {
      const isCurrentlyFollowing = followingStates[followerUuid];
      if (isCurrentlyFollowing) {
        await unfollowUser(followerUuid);
      } else {
        await followUser(followerUuid);
      }
      setFollowingStates(prev => ({ ...prev, [followerUuid]: !isCurrentlyFollowing }));
    } catch (err) {
      console.error('Failed to toggle follow:', err);
      setError('Failed to update follow status');
    } finally {
      setLoadingFollow(prev => ({ ...prev, [followerUuid]: false }));
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
        No Followers Yet
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}>
        When people follow you, they'll appear here. Share your posts and engage with the community to grow your following!
      </Typography>
      <Button
        variant="contained"
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
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
            <IconUsers size={28} />
            <Typography variant="h4" fontWeight={600}>
              Followers
            </Typography>
          </Stack>
          <Typography variant="body1" color="text.secondary">
            {!loading && !error && (
              <>{total} {total === 1 ? 'person follows' : 'people follow'} you</>
            )}
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<IconRefresh size={18} />}
          onClick={loadFollowers}
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
            <Button color="inherit" size="small" onClick={loadFollowers}>
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
      ) : followers.length === 0 ? (
        renderEmptyState()
      ) : (
        <>
          <Grid container spacing={3}>
            {followers.map((follower) => (
              <Grid key={follower.uuid || follower.id} size={{ xs: 12, sm: 6, md: 4 }}>
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
                        src={follower.avatar_url}
                        sx={{ 
                          width: 56, 
                          height: 56,
                          cursor: 'pointer'
                        }}
                        onClick={() => handleViewProfile(follower.username)}
                      >
                        {follower.full_name?.[0] || follower.username?.[0] || '?'}
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
                          onClick={() => handleViewProfile(follower.username)}
                        >
                          {follower.full_name || follower.username}
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
                          @{follower.username}
                        </Typography>
                        {follower.bio && (
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
                            {follower.bio}
                          </Typography>
                        )}
                      </Box>
                    </Stack>
                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                      <Button
                        size="small"
                        variant={followingStates[follower.uuid] ? "outlined" : "contained"}
                        startIcon={followingStates[follower.uuid] ? <IconUserCheck size={16} /> : <IconUserPlus size={16} />}
                        onClick={() => handleFollowToggle(follower.uuid)}
                        disabled={loadingFollow[follower.uuid]}
                      >
                        {followingStates[follower.uuid] ? 'Following' : 'Follow Back'}
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
