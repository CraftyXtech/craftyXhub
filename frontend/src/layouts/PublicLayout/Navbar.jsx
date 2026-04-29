import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import {
  Avatar,
  Box,
  Button,
  Collapse,
  Divider,
  Drawer,
  IconButton,
  InputAdornment,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Skeleton,
  Stack,
  TextField,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  IconArrowRight,
  IconBell,
  IconBrandFacebook,
  IconBrandInstagram,
  IconBrandLinkedin,
  IconBrandX,
  IconChevronDown,
  IconChevronRight,
  IconDashboard,
  IconLogout,
  IconMenu2,
  IconPencil,
  IconSearch,
  IconUser,
  IconX,
} from '@tabler/icons-react';

import Logo from '@/components/Logo';
import { useAuth } from '@/api/AuthProvider';
import { getCategories } from '@/api/services/categoryService';
import { getBreakingPosts } from '@/api/services/postService';
import { getPublicSettings } from '@/api/services/settingsService';
import { getImageUrl } from '@/api/utils/imageUrl';

const staticNavItems = [{ label: 'Home', path: '/' }];

const defaultSettings = {
  identity_label: 'MARKET WATCH',
  breaking_label: 'BREAKING',
  daily_brief_label: 'DAILY BRIEF',
  daily_brief_url: '/brief',
  ad_slot: {
    enabled: true,
    mode: 'placeholder',
    label: 'ADVERTISEMENT',
    image_url: '',
    target_url: '',
    background_color: '#F4F6F8',
  },
  social_links: [
    { platform: 'x', label: 'X', url: '' },
    { platform: 'facebook', label: 'Facebook', url: '' },
    { platform: 'instagram', label: 'Instagram', url: '' },
    { platform: 'linkedin', label: 'LinkedIn', url: '' },
  ],
  active_spotlight: {
    label: 'AI PULSE',
    target_url: '/category/ai',
    theme: 'emerald',
    icon: 'sparkles',
  },
  market_strip: [],
};

const MOCK_MARKET_PATTERN = [0, 1, -1, 2, -1, 1, 0, -2];

const socialIconMap = {
  x: IconBrandX,
  twitter: IconBrandX,
  facebook: IconBrandFacebook,
  instagram: IconBrandInstagram,
  linkedin: IconBrandLinkedin,
};

const spotlightThemeMap = {
  emerald: { bgcolor: '#1C7A5B', color: '#FFFFFF' },
  violet: { bgcolor: '#352B7A', color: '#FFFFFF' },
  amber: { bgcolor: '#B76A18', color: '#FFFFFF' },
  crimson: { bgcolor: '#A92E3B', color: '#FFFFFF' },
  slate: { bgcolor: '#1F2937', color: '#FFFFFF' },
  blue: { bgcolor: '#1D5FA8', color: '#FFFFFF' },
};

const transformCategoriesToNav = (apiCategories) => {
  if (!Array.isArray(apiCategories)) return [];

  return apiCategories.map((category) => ({
    label: category.name,
    path: `/category/${category.slug}`,
    dropdown: category.subcategories?.length
      ? category.subcategories.map((sub) => ({
          label: sub.name,
          path: `/category/${sub.slug}`,
        }))
      : null,
  }));
};

const formatMarketPrice = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '--';
  }

  const numericValue = Number(value);
  if (Math.abs(numericValue) >= 1000) {
    return numericValue.toLocaleString('en-US', { maximumFractionDigits: 2 });
  }
  if (Math.abs(numericValue) >= 1) {
    return numericValue.toLocaleString('en-US', { maximumFractionDigits: 2 });
  }
  return numericValue.toLocaleString('en-US', { maximumFractionDigits: 4 });
};

const formatPercentChange = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return null;
  }
  return `${Number(value) > 0 ? '+' : ''}${Number(value).toFixed(2)}%`;
};

const buildSearchPath = (query) => `/search?q=${encodeURIComponent(query.trim())}`;

const getNavigationProps = (url) => {
  if (!url) {
    return {};
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return {
      component: 'a',
      href: url,
      target: '_blank',
      rel: 'noopener noreferrer',
    };
  }
  return {
    component: RouterLink,
    to: url,
  };
};

