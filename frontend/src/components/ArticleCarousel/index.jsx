import { useRef, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Box, IconButton, useMediaQuery, useTheme } from '@mui/material';
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-react';

/**
 * ArticleCarousel - Reusable horizontal scrolling carousel with arrow navigation
 * 
 * Design: Maintains the same card sizing and spacing as the original Grid layout,
 * but enables horizontal scrolling with smooth arrow navigation.
 * 
 * @param {Array} items - Array of items to display
 * @param {Function} renderItem - Function to render each item (item, index) => JSX
 * @param {Object} itemsPerView - Responsive items per view { xs, sm, md, lg }
 * @param {number} gap - Gap between items in theme spacing units (default: 3)
 * @param {boolean} showArrows - Whether to show navigation arrows
 * @param {string} arrowPosition - 'inside' | 'outside' (default: 'outside')
 */
export default function ArticleCarousel({
  items = [],
  renderItem,
  itemsPerView = { xs: 1, sm: 2, md: 3, lg: 3 },
  gap = 3,
  showArrows = true,
  arrowPosition = 'outside',
}) {
  const theme = useTheme();
  const scrollContainerRef = useRef(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // Responsive breakpoints
  const isXs = useMediaQuery(theme.breakpoints.only('xs'));
  const isSm = useMediaQuery(theme.breakpoints.only('sm'));
  const isMd = useMediaQuery(theme.breakpoints.only('md'));

  // Get current items per view based on breakpoint
  const getCurrentItemsPerView = useCallback(() => {
    if (isXs) return itemsPerView.xs || 1;
    if (isSm) return itemsPerView.sm || 2;
    if (isMd) return itemsPerView.md || 3;
    return itemsPerView.lg || 3;
  }, [isXs, isSm, isMd, itemsPerView]);

  // Calculate card width as percentage
  const getCardWidth = useCallback(() => {
    const perView = getCurrentItemsPerView();
    const gapPx = theme.spacing(gap);
    // Account for gaps between cards
    // Total gap space = (perView - 1) * gapPx
    // Each card width = (100% - total gap space) / perView
    return `calc((100% - ${(perView - 1) * parseFloat(gapPx)}px) / ${perView})`;
  }, [getCurrentItemsPerView, gap, theme]);

  // Check scroll boundaries
  const checkScrollBoundaries = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const { scrollLeft, scrollWidth, clientWidth } = container;
    setCanScrollLeft(scrollLeft > 1);
    setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
  }, []);

  // Update scroll boundaries on mount and resize
  useEffect(() => {
    checkScrollBoundaries();

    const container = scrollContainerRef.current;
    if (container) {
      container.addEventListener('scroll', checkScrollBoundaries, { passive: true });
    }

    window.addEventListener('resize', checkScrollBoundaries);

    return () => {
      if (container) {
        container.removeEventListener('scroll', checkScrollBoundaries);
      }
      window.removeEventListener('resize', checkScrollBoundaries);
    };
  }, [checkScrollBoundaries, items]);

  // Re-check when items change
  useEffect(() => {
    // Small delay to allow DOM to update
    const timer = setTimeout(checkScrollBoundaries, 100);
    return () => clearTimeout(timer);
  }, [items, checkScrollBoundaries]);

  // Scroll by one "page" (number of visible items)
  const scroll = useCallback((direction) => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const perView = getCurrentItemsPerView();
    const gapPx = parseFloat(theme.spacing(gap));
    const containerWidth = container.clientWidth;
    
    // Calculate scroll distance (one card width + gap)
    const cardWidth = (containerWidth - (perView - 1) * gapPx) / perView;
    const scrollAmount = (cardWidth + gapPx) * Math.max(1, Math.floor(perView / 2));

    container.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth',
    });
  }, [getCurrentItemsPerView, gap, theme]);

  // Arrow button styles
  const arrowButtonStyles = {
    position: 'absolute',
    top: '50%',
    transform: 'translateY(-50%)',
    zIndex: 2,
    bgcolor: 'background.paper',
    boxShadow: 3,
    border: '1px solid',
    borderColor: 'divider',
    width: 44,
    height: 44,
    '&:hover': {
      bgcolor: 'primary.main',
      color: 'white',
      borderColor: 'primary.main',
    },
    '&.Mui-disabled': {
      bgcolor: 'grey.100',
      color: 'grey.400',
      opacity: 0.5,
    },
    transition: 'all 0.2s ease-in-out',
  };

  if (!items || items.length === 0) {
    return null;
  }

  const showLeftArrow = showArrows && canScrollLeft;
  const showRightArrow = showArrows && canScrollRight;
  const outsideOffset = arrowPosition === 'outside' ? -56 : 16;

  return (
    <Box
      sx={{
        position: 'relative',
        // Add padding for outside arrows
        mx: arrowPosition === 'outside' && showArrows ? { md: 7 } : 0,
      }}
    >
      {/* Left Arrow */}
      {showLeftArrow && (
        <IconButton
          onClick={() => scroll('left')}
          sx={{
            ...arrowButtonStyles,
            left: outsideOffset,
            display: { xs: 'none', md: 'flex' },
          }}
          aria-label="Scroll left"
        >
          <IconChevronLeft size={24} />
        </IconButton>
      )}

      {/* Scroll Container */}
      <Box
        ref={scrollContainerRef}
        sx={{
          display: 'flex',
          gap: gap,
          overflowX: 'auto',
          scrollBehavior: 'smooth',
          scrollSnapType: 'x mandatory',
          // Hide scrollbar but keep functionality
          scrollbarWidth: 'none', // Firefox
          msOverflowStyle: 'none', // IE/Edge
          '&::-webkit-scrollbar': {
            display: 'none', // Chrome/Safari/Opera
          },
          // Padding to prevent card shadows from being clipped
          py: 1,
          px: 0.5,
          mx: -0.5,
        }}
      >
        {items.map((item, index) => (
          <Box
            key={item.uuid || item.id || index}
            sx={{
              flex: '0 0 auto',
              width: getCardWidth(),
              minWidth: { xs: '280px', sm: 'auto' },
              scrollSnapAlign: 'start',
            }}
          >
            {renderItem(item, index)}
          </Box>
        ))}
      </Box>

      {/* Right Arrow */}
      {showRightArrow && (
        <IconButton
          onClick={() => scroll('right')}
          sx={{
            ...arrowButtonStyles,
            right: outsideOffset,
            display: { xs: 'none', md: 'flex' },
          }}
          aria-label="Scroll right"
        >
          <IconChevronRight size={24} />
        </IconButton>
      )}

      {/* Mobile swipe indicator dots (optional enhancement) */}
      {items.length > getCurrentItemsPerView() && (
        <Box
          sx={{
            display: { xs: 'flex', md: 'none' },
            justifyContent: 'center',
            mt: 2,
            gap: 0.5,
          }}
        >
          {Array.from({ length: Math.ceil(items.length / getCurrentItemsPerView()) }).map((_, i) => (
            <Box
              key={i}
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                bgcolor: 'grey.300',
              }}
            />
          ))}
        </Box>
      )}
    </Box>
  );
}

ArticleCarousel.propTypes = {
  items: PropTypes.array.isRequired,
  renderItem: PropTypes.func.isRequired,
  itemsPerView: PropTypes.shape({
    xs: PropTypes.number,
    sm: PropTypes.number,
    md: PropTypes.number,
    lg: PropTypes.number,
  }),
  gap: PropTypes.number,
  showArrows: PropTypes.bool,
  arrowPosition: PropTypes.oneOf(['inside', 'outside']),
};
