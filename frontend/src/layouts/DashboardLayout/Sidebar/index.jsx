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
  padding: theme.spacing(1, 2),
  minHeight: 48
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

  // Whether sidebar is in collapsed icon-only mode
  const isCollapsed = !open && !isMobile;

  // Render menu item
  const renderMenuItem = (item, depth = 0) => {
    const Icon = iconMap[item.icon];
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expanded[item.id] || isGroupActive(item.children);
    const active = item.url ? isActive(item.url) : isGroupActive(item.children);

    return (
      <Box key={item.id}>
        <ListItem disablePadding sx={{ px: isCollapsed ? 0.5 : 1 }}>
          <ListItemButton
            onClick={() => {
              if (hasChildren) {
                if (isCollapsed) {
                  // In collapsed mode, navigate to first child
                  if (item.children[0]?.url) handleNavigate(item.children[0].url);
                } else {
                  handleExpand(item.id);
                }
              } else if (item.url) {
                handleNavigate(item.url);
              }
            }}
            sx={{
              borderRadius: 1,
              mb: 0.25,
              py: 0.5,
              px: isCollapsed ? 0 : 1.5,
              pl: isCollapsed ? 0 : (depth > 0 ? 3.5 : 1.5),
              justifyContent: isCollapsed ? 'center' : 'flex-start',
              backgroundColor: active ? dashboardTokens.sidebar.activeBackground : 'transparent',
              '&:hover': {
                backgroundColor: dashboardTokens.sidebar.hoverBackground
              }
            }}
            title={isCollapsed ? item.title : undefined}
          >
            {Icon && (
              <ListItemIcon sx={{ color: 'inherit', minWidth: isCollapsed ? 0 : 28, justifyContent: 'center' }}>
                <Icon size={18} />
              </ListItemIcon>
            )}
            {!isCollapsed && (
              <ListItemText
                primary={item.title}
                primaryTypographyProps={{
                  fontSize: 13,
                  fontWeight: active ? 600 : 400
                }}
              />
            )}
            {!isCollapsed && hasChildren && (
              isExpanded ? <IconChevronDown size={16} /> : <IconChevronRight size={16} />
            )}
          </ListItemButton>
        </ListItem>

        {/* Children (hidden when collapsed) */}
        {hasChildren && !isCollapsed && (
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
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: 1,
              backgroundColor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}
          >
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#fff' }}>
              C
            </Typography>
          </Box>
          {(open || isMobile) && (
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'text.primary' }}>
              CraftyXHub
            </Typography>
          )}
        </Box>
        {isMobile && (
          <IconButton onClick={onMobileClose} size="small" sx={{ color: 'text.primary' }}>
            <IconX size={20} />
          </IconButton>
        )}
      </LogoSection>

      <Divider sx={{ borderColor: dashboardTokens.sidebar.divider }} />

      {/* Navigation */}
      <Box sx={{ py: 1, overflowY: 'auto', flex: 1 }}>
        <List disablePadding>
          {filteredMenu.map((item) => renderMenuItem(item))}
        </List>
      </Box>

      {/* Collapse Toggle (desktop only) */}
      {!isMobile && (
        <>
          <Divider sx={{ borderColor: dashboardTokens.sidebar.divider }} />
          <Box sx={{ p: 1, display: 'flex', justifyContent: open ? 'flex-end' : 'center' }}>
            <IconButton
              onClick={onToggle}
              size="small"
              sx={{
                color: 'text.secondary',
                '&:hover': { color: 'text.primary', backgroundColor: dashboardTokens.sidebar.hoverBackground }
              }}
              title={open ? 'Collapse sidebar' : 'Expand sidebar'}
            >
              {open ? <IconChevronLeft size={18} /> : <IconChevronRight size={18} />}
            </IconButton>
          </Box>
        </>
      )}
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
