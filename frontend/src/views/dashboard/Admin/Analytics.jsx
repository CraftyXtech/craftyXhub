import { useState, useEffect, useCallback } from 'react';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Stack from '@mui/material/Stack';
import Grid from '@mui/material/Grid';
import Avatar from '@mui/material/Avatar';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Skeleton from '@mui/material/Skeleton';
import Alert from '@mui/material/Alert';

// Icons
import {
  IconEye,
  IconFileText,
  IconUsers,
  IconMessageCircle,
  IconHeart,
  IconTrendingUp,
  IconCalendar,
  IconBookmark
} from '@tabler/icons-react';

// API
import { getAdminDashboard } from '@/api/services/dashboardService';

// Stat Card component
const StatCard = ({ icon: Icon, title, value, change, color = 'primary' }) => (
  <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', height: '100%' }}>
    <CardContent>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight={600}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Typography>
          {change && (
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
 * Analytics Dashboard (Admin Only)
 */
export default function Analytics() {
  // State
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('30d');
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  // Fetch analytics
  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAdminDashboard();
      setData(response);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
      setError('Failed to load analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  // Map API response to stats structure
  const stats = {
    total_views: data?.engagement_metrics?.total_views || 0,
    total_posts: data?.posts_overview?.total_posts || 0,
    total_users: data?.overview?.total_users || 0,
    total_comments: data?.engagement_metrics?.total_comments || 0,
    total_likes: data?.engagement_metrics?.total_likes || 0,
    total_bookmarks: data?.engagement_metrics?.total_bookmarks || 0
  };

  const topPosts = data?.top_posts || [];
  const recentActivity = data?.recent_activity || [];

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Analytics
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Site performance overview
          </Typography>
        </Box>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <Select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <MenuItem value="7d">Last 7 days</MenuItem>
            <MenuItem value="30d">Last 30 days</MenuItem>
            <MenuItem value="90d">Last 90 days</MenuItem>
            <MenuItem value="1y">Last year</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {loading ? (
          [...Array(6)].map((_, i) => (
            <Grid item xs={12} sm={6} md={4} lg={2} key={i}>
              <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
                <CardContent>
                  <Skeleton width="60%" height={20} />
                  <Skeleton width="40%" height={40} sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
          ))
        ) : (
          <>
            <Grid item xs={12} sm={6} md={4} lg={2}>
              <StatCard
                icon={IconEye}
                title="Total Views"
                value={stats.total_views}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2}>
              <StatCard
                icon={IconFileText}
                title="Total Posts"
                value={stats.total_posts}
                color="info"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2}>
              <StatCard
                icon={IconUsers}
                title="Total Users"
                value={stats.total_users}
                color="success"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2}>
              <StatCard
                icon={IconMessageCircle}
                title="Comments"
                value={stats.total_comments}
                color="warning"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2}>
              <StatCard
                icon={IconHeart}
                title="Total Likes"
                value={stats.total_likes}
                color="error"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2}>
              <StatCard
                icon={IconBookmark}
                title="Bookmarks"
                value={stats.total_bookmarks}
                color="secondary"
              />
            </Grid>
          </>
        )}
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                Top Performing Posts
              </Typography>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <Stack key={i} direction="row" spacing={2} sx={{ mb: 2 }}>
                    <Skeleton width={40} height={40} variant="rounded" />
                    <Box sx={{ flex: 1 }}>
                      <Skeleton width="80%" />
                      <Skeleton width="40%" height={16} />
                    </Box>
                  </Stack>
                ))
              ) : topPosts.length ? (
                topPosts.slice(0, 5).map((post, i) => (
                  <Stack key={post.uuid || i} direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                    <Avatar variant="rounded" sx={{ bgcolor: 'primary.lighter', color: 'primary.main' }}>
                      {i + 1}
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" fontWeight={500} noWrap>
                        {post.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {(post.view_count || 0).toLocaleString()} views • {(post.like_count || 0).toLocaleString()} likes
                      </Typography>
                    </Box>
                  </Stack>
                ))
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
                  No data available for the selected period
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
                Recent Activity
              </Typography>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <Stack key={i} direction="row" spacing={2} sx={{ mb: 2 }}>
                    <Skeleton width={40} height={40} variant="circular" />
                    <Box sx={{ flex: 1 }}>
                      <Skeleton width="70%" />
                      <Skeleton width="30%" height={16} />
                    </Box>
                  </Stack>
                ))
              ) : recentActivity.length ? (
                recentActivity.slice(0, 5).map((activity, i) => (
                  <Stack key={activity.id || i} direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                    <Avatar sx={{ bgcolor: 'grey.100', color: 'grey.600' }}>
                      <IconCalendar size={20} />
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" fontWeight={500} noWrap>
                        {activity.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {activity.type} • {activity.description}
                      </Typography>
                    </Box>
                  </Stack>
                ))
              ) : (
                <Box sx={{ py: 4, textAlign: 'center' }}>
                  <IconCalendar size={40} color="#9E9E9E" style={{ marginBottom: 8 }} />
                  <Typography variant="body2" color="text.secondary">
                    No recent activity
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
