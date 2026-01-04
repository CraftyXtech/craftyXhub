import React, { useState, useEffect } from 'react';
import { useLocation, Link as RouterLink, useNavigate } from 'react-router-dom';

// MUI
import { styled } from '@mui/material/styles';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import Avatar from '@mui/material/Avatar';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import Divider from '@mui/material/Divider';
import Badge from '@mui/material/Badge';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Link from '@mui/material/Link';
import Tooltip from '@mui/material/Tooltip';
import Button from '@mui/material/Button';

// Icons
import {
  IconMenu2,
  IconBell,
  IconUser,
  IconSettings,
  IconLogout,
  IconHome,
  IconChevronRight,
  IconEdit,
  IconSearch,
  IconCompass,
  IconExternalLink
} from '@tabler/icons-react';

// Auth & API
import { useAuth } from '@/api/AuthProvider';
import { dashboardTokens } from '@/config/dashboard';
import { getNotificationStats } from '@/api/services/notificationService';

// Styled AppBar
const StyledAppBar = styled(AppBar)(({ theme }) => ({
  backgroundColor: dashboardTokens.header.background,
  boxShadow: dashboardTokens.header.shadow,
  color: theme.palette.text.primary,
  zIndex: theme.zIndex.drawer + 1
}));

/**
 * Dashboard Header Component
 */
