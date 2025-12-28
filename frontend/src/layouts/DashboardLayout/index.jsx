import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';

// MUI
import { styled, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import useMediaQuery from '@mui/material/useMediaQuery';

// Components
import Sidebar from './Sidebar';
import Header from './Header';

// Config
import { DRAWER_WIDTH, DRAWER_WIDTH_COLLAPSED } from '@/config/dashboard';

// Styled main content area
const Main = styled('main', {
  shouldForwardProp: (prop) => prop !== 'open' && prop !== 'isMobile'
})(({ theme, open, isMobile }) => ({
  flexGrow: 1,
  width: isMobile ? '100%' : `calc(100% - ${open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED}px)`,
  minHeight: '100vh',
  backgroundColor: theme.palette.grey[100],
  padding: theme.spacing(3),
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  [theme.breakpoints.down('md')]: {
    width: '100%',
    padding: theme.spacing(2),
  }
}));

/**
 * Dashboard Layout
 * MUI-based layout with collapsible sidebar and header
 */
export default function DashboardLayout() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  // Sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close sidebar on mobile when viewport changes
  useEffect(() => {
    setSidebarOpen(!isMobile);
    if (!isMobile) {
      setMobileOpen(false);
    }
  }, [isMobile]);

  const handleSidebarToggle = () => {
    if (isMobile) {
      setMobileOpen(!mobileOpen);
    } else {
      setSidebarOpen(!sidebarOpen);
    }
  };

  const handleMobileClose = () => {
    setMobileOpen(false);
  };

  return (
    <Stack direction="row" sx={{ minHeight: '100vh' }}>
      {/* Sidebar */}
      <Sidebar
        open={sidebarOpen}
        mobileOpen={mobileOpen}
        isMobile={isMobile}
        onToggle={handleSidebarToggle}
        onMobileClose={handleMobileClose}
      />

      {/* Main Content Area */}
      <Main open={sidebarOpen} isMobile={isMobile}>
        {/* Header */}
        <Header onMenuClick={handleSidebarToggle} />
        
        {/* Toolbar spacer */}
        <Toolbar sx={{ minHeight: { xs: 56, md: 64 } }} />

        {/* Page Content */}
        <Box sx={{ py: 2 }}>
          <Outlet />
        </Box>
      </Main>
    </Stack>
  );
}
