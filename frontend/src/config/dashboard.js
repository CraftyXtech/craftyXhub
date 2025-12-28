/**
 * Dashboard configuration constants
 */

// Layout dimensions
export const DRAWER_WIDTH = 260;
export const DRAWER_WIDTH_COLLAPSED = 72;
export const HEADER_HEIGHT = 64;
export const HEADER_HEIGHT_MOBILE = 56;

// Breakpoints
export const MOBILE_BREAKPOINT = 'md';

// Animation durations
export const DRAWER_TRANSITION = 225;

// Theme tokens for dashboard
export const dashboardTokens = {
  sidebar: {
    background: '#14213D', // Oxford Blue from palette
    textColor: '#FFFFFF',
    activeBackground: 'rgba(255, 255, 255, 0.1)',
    hoverBackground: 'rgba(255, 255, 255, 0.05)',
    divider: 'rgba(255, 255, 255, 0.12)'
  },
  header: {
    background: '#FFFFFF',
    shadow: '0 1px 4px rgba(0, 0, 0, 0.08)'
  }
};
