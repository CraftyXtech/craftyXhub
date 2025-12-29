import { useState, useEffect, useMemo } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  Menu,
  MenuItem,
  Collapse,
  Skeleton,
  Avatar,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { 
  IconMenu2, 
  IconX, 
  IconChevronDown, 
  IconChevronRight,
  IconPencil,
  IconDashboard,
  IconUser,
  IconLogout,
  IconBell
} from '@tabler/icons-react';
import Logo from '@/components/Logo';
import { getCategories } from '@/api/services/categoryService';
import { useAuth } from '@/api/AuthProvider';

// Static nav items - only Home, categories come from API
const staticNavItems = [
  { label: 'Home', path: '/' }
];

/**
 * Transform API categories to navigation menu format
 * @param {Array} apiCategories - Categories from API
 * @returns {Array} - Formatted nav items with optional dropdowns
 */
const transformCategoriesToNav = (apiCategories) => {
  if (!Array.isArray(apiCategories)) return [];
  
  return apiCategories.map(category => ({
    label: category.name,
    path: `/category/${category.slug}`,
    dropdown: category.subcategories?.length > 0 
      ? category.subcategories.map(sub => ({
          label: sub.name,
          path: `/category/${sub.slug}`
        }))
      : null
  }));
};

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Desktop dropdown menu state
  const [anchorEl, setAnchorEl] = useState(null);
  const [openMenuIndex, setOpenMenuIndex] = useState(null);
  
  // User avatar menu state
  const [userAnchorEl, setUserAnchorEl] = useState(null);
  
  // Mobile accordion state
  const [mobileExpandedIndex, setMobileExpandedIndex] = useState(null);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Auth state
  const { isAuthenticated, user, logout } = useAuth();

  // Fetch categories on mount
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        const data = await getCategories();
        const navCategories = transformCategoriesToNav(data.categories || []);
        setCategories(navCategories);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch categories:', err);
        setError(err.message);
        setCategories([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCategories();
  }, []);

  // Combine static nav items with dynamic categories
  const navItems = useMemo(() => {
    return [...staticNavItems, ...categories];
  }, [categories]);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
    setMobileExpandedIndex(null);
  };

  // Desktop dropdown handlers
  const handleMenuOpen = (event, index) => {
    setAnchorEl(event.currentTarget);
    setOpenMenuIndex(index);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setOpenMenuIndex(null);
  };

  // User menu handlers
  const handleUserMenuOpen = (event) => {
    setUserAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserAnchorEl(null);
  };

  const handleLogout = () => {
    handleUserMenuClose();
    logout();
  };

  // Mobile accordion toggle
  const handleMobileExpand = (index) => {
    setMobileExpandedIndex(mobileExpandedIndex === index ? null : index);
  };

  return (
    <>
      <AppBar 
        position="sticky" 
        color="inherit" 
        sx={{ 
          bgcolor: 'background.default',
          backdropFilter: 'blur(8px)'
        }}
      >
        {/* Full-width Toolbar with edge-to-edge layout like Medium */}
        <Toolbar 
          disableGutters 
          sx={{ 
            justifyContent: 'space-between',
            px: { xs: 2, sm: 3, md: 4 },  // Padding from viewport edges
            minHeight: { xs: 56, md: 64 }
          }}
        >
          {/* Logo - Absolute Left */}
          <Box sx={{ 
            position: 'absolute', 
            left: { xs: 16, sm: 24, md: 32 },
            display: 'flex',
            alignItems: 'center'
          }}>
            <RouterLink to="/" style={{ display: 'flex', alignItems: 'center' }}>
              <Logo />
            </RouterLink>
          </Box>

          {/* Desktop Navigation - Centered */}
          {!isMobile && (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              flex: 1
            }}>
              {/* Nav items */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  {loading ? (
                    // Loading skeleton
                    <>
                      {staticNavItems.map((item) => (
                        <Button
                          key={item.label}
                          component={RouterLink}
                          to={item.path}
                          sx={{ 
                            color: 'text.primary',
                            fontWeight: 500,
                            px: 2,
                            '&:hover': { bgcolor: 'action.hover' }
                          }}
                        >
                          {item.label}
                        </Button>
                      ))}
                      <Skeleton variant="rounded" width={80} height={32} sx={{ mx: 1 }} />
                      <Skeleton variant="rounded" width={80} height={32} sx={{ mx: 1 }} />
                    </>
                  ) : (
                    // Loaded nav items
                    navItems.map((item, index) => (
                      item.dropdown ? (
                        // Item with dropdown
                        <Box key={item.label}>
                          <Button
                            onClick={(e) => handleMenuOpen(e, index)}
                            sx={{ 
                              color: 'text.primary',
                              fontWeight: 500,
                              px: 2,
                              '&:hover': { bgcolor: 'action.hover' }
                            }}
                            endIcon={<IconChevronDown size={16} />}
                          >
                            {item.label}
                          </Button>
                          <Menu
                            anchorEl={anchorEl}
                            open={openMenuIndex === index}
                            onClose={handleMenuClose}
                            MenuListProps={{
                              onMouseLeave: handleMenuClose
                            }}
                            anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                            transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                          >
                            {/* View all link */}
                            <MenuItem
                              component={RouterLink}
                              to={item.path}
                              onClick={handleMenuClose}
                              sx={{ fontWeight: 600 }}
                            >
                              View All {item.label}
                            </MenuItem>
                            {/* Subcategories */}
                            {item.dropdown.map((subItem) => (
                              <MenuItem
                                key={subItem.path}
                                component={RouterLink}
                                to={subItem.path}
                                onClick={handleMenuClose}
                              >
                                {subItem.label}
                              </MenuItem>
                            ))}
                          </Menu>
                        </Box>
                      ) : (
                        // Simple link
                        <Button
                          key={item.label}
                          component={RouterLink}
                          to={item.path}
                          sx={{ 
                            color: 'text.primary',
                            fontWeight: 500,
                            px: 2,
                            '&:hover': { bgcolor: 'action.hover' }
                          }}
                        >
                          {item.label}
                        </Button>
                      )
                    ))
                  )}
                </Box>
            </Box>
          )}

          {/* Auth buttons - Absolute Right */}
          {!isMobile && (
            <Box sx={{ 
              position: 'absolute', 
              right: { xs: 16, sm: 24, md: 32 },
              display: 'flex', 
              alignItems: 'center', 
              gap: 1 
            }}>
                  {isAuthenticated ? (
                    // Authenticated user UI
                    <>
                      <Button
                        component={RouterLink}
                        to="/dashboard/posts/new"
                        variant="text"
                        size="small"
                        startIcon={
                          <Box
                            sx={{
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              width: 28,
                              height: 28,
                              border: '1px solid',
                              borderColor: 'grey.400',
                              borderRadius: 1.5,
                            }}
                          >
                            <IconPencil size={16} stroke={1.5} />
                          </Box>
                        }
                        sx={{ 
                          color: 'text.primary',
                          fontWeight: 400,
                          fontSize: '0.9rem',
                          px: 0.5,
                          py: 0.5,
                          '& .MuiButton-startIcon': {
                            marginRight: 0.75
                          }
                        }}
                      >
                        Write
                      </Button>
                      
                      {/* Notification Bell */}
                      <IconButton
                        component={RouterLink}
                        to="/dashboard/notifications"
                        size="small"
                        sx={{ color: 'text.secondary' }}
                      >
                        <IconBell size={22} stroke={1.5} />
                      </IconButton>
                      
                      {/* User Avatar */}
                      <IconButton
                        onClick={handleUserMenuOpen}
                        size="small"
                      >
                        <Avatar
                          src={user?.avatar}
                          alt={user?.full_name || user?.username}
                          sx={{
                            width: 32,
                            height: 32,
                            bgcolor: 'grey.200',
                            border: '2px solid',
                            borderColor: 'primary.main'
                          }}
                        >
                          <IconUser size={18} color="#666" />
                        </Avatar>
                      </IconButton>
                      <Menu
                        anchorEl={userAnchorEl}
                        open={Boolean(userAnchorEl)}
                        onClose={handleUserMenuClose}
                        onClick={handleUserMenuClose}
                        PaperProps={{
                          elevation: 3,
                          sx: {
                            minWidth: 180,
                            mt: 1.5,
                            borderRadius: 2
                          }
                        }}
                        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
                      >
                        <MenuItem component={RouterLink} to="/dashboard">
                          <ListItemIcon>
                            <IconDashboard size={18} />
                          </ListItemIcon>
                          Dashboard
                        </MenuItem>
                        <MenuItem component={RouterLink} to="/dashboard/profile">
                          <ListItemIcon>
                            <IconUser size={18} />
                          </ListItemIcon>
                          Profile
                        </MenuItem>
                        <Divider />
                        <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
                          <ListItemIcon>
                            <IconLogout size={18} color="currentColor" />
                          </ListItemIcon>
                          Logout
                        </MenuItem>
                      </Menu>
                    </>
                  ) : (
                    // Guest user UI
                    <>
                      <Button
                        component={RouterLink}
                        to="/auth/login"
                        variant="text"
                        size="small"
                        sx={{ 
                          color: 'text.primary',
                          fontWeight: 500,
                          px: 1.5,
                          py: 0.5
                        }}
                      >
                        Sign In
                      </Button>
                      <Button
                        component={RouterLink}
                        to="/auth/register"
                        variant="contained"
                        size="small"
                        sx={{
                          bgcolor: 'secondary.main',
                          color: 'white',
                          px: 2,
                          py: 0.5,
                          '&:hover': { bgcolor: 'secondary.dark' }
                        }}
                      >
                        Get Started
                      </Button>
                    </>
                  )}
            </Box>
          )}

          {/* Mobile Menu Button */}
          {isMobile && (
            <IconButton
              onClick={handleDrawerToggle}
              sx={{ color: 'text.primary' }}
            >
              {mobileOpen ? <IconX /> : <IconMenu2 />}
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        sx={{
          '& .MuiDrawer-paper': {
            width: 280,
            bgcolor: 'background.default'
          }
        }}
      >
        <Box sx={{ p: 2 }}>
          <List>
            {loading ? (
              // Loading skeleton for mobile
              <>
                {staticNavItems.map((item) => (
                  <ListItem key={item.label} disablePadding>
                    <ListItemButton
                      component={RouterLink}
                      to={item.path}
                      onClick={handleDrawerToggle}
                    >
                      <ListItemText primary={item.label} />
                    </ListItemButton>
                  </ListItem>
                ))}
                <ListItem disablePadding>
                  <Skeleton variant="text" width="60%" height={40} sx={{ mx: 2 }} />
                </ListItem>
                <ListItem disablePadding>
                  <Skeleton variant="text" width="70%" height={40} sx={{ mx: 2 }} />
                </ListItem>
              </>
            ) : (
              // Loaded mobile nav items
              navItems.map((item, index) => (
                <Box key={item.label}>
                  {item.dropdown ? (
                    // Item with expandable dropdown
                    <>
                      <ListItem disablePadding>
                        <ListItemButton onClick={() => handleMobileExpand(index)}>
                          <ListItemText primary={item.label} />
                          {mobileExpandedIndex === index 
                            ? <IconChevronDown size={18} /> 
                            : <IconChevronRight size={18} />
                          }
                        </ListItemButton>
                      </ListItem>
                      <Collapse in={mobileExpandedIndex === index} timeout="auto" unmountOnExit>
                        <List component="div" disablePadding>
                          {/* View all link */}
                          <ListItemButton
                            component={RouterLink}
                            to={item.path}
                            onClick={handleDrawerToggle}
                            sx={{ pl: 4 }}
                          >
                            <ListItemText 
                              primary={`All ${item.label}`} 
                              primaryTypographyProps={{ fontWeight: 600 }}
                            />
                          </ListItemButton>
                          {/* Subcategories */}
                          {item.dropdown.map((subItem) => (
                            <ListItemButton
                              key={subItem.path}
                              component={RouterLink}
                              to={subItem.path}
                              onClick={handleDrawerToggle}
                              sx={{ pl: 4 }}
                            >
                              <ListItemText primary={subItem.label} />
                            </ListItemButton>
                          ))}
                        </List>
                      </Collapse>
                    </>
                  ) : (
                    // Simple link
                    <ListItem disablePadding>
                      <ListItemButton
                        component={RouterLink}
                        to={item.path}
                        onClick={handleDrawerToggle}
                      >
                        <ListItemText primary={item.label} />
                      </ListItemButton>
                    </ListItem>
                  )}
                </Box>
              ))
            )}
            
            {/* Mobile auth buttons - conditional based on auth state */}
            {isAuthenticated ? (
              // Authenticated user mobile UI
              <>
                <ListItem disablePadding sx={{ mt: 2 }}>
                  <Button
                    fullWidth
                    component={RouterLink}
                    to="/dashboard/posts/new"
                    variant="outlined"
                    startIcon={<IconPencil size={18} />}
                    sx={{ 
                      borderColor: 'primary.main',
                      color: 'primary.main',
                      py: 1
                    }}
                    onClick={handleDrawerToggle}
                  >
                    Write
                  </Button>
                </ListItem>
                <ListItem disablePadding sx={{ mt: 1 }}>
                  <Button
                    fullWidth
                    component={RouterLink}
                    to="/dashboard"
                    variant="contained"
                    startIcon={<IconDashboard size={18} />}
                    sx={{
                      bgcolor: 'primary.main',
                      color: 'white',
                      py: 1,
                      '&:hover': { bgcolor: 'primary.dark' }
                    }}
                    onClick={handleDrawerToggle}
                  >
                    Dashboard
                  </Button>
                </ListItem>
                <ListItem disablePadding sx={{ mt: 1 }}>
                  <Button
                    fullWidth
                    variant="text"
                    startIcon={<IconLogout size={18} />}
                    sx={{ 
                      color: 'error.main',
                      py: 1
                    }}
                    onClick={() => {
                      handleDrawerToggle();
                      logout();
                    }}
                  >
                    Logout
                  </Button>
                </ListItem>
              </>
            ) : (
              // Guest user mobile UI
              <>
                <ListItem disablePadding sx={{ mt: 2 }}>
                  <Button
                    fullWidth
                    component={RouterLink}
                    to="/auth/login"
                    variant="outlined"
                    sx={{ 
                      borderColor: 'grey.300',
                      color: 'text.primary',
                      py: 1
                    }}
                    onClick={handleDrawerToggle}
                  >
                    Sign In
                  </Button>
                </ListItem>
                <ListItem disablePadding sx={{ mt: 1 }}>
                  <Button
                    fullWidth
                    component={RouterLink}
                    to="/auth/register"
                    variant="contained"
                    sx={{
                      bgcolor: 'secondary.main',
                      color: 'white',
                      py: 1,
                      '&:hover': { bgcolor: 'secondary.dark' }
                    }}
                    onClick={handleDrawerToggle}
                  >
                    Get Started
                  </Button>
                </ListItem>
              </>
            )}
          </List>
        </Box>
      </Drawer>
    </>
  );
}
