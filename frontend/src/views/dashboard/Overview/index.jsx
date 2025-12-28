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
import Chip from '@mui/material/Chip';
import LinearProgress from '@mui/material/LinearProgress';

// Icons
import {
  IconFileText,
  IconEye,
  IconMessageCircle,
  IconHeart,
  IconPlus,
  IconTrendingUp,
  IconClock,
  IconEdit
} from '@tabler/icons-react';

// Auth
import { useAuth } from '@/api/AuthProvider';

// Role display names
const roleLabels = {
  user: 'Author',
  moderator: 'Editor',
  admin: 'Admin'
};

// Stats card component
const StatCard = ({ icon: Icon, title, value, change, color = 'primary' }) => (
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
          <Typography variant="h4" fontWeight={600}>
            {value}
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
 * Dashboard Overview Page
 * Welcome dashboard with stats and quick actions
 */
export default function Overview() {
  const { user } = useAuth();
  
  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }, []);

  const roleLabel = roleLabels[user?.role?.toLowerCase()] || 'Author';

  return (
    <Box>
      {/* Welcome Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight={600}>
          {greeting}, {user?.full_name || user?.username || 'there'}! 👋
        </Typography>
        <Stack direction="row" alignItems="center" spacing={1}>
          <Typography variant="body1" color="text.secondary">
            Welcome back to your dashboard.
          </Typography>
          <Chip 
            label={roleLabel} 
            size="small" 
            color="primary" 
            variant="outlined"
          />
        </Stack>
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
      </Stack>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={IconFileText}
            title="Total Posts"
            value="24"
            change="+3 this week"
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={IconEye}
            title="Total Views"
            value="1,842"
            change="+12% from last month"
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={IconMessageCircle}
            title="Comments"
            value="156"
            change="+8 new"
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={IconHeart}
            title="Likes"
            value="489"
            change="+23 this week"
            color="error"
          />
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
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

        <Grid item xs={12} md={4}>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Writing Goals
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2">Weekly posts</Typography>
                  <Typography variant="body2" fontWeight={600}>2/3</Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={66} 
                  sx={{ 
                    height: 8, 
                    borderRadius: 4,
                    bgcolor: 'grey.200'
                  }} 
                />
              </Box>

              <Box sx={{ mt: 3 }}>
                <Stack direction="row" justifyContent="space-between" sx={{ mb: 1 }}>
                  <Typography variant="body2">Monthly views goal</Typography>
                  <Typography variant="body2" fontWeight={600}>1,842/2,500</Typography>
                </Stack>
                <LinearProgress 
                  variant="determinate" 
                  value={74} 
                  color="success"
                  sx={{ 
                    height: 8, 
                    borderRadius: 4,
                    bgcolor: 'grey.200'
                  }} 
                />
              </Box>
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
                You have <strong>3 drafts</strong> waiting to be published.
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
