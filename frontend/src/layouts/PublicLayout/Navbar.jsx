import { useState } from 'react';
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
  useTheme,
  useMediaQuery
} from '@mui/material';
import { IconMenu2, IconX } from '@tabler/icons-react';
import Logo from '@/components/Logo';

const navItems = [
  { label: 'Home', path: '/' },
  { label: 'Blog', path: '/blog' },
  { label: 'About', path: '/about' },
  { label: 'Contact', path: '/contact' }
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
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
        <Container maxWidth="lg">
          <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
            {/* Logo */}
            <RouterLink to="/" style={{ display: 'flex', alignItems: 'center' }}>
              <Logo />
            </RouterLink>

            {/* Desktop Navigation */}
            {!isMobile && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {navItems.map((item) => (
                  <Button
                    key={item.label}
                    component={RouterLink}
                    to={item.path}
                    sx={{ 
                      color: 'text.primary',
                      fontWeight: 500,
                      px: 2,
                      '&:hover': {
                        bgcolor: 'action.hover'
                      }
                    }}
                  >
                    {item.label}
                  </Button>
                ))}
                <Button
                  component={RouterLink}
                  to="/auth/login"
                  variant="text"
                  sx={{ 
                    ml: 2,
                    color: 'text.primary',
                    fontWeight: 500
                  }}
                >
                  Sign In
                </Button>
                <Button
                  component={RouterLink}
                  to="/auth/register"
                  variant="contained"
                  sx={{
                    bgcolor: 'secondary.main',
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'secondary.dark'
                    }
                  }}
                >
                  Get Started
                </Button>
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
            {navItems.map((item) => (
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
            <ListItem disablePadding sx={{ mt: 2 }}>
              <Button
                fullWidth
                component={RouterLink}
                to="/auth/login"
                variant="outlined"
                sx={{ 
                  borderColor: 'grey.300',
                  color: 'text.primary'
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
                  '&:hover': {
                    bgcolor: 'secondary.dark'
                  }
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
