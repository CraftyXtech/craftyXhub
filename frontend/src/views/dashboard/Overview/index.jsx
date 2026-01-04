import { useMemo } from 'react';

// MUI
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import Avatar from '@mui/material/Avatar';
import LinearProgress from '@mui/material/LinearProgress';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Skeleton from '@mui/material/Skeleton';

// Icons
import {
  IconFileText,
  IconEye,
  IconMessageCircle,
  IconHeart,
  IconPlus,
  IconTrendingUp,
  IconClock,
  IconEdit,
  IconRefresh
} from '@tabler/icons-react';

// API
import { useAuth } from '@/api/AuthProvider';
import { useDashboard } from '@/api';


// Stats card component
const StatCard = ({ icon: Icon, title, value, change, color = 'primary', loading }) => (
  <Card 
    elevation={0} 
    sx={{ 
      border: '1px solid',
      borderColor: 'divider',
      height: '100%'
    }}
  >
    <CardContent>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          {loading ? (
            <Skeleton width={60} height={40} />
          ) : (
            <Typography variant="h4" fontWeight={600}>
              {value ?? '—'}
            </Typography>
          )}
          {change && !loading && (
            <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 1 }}>
              <IconTrendingUp size={14} color="#4CAF50" />
              <Typography variant="caption" color="success.main">
                {change}
              </Typography>
            </Stack>
          )}
        </Box>
        <Avatar
          sx={{
            width: 48,
            height: 48,
            bgcolor: `${color}.lighter`,
            color: `${color}.main`
          }}
        >
          <Icon size={24} />
        </Avatar>
      </Stack>
    </CardContent>
  </Card>
);

/**
 * Dashboard Overview Page
 * Welcome dashboard with stats and quick actions
 */
export default function Overview() {
  const { user } = useAuth();
  const { data, isLoading, error, refetch } = useDashboard();
  
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }, []);

  // Extract stats from API response
  const stats = data?.post_stats || {};
  const engagement = data?.engagement || {};
  const topPosts = data?.top_posts || [];
  const draftsCount = stats.drafts || data?.drafts?.length || 0;

  // Compute display name with fallbacks
  const displayName = user?.username || user?.full_name || user?.email?.split('@')[0] || 'there';

  return (
    <Box>
      {/* Welcome Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={600}>
          {greeting}, {displayName}! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back to your dashboard.
        </Typography>
      </Box>

      {/* Quick Actions */}
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 4 }}>
        <Button
          variant="contained"
          startIcon={<IconPlus size={18} />}
          href="/dashboard/posts/create"
          sx={{ 
            py: 1.5,
            px: 3,
            borderRadius: 2
          }}
        >
          Create New Post
        </Button>
        <Button
          variant="outlined"
          startIcon={<IconEdit size={18} />}
          href="/dashboard/drafts"
          sx={{ 
            py: 1.5,
            px: 3,
            borderRadius: 2
          }}
        >
          View Drafts
        </Button>
        {error && (
          <Button
            variant="text"
            startIcon={<IconRefresh size={18} />}
            onClick={refetch}
            color="error"
          >
            Retry
          </Button>
        )}
      </Stack>

      {/* Error Alert */}
      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Could not load dashboard data: {error}
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            icon={IconFileText}
            title="Total Posts"
            value={stats.total ?? stats.published ?? 0}
            loading={isLoading}
            color="primary"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            icon={IconEye}
            title="Total Views"
            value={engagement.total_views?.toLocaleString() ?? 0}
            loading={isLoading}
            color="info"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            icon={IconMessageCircle}
            title="Comments"
            value={engagement.total_comments?.toLocaleString() ?? 0}
            loading={isLoading}
            color="success"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatCard
            icon={IconHeart}
            title="Likes"
            value={engagement.total_likes?.toLocaleString() ?? 0}
            loading={isLoading}
            color="error"
          />
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 8 }}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Recent Posts
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Your recently published posts will appear here.
              </Typography>
              
              {/* Placeholder for posts list */}
              <Box sx={{ mt: 3, textAlign: 'center', py: 4 }}>
                <IconFileText size={48} color="#9E9E9E" />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  No posts yet. Start writing!
                </Typography>
                <Button
                  variant="text"
                  href="/dashboard/posts/create"
                  sx={{ mt: 1 }}
                >
                  Create your first post
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                <IconTrendingUp size={20} />
                <Typography variant="h6" fontWeight={600}>
                  Top Posts
                </Typography>
              </Stack>
              
              {isLoading ? (
                <Stack spacing={1.5}>
                  {[1, 2, 3].map((i) => (
                    <Skeleton key={i} height={24} />
                  ))}
                </Stack>
              ) : topPosts.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No posts yet. Your top performing posts will appear here.
                </Typography>
              ) : (
                <Stack spacing={1.5}>
                  {topPosts.slice(0, 3).map((post, index) => (
                    <Box key={post.uuid} sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          width: 20, 
                          height: 20, 
                          borderRadius: '50%', 
                          bgcolor: index === 0 ? 'primary.main' : 'grey.200',
                          color: index === 0 ? 'white' : 'text.secondary',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 600,
                          fontSize: 11
                        }}
                      >
                        {index + 1}
                      </Typography>
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="body2" noWrap fontWeight={500}>
                          {post.title}
                        </Typography>
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <Typography variant="caption" color="text.secondary">
                            {post.view_count?.toLocaleString() || 0} views
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {post.like_count || 0} likes
                          </Typography>
                        </Stack>
                      </Box>
                    </Box>
                  ))}
                </Stack>
              )}
              
              {topPosts.length > 3 && (
                <Button
                  variant="text"
                  size="small"
                  href="/dashboard/posts"
                  sx={{ mt: 2, px: 0 }}
                >
                  View all posts →
                </Button>
              )}
            </CardContent>
          </Card>

          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', mt: 3 }}>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
                <IconClock size={20} />
                <Typography variant="h6" fontWeight={600}>
                  Drafts
                </Typography>
              </Stack>
              
              <Typography variant="body2" color="text.secondary">
                {isLoading ? (
                  <Skeleton width={200} />
                ) : (
                  <>You have <strong>{draftsCount} {draftsCount === 1 ? 'draft' : 'drafts'}</strong> waiting to be published.</>
                )}
              </Typography>
              
              <Button
                variant="text"
                size="small"
                href="/dashboard/drafts"
                sx={{ mt: 1, px: 0 }}
              >
                View all drafts →
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