const getHrefButtonProps = (url, fallback = '/brief') => ({
  component: 'a',
  href: url || fallback,
});

const getMockSwingPercent = (item, index, tick) => {
  const symbol = `${item.symbol || item.label || index}`;
  const signature = Array.from(symbol).reduce((total, char) => total + char.charCodeAt(0), 0);
  const direction = MOCK_MARKET_PATTERN[(tick + index + signature) % MOCK_MARKET_PATTERN.length];

  if (symbol.includes('BTC')) return direction * 0.09;
  if (symbol.includes('ETH')) return direction * 0.07;
  if (symbol.includes('/')) return direction * 0.025;
  return direction * 0.05;
};

const animateMockMarketStrip = (items, tick) => {
  if (!tick) {
    return items;
  }

  return items.map((item, index) => {
    if (!item?.is_mock) {
      return item;
    }

    const basePrice = Number(item.price);
    const baseChange = Number(item.change ?? 0);
    const basePercent = Number(item.percent_change ?? 0);
    if (!Number.isFinite(basePrice)) {
      return item;
    }

    const previousClose = Number.isFinite(baseChange)
      ? basePrice - baseChange
      : basePercent
        ? basePrice / (1 + (basePercent / 100))
        : basePrice;
    const swingPercent = getMockSwingPercent(item, index, tick);
    const nextPercent = Number((basePercent + swingPercent).toFixed(2));
    const nextPrice = previousClose * (1 + (nextPercent / 100));
    const nextChange = nextPrice - previousClose;

    return {
      ...item,
      price: nextPrice < 10 ? Number(nextPrice.toFixed(4)) : Number(nextPrice.toFixed(2)),
      change: Math.abs(nextChange) < 10 ? Number(nextChange.toFixed(4)) : Number(nextChange.toFixed(2)),
      percent_change: nextPercent,
      is_up: nextPercent >= 0,
    };
  });
};

function MarketChip({ item, pulseKey = 0 }) {
  const tone = item.is_up === false ? 'error' : item.is_up === true ? 'success' : 'info';
  const toneMap = {
    success: {
      bgcolor: 'rgba(25, 135, 84, 0.18)',
      color: '#B8FFD8',
    },
    error: {
      bgcolor: 'rgba(220, 53, 69, 0.16)',
      color: '#FFD1D7',
    },
    info: {
      bgcolor: 'rgba(255,255,255,0.08)',
      color: 'rgba(255,255,255,0.84)',
    },
  };
  const colors = toneMap[tone];
  const percentChange = formatPercentChange(item.percent_change);

  return (
    <Box
      sx={{
        px: 1.25,
        py: 0.7,
        borderRadius: 1.25,
        bgcolor: colors.bgcolor,
        color: colors.color,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 0.75,
        minWidth: 'fit-content',
        whiteSpace: 'nowrap',
        transition: 'transform 220ms ease, box-shadow 220ms ease, background-color 220ms ease',
        '@keyframes marketChipPulse': {
          '0%': { transform: 'scale(1)', boxShadow: '0 0 0 rgba(0,0,0,0)' },
          '45%': { transform: 'scale(1.04)', boxShadow: '0 10px 24px rgba(0,0,0,0.18)' },
          '100%': { transform: 'scale(1)', boxShadow: '0 0 0 rgba(0,0,0,0)' },
        },
        animation: item.is_mock && pulseKey > 0 ? 'marketChipPulse 560ms ease' : 'none',
      }}
    >
      <Typography variant="caption" sx={{ fontWeight: 800, letterSpacing: 0.3, color: 'inherit' }}>
        {item.label}
      </Typography>
      <Typography variant="caption" sx={{ fontWeight: 700, color: 'inherit', fontVariantNumeric: 'tabular-nums' }}>
        {formatMarketPrice(item.price)}
      </Typography>
      {percentChange && (
        <Typography
          variant="caption"
          sx={{ color: 'inherit', opacity: item.is_stale ? 0.72 : 1, fontVariantNumeric: 'tabular-nums' }}
        >
          {percentChange}
        </Typography>
      )}
    </Box>
  );
}

