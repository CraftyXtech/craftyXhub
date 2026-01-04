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
    background: '#FFFFFF',
    textColor: '#14213D',
    activeBackground: 'rgba(20, 33, 61, 0.08)',
    hoverBackground: 'rgba(20, 33, 61, 0.04)',
    divider: 'rgba(0, 0, 0, 0.08)'
  },
  header: {
    background: '#FFFFFF',
    shadow: '0 1px 4px rgba(0, 0, 0, 0.08)'
  }
};
