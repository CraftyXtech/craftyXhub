import React, { useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// MUI
import { styled, useTheme } from '@mui/material/styles';
import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Divider from '@mui/material/Divider';

// Icons
import {
  IconLayoutGrid,
  IconFileText,
  IconPhoto,
  IconSparkles,
  IconShieldCheck,
  IconSettings,
  IconChevronDown,
  IconChevronRight,
  IconChevronLeft,
  IconX,
  IconHome,
  IconBookmark
} from '@tabler/icons-react';

// Menu & Utils
import { menuItems } from '@/menu';
import { filterMenuByRole } from '@/utils/roleUtils';
import { useAuth } from '@/api/AuthProvider';
import { DRAWER_WIDTH, DRAWER_WIDTH_COLLAPSED, dashboardTokens } from '@/config/dashboard';

// Icon mapping
const iconMap = {
  IconHome,
  IconLayoutGrid,
  IconFileText,
  IconPhoto,
  IconSparkles,
  IconShieldCheck,
  IconSettings,
  IconBookmark
};

// Styled drawer
const StyledDrawer = styled(Drawer)(({ theme }) => ({
  '& .MuiDrawer-paper': {
    backgroundColor: dashboardTokens.sidebar.background,
    color: dashboardTokens.sidebar.textColor,
    borderRight: 'none',
    boxShadow: '2px 0 8px rgba(0, 0, 0, 0.1)'
  }
}));

// Logo section
const LogoSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2, 2.5),
  minHeight: 64
}));

/**
 * Sidebar Component
 * Role-filtered navigation drawer
 */
export default function Sidebar({ open, mobileOpen, isMobile, onToggle, onMobileClose }) {
  const theme = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  // Filter menu based on user role
  const filteredMenu = useMemo(() => {
    const userRole = user?.role || 'user';
    return filterMenuByRole(menuItems, userRole);
  }, [user?.role]);

  // Track expanded menu groups
  const [expanded, setExpanded] = useState({});

  const handleExpand = (id) => {
    setExpanded((prev) => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleNavigate = (url) => {
    navigate(url);
    if (isMobile) {
      onMobileClose();
    }
  };

  const isActive = (url) => location.pathname === url;
  const isGroupActive = (children) => children?.some((child) => location.pathname === child.url);

  // Render menu item
  const renderMenuItem = (item, depth = 0) => {
    const Icon = iconMap[item.icon];
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expanded[item.id] || isGroupActive(item.children);
    const active = item.url ? isActive(item.url) : isGroupActive(item.children);

    return (
      <Box key={item.id}>
        <ListItem disablePadding sx={{ px: 1.5 }}>
          <ListItemButton
            onClick={() => {
              if (hasChildren) {
                handleExpand(item.id);
              } else if (item.url) {
                handleNavigate(item.url);
              }
            }}
            sx={{
              borderRadius: 1,
              mb: 0.5,
              py: 1,
              pl: depth > 0 ? 4 : 2,
              backgroundColor: active ? dashboardTokens.sidebar.activeBackground : 'transparent',
              '&:hover': {
                backgroundColor: dashboardTokens.sidebar.hoverBackground
              }
            }}
          >
            {Icon && (
              <ListItemIcon sx={{ color: 'inherit', minWidth: 36 }}>
                <Icon size={20} />
              </ListItemIcon>
            )}
            <ListItemText
              primary={item.title}
              primaryTypographyProps={{
                fontSize: depth > 0 ? 13 : 14,
                fontWeight: active ? 600 : 400
              }}
            />
            {hasChildren && (
              isExpanded ? <IconChevronDown size={16} /> : <IconChevronRight size={16} />
            )}
          </ListItemButton>
        </ListItem>

        {/* Children */}
        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List disablePadding>
              {item.children.map((child) => renderMenuItem(child, depth + 1))}
            </List>
          </Collapse>
        )}
      </Box>
    );
  };

  // Drawer content
  const drawerContent = (
    <>
      {/* Logo */}
      <LogoSection>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: 1,
              backgroundColor: 'rgba(255,255,255,0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#fff' }}>
              C
            </Typography>
          </Box>
          {(open || isMobile) && (
            <Typography variant="h6" sx={{ fontWeight: 600, color: '#fff' }}>
              CraftyXHub
            </Typography>
          )}
        </Box>
        {isMobile && (
          <IconButton onClick={onMobileClose} size="small" sx={{ color: '#fff' }}>
            <IconX size={20} />
          </IconButton>
        )}
      </LogoSection>

      <Divider sx={{ borderColor: dashboardTokens.sidebar.divider }} />

      {/* Navigation */}
      <Box sx={{ py: 2, overflowY: 'auto', flex: 1 }}>
        <List disablePadding>
          {filteredMenu.map((item) => renderMenuItem(item))}
        </List>
      </Box>


    </>
  );

  // Mobile drawer (temporary)
  if (isMobile) {
    return (
      <StyledDrawer
        variant="temporary"
        open={mobileOpen}
        onClose={onMobileClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH
          }
        }}
      >
        {drawerContent}
      </StyledDrawer>
    );
  }

  // Desktop drawer (persistent)
  return (
    <StyledDrawer
      variant="permanent"
      open={open}
      sx={{
        width: open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: open ? DRAWER_WIDTH : DRAWER_WIDTH_COLLAPSED,
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen
          }),
          overflowX: 'hidden'
        }
      }}
    >
      {drawerContent}
    </StyledDrawer>
  );
}