export default function Header({ onMenuClick }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [searchAnchorEl, setSearchAnchorEl] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);

  // Fetch unread notification count
  useEffect(() => {
    const fetchUnreadCount = async () => {
      try {
        const stats = await getNotificationStats();
        setUnreadCount(stats.unread || 0);
      } catch (err) {
        console.error('Failed to fetch notification stats:', err);
      }
    };

    fetchUnreadCount();
    
    // Refresh every 60 seconds
    const interval = setInterval(fetchUnreadCount, 60000);
    return () => clearInterval(interval);
  }, []);

  // Search dropdown handlers
  const handleSearchClick = (event) => {
    setSearchAnchorEl(event.currentTarget);
  };

  const handleSearchClose = () => {
    setSearchAnchorEl(null);
  };

  const handleExploreTopics = () => {
    handleSearchClose();
    navigate('/#categories');
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
  };

  const handleNotificationsClick = () => {
    navigate('/dashboard/notifications');
  };

  // Generate breadcrumbs from path
  const generateBreadcrumbs = () => {
    const pathnames = location.pathname.split('/').filter((x) => x);
    
    return pathnames.map((value, index) => {
      const to = `/${pathnames.slice(0, index + 1).join('/')}`;
      const isLast = index === pathnames.length - 1;
      const label = value.charAt(0).toUpperCase() + value.slice(1).replace(/-/g, ' ');

      return isLast ? (
        <Typography key={to} color="text.primary" sx={{ fontSize: 14, fontWeight: 500 }}>
          {label}
        </Typography>
      ) : (
        <Link
          key={to}
          component={RouterLink}
          to={to}
          underline="hover"
          color="text.secondary"
          sx={{ fontSize: 14 }}
        >
          {label}
        </Link>
      );
    });
  };

  return (
    <StyledAppBar position="fixed">
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left side - Menu button and breadcrumbs */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={onMenuClick} edge="start" color="inherit">
            <IconMenu2 size={22} />
          </IconButton>

          {/* Breadcrumbs - hidden on mobile */}
          <Box sx={{ display: { xs: 'none', md: 'block' } }}>
            <Breadcrumbs
              separator={<IconChevronRight size={14} />}
              sx={{ '& .MuiBreadcrumbs-separator': { mx: 0.5 } }}
            >
              <Link
                component={RouterLink}
                to="/dashboard"
                underline="hover"
                color="text.secondary"
                sx={{ display: 'flex', alignItems: 'center', fontSize: 14 }}
              >
                <IconHome size={16} style={{ marginRight: 4 }} />
                Dashboard
              </Link>
              {location.pathname !== '/dashboard' && generateBreadcrumbs().slice(1)}
            </Breadcrumbs>
          </Box>

          {/* Search Input - Medium style */}
          <Box
            onClick={handleSearchClick}
            sx={{
              display: { xs: 'none', sm: 'flex' },
              alignItems: 'center',
              bgcolor: 'grey.100',
              borderRadius: 5,
              px: 1.5,
              py: 0.75,
              ml: 2,
              minWidth: 200,
              cursor: 'pointer',
              '&:hover': {
                bgcolor: 'grey.200'
              }
            }}
          >
            <IconSearch size={18} style={{ color: '#666', marginRight: 8 }} />
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Search
            </Typography>
          </Box>

          {/* Search Dropdown Menu */}
          <Menu
            anchorEl={searchAnchorEl}
            open={Boolean(searchAnchorEl)}
            onClose={handleSearchClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
            transformOrigin={{ vertical: 'top', horizontal: 'left' }}
            PaperProps={{
              sx: {
                mt: 1,
                minWidth: 220,
                borderRadius: 2,
                boxShadow: 3
              }
            }}
          >
            <MenuItem onClick={handleExploreTopics} sx={{ py: 1.5 }}>
              <ListItemIcon>
                <IconCompass size={20} />
              </ListItemIcon>
              <Typography variant="body2">Explore topics</Typography>
              <Box sx={{ flex: 1 }} />
              <IconExternalLink size={16} style={{ color: '#999' }} />
            </MenuItem>
          </Menu>
        </Box>

        {/* Right side - Write button, Notifications and user menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Write Button */}
          <Button
            variant="text"
            startIcon={<IconEdit size={18} />}
            onClick={() => {
              const role = user?.role || 'user';
              if (role === 'admin' || role === 'moderator') {
                navigate('/dashboard/ai-writer');
              } else {
                navigate('/dashboard/posts/create');
              }
            }}
            sx={{
              color: 'text.primary',
              fontWeight: 500,
              textTransform: 'none',
              '&:hover': {
                backgroundColor: 'action.hover'
              }
            }}
          >
            Write
          </Button>

          {/* Notifications */}
          <Tooltip title={unreadCount > 0 ? `${unreadCount} unread notifications` : 'Notifications'}>
            <IconButton 
              color="inherit" 
              onClick={handleNotificationsClick}
              sx={{
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }}
            >
              <Badge 
                badgeContent={unreadCount} 
                color="error" 
                max={99}
                invisible={unreadCount === 0}
              >
                <IconBell size={20} />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Avatar */}
          <IconButton onClick={handleMenuOpen} sx={{ ml: 1 }}>
            <Avatar
              src={user?.avatar}
              alt={user?.full_name || user?.username}
              sx={{
                width: 36,
                height: 36,
                bgcolor: 'primary.main',
                fontSize: 14
              }}
            >
              {(user?.full_name || user?.username || 'U')[0].toUpperCase()}
            </Avatar>
          </IconButton>

          {/* User Dropdown Menu */}
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            onClick={handleMenuClose}
            PaperProps={{
              elevation: 3,
              sx: {
                minWidth: 200,
                mt: 1.5,
                borderRadius: 2,
                overflow: 'visible',
                '&:before': {
                  content: '""',
                  display: 'block',
                  position: 'absolute',
                  top: 0,
                  right: 14,
                  width: 10,
                  height: 10,
                  bgcolor: 'background.paper',
                  transform: 'translateY(-50%) rotate(45deg)',
                  zIndex: 0
                }
              }
            }}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            {/* User info */}
            <Box sx={{ px: 2, py: 1.5 }}>
              <Typography variant="subtitle2" noWrap>
                {user?.username || user?.full_name || user?.email?.split('@')[0]}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                {user?.email}
              </Typography>
            </Box>

            <Divider />

            <MenuItem component={RouterLink} to="/">
              <ListItemIcon>
                <IconHome size={18} />
              </ListItemIcon>
              Home
            </MenuItem>

            <MenuItem component={RouterLink} to="/dashboard/profile">
              <ListItemIcon>
                <IconUser size={18} />
              </ListItemIcon>
              Profile
            </MenuItem>

            <MenuItem component={RouterLink} to="/dashboard/notifications">
              <ListItemIcon>
                <Badge badgeContent={unreadCount} color="error" max={9}>
                  <IconBell size={18} />
                </Badge>
              </ListItemIcon>
              Notifications
            </MenuItem>

            <MenuItem component={RouterLink} to="/dashboard/settings">
              <ListItemIcon>
                <IconSettings size={18} />
              </ListItemIcon>
              Settings
            </MenuItem>

            <Divider />

            <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
              <ListItemIcon>
                <IconLogout size={18} color="currentColor" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </StyledAppBar>
  );
}