function BreakingTicker({ label, posts }) {
  if (!posts.length) return null;

  const loopPosts = [...posts, ...posts];

  return (
    <Box
      sx={{
        bgcolor: '#D62839',
        borderBottom: '1px solid rgba(0,0,0,0.06)',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          maxWidth: 'none',
          mx: 'auto',
          px: { xs: 2, md: 6 },
          py: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          minHeight: 48,
        }}
      >
        <Box
          sx={{
            px: 1.5,
            py: 0.6,
            borderRadius: 1,
            bgcolor: '#352B7A',
            color: 'white',
            fontSize: 12,
            fontWeight: 800,
            letterSpacing: 1,
            flexShrink: 0,
          }}
        >
          {label}
        </Box>

        <Box sx={{ position: 'relative', overflow: 'hidden', flex: 1 }}>
          <Stack
            direction="row"
            spacing={4}
            sx={{
              width: 'max-content',
              minWidth: '200%',
              color: 'white',
              '@keyframes breakingTickerScroll': {
                '0%': { transform: 'translateX(0)' },
                '100%': { transform: 'translateX(-50%)' },
              },
              animation: 'breakingTickerScroll 28s linear infinite',
            }}
          >
            {loopPosts.map((post, index) => (
              <Typography
                key={`${post.uuid}-${index}`}
                component={RouterLink}
                to={`/post/${post.slug}`}
                sx={{
                  color: 'inherit',
                  textDecoration: 'none',
                  fontWeight: 700,
                  minWidth: 'max-content',
                  '&:hover': { textDecoration: 'underline' },
                }}
              >
                {post.title}
              </Typography>
            ))}
          </Stack>
        </Box>
      </Box>
    </Box>
  );
}

function AdvertisementBand({ adSlot }) {
  if (!adSlot?.enabled) return null;

  const imageUrl = getImageUrl(adSlot.image_url);
  const content = adSlot.mode === 'image' && adSlot.image_url ? (
    <Box
      component="img"
      src={imageUrl}
      alt={adSlot.label || 'Advertisement'}
      sx={{
        width: '100%',
        maxHeight: { xs: 120, md: 160 },
        objectFit: 'cover',
        display: 'block',
      }}
    />
  ) : (
    <Box
      sx={{
        minHeight: { xs: 88, md: 132 },
        display: 'grid',
        placeItems: 'center',
        borderTop: '1px dashed rgba(23,24,28,0.12)',
        borderBottom: '1px dashed rgba(23,24,28,0.12)',
        color: '#8A95A5',
        fontSize: 13,
        letterSpacing: 1.2,
        textTransform: 'uppercase',
      }}
    >
      {adSlot.label || 'Advertisement'}
    </Box>
  );

  return (
    <Box sx={{ bgcolor: adSlot.background_color || '#F4F6F8' }}>
      <Box sx={{ maxWidth: 1280, mx: 'auto', px: { xs: 2, md: 3 } }}>
        {adSlot.target_url ? (
          <Box component="a" href={adSlot.target_url} target="_blank" rel="noopener noreferrer" sx={{ display: 'block' }}>
            {content}
          </Box>
        ) : (
          content
        )}
      </Box>
    </Box>
  );
}

