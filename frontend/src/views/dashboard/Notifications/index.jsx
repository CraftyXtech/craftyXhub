import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

// MUI
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Stack from '@mui/material/Stack';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemAvatar from '@mui/material/ListItemAvatar';
import ListItemText from '@mui/material/ListItemText';
import Avatar from '@mui/material/Avatar';
import Skeleton from '@mui/material/Skeleton';
import Alert from '@mui/material/Alert';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Tooltip from '@mui/material/Tooltip';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Pagination from '@mui/material/Pagination';

// Icons
import {
  IconBell,
  IconBellOff,
  IconRefresh,
  IconTrash,
  IconCheck,
  IconChecks,
  IconMoodEmpty,
  IconHeart,
  IconMessageCircle,
  IconUserPlus,
  IconFileText,
  IconAt
} from '@tabler/icons-react';

// API
import { 
  getNotifications, 
  markAsRead, 
  markAllAsRead, 
  deleteNotification,
  deleteAllNotifications 
} from '@/api/services/notificationService';

// Notification type icons mapping
const notificationIcons = {
  like: IconHeart,
  comment: IconMessageCircle,
  follow: IconUserPlus,
  mention: IconAt,
  post: IconFileText,
  default: IconBell
};

// Notification type colors
const notificationColors = {
  like: 'error',
  comment: 'info',
  follow: 'success',
  mention: 'warning',
  post: 'primary',
  default: 'default'
};

/**
 * Notifications Page
 * Full notifications management view
 */
