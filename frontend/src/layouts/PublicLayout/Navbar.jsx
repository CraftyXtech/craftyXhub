import { useState, useEffect, useMemo } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Container,
  Box,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Menu,
  MenuItem,
  Collapse,
  Skeleton,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { IconMenu2, IconX, IconChevronDown, IconChevronRight } from '@tabler/icons-react';
import Logo from '@/components/Logo';
import { getCategories } from '@/api/services/categoryService';

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
  
  // Mobile accordion state
  const [mobileExpandedIndex, setMobileExpandedIndex] = useState(null);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

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
        <Container maxWidth="xl" sx={{ px: { xs: 2, md: 4 } }}>
          <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
            {/* Logo */}
            <RouterLink to="/" style={{ display: 'flex', alignItems: 'center' }}>
              <Logo />
            </RouterLink>

            {/* Desktop Navigation */}
            {!isMobile && (
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, ml: 4 }}>
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
                
                {/* Spacer to push auth buttons to far right */}
                <Box sx={{ flex: 1 }} />
                
                {/* Auth buttons */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
                </Box>
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
        </Container>
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
            
            {/* Mobile auth buttons */}
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
          </List>
        </Box>
      </Drawer>
    </>
  );
}