export default function Navbar() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);
  const [categories, setCategories] = useState([]);
  const [settings, setSettings] = useState(defaultSettings);
  const [breakingPosts, setBreakingPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [anchorEl, setAnchorEl] = useState(null);
  const [openMenuIndex, setOpenMenuIndex] = useState(null);
  const [userAnchorEl, setUserAnchorEl] = useState(null);
  const [mobileExpandedIndex, setMobileExpandedIndex] = useState(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [marketPulseKey, setMarketPulseKey] = useState(0);

  useEffect(() => {
    const routeQuery = new URLSearchParams(location.search).get('q');
    if (location.pathname === '/search' && routeQuery) {
      setSearchQuery(routeQuery);
    }
  }, [location.pathname, location.search]);

  useEffect(() => {
    const loadHeader = async () => {
      try {
        setLoading(true);
        const [categoryData, publicSettings, breakingResponse] = await Promise.all([
          getCategories(),
          getPublicSettings(),
          getBreakingPosts({ limit: 8 }),
        ]);

        setCategories(transformCategoriesToNav(categoryData || []));
        setSettings({
          ...defaultSettings,
          ...(publicSettings || {}),
          ad_slot: { ...defaultSettings.ad_slot, ...(publicSettings?.ad_slot || {}) },
          social_links: publicSettings?.social_links?.length
            ? publicSettings.social_links
            : defaultSettings.social_links,
        });
        setBreakingPosts(breakingResponse?.posts || []);
      } catch (err) {
        console.error('Failed to load public masthead data:', err);
        setCategories([]);
        setSettings(defaultSettings);
        setBreakingPosts([]);
      } finally {
        setLoading(false);
      }
    };

    loadHeader();
  }, []);

  useEffect(() => {
    const hasMockMarkets = (settings.market_strip || []).some((item) => item?.is_mock);
    if (!hasMockMarkets) {
      setMarketPulseKey(0);
      return undefined;
    }

    setMarketPulseKey(0);
    const intervalId = window.setInterval(() => {
      setMarketPulseKey((current) => current + 1);
    }, 4200);

    return () => window.clearInterval(intervalId);
  }, [settings.market_strip]);

  const navItems = useMemo(() => [...staticNavItems, ...categories], [categories]);
  const visibleMarketStrip = useMemo(
    () => animateMockMarketStrip(settings.market_strip || [], marketPulseKey).slice(0, 4),
    [settings.market_strip, marketPulseKey],
  );

  const handleDrawerToggle = () => {
    setMobileOpen((open) => !open);
    setMobileExpandedIndex(null);
  };

  const handleMenuOpen = (event, index) => {
    setAnchorEl(event.currentTarget);
    setOpenMenuIndex(index);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setOpenMenuIndex(null);
  };

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

  const handleMobileExpand = (index) => {
    setMobileExpandedIndex((current) => (current === index ? null : index));
  };

  const handleSearchSubmit = (event) => {
    event.preventDefault();
    const trimmedQuery = searchQuery.trim();
    if (!trimmedQuery) return;
    navigate(buildSearchPath(trimmedQuery));
    setMobileSearchOpen(false);
  };

  const activeSpotlightStyles =
    spotlightThemeMap[settings.active_spotlight?.theme] || spotlightThemeMap.emerald;

  const socialLinks = (settings.social_links || []).filter((item) => item.url && socialIconMap[item.platform?.toLowerCase()]);

  return (
    <Box component="header">
      <Box sx={{ bgcolor: '#17181C', color: 'white' }}>
        <Stack
          direction={{ xs: 'column', lg: 'row' }}
          spacing={2}
          alignItems={{ xs: 'stretch', lg: 'center' }}
          sx={{
            maxWidth: 'none',
            mx: 'auto',
            px: { xs: 2, md: 6 },
            py: { xs: 1.25, md: 1 },
          }}
        >
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1.25}
            alignItems={{ xs: 'flex-start', sm: 'center' }}
            sx={{ flexShrink: 0 }}
          >
              <Box
                sx={{
                  px: 1.5,
                  py: 0.7,
                  borderRadius: 1,
                  bgcolor: '#D62839',
                  fontSize: 12,
                  fontWeight: 800,
                  letterSpacing: 0.9,
                  lineHeight: 1,
                  whiteSpace: 'nowrap',
                }}
              >
                {settings.identity_label}
              </Box>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.78)' }}>
                {new Date().toLocaleDateString('en-US', {
                  weekday: 'short',
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </Typography>
            </Stack>

            {visibleMarketStrip.length > 0 && (
              <Box sx={{ flex: 1, minWidth: 0, overflowX: 'auto', display: 'flex', alignItems: 'center' }}>
                <Stack direction="row" spacing={1} sx={{ pb: 0.2 }}>
                  {visibleMarketStrip.map((item) => (
                    <MarketChip key={`${item.symbol}-${item.label}`} item={item} pulseKey={marketPulseKey} />
                  ))}
                </Stack>
              </Box>
            )}

            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              justifyContent={{ xs: 'space-between', lg: 'flex-end' }}
              sx={{ flexShrink: 0 }}
            >
              {!isMobile && socialLinks.length > 0 && (
                <Stack direction="row" spacing={0.5}>
                  {socialLinks.map((social) => {
                    const Icon = socialIconMap[social.platform.toLowerCase()];
                    return (
                      <Tooltip key={`${social.platform}-${social.label}`} title={social.label}>
                        <IconButton
                          component="a"
                          href={social.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          size="small"
                          sx={{
                            color: 'rgba(255,255,255,0.76)',
                            border: '1px solid rgba(255,255,255,0.16)',
                            borderRadius: 1,
                            '&:hover': { color: 'white', bgcolor: 'rgba(255,255,255,0.08)' },
                          }}
                        >
                          <Icon size={16} />
                        </IconButton>
                      </Tooltip>
                    );
                  })}
                </Stack>
              )}

              {!isMobile && (
                isAuthenticated ? (
                  <>
                    <IconButton
                      component={RouterLink}
                      to="/dashboard/notifications"
                      size="small"
                      sx={{ color: 'rgba(255,255,255,0.78)' }}
                    >
                      <IconBell size={18} />
                    </IconButton>
                    <Button
                      component={RouterLink}
                      to="/dashboard"
                      size="small"
                      variant="contained"
                      sx={{ bgcolor: 'rgba(255,255,255,0.1)', color: 'white' }}
                    >
                      Dashboard
                    </Button>
                    <IconButton onClick={handleUserMenuOpen} size="small">
                      <Avatar src={user?.profile?.avatar || undefined} sx={{ width: 32, height: 32 }}>
                        {user?.full_name?.[0] || user?.username?.[0] || 'U'}
                      </Avatar>
                    </IconButton>
                  </>
                ) : (
                  <Stack direction="row" spacing={1}>
                    <Button component={RouterLink} to="/auth/login" size="small" sx={{ color: 'white' }}>
                      Log In
                    </Button>
                    <Button component={RouterLink} to="/auth/register" size="small" variant="contained" color="error">
                      Join
                    </Button>
                  </Stack>
                )
              )}
            </Stack>
        </Stack>
      </Box>

      <BreakingTicker label={settings.breaking_label} posts={breakingPosts} />
      <AdvertisementBand adSlot={settings.ad_slot} />

      <Box sx={{ bgcolor: 'white', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Box
          sx={{
            maxWidth: 'none',
            mx: 'auto',
            px: { xs: 2, md: 6 },
            py: { xs: 2, md: 2.5 },
          }}
        >
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            spacing={2}
            alignItems="center"
            justifyContent="space-between"
          >
            <Stack
              direction={{ xs: 'row', md: 'row' }}
              spacing={1}
              alignItems="center"
              sx={{ flex: 1, justifyContent: { xs: 'space-between', md: 'flex-start' } }}
            >
              {isMobile && (
                <IconButton onClick={handleDrawerToggle}>
                  {mobileOpen ? <IconX size={22} /> : <IconMenu2 size={22} />}
                </IconButton>
              )}
              <Button
                {...getHrefButtonProps(settings.daily_brief_url, '/brief')}
                variant="contained"
                color="error"
                sx={{
                  fontWeight: 700,
                  px: 3,
                }}
              >
                {settings.daily_brief_label}
              </Button>
            </Stack>

            <Box sx={{ display: 'flex', justifyContent: 'center', flex: 1 }}>
              <RouterLink to="/" style={{ display: 'inline-flex', alignItems: 'center' }}>
                <Logo />
              </RouterLink>
            </Box>

            <Stack
              direction={{ xs: 'row', md: 'row' }}
              spacing={1}
              alignItems="center"
              sx={{ flex: 1, justifyContent: { xs: 'stretch', md: 'flex-end' } }}
            >
              {settings.active_spotlight && (
                <Button
                  {...getNavigationProps(settings.active_spotlight.target_url)}
                  variant="contained"
                  endIcon={<IconArrowRight size={14} />}
                  sx={{
                    fontWeight: 800,
                    px: 3,
                    ...activeSpotlightStyles,
                    '&:hover': {
                      ...activeSpotlightStyles,
                      filter: 'brightness(0.94)',
                    },
                  }}
                >
                  {settings.active_spotlight.label}
                </Button>
              )}
            </Stack>
          </Stack>
        </Box>
      </Box>

      <Box
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: (currentTheme) => currentTheme.zIndex.appBar,
          bgcolor: '#000000',
          color: 'white',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <Box
          sx={{
            maxWidth: 1280,
            mx: 'auto',
            px: { xs: 2, md: 3 },
            minHeight: 60,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {isMobile ? (
            <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" sx={{ width: '100%' }}>
              <Typography variant="body2" sx={{ fontWeight: 800, letterSpacing: 1 }}>
                SECTIONS
              </Typography>
              <Stack direction="row" spacing={0.5} alignItems="center">
                <IconButton
                  onClick={() => setMobileSearchOpen(true)}
                  sx={{ color: 'white' }}
                  size="small"
                >
                  <IconSearch size={18} />
                </IconButton>
                <Button
                  onClick={handleDrawerToggle}
                  startIcon={mobileOpen ? <IconX size={16} /> : <IconMenu2 size={16} />}
                  sx={{ color: 'white' }}
                >
                  Browse
                </Button>
              </Stack>
            </Stack>
          ) : (
            <Stack direction="row" spacing={0.5} alignItems="center" useFlexGap flexWrap="wrap" justifyContent="center">
              {loading ? (
                <>
                  <Skeleton variant="rounded" width={80} height={32} sx={{ bgcolor: 'rgba(255,255,255,0.16)' }} />
                  <Skeleton variant="rounded" width={96} height={32} sx={{ bgcolor: 'rgba(255,255,255,0.16)' }} />
                  <Skeleton variant="rounded" width={88} height={32} sx={{ bgcolor: 'rgba(255,255,255,0.16)' }} />
                </>
              ) : (
                navItems.map((item, index) => (
                  item.dropdown ? (
                    <Box key={item.label}>
                      <Button
                        onClick={(event) => handleMenuOpen(event, index)}
                        endIcon={<IconChevronDown size={14} />}
                        sx={{
                          color: 'white',
                          fontWeight: 800,
                          letterSpacing: 0.5,
                          px: 1.5,
                        }}
                      >
                        {item.label}
                      </Button>
                      <Menu
                        anchorEl={anchorEl}
                        open={openMenuIndex === index}
                        onClose={handleMenuClose}
                        MenuListProps={{ onMouseLeave: handleMenuClose }}
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                        transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                      >
                        <MenuItem component={RouterLink} to={item.path} onClick={handleMenuClose} sx={{ fontWeight: 700 }}>
                          View All {item.label}
                        </MenuItem>
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
                    <Button
                      key={item.label}
                      component={RouterLink}
                      to={item.path}
                      sx={{
                        color: 'white',
                        fontWeight: 800,
                        letterSpacing: 0.5,
                        px: 1.5,
                      }}
                    >
                      {item.label}
                    </Button>
                  )
                ))
              )}
            </Stack>
          )}
        </Box>
      </Box>

      <Drawer anchor="left" open={mobileOpen} onClose={handleDrawerToggle}>
        <Box sx={{ width: 320, display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 2, py: 2 }}>
            <Logo showText={false} />
            <IconButton onClick={handleDrawerToggle}>
              <IconX size={22} />
            </IconButton>
          </Stack>
          <Divider />

          <Box sx={{ px: 2, py: 2 }}>
            <Button
              {...getHrefButtonProps(settings.daily_brief_url, '/brief')}
              variant="contained"
              color="error"
              fullWidth
              onClick={handleDrawerToggle}
            >
              {settings.daily_brief_label}
            </Button>
            {settings.active_spotlight && (
              <Button
                {...getNavigationProps(settings.active_spotlight.target_url)}
                variant="contained"
                fullWidth
                onClick={handleDrawerToggle}
                sx={{
                  mt: 1,
                  ...activeSpotlightStyles,
                  '&:hover': {
                    ...activeSpotlightStyles,
                    filter: 'brightness(0.94)',
                  },
                }}
              >
                {settings.active_spotlight.label}
              </Button>
            )}
          </Box>

          <Divider />
          <List sx={{ flexGrow: 1 }}>
            {navItems.map((item, index) => (
              <Box key={item.label}>
                <ListItem disablePadding>
                  {item.dropdown ? (
                    <ListItemButton onClick={() => handleMobileExpand(index)}>
                      <ListItemText primary={item.label} />
                      {mobileExpandedIndex === index ? <IconChevronDown size={18} /> : <IconChevronRight size={18} />}
                    </ListItemButton>
                  ) : (
                    <ListItemButton component={RouterLink} to={item.path} onClick={handleDrawerToggle}>
                      <ListItemText primary={item.label} />
                    </ListItemButton>
                  )}
                </ListItem>
                {item.dropdown && (
                  <Collapse in={mobileExpandedIndex === index} timeout="auto" unmountOnExit>
                    <List disablePadding>
                      <ListItem disablePadding>
                        <ListItemButton
                          component={RouterLink}
                          to={item.path}
                          onClick={handleDrawerToggle}
                          sx={{ pl: 4 }}
                        >
                          <ListItemText primary={`View All ${item.label}`} />
                        </ListItemButton>
                      </ListItem>
                      {item.dropdown.map((subItem) => (
                        <ListItem key={subItem.path} disablePadding>
                          <ListItemButton
                            component={RouterLink}
                            to={subItem.path}
                            onClick={handleDrawerToggle}
                            sx={{ pl: 4 }}
                          >
                            <ListItemText primary={subItem.label} />
                          </ListItemButton>
                        </ListItem>
                      ))}
                    </List>
                  </Collapse>
                )}
              </Box>
            ))}
          </List>

          <Divider />
          <Box sx={{ p: 2 }}>
            {isAuthenticated ? (
              <Stack spacing={1}>
                <Button component={RouterLink} to="/dashboard" variant="outlined" onClick={handleDrawerToggle}>
                  Dashboard
                </Button>
                <Button component={RouterLink} to="/dashboard/profile" variant="outlined" onClick={handleDrawerToggle}>
                  Profile
                </Button>
                <Button color="error" variant="contained" onClick={handleLogout}>
                  Log Out
                </Button>
              </Stack>
            ) : (
              <Stack spacing={1}>
                <Button component={RouterLink} to="/auth/login" variant="outlined" onClick={handleDrawerToggle}>
                  Log In
                </Button>
                <Button component={RouterLink} to="/auth/register" variant="contained" onClick={handleDrawerToggle}>
                  Join
                </Button>
              </Stack>
            )}
          </Box>
        </Box>
      </Drawer>

      <Drawer anchor="top" open={mobileSearchOpen} onClose={() => setMobileSearchOpen(false)}>
        <Box component="form" onSubmit={handleSearchSubmit} sx={{ p: 2 }}>
          <Stack direction="row" spacing={1}>
            <TextField
              autoFocus
              fullWidth
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Search coverage"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <IconSearch size={16} />
                  </InputAdornment>
                ),
              }}
            />
            <Button type="submit" variant="contained">
              Search
            </Button>
          </Stack>
        </Box>
      </Drawer>

      <Menu
        anchorEl={userAnchorEl}
        open={Boolean(userAnchorEl)}
        onClose={handleUserMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem component={RouterLink} to="/dashboard/profile" onClick={handleUserMenuClose}>
          <ListItemIcon><IconUser size={18} /></ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem component={RouterLink} to="/dashboard/posts" onClick={handleUserMenuClose}>
          <ListItemIcon><IconPencil size={18} /></ListItemIcon>
          My Posts
        </MenuItem>
        <MenuItem component={RouterLink} to="/dashboard" onClick={handleUserMenuClose}>
          <ListItemIcon><IconDashboard size={18} /></ListItemIcon>
          Dashboard
        </MenuItem>
        <MenuItem onClick={handleLogout}>
          <ListItemIcon><IconLogout size={18} /></ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
    </Box>
  );
}
