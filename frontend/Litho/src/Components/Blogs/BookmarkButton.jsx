import React, { useState, memo } from 'react'
import PropTypes from "prop-types"

// Libraries
import { m } from "framer-motion"

// API & Auth
import { useBookmark } from '../../api/usePosts'
import useAuth from '../../api/useAuth'

// Animation
import { fadeIn } from '../../Functions/GlobalAnimations'

// CSS
import "../../Assets/scss/components/_bookmark-button.scss"

const BookmarkButton = (props) => {
  const { 
    postUuid, 
    isBookmarked: initialBookmarked = false,
    className,
    showTooltip = true,
    size = "md",
    variant = "default",
    onBookmarkChange,
    ...restProps 
  } = props;

  const [isBookmarked, setIsBookmarked] = useState(initialBookmarked);
  const [showTooltipText, setShowTooltipText] = useState(false);
  
  const { isAuthenticated } = useAuth();
  const { toggleBookmark, loading, error } = useBookmark();

  // Dynamic styling with CSS custom properties
  const style = {
    "--gradient-color": typeof(props.themeColor) === "object" 
      ? `linear-gradient(45deg, ${props.themeColor[0]}, ${props.themeColor[1]})` 
      : props.themeColor,
    "--brand-color": props.brandColor,
  }

  const handleBookmarkClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      // You could show a login modal here
      console.warn('User must be authenticated to bookmark posts');
      return;
    }

    if (loading) return;

    try {
      const result = await toggleBookmark(postUuid);
      const newBookmarkState = result; // API returns true if bookmarked, false if unbookmarked
      setIsBookmarked(newBookmarkState);
      
      if (onBookmarkChange) {
        onBookmarkChange(newBookmarkState);
      }
    } catch (err) {
      console.error('Error toggling bookmark:', err);
      // Could show an error toast here
    }
  };

  const getButtonClasses = () => {
    let classes = `bookmark-button bookmark-button-${size} bookmark-button-${variant}`;
    
    if (isBookmarked) {
      classes += ' bookmarked';
    }
    
    if (loading) {
      classes += ' loading';
    }
    
    if (!isAuthenticated) {
      classes += ' disabled';
    }
    
    if (className) {
      classes += ` ${className}`;
    }
    
    return classes;
  };

  const getIconClasses = () => {
    if (loading) {
      return 'feather-loader animate-spin';
    }
    
    return isBookmarked ? 'feather-bookmark-filled' : 'feather-bookmark';
  };

  const getTooltipText = () => {
    if (!isAuthenticated) {
      return 'Login to bookmark';
    }
    
    if (loading) {
      return 'Updating...';
    }
    
    return isBookmarked ? 'Remove bookmark' : 'Add bookmark';
  };

  return (
    <m.button
      type="button"
      className={getButtonClasses()}
      onClick={handleBookmarkClick}
      disabled={loading || !isAuthenticated}
      style={style}
      onMouseEnter={() => setShowTooltipText(true)}
      onMouseLeave={() => setShowTooltipText(false)}
      aria-label={getTooltipText()}
      {...fadeIn}
      {...restProps}
    >
      <i className={getIconClasses()}></i>
      
      {showTooltip && showTooltipText && (
        <m.span 
          className="bookmark-tooltip"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {getTooltipText()}
        </m.span>
      )}
      
      {error && (
        <m.span 
          className="bookmark-error"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
        >
          Error!
        </m.span>
      )}
    </m.button>
  )
}

BookmarkButton.defaultProps = {
  className: "",
  isBookmarked: false,
  showTooltip: true,
  size: "md",
  variant: "default"
}

BookmarkButton.propTypes = {
  postUuid: PropTypes.string.isRequired,
  isBookmarked: PropTypes.bool,
  className: PropTypes.string,
  showTooltip: PropTypes.bool,
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  variant: PropTypes.oneOf(['default', 'outline', 'ghost']),
  themeColor: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
  brandColor: PropTypes.string,
  onBookmarkChange: PropTypes.func,
}

export default memo(BookmarkButton)