export default function Notifications() {
  const navigate = useNavigate();
  
  const [notifications, setNotifications] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [tabValue, setTabValue] = useState(0); // 0 = all, 1 = unread
  const [actionLoading, setActionLoading] = useState({});
  
  const itemsPerPage = 20;

  // Load notifications
  const loadNotifications = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getNotifications(
        (page - 1) * itemsPerPage,
        itemsPerPage,
        tabValue === 1 // unread only
      );
      setNotifications(response.notifications || response || []);
      setTotal(response.total || 0);
    } catch (err) {
      console.error('Failed to load notifications:', err);
      setError(err.message || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  }, [page, tabValue]);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setPage(1);
  };

  // Mark single as read
  const handleMarkAsRead = async (uuid) => {
    setActionLoading(prev => ({ ...prev, [uuid]: true }));
    try {
      await markAsRead(uuid);
      setNotifications(prev => 
        prev.map(n => n.uuid === uuid ? { ...n, is_read: true } : n)
      );
    } catch (err) {
      console.error('Failed to mark as read:', err);
      setError('Failed to mark notification as read');
    } finally {
      setActionLoading(prev => ({ ...prev, [uuid]: false }));
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    setActionLoading(prev => ({ ...prev, all: true }));
    try {
      await markAllAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Failed to mark all as read:', err);
      setError('Failed to mark all as read');
    } finally {
      setActionLoading(prev => ({ ...prev, all: false }));
    }
  };

  // Delete notification
  const handleDelete = async (uuid) => {
    setActionLoading(prev => ({ ...prev, [`del_${uuid}`]: true }));
    try {
      await deleteNotification(uuid);
      setNotifications(prev => prev.filter(n => n.uuid !== uuid));
      setTotal(prev => prev - 1);
    } catch (err) {
      console.error('Failed to delete notification:', err);
      setError('Failed to delete notification');
    } finally {
      setActionLoading(prev => ({ ...prev, [`del_${uuid}`]: false }));
    }
  };

  // Delete all notifications
  const handleDeleteAll = async () => {
    if (!window.confirm('Are you sure you want to delete all notifications?')) {
      return;
    }
    setActionLoading(prev => ({ ...prev, deleteAll: true }));
    try {
      await deleteAllNotifications();
      setNotifications([]);
      setTotal(0);
    } catch (err) {
      console.error('Failed to delete all notifications:', err);
      setError('Failed to delete all notifications');
    } finally {
      setActionLoading(prev => ({ ...prev, deleteAll: false }));
    }
  };

  // Format time ago
  const formatTimeAgo = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  // Get icon for notification type
  const getNotificationIcon = (type) => {
    const Icon = notificationIcons[type] || notificationIcons.default;
    return <Icon size={20} />;
  };

  const totalPages = Math.ceil(total / itemsPerPage);
  const unreadCount = notifications.filter(n => !n.is_read).length;

  // Render loading skeleton
  const renderSkeleton = () => (
    <List>
      {[1, 2, 3, 4, 5].map((i) => (
        <ListItem key={i} sx={{ py: 2 }}>
          <ListItemAvatar>
            <Skeleton variant="circular" width={40} height={40} />
          </ListItemAvatar>
          <ListItemText
            primary={<Skeleton width="60%" />}
            secondary={<Skeleton width="40%" />}
          />
        </ListItem>
      ))}
    </List>
  );

  // Render empty state
  const renderEmptyState = () => (
    <Box sx={{ textAlign: 'center', py: 8, px: 2 }}>
      <IconBellOff size={64} color="#9E9E9E" />
      <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
        {tabValue === 1 ? 'No Unread Notifications' : 'No Notifications Yet'}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3, maxWidth: 400, mx: 'auto' }}>
        {tabValue === 1 
          ? "You're all caught up! Check back later for new notifications."
          : "When someone likes your posts, comments, or follows you, you'll see notifications here."
        }
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
        sx={{ mb: 3 }}
      >
        <Box>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
            <IconBell size={28} />
            <Typography variant="h4" fontWeight={600}>
              Notifications
            </Typography>
            {!loading && unreadCount > 0 && (
              <Chip 
                label={unreadCount} 
                color="error" 
                size="small" 
              />
            )}
          </Stack>
          <Typography variant="body1" color="text.secondary">
            {!loading && !error && `${total} notification${total !== 1 ? 's' : ''}`}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<IconChecks size={18} />}
            onClick={handleMarkAllAsRead}
            disabled={loading || actionLoading.all || unreadCount === 0}
          >
            Mark All Read
          </Button>
          <Button
            variant="outlined"
            color="error"
            size="small"
            startIcon={<IconTrash size={18} />}
            onClick={handleDeleteAll}
            disabled={loading || actionLoading.deleteAll || notifications.length === 0}
          >
            Clear All
          </Button>
          <IconButton onClick={loadNotifications} disabled={loading}>
            <IconRefresh size={20} />
          </IconButton>
        </Stack>
      </Stack>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={loadNotifications}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      )}

      {/* Tabs */}
      <Tabs 
        value={tabValue} 
        onChange={handleTabChange}
        sx={{ mb: 2, borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="All" />
        <Tab 
          label={
            <Stack direction="row" spacing={1} alignItems="center">
              <span>Unread</span>
              {unreadCount > 0 && (
                <Chip label={unreadCount} size="small" color="error" sx={{ height: 20 }} />
              )}
            </Stack>
          } 
        />
      </Tabs>

      {/* Content */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider' }}>
        {loading ? (
          renderSkeleton()
        ) : notifications.length === 0 ? (
          renderEmptyState()
        ) : (
          <>
            <List disablePadding>
              {notifications.map((notification, index) => (
                <Box key={notification.uuid || index}>
                  <ListItem
                    sx={{
                      py: 2,
                      px: 3,
                      bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                      '&:hover': {
                        bgcolor: 'action.selected'
                      }
                    }}
                    secondaryAction={
                      <Stack direction="row" spacing={0.5}>
                        {!notification.is_read && (
                          <Tooltip title="Mark as read">
                            <IconButton
                              size="small"
                              onClick={() => handleMarkAsRead(notification.uuid)}
                              disabled={actionLoading[notification.uuid]}
                            >
                              <IconCheck size={18} />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDelete(notification.uuid)}
                            disabled={actionLoading[`del_${notification.uuid}`]}
                          >
                            <IconTrash size={18} />
                          </IconButton>
                        </Tooltip>
                      </Stack>
                    }
                  >
                    <ListItemAvatar>
                      <Avatar
                        sx={{ 
                          bgcolor: `${notificationColors[notification.type] || 'default'}.lighter`,
                          color: `${notificationColors[notification.type] || 'default'}.main`
                        }}
                      >
                        {getNotificationIcon(notification.type)}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Typography 
                          variant="body1"
                          fontWeight={notification.is_read ? 400 : 600}
                        >
                          {notification.title || notification.message}
                        </Typography>
                      }
                      secondary={
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {formatTimeAgo(notification.created_at)}
                          </Typography>
                          {notification.type && (
                            <Chip 
                              label={notification.type} 
                              size="small" 
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.65rem' }}
                            />
                          )}
                        </Stack>
                      }
                    />
                  </ListItem>
                  {index < notifications.length - 1 && <Divider />}
                </Box>
              ))}
            </List>

            {/* Pagination */}
            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
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
      </Card>
    </Box>
  );
}